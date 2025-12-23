#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动恢复机制模块

此模块提供了机器人系统在发生错误或故障时的自动检测、诊断和恢复功能，
包括连接恢复、错误清除、安全状态恢复和任务重试等机制。

作者: Nonead
日期: 2024
版本: 1.0
"""

import threading
import time
import logging
import traceback
from enum import Enum
from typing import Dict, List, Optional, Union, Callable, Tuple, Set

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入必要的模块
from URBasic.error_handling import RobotError, ErrorCategory, ErrorHandler, ErrorSeverity


class RecoveryAction(Enum):
    """恢复操作类型枚举"""
    RETRY_OPERATION = "retry_operation"
    RESET_ERROR = "reset_error"
    RECONNECT = "reconnect"
    MOVE_TO_SAFE_POSE = "move_to_safe_pose"
    RESTART_CONTROLLER = "restart_controller"
    ABORT_TASK = "abort_task"
    SWITCH_TO_BACKUP = "switch_to_backup"
    NOTIFY_OPERATOR = "notify_operator"
    CUSTOM_ACTION = "custom_action"


class RecoveryPolicy(Enum):
    """恢复策略枚举"""
    IMMEDIATE = "immediate"  # 立即尝试恢复
    DELAYED = "delayed"      # 延迟后恢复
    GRADUAL = "gradual"      # 渐进式恢复，从轻到重的恢复措施
    CONSERVATIVE = "conservative"  # 保守策略，先通知再恢复
    AGGRESSIVE = "aggressive"  # 激进策略，尝试所有可能的恢复措施


class RecoveryStatus(Enum):
    """恢复状态枚举"""
    IDLE = "idle"
    DETECTING = "detecting"
    DIAGNOSING = "diagnosing"
    RECOVERING = "recovering"
    RECOVERED = "recovered"
    FAILED = "failed"
    MANUAL_INTERVENTION_NEEDED = "manual_intervention_needed"


class RecoveryAttempt:
    """恢复尝试记录类"""
    
    def __init__(self, error: RobotError, action: RecoveryAction):
        """
        初始化恢复尝试记录
        
        Args:
            error: 错误对象
            action: 恢复操作
        """
        self.error = error
        self.action = action
        self.attempt_time = time.time()
        self.success = False
        self.duration = 0.0
        self.details = ""
    
    def complete(self, success: bool, duration: float, details: str = "") -> None:
        """
        完成恢复尝试记录
        
        Args:
            success: 是否成功
            duration: 持续时间(秒)
            details: 详细信息
        """
        self.success = success
        self.duration = duration
        self.details = details


class RecoveryActionHandler:
    """恢复操作处理器基类"""
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化恢复操作处理器
        
        Args:
            name: 处理器名称
            description: 处理器描述
        """
        self.name = name
        self.description = description
        self._lock = threading.RLock()
    
    def execute(self, context: Dict) -> bool:
        """
        执行恢复操作
        
        Args:
            context: 上下文信息字典，包含执行所需的对象和参数
            
        Returns:
            bool: 是否执行成功
        """
        raise NotImplementedError("子类必须实现execute方法")
    
    def can_execute(self, context: Dict) -> bool:
        """
        检查是否可以执行此恢复操作
        
        Args:
            context: 上下文信息字典
            
        Returns:
            bool: 是否可以执行
        """
        return True


class RetryOperationHandler(RecoveryActionHandler):
    """重试操作处理器"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        初始化重试操作处理器
        
        Args:
            max_retries: 最大重试次数
            retry_delay: 重试延迟(秒)
        """
        super().__init__("RetryOperation", "重试失败的操作")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def execute(self, context: Dict) -> bool:
        """
        执行重试操作
        
        Args:
            context: 上下文信息字典，需要包含 'operation' 函数和 'operation_args' 参数
            
        Returns:
            bool: 是否重试成功
        """
        operation = context.get('operation')
        operation_args = context.get('operation_args', {})
        
        if not callable(operation):
            logger.error("重试操作失败：上下文中缺少可调用的operation")
            return False
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"正在执行第 {attempt + 1}/{self.max_retries} 次重试操作")
                result = operation(**operation_args)
                logger.info(f"重试操作成功")
                return True
            except Exception as e:
                logger.error(f"重试操作失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        logger.error(f"所有重试尝试均失败")
        return False


class ResetErrorHandler(RecoveryActionHandler):
    """错误重置处理器"""
    
    def __init__(self):
        super().__init__("ResetError", "重置机器人错误")
    
    def execute(self, context: Dict) -> bool:
        """
        执行错误重置
        
        Args:
            context: 上下文信息字典，需要包含 'robot' 对象
            
        Returns:
            bool: 是否重置成功
        """
        robot = context.get('robot')
        
        if not robot:
            logger.error("错误重置失败：上下文中缺少robot对象")
            return False
        
        try:
            logger.info("正在重置机器人错误")
            # 尝试调用机器人的错误重置方法
            if hasattr(robot, 'reset_error'):
                robot.reset_error()
            elif hasattr(robot, 'clear_errors'):
                robot.clear_errors()
            else:
                logger.warning("机器人对象没有重置错误的方法")
                return False
            
            # 等待错误重置完成
            time.sleep(0.5)
            logger.info("机器人错误已重置")
            return True
        except Exception as e:
            logger.error(f"错误重置失败: {str(e)}")
            return False


class ReconnectHandler(RecoveryActionHandler):
    """重新连接处理器"""
    
    def __init__(self, max_attempts: int = 3, retry_delay: float = 2.0):
        """
        初始化重新连接处理器
        
        Args:
            max_attempts: 最大尝试次数
            retry_delay: 重试延迟(秒)
        """
        super().__init__("Reconnect", "重新连接机器人")
        self.max_attempts = max_attempts
        self.retry_delay = retry_delay
    
    def execute(self, context: Dict) -> bool:
        """
        执行重新连接
        
        Args:
            context: 上下文信息字典，需要包含 'connector' 对象或 'robot' 对象中的connector
            
        Returns:
            bool: 是否重新连接成功
        """
        connector = context.get('connector')
        robot = context.get('robot')
        
        # 尝试从robot获取connector
        if not connector and robot and hasattr(robot, 'connector'):
            connector = robot.connector
        
        if not connector:
            logger.error("重新连接失败：上下文中缺少connector对象")
            return False
        
        for attempt in range(self.max_attempts):
            try:
                logger.info(f"正在执行第 {attempt + 1}/{self.max_attempts} 次重新连接")
                
                # 首先关闭连接
                if hasattr(connector, 'close'):
                    connector.close()
                time.sleep(0.5)
                
                # 然后重新连接
                if hasattr(connector, 'connect'):
                    connector.connect()
                elif hasattr(connector, 'open'):
                    connector.open()
                else:
                    logger.warning("connector对象没有连接方法")
                    return False
                
                # 验证连接是否成功
                if hasattr(connector, 'is_connected'):
                    if connector.is_connected():
                        logger.info("重新连接成功")
                        return True
                else:
                    # 没有is_connected方法，假设连接成功
                    logger.info("重新连接操作完成")
                    return True
                    
            except Exception as e:
                logger.error(f"重新连接失败 (尝试 {attempt + 1}/{self.max_attempts}): {str(e)}")
                if attempt < self.max_attempts - 1:
                    time.sleep(self.retry_delay)
        
        logger.error("所有重新连接尝试均失败")
        return False


class MoveToSafePoseHandler(RecoveryActionHandler):
    """移动到安全位置处理器"""
    
    def __init__(self, safe_pose: Optional[List[float]] = None, 
                 speed: float = 0.1, acceleration: float = 0.1):
        """
        初始化安全位置移动处理器
        
        Args:
            safe_pose: 安全位置的位姿
            speed: 移动速度
            acceleration: 移动加速度
        """
        super().__init__("MoveToSafePose", "将机器人移动到安全位置")
        self.safe_pose = safe_pose or [0.0, 0.0, 0.5, 0.0, 3.14, 0.0]  # 默认安全位置
        self.speed = speed
        self.acceleration = acceleration
    
    def execute(self, context: Dict) -> bool:
        """
        执行移动到安全位置
        
        Args:
            context: 上下文信息字典，需要包含 'robot' 对象
            
        Returns:
            bool: 是否移动成功
        """
        robot = context.get('robot')
        
        if not robot:
            logger.error("移动到安全位置失败：上下文中缺少robot对象")
            return False
        
        try:
            # 从上下文获取安全位置，如果没有则使用默认值
            safe_pose = context.get('safe_pose', self.safe_pose)
            speed = context.get('speed', self.speed)
            acceleration = context.get('acceleration', self.acceleration)
            
            logger.info(f"正在将机器人移动到安全位置: {safe_pose}")
            
            # 尝试调用机器人的移动方法
            if hasattr(robot, 'movej'):
                robot.movej(safe_pose, speed, acceleration)
            elif hasattr(robot, 'movel'):
                robot.movel(safe_pose, speed, acceleration)
            else:
                logger.warning("机器人对象没有移动方法")
                return False
            
            logger.info("机器人已成功移动到安全位置")
            return True
        except Exception as e:
            logger.error(f"移动到安全位置失败: {str(e)}")
            return False


class NotifyOperatorHandler(RecoveryActionHandler):
    """通知操作员处理器"""
    
    def __init__(self):
        super().__init__("NotifyOperator", "通知操作员需要手动干预")
    
    def execute(self, context: Dict) -> bool:
        """
        执行操作员通知
        
        Args:
            context: 上下文信息字典，包含通知所需的信息
            
        Returns:
            bool: 通知是否成功
        """
        error = context.get('error')
        recovery_status = context.get('recovery_status')
        
        try:
            logger.warning("=== 需要手动干预 ===")
            logger.warning(f"错误类型: {error.__class__.__name__ if error else 'Unknown'}")
            logger.warning(f"错误信息: {str(error) if error else 'No error information'}")
            logger.warning(f"恢复状态: {recovery_status}")
            logger.warning(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.warning(f"建议操作: 请检查机器人状态，排除故障后重启系统")
            logger.warning("==================")
            
            # 可以扩展为发送邮件、短信或其他通知方式
            if 'notification_callback' in context:
                notification_callback = context['notification_callback']
                if callable(notification_callback):
                    notification_callback({
                        'error': error,
                        'recovery_status': recovery_status,
                        'timestamp': time.time()
                    })
            
            return True
        except Exception as e:
            logger.error(f"通知操作员失败: {str(e)}")
            return False


class CustomActionHandler(RecoveryActionHandler):
    """自定义操作处理器"""
    
    def __init__(self, action_name: str, action_function: Callable):
        """
        初始化自定义操作处理器
        
        Args:
            action_name: 操作名称
            action_function: 操作函数
        """
        super().__init__(f"CustomAction:{action_name}", f"自定义恢复操作: {action_name}")
        self.action_function = action_function
    
    def execute(self, context: Dict) -> bool:
        """
        执行自定义操作
        
        Args:
            context: 上下文信息字典
            
        Returns:
            bool: 是否执行成功
        """
        try:
            logger.info(f"正在执行自定义操作: {self.name}")
            result = self.action_function(context)
            success = bool(result)
            
            if success:
                logger.info(f"自定义操作执行成功")
            else:
                logger.error(f"自定义操作执行失败")
                
            return success
        except Exception as e:
            logger.error(f"自定义操作执行异常: {str(e)}")
            return False


class AutoRecoveryManager:
    """自动恢复管理器类"""
    
    def __init__(self, recovery_policy: RecoveryPolicy = RecoveryPolicy.GRADUAL):
        """
        初始化自动恢复管理器
        
        Args:
            recovery_policy: 恢复策略
        """
        self.recovery_policy = recovery_policy
        self.status = RecoveryStatus.IDLE
        self.error_handlers = {}
        self.recovery_history = []
        self.max_history_size = 100
        self._lock = threading.RLock()
        self._error_handler = ErrorHandler()
        self._current_recovery_thread = None
        self._recovery_in_progress = False
        self._disabled_errors: Set[str] = set()  # 禁用自动恢复的错误类型
    
    def register_handler(self, action: RecoveryAction, handler: RecoveryActionHandler) -> bool:
        """
        注册恢复操作处理器
        
        Args:
            action: 恢复操作类型
            handler: 恢复操作处理器
            
        Returns:
            bool: 注册是否成功
        """
        try:
            with self._lock:
                self.error_handlers[action] = handler
                logger.info(f"已注册恢复操作处理器: {action.value} -> {handler.name}")
                return True
        except Exception as e:
            logger.error(f"注册恢复操作处理器失败: {str(e)}")
            return False
    
    def unregister_handler(self, action: RecoveryAction) -> bool:
        """
        注销恢复操作处理器
        
        Args:
            action: 恢复操作类型
            
        Returns:
            bool: 注销是否成功
        """
        try:
            with self._lock:
                if action in self.error_handlers:
                    del self.error_handlers[action]
                    logger.info(f"已注销恢复操作处理器: {action.value}")
                    return True
                return False
        except Exception as e:
            logger.error(f"注销恢复操作处理器失败: {str(e)}")
            return False
    
    def disable_auto_recovery(self, error_type: str) -> None:
        """
        禁用特定类型错误的自动恢复
        
        Args:
            error_type: 错误类型名称
        """
        self._disabled_errors.add(error_type)
        logger.info(f"已禁用错误类型 {error_type} 的自动恢复")
    
    def enable_auto_recovery(self, error_type: str) -> None:
        """
        启用特定类型错误的自动恢复
        
        Args:
            error_type: 错误类型名称
        """
        if error_type in self._disabled_errors:
            self._disabled_errors.remove(error_type)
            logger.info(f"已启用错误类型 {error_type} 的自动恢复")
    
    def is_auto_recovery_enabled(self, error_type: str) -> bool:
        """
        检查是否启用了特定类型错误的自动恢复
        
        Args:
            error_type: 错误类型名称
            
        Returns:
            bool: 是否启用
        """
        return error_type not in self._disabled_errors
    
    def diagnose_error(self, error: RobotError, context: Dict) -> List[RecoveryAction]:
        """
        诊断错误并确定恢复操作序列
        
        Args:
            error: 错误对象
            context: 上下文信息
            
        Returns:
            List[RecoveryAction]: 建议的恢复操作序列
        """
        # 根据错误类型和策略确定恢复操作序列
        recovery_actions = []
        
        # 检查是否禁用了此错误类型的自动恢复
        error_type = error.__class__.__name__
        if not self.is_auto_recovery_enabled(error_type):
            logger.info(f"错误类型 {error_type} 的自动恢复已禁用")
            return [RecoveryAction.NOTIFY_OPERATOR]
        
        # 根据错误类别和严重程度推荐恢复操作
        if error.category == ErrorCategory.COMMUNICATION:
            # 通信错误
            recovery_actions.extend([
                RecoveryAction.RECONNECT,
                RecoveryAction.RESET_ERROR,
                RecoveryAction.MOVE_TO_SAFE_POSE
            ])
        
        elif error.category == ErrorCategory.CONTROLLER:
            # 控制器错误
            recovery_actions.extend([
                RecoveryAction.RESET_ERROR,
                RecoveryAction.RECONNECT,
                RecoveryAction.MOVE_TO_SAFE_POSE
            ])
        
        elif error.category == ErrorCategory.MOTION:
            # 运动错误
            recovery_actions.extend([
                RecoveryAction.RESET_ERROR,
                RecoveryAction.MOVE_TO_SAFE_POSE,
                RecoveryAction.RETRY_OPERATION
            ])
        
        elif error.category == ErrorCategory.SAFETY:
            # 安全错误
            if error.severity == ErrorSeverity.HIGH:
                # 高严重性安全错误，直接通知操作员
                return [RecoveryAction.NOTIFY_OPERATOR]
            else:
                recovery_actions.extend([
                    RecoveryAction.RESET_ERROR,
                    RecoveryAction.MOVE_TO_SAFE_POSE,
                    RecoveryAction.NOTIFY_OPERATOR
                ])
        
        else:
            # 其他错误
            recovery_actions.extend([
                RecoveryAction.RESET_ERROR,
                RecoveryAction.MOVE_TO_SAFE_POSE
            ])
        
        # 根据策略调整恢复操作
        if self.recovery_policy == RecoveryPolicy.CONSERVATIVE:
            # 保守策略，先通知再恢复
            recovery_actions.insert(0, RecoveryAction.NOTIFY_OPERATOR)
        
        elif self.recovery_policy == RecoveryPolicy.AGGRESSIVE:
            # 激进策略，添加更多恢复措施
            if RecoveryAction.RESTART_CONTROLLER not in recovery_actions:
                recovery_actions.append(RecoveryAction.RESTART_CONTROLLER)
        
        elif self.recovery_policy == RecoveryPolicy.GRADUAL:
            # 渐进式策略（默认），从轻到重
            pass  # 已经按照从轻到重排序
        
        # 确保最后都有通知操作员的选项
        if RecoveryAction.NOTIFY_OPERATOR not in recovery_actions:
            recovery_actions.append(RecoveryAction.NOTIFY_OPERATOR)
        
        return recovery_actions
    
    def _execute_recovery_sequence(self, error: RobotError, actions: List[RecoveryAction], 
                                  context: Dict) -> RecoveryStatus:
        """
        执行恢复操作序列
        
        Args:
            error: 错误对象
            actions: 恢复操作序列
            context: 上下文信息
            
        Returns:
            RecoveryStatus: 恢复状态
        """
        self.status = RecoveryStatus.RECOVERING
        context['error'] = error
        
        for action in actions:
            if action not in self.error_handlers:
                logger.warning(f"跳过恢复操作 {action.value}: 没有对应的处理器")
                continue
            
            handler = self.error_handlers[action]
            
            # 检查是否可以执行此操作
            if not handler.can_execute(context):
                logger.warning(f"跳过恢复操作 {action.value}: 处理器报告不可执行")
                continue
            
            # 创建恢复尝试记录
            recovery_attempt = RecoveryAttempt(error, action)
            
            try:
                logger.info(f"执行恢复操作: {action.value} - {handler.description}")
                start_time = time.time()
                
                # 执行恢复操作
                success = handler.execute(context)
                
                # 完成恢复尝试记录
                duration = time.time() - start_time
                recovery_attempt.complete(success, duration)
                
                # 添加到历史记录
                self._add_to_history(recovery_attempt)
                
                if success:
                    logger.info(f"恢复操作 {action.value} 执行成功，耗时 {duration:.2f}秒")
                    
                    # 根据策略决定是否继续执行后续操作
                    if self.recovery_policy == RecoveryPolicy.IMMEDIATE:
                        # 立即策略，成功后停止
                        self.status = RecoveryStatus.RECOVERED
                        return RecoveryStatus.RECOVERED
                else:
                    logger.error(f"恢复操作 {action.value} 执行失败，耗时 {duration:.2f}秒")
                    
            except Exception as e:
                logger.error(f"恢复操作 {action.value} 执行异常: {str(e)}")
                recovery_attempt.complete(False, 0, str(e))
                self._add_to_history(recovery_attempt)
        
        # 所有恢复操作都已尝试
        self.status = RecoveryStatus.FAILED
        
        # 尝试通知操作员
        if RecoveryAction.NOTIFY_OPERATOR in self.error_handlers:
            context['recovery_status'] = self.status
            notify_handler = self.error_handlers[RecoveryAction.NOTIFY_OPERATOR]
            notify_handler.execute(context)
        
        return RecoveryStatus.MANUAL_INTERVENTION_NEEDED
    
    def _add_to_history(self, recovery_attempt: RecoveryAttempt) -> None:
        """
        添加恢复尝试记录到历史
        
        Args:
            recovery_attempt: 恢复尝试记录
        """
        with self._lock:
            self.recovery_history.append(recovery_attempt)
            # 限制历史记录大小
            if len(self.recovery_history) > self.max_history_size:
                self.recovery_history = self.recovery_history[-self.max_history_size:]
    
    def recover_from_error(self, error: RobotError, context: Dict) -> bool:
        """
        从错误中恢复
        
        Args:
            error: 错误对象
            context: 上下文信息
            
        Returns:
            bool: 是否恢复成功
        """
        try:
            # 检查是否已经有恢复操作在进行
            if self._recovery_in_progress:
                logger.warning("恢复操作正在进行中，跳过新的恢复请求")
                return False
            
            with self._lock:
                self._recovery_in_progress = True
            
            self.status = RecoveryStatus.DETECTING
            logger.info(f"检测到错误: {error.__class__.__name__} - {str(error)}")
            
            self.status = RecoveryStatus.DIAGNOSING
            # 诊断错误并获取恢复操作序列
            recovery_actions = self.diagnose_error(error, context)
            logger.info(f"确定的恢复操作序列: {[action.value for action in recovery_actions]}")
            
            # 执行恢复操作序列
            final_status = self._execute_recovery_sequence(error, recovery_actions, context)
            
            success = final_status == RecoveryStatus.RECOVERED
            logger.info(f"恢复过程完成，状态: {final_status.value}, 结果: {'成功' if success else '失败'}")
            
            return success
            
        except Exception as e:
            logger.error(f"恢复过程异常: {str(e)}")
            return False
        finally:
            with self._lock:
                self._recovery_in_progress = False
    
    def recover_from_error_async(self, error: RobotError, context: Dict, 
                               callback: Optional[Callable] = None) -> bool:
        """
        异步从错误中恢复
        
        Args:
            error: 错误对象
            context: 上下文信息
            callback: 完成回调函数
            
        Returns:
            bool: 是否成功启动异步恢复
        """
        # 检查是否已经有恢复线程在运行
        if self._current_recovery_thread and self._current_recovery_thread.is_alive():
            logger.warning("异步恢复线程已在运行，跳过新的异步恢复请求")
            return False
        
        def recovery_thread_func():
            try:
                success = self.recover_from_error(error, context)
                if callback:
                    callback(success)
            except Exception as e:
                logger.error(f"异步恢复线程异常: {str(e)}")
                if callback:
                    callback(False)
        
        # 创建并启动恢复线程
        self._current_recovery_thread = threading.Thread(
            target=recovery_thread_func,
            daemon=True
        )
        self._current_recovery_thread.start()
        logger.info("已启动异步恢复线程")
        return True
    
    def get_recovery_history(self) -> List[RecoveryAttempt]:
        """
        获取恢复历史记录
        
        Returns:
            List[RecoveryAttempt]: 恢复尝试记录列表
        """
        with self._lock:
            return self.recovery_history.copy()
    
    def clear_recovery_history(self) -> None:
        """
        清除恢复历史记录
        """
        with self._lock:
            self.recovery_history.clear()
            logger.info("已清除恢复历史记录")
    
    def get_recovery_statistics(self) -> Dict:
        """
        获取恢复统计信息
        
        Returns:
            Dict: 恢复统计信息
        """
        with self._lock:
            total_attempts = len(self.recovery_history)
            successful_attempts = sum(1 for attempt in self.recovery_history if attempt.success)
            
            # 按错误类型统计
            error_type_stats = {}
            action_stats = {}
            
            for attempt in self.recovery_history:
                error_type = attempt.error.__class__.__name__
                action_type = attempt.action.value
                
                # 错误类型统计
                if error_type not in error_type_stats:
                    error_type_stats[error_type] = {'total': 0, 'success': 0}
                error_type_stats[error_type]['total'] += 1
                if attempt.success:
                    error_type_stats[error_type]['success'] += 1
                
                # 操作类型统计
                if action_type not in action_stats:
                    action_stats[action_type] = {'total': 0, 'success': 0}
                action_stats[action_type]['total'] += 1
                if attempt.success:
                    action_stats[action_type]['success'] += 1
            
            return {
                'total_attempts': total_attempts,
                'successful_attempts': successful_attempts,
                'success_rate': successful_attempts / total_attempts if total_attempts > 0 else 0.0,
                'error_type_statistics': error_type_stats,
                'action_type_statistics': action_stats,
                'current_status': self.status.value,
                'recovery_policy': self.recovery_policy.value,
                'disabled_error_types': list(self._disabled_errors)
            }


class RecoveryDecorator:
    """
    恢复装饰器类，用于自动捕获和恢复函数执行中的错误
    """
    
    def __init__(self, recovery_manager: AutoRecoveryManager, 
                 max_retries: int = 3, 
                 retry_delay: float = 1.0,
                 context_provider: Optional[Callable] = None):
        """
        初始化恢复装饰器
        
        Args:
            recovery_manager: 自动恢复管理器
            max_retries: 最大重试次数
            retry_delay: 重试延迟
            context_provider: 上下文提供函数
        """
        self.recovery_manager = recovery_manager
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.context_provider = context_provider or (lambda: {})
    
    def __call__(self, func):
        """
        装饰器调用
        
        Args:
            func: 被装饰的函数
            
        Returns:
            Callable: 装饰后的函数
        """
        def wrapper(*args, **kwargs):
            # 准备上下文
            context = self.context_provider()
            context['function'] = func
            context['args'] = args
            context['kwargs'] = kwargs
            
            # 添加重试操作到上下文
            context['operation'] = func
            context['operation_args'] = kwargs
            
            for attempt in range(self.max_retries):
                try:
                    # 尝试执行原始函数
                    return func(*args, **kwargs)
                    
                except RobotError as e:
                    logger.warning(f"函数 {func.__name__} 执行出错 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    
                    # 尝试自动恢复
                    recovery_success = self.recovery_manager.recover_from_error(e, context)
                    
                    if not recovery_success or attempt >= self.max_retries - 1:
                        logger.error(f"函数 {func.__name__} 所有恢复尝试失败")
                        raise
                    
                    # 等待后重试
                    time.sleep(self.retry_delay)
                    
                except Exception as e:
                    # 非RobotError类型的异常，包装后再尝试恢复
                    wrapped_error = RobotError(
                        message=str(e),
                        category=ErrorCategory.GENERAL,
                        severity=ErrorSeverity.MEDIUM
                    )
                    logger.warning(f"函数 {func.__name__} 执行异常 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    
                    # 尝试自动恢复
                    recovery_success = self.recovery_manager.recover_from_error(wrapped_error, context)
                    
                    if not recovery_success or attempt >= self.max_retries - 1:
                        logger.error(f"函数 {func.__name__} 所有恢复尝试失败")
                        raise
                    
                    # 等待后重试
                    time.sleep(self.retry_delay)
        
        # 保留原始函数的元数据
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        
        return wrapper


# 创建全局恢复管理器实例
_global_recovery_manager = None


def get_recovery_manager() -> AutoRecoveryManager:
    """
    获取全局恢复管理器实例
    
    Returns:
        AutoRecoveryManager: 恢复管理器实例
    """
    global _global_recovery_manager
    if _global_recovery_manager is None:
        _global_recovery_manager = AutoRecoveryManager()
        # 注册默认处理器
        _global_recovery_manager.register_handler(RecoveryAction.RETRY_OPERATION, RetryOperationHandler())
        _global_recovery_manager.register_handler(RecoveryAction.RESET_ERROR, ResetErrorHandler())
        _global_recovery_manager.register_handler(RecoveryAction.RECONNECT, ReconnectHandler())
        _global_recovery_manager.register_handler(RecoveryAction.MOVE_TO_SAFE_POSE, MoveToSafePoseHandler())
        _global_recovery_manager.register_handler(RecoveryAction.NOTIFY_OPERATOR, NotifyOperatorHandler())
    return _global_recovery_manager


def reset_recovery_manager() -> None:
    """
    重置全局恢复管理器实例
    """
    global _global_recovery_manager
    _global_recovery_manager = None


def with_auto_recovery(max_retries: int = 3, retry_delay: float = 1.0,
                       context_provider: Optional[Callable] = None):
    """
    自动恢复装饰器
    
    Args:
        max_retries: 最大重试次数
        retry_delay: 重试延迟
        context_provider: 上下文提供函数
        
    Returns:
        Callable: 装饰器
    """
    recovery_manager = get_recovery_manager()
    return RecoveryDecorator(recovery_manager, max_retries, retry_delay, context_provider)


# 示例用法
if __name__ == '__main__':
    # 创建恢复管理器
    recovery_manager = get_recovery_manager()
    
    # 模拟机器人对象
    class MockRobot:
        def __init__(self):
            self.connected = True
            self.errors = []
        
        def reset_error(self):
            self.errors.clear()
            print("机器人错误已重置")
        
        def movej(self, pose, speed, acceleration):
            if self.errors:
                raise RobotError("机器人有错误", ErrorCategory.MOTION, ErrorSeverity.MEDIUM)
            print(f"机器人移动到位置: {pose}")
    
    # 创建模拟机器人
    robot = MockRobot()
    
    # 准备上下文
    context = {
        'robot': robot,
        'connector': type('obj', (object,), {
            'is_connected': lambda: robot.connected,
            'connect': lambda: print("连接器已连接"),
            'close': lambda: print("连接器已关闭")
        })
    }
    
    # 创建错误
    error = RobotError("测试错误", ErrorCategory.MOTION, ErrorSeverity.MEDIUM)
    
    # 尝试恢复
    robot.errors.append("测试错误")  # 添加错误
    success = recovery_manager.recover_from_error(error, context)
    print(f"恢复结果: {success}")
    
    # 使用装饰器示例
    @with_auto_recovery(max_retries=2)
    def test_function():
        robot.movej([0, 0, 0, 0, 0, 0], 0.1, 0.1)
        print("函数执行成功")
    
    try:
        test_function()
    except Exception as e:
        print(f"函数执行失败: {e}")
    
    # 打印统计信息
    stats = recovery_manager.get_recovery_statistics()
    print("恢复统计信息:")
    for key, value in stats.items():
        print(f"{key}: {value}")
