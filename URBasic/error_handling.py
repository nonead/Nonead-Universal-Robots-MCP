#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
错误处理模块

此模块提供详细的错误类型和错误码定义，用于统一的错误处理机制。
"""

import logging
import traceback
from enum import Enum, IntEnum

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('error_handling')

class ErrorCategory(IntEnum):
    """
    错误类别枚举
    """
    # 通信相关错误 (1000-1999)
    COMMUNICATION = 1000
    # 连接相关错误 (2000-2999)
    CONNECTION = 2000
    # 运动控制相关错误 (3000-3999)
    MOTION = 3000
    # 轨迹规划相关错误 (4000-4999)
    TRAJECTORY = 4000
    # 力控制相关错误 (5000-5999)
    FORCE = 5000
    # 程序执行相关错误 (6000-6999)
    EXECUTION = 6000
    # 系统相关错误 (7000-7999)
    SYSTEM = 7000
    # 参数相关错误 (8000-8999)
    PARAMETER = 8000
    # 安全相关错误 (9000-9999)
    SAFETY = 9000

class ErrorCode(IntEnum):
    """
    错误码枚举
    """
    # 通信相关错误
    COMMUNICATION_TIMEOUT = 1001
    COMMUNICATION_FAILED = 1002
    COMMUNICATION_CORRUPTED_DATA = 1003
    COMMUNICATION_DISCONNECTED = 1004
    
    # 连接相关错误
    CONNECTION_FAILED = 2001
    CONNECTION_REFUSED = 2002
    CONNECTION_LOST = 2003
    CONNECTION_INVALID_IP = 2004
    CONNECTION_INVALID_PORT = 2005
    
    # 运动控制相关错误
    MOTION_PLANNING_FAILED = 3001
    MOTION_EXECUTION_FAILED = 3002
    MOTION_INTERRUPTED = 3003
    MOTION_TARGET_UNREACHABLE = 3004
    MOTION_SINGULARITY = 3005
    MOTION_COLLISION = 3006
    
    # 轨迹规划相关错误
    TRAJECTORY_GENERATION_FAILED = 4001
    TRAJECTORY_OPTIMIZATION_FAILED = 4002
    TRAJECTORY_TOO_COMPLEX = 4003
    TRAJECTORY_VIOLATES_CONSTRAINTS = 4004
    
    # 力控制相关错误
    FORCE_SENSOR_ERROR = 5001
    FORCE_CONTROL_FAILED = 5002
    FORCE_LIMIT_EXCEEDED = 5003
    FORCE_CONTROL_NOT_ENABLED = 5004
    
    # 程序执行相关错误
    PROGRAM_NOT_FOUND = 6001
    PROGRAM_EXECUTION_FAILED = 6002
    PROGRAM_SYNTAX_ERROR = 6003
    PROGRAM_ABORTED = 6004
    
    # 系统相关错误
    SYSTEM_ERROR = 7001
    SYSTEM_OVERLOAD = 7002
    MEMORY_ERROR = 7003
    RESOURCE_BUSY = 7004
    
    # 参数相关错误
    PARAMETER_INVALID = 8001
    PARAMETER_OUT_OF_RANGE = 8002
    PARAMETER_MISSING = 8003
    PARAMETER_TYPE_ERROR = 8004
    
    # 安全相关错误
    SAFETY_STOP_ACTIVATED = 9001
    SAFETY_LIMIT_VIOLATED = 9002
    SAFETY_DOOR_OPEN = 9003
    SAFETY_VIOLATION = 9004

class ErrorSeverity(Enum):
    """
    错误严重性枚举
    """
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"

class RobotError(Exception):
    """
    机器人错误基类
    """
    
    def __init__(self, error_code, message=None, details=None):
        """
        初始化错误
        
        Args:
            error_code: ErrorCode枚举值
            message: 错误消息
            details: 错误详情
        """
        self.error_code = error_code
        self.error_category = self._get_error_category(error_code)
        self.severity = self._get_severity(error_code)
        self.details = details or {}
        
        # 如果没有提供消息，使用默认消息
        if message is None:
            message = self._get_default_message(error_code)
        
        self.message = message
        self.timestamp = self._get_timestamp()
        self.stack_trace = traceback.format_exc()
        
        # 记录错误日志
        self._log_error()
        
        super().__init__(f"Error {error_code}: {message}")
    
    def _get_error_category(self, error_code):
        """
        根据错误码获取错误类别
        
        Args:
            error_code: 错误码
            
        Returns:
            ErrorCategory: 错误类别
        """
        for category in ErrorCategory:
            if category.value <= error_code <= category.value + 999:
                return category
        return ErrorCategory.SYSTEM
    
    def _get_severity(self, error_code):
        """
        根据错误码获取严重性
        
        Args:
            error_code: 错误码
            
        Returns:
            ErrorSeverity: 严重性级别
        """
        # 这里可以根据错误码定义不同的严重性级别
        if error_code in [ErrorCode.SAFETY_STOP_ACTIVATED, ErrorCode.SAFETY_VIOLATION]:
            return ErrorSeverity.FATAL
        elif error_code in [ErrorCode.MOTION_COLLISION, ErrorCode.SAFETY_LIMIT_VIOLATED]:
            return ErrorSeverity.CRITICAL
        elif error_code >= 1000:
            return ErrorSeverity.ERROR
        else:
            return ErrorSeverity.WARNING
    
    def _get_default_message(self, error_code):
        """
        获取错误码的默认消息
        
        Args:
            error_code: 错误码
            
        Returns:
            str: 默认错误消息
        """
        default_messages = {
            ErrorCode.COMMUNICATION_TIMEOUT: "通信超时",
            ErrorCode.COMMUNICATION_FAILED: "通信失败",
            ErrorCode.COMMUNICATION_CORRUPTED_DATA: "接收到的数据已损坏",
            ErrorCode.COMMUNICATION_DISCONNECTED: "通信已断开",
            
            ErrorCode.CONNECTION_FAILED: "连接失败",
            ErrorCode.CONNECTION_REFUSED: "连接被拒绝",
            ErrorCode.CONNECTION_LOST: "连接丢失",
            ErrorCode.CONNECTION_INVALID_IP: "无效的IP地址",
            ErrorCode.CONNECTION_INVALID_PORT: "无效的端口号",
            
            ErrorCode.MOTION_PLANNING_FAILED: "运动规划失败",
            ErrorCode.MOTION_EXECUTION_FAILED: "运动执行失败",
            ErrorCode.MOTION_INTERRUPTED: "运动被中断",
            ErrorCode.MOTION_TARGET_UNREACHABLE: "目标位置无法到达",
            ErrorCode.MOTION_SINGULARITY: "机器人处于奇异点位置",
            ErrorCode.MOTION_COLLISION: "检测到碰撞",
            
            ErrorCode.TRAJECTORY_GENERATION_FAILED: "轨迹生成失败",
            ErrorCode.TRAJECTORY_OPTIMIZATION_FAILED: "轨迹优化失败",
            ErrorCode.TRAJECTORY_TOO_COMPLEX: "轨迹过于复杂",
            ErrorCode.TRAJECTORY_VIOLATES_CONSTRAINTS: "轨迹违反约束条件",
            
            ErrorCode.FORCE_SENSOR_ERROR: "力传感器错误",
            ErrorCode.FORCE_CONTROL_FAILED: "力控制失败",
            ErrorCode.FORCE_LIMIT_EXCEEDED: "超出力限制",
            ErrorCode.FORCE_CONTROL_NOT_ENABLED: "力控制未启用",
            
            ErrorCode.PROGRAM_NOT_FOUND: "程序未找到",
            ErrorCode.PROGRAM_EXECUTION_FAILED: "程序执行失败",
            ErrorCode.PROGRAM_SYNTAX_ERROR: "程序语法错误",
            ErrorCode.PROGRAM_ABORTED: "程序已中止",
            
            ErrorCode.SYSTEM_ERROR: "系统错误",
            ErrorCode.SYSTEM_OVERLOAD: "系统过载",
            ErrorCode.MEMORY_ERROR: "内存错误",
            ErrorCode.RESOURCE_BUSY: "资源忙",
            
            ErrorCode.PARAMETER_INVALID: "无效参数",
            ErrorCode.PARAMETER_OUT_OF_RANGE: "参数超出范围",
            ErrorCode.PARAMETER_MISSING: "缺少参数",
            ErrorCode.PARAMETER_TYPE_ERROR: "参数类型错误",
            
            ErrorCode.SAFETY_STOP_ACTIVATED: "安全停止已激活",
            ErrorCode.SAFETY_LIMIT_VIOLATED: "违反安全限制",
            ErrorCode.SAFETY_DOOR_OPEN: "安全门已打开",
            ErrorCode.SAFETY_VIOLATION: "安全违规",
        }
        
        return default_messages.get(error_code, f"未知错误 {error_code}")
    
    def _get_timestamp(self):
        """
        获取当前时间戳
        
        Returns:
            str: 格式化的时间戳
        """
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def _log_error(self):
        """
        记录错误日志
        """
        log_message = f"[{self.severity.value}] {self.error_category.name} Error {self.error_code}: {self.message}"
        
        if self.details:
            log_message += f" | Details: {self.details}"
        
        if self.severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif self.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif self.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif self.severity == ErrorSeverity.FATAL:
            logger.critical(log_message + " | FATAL ERROR - SYSTEM SHUTDOWN IMMINENT")
    
    def to_dict(self):
        """
        将错误信息转换为字典
        
        Returns:
            dict: 错误信息字典
        """
        return {
            "error_code": self.error_code.value,
            "error_category": self.error_category.name,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "details": self.details
        }

# 特定错误类型定义
class CommunicationError(RobotError):
    """
    通信错误类
    """
    pass

class ConnectionError(RobotError):
    """
    连接错误类
    """
    pass

class MotionError(RobotError):
    """
    运动错误类
    """
    pass

class TrajectoryError(RobotError):
    """
    轨迹错误类
    """
    pass

class ForceError(RobotError):
    """
    力控制错误类
    """
    pass

class ExecutionError(RobotError):
    """
    执行错误类
    """
    pass

class ParameterError(RobotError):
    """
    参数错误类
    """
    pass

class SafetyError(RobotError):
    """
    安全错误类
    """
    pass

class ErrorHandler:
    """
    错误处理器类
    """
    
    def __init__(self):
        """
        初始化错误处理器
        """
        self.error_history = []
        self.max_history_size = 1000
    
    def handle_error(self, error, raise_exception=True):
        """
        处理错误
        
        Args:
            error: 异常对象
            raise_exception: 是否抛出异常
            
        Returns:
            dict: 错误信息字典
        """
        # 如果是RobotError，直接使用
        if isinstance(error, RobotError):
            robot_error = error
        else:
            # 否则，转换为通用系统错误
            robot_error = RobotError(
                ErrorCode.SYSTEM_ERROR,
                str(error),
                {"original_error": str(type(error).__name__)}
            )
        
        # 记录错误历史
        self._record_error(robot_error)
        
        # 根据严重性执行不同操作
        if robot_error.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
            # 对于严重错误，可以执行额外操作，如紧急停止等
            self._handle_critical_error(robot_error)
        
        # 返回错误信息
        error_info = robot_error.to_dict()
        
        # 如果需要，抛出异常
        if raise_exception:
            raise robot_error
        
        return error_info
    
    def _record_error(self, error):
        """
        记录错误到历史
        
        Args:
            error: RobotError对象
        """
        self.error_history.append(error)
        
        # 保持历史记录大小
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
    
    def _handle_critical_error(self, error):
        """
        处理严重错误
        
        Args:
            error: RobotError对象
        """
        # 这里可以实现严重错误的处理逻辑
        # 例如，对于运动碰撞，可以发送停止命令
        logger.critical(f"执行严重错误处理: {error.error_code} - {error.message}")
    
    def get_error_history(self, limit=100):
        """
        获取错误历史
        
        Args:
            limit: 返回的最大错误数量
            
        Returns:
            list: 错误信息字典列表
        """
        history = []
        for error in self.error_history[-limit:]:
            history.append(error.to_dict())
        return history
    
    def clear_error_history(self):
        """
        清除错误历史
        """
        self.error_history.clear()
        logger.info("错误历史已清除")
    
    def get_error_statistics(self):
        """
        获取错误统计信息
        
        Returns:
            dict: 错误统计信息
        """
        stats = {
            "total_errors": len(self.error_history),
            "by_category": {},
            "by_severity": {},
            "most_common_errors": {}
        }
        
        # 初始化统计计数器
        for category in ErrorCategory:
            stats["by_category"][category.name] = 0
        
        for severity in ErrorSeverity:
            stats["by_severity"][severity.value] = 0
        
        error_counts = {}
        
        # 统计错误
        for error in self.error_history:
            stats["by_category"][error.error_category.name] += 1
            stats["by_severity"][error.severity.value] += 1
            
            error_code = error.error_code.value
            error_counts[error_code] = error_counts.get(error_code, 0) + 1
        
        # 获取最常见的错误
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for error_code, count in sorted_errors:
            stats["most_common_errors"][error_code] = count
        
        return stats

# 创建全局错误处理器实例
global_error_handler = ErrorHandler()

def handle_robot_error(func):
    """
    错误处理装饰器
    
    Args:
        func: 要装饰的函数
        
    Returns:
        function: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 处理错误并重新抛出
            global_error_handler.handle_error(e, raise_exception=True)
    
    return wrapper