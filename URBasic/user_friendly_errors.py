#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户友好错误提示模块

此模块提供了将技术错误信息转换为用户可理解的友好提示的功能，
包括多语言支持、错误上下文解释、解决方案建议和错误可视化等。

作者: Nonead
日期: 2024
版本: 1.0
"""

import os
import json
import logging
import traceback
import datetime
from typing import Dict, List, Optional, Union, Callable, Tuple

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入必要的模块
from URBasic.error_handling import RobotError, ErrorCategory, ErrorSeverity


class ErrorLocalization:
    """
    错误本地化类，管理多语言错误消息
    """
    
    def __init__(self, default_language: str = "zh_CN"):
        """
        初始化错误本地化管理器
        
        Args:
            default_language: 默认语言代码 (如 'zh_CN', 'en_US')
        """
        self.default_language = default_language
        self.current_language = default_language
        self.message_catalogs: Dict[str, Dict[str, str]] = {}
        self._load_default_catalogs()
    
    def _load_default_catalogs(self) -> None:
        """
        加载默认的错误消息目录
        """
        # 中文错误消息
        self.message_catalogs['zh_CN'] = {
            # 通用错误
            'error.generic': '发生错误: {message}',
            'error.unknown': '发生未知错误',
            
            # 通信错误
            'error.communication.connection_failed': '无法连接到机器人，请检查网络连接和IP地址',
            'error.communication.timeout': '与机器人通信超时，请检查机器人是否在线',
            'error.communication.data_corrupted': '接收到的数据已损坏，可能是网络问题',
            
            # 运动错误
            'error.motion.joint_limit': '关节运动超出限制范围，请检查目标位置',
            'error.motion.singularity': '机器人遇到奇异点，无法执行该运动',
            'error.motion.collision': '检测到碰撞风险，请重新规划路径',
            'error.motion.path_invalid': '规划的路径无效，请调整目标位置',
            
            # 安全错误
            'error.safety.protective_stop': '机器人已进入保护性停止状态，请检查是否有障碍物',
            'error.safety.emergency_stop': '急停按钮已激活，请释放急停按钮并重启机器人',
            'error.safety.limit_exceeded': '安全限制已超出，请检查机器人状态',
            
            # 控制器错误
            'error.controller.not_responding': '控制器无响应，请检查电源和连接',
            'error.controller.overload': '控制器过载，请减少负载或降低速度',
            
            # 系统错误
            'error.system.resource_shortage': '系统资源不足，请关闭不必要的程序',
            'error.system.permission_denied': '权限不足，无法执行操作',
            
            # 解决方案
            'solution.check_connection': '请检查网络连接和机器人电源',
            'solution.reset_robot': '请尝试重置机器人并重新连接',
            'solution.retry_operation': '请稍后重试操作',
            'solution.contact_support': '请联系技术支持获取帮助',
            'solution.reduce_speed': '请降低运动速度和加速度',
            'solution.check_workspace': '请检查工作空间是否有障碍物',
            'solution.reboot_system': '请重启控制系统后再试',
        }
        
        # 英文错误消息
        self.message_catalogs['en_US'] = {
            # Generic errors
            'error.generic': 'Error occurred: {message}',
            'error.unknown': 'Unknown error occurred',
            
            # Communication errors
            'error.communication.connection_failed': 'Failed to connect to robot. Please check network connection and IP address',
            'error.communication.timeout': 'Communication timeout with robot. Please check if robot is online',
            'error.communication.data_corrupted': 'Received corrupted data, possible network issue',
            
            # Motion errors
            'error.motion.joint_limit': 'Joint motion exceeds limit range. Please check target position',
            'error.motion.singularity': 'Robot encountered singularity, cannot execute this motion',
            'error.motion.collision': 'Collision risk detected. Please re-plan path',
            'error.motion.path_invalid': 'Planned path is invalid. Please adjust target position',
            
            # Safety errors
            'error.safety.protective_stop': 'Robot entered protective stop state. Please check for obstacles',
            'error.safety.emergency_stop': 'Emergency stop activated. Please release emergency stop and restart robot',
            'error.safety.limit_exceeded': 'Safety limit exceeded. Please check robot status',
            
            # Controller errors
            'error.controller.not_responding': 'Controller not responding. Please check power and connection',
            'error.controller.overload': 'Controller overload. Please reduce load or decrease speed',
            
            # System errors
            'error.system.resource_shortage': 'System resource shortage. Please close unnecessary programs',
            'error.system.permission_denied': 'Permission denied. Cannot execute operation',
            
            # Solutions
            'solution.check_connection': 'Please check network connection and robot power',
            'solution.reset_robot': 'Please try to reset robot and reconnect',
            'solution.retry_operation': 'Please retry operation later',
            'solution.contact_support': 'Please contact technical support for assistance',
            'solution.reduce_speed': 'Please reduce motion speed and acceleration',
            'solution.check_workspace': 'Please check workspace for obstacles',
            'solution.reboot_system': 'Please reboot control system and try again',
        }
    
    def load_catalog(self, language_code: str, catalog: Dict[str, str]) -> bool:
        """
        加载指定语言的消息目录
        
        Args:
            language_code: 语言代码
            catalog: 消息目录字典
            
        Returns:
            bool: 是否加载成功
        """
        try:
            if language_code not in self.message_catalogs:
                self.message_catalogs[language_code] = {}
            
            self.message_catalogs[language_code].update(catalog)
            logger.info(f"已加载语言 {language_code} 的消息目录")
            return True
        except Exception as e:
            logger.error(f"加载消息目录失败: {str(e)}")
            return False
    
    def load_catalog_from_file(self, language_code: str, file_path: str) -> bool:
        """
        从文件加载消息目录
        
        Args:
            language_code: 语言代码
            file_path: 文件路径
            
        Returns:
            bool: 是否加载成功
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"消息目录文件不存在: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                catalog = json.load(f)
            
            return self.load_catalog(language_code, catalog)
        except Exception as e:
            logger.error(f"从文件加载消息目录失败: {str(e)}")
            return False
    
    def set_language(self, language_code: str) -> bool:
        """
        设置当前语言
        
        Args:
            language_code: 语言代码
            
        Returns:
            bool: 是否设置成功
        """
        if language_code in self.message_catalogs:
            self.current_language = language_code
            logger.info(f"已设置当前语言为: {language_code}")
            return True
        else:
            logger.warning(f"语言 {language_code} 不可用，使用默认语言: {self.default_language}")
            return False
    
    def get_message(self, message_id: str, **kwargs) -> str:
        """
        获取指定ID的消息
        
        Args:
            message_id: 消息ID
            **kwargs: 消息参数
            
        Returns:
            str: 本地化后的消息
        """
        # 尝试从当前语言目录获取
        if (self.current_language in self.message_catalogs and 
            message_id in self.message_catalogs[self.current_language]):
            return self.message_catalogs[self.current_language][message_id].format(**kwargs)
        
        # 尝试从默认语言目录获取
        if (self.default_language in self.message_catalogs and 
            message_id in self.message_catalogs[self.default_language]):
            return self.message_catalogs[self.default_language][message_id].format(**kwargs)
        
        # 返回默认消息
        default_message = f"[{message_id}]"
        if kwargs:
            default_message += f" {kwargs}"
        return default_message


class ErrorExplainer:
    """
    错误解释器类，提供错误的详细解释和解决方案
    """
    
    def __init__(self, localization: Optional[ErrorLocalization] = None):
        """
        初始化错误解释器
        
        Args:
            localization: 错误本地化实例
        """
        self.localization = localization or ErrorLocalization()
        self.error_mappings: Dict[str, Dict] = {
            # 通信错误映射
            'ConnectionError': {
                'message_id': 'error.communication.connection_failed',
                'severity': ErrorSeverity.HIGH,
                'solutions': [
                    'solution.check_connection',
                    'solution.reset_robot'
                ]
            },
            'TimeoutError': {
                'message_id': 'error.communication.timeout',
                'severity': ErrorSeverity.MEDIUM,
                'solutions': [
                    'solution.check_connection',
                    'solution.retry_operation'
                ]
            },
            # 可以添加更多错误映射...
        }
    
    def register_error_mapping(self, error_type: str, mapping: Dict) -> bool:
        """
        注册错误类型映射
        
        Args:
            error_type: 错误类型名称
            mapping: 映射信息，包含message_id, severity, solutions等
            
        Returns:
            bool: 是否注册成功
        """
        try:
            self.error_mappings[error_type] = mapping
            logger.info(f"已注册错误类型映射: {error_type}")
            return True
        except Exception as e:
            logger.error(f"注册错误类型映射失败: {str(e)}")
            return False
    
    def get_error_explanation(self, error: Exception) -> Dict:
        """
        获取错误的详细解释
        
        Args:
            error: 错误对象
            
        Returns:
            Dict: 错误解释信息
        """
        error_type = error.__class__.__name__
        
        # 基础信息
        explanation = {
            'error_type': error_type,
            'original_message': str(error),
            'timestamp': datetime.datetime.now().isoformat(),
            'stack_trace': traceback.format_exc(),
            'user_friendly_message': '',
            'severity': 'unknown',
            'solutions': [],
            'context': {}
        }
        
        # 如果是RobotError类型，获取更多信息
        if isinstance(error, RobotError):
            explanation['category'] = error.category.value
            explanation['error_code'] = error.error_code if hasattr(error, 'error_code') else 'unknown'
            explanation['severity'] = error.severity.value
            
            # 根据错误类别获取友好消息
            if error.category == ErrorCategory.COMMUNICATION:
                message_id = 'error.communication.connection_failed'
            elif error.category == ErrorCategory.MOTION:
                message_id = 'error.motion.path_invalid'
            elif error.category == ErrorCategory.SAFETY:
                message_id = 'error.safety.protective_stop'
            elif error.category == ErrorCategory.CONTROLLER:
                message_id = 'error.controller.not_responding'
            else:
                message_id = 'error.generic'
                
            explanation['user_friendly_message'] = self.localization.get_message(
                message_id, 
                message=str(error)
            )
            
            # 根据错误类别推荐解决方案
            if error.category == ErrorCategory.COMMUNICATION:
                solutions = ['solution.check_connection', 'solution.reset_robot']
            elif error.category == ErrorCategory.MOTION:
                solutions = ['solution.reduce_speed', 'solution.check_workspace']
            elif error.category == ErrorCategory.SAFETY:
                solutions = ['solution.check_workspace', 'solution.reset_robot']
            else:
                solutions = ['solution.retry_operation', 'solution.contact_support']
        else:
            # 非RobotError，检查是否有预定义映射
            if error_type in self.error_mappings:
                mapping = self.error_mappings[error_type]
                explanation['user_friendly_message'] = self.localization.get_message(
                    mapping['message_id'],
                    message=str(error)
                )
                explanation['severity'] = mapping['severity'].value
                solutions = mapping.get('solutions', [])
            else:
                # 默认错误消息
                explanation['user_friendly_message'] = self.localization.get_message(
                    'error.generic',
                    message=str(error)
                )
                solutions = ['solution.retry_operation', 'solution.contact_support']
        
        # 本地化解决方案
        localized_solutions = []
        for solution_id in solutions:
            localized_solutions.append(self.localization.get_message(solution_id))
        
        explanation['solutions'] = localized_solutions
        
        return explanation
    
    def generate_context_specific_advice(self, error: Exception, context: Dict) -> str:
        """
        根据上下文生成特定的建议
        
        Args:
            error: 错误对象
            context: 上下文信息
            
        Returns:
            str: 上下文特定的建议
        """
        # 这里可以根据上下文信息生成更具体的建议
        # 例如，如果知道机器人正在执行的任务、当前位置等
        robot_name = context.get('robot_name', '机器人')
        current_task = context.get('current_task', '操作')
        
        if isinstance(error, RobotError):
            if error.category == ErrorCategory.MOTION:
                # 运动错误的特定建议
                return f"在{robot_name}执行{current_task}时发生运动错误。建议检查目标位置是否可达，以及工作空间中是否有障碍物。"
            elif error.category == ErrorCategory.COMMUNICATION:
                # 通信错误的特定建议
                robot_ip = context.get('robot_ip', '未知IP')
                return f"无法与{robot_name}({robot_ip})通信。请确认网络连接正常，机器人电源已开启，并且IP地址配置正确。"
        
        # 默认建议
        return f"在执行{current_task}时发生错误。请参考提供的解决方案。"


class ErrorFormatter:
    """
    错误格式化器类，提供不同格式的错误输出
    """
    
    @staticmethod
    def format_text(explanation: Dict) -> str:
        """
        格式化为文本形式
        
        Args:
            explanation: 错误解释信息
            
        Returns:
            str: 格式化后的文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("错误提示")
        lines.append("=" * 60)
        lines.append(f"错误类型: {explanation['error_type']}")
        lines.append(f"友好提示: {explanation['user_friendly_message']}")
        lines.append(f"严重程度: {explanation['severity']}")
        
        if 'category' in explanation:
            lines.append(f"错误类别: {explanation['category']}")
        if 'error_code' in explanation:
            lines.append(f"错误代码: {explanation['error_code']}")
        
        lines.append("\n建议解决方案:")
        for i, solution in enumerate(explanation['solutions'], 1):
            lines.append(f"  {i}. {solution}")
        
        lines.append("\n原始错误信息:")
        lines.append(f"  {explanation['original_message']}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    @staticmethod
    def format_html(explanation: Dict) -> str:
        """
        格式化为HTML形式
        
        Args:
            explanation: 错误解释信息
            
        Returns:
            str: 格式化后的HTML
        """
        html_parts = []
        html_parts.append("<div class='error-message'>")
        html_parts.append("<h3>错误提示</h3>")
        
        # 错误头部信息
        html_parts.append("<div class='error-header'>")
        html_parts.append(f"<p><strong>错误类型:</strong> {explanation['error_type']}</p>")
        html_parts.append(f"<p><strong>友好提示:</strong> {explanation['user_friendly_message']}</p>")
        html_parts.append(f"<p><strong>严重程度:</strong> {explanation['severity']}</p>")
        
        if 'category' in explanation:
            html_parts.append(f"<p><strong>错误类别:</strong> {explanation['category']}</p>")
        if 'error_code' in explanation:
            html_parts.append(f"<p><strong>错误代码:</strong> {explanation['error_code']}</p>")
        
        html_parts.append("</div>")
        
        # 解决方案
        html_parts.append("<div class='error-solutions'>")
        html_parts.append("<h4>建议解决方案:</h4>")
        html_parts.append("<ul>")
        for solution in explanation['solutions']:
            html_parts.append(f"<li>{solution}</li>")
        html_parts.append("</ul>")
        html_parts.append("</div>")
        
        # 原始错误信息
        html_parts.append("<div class='error-details'>")
        html_parts.append("<h4>详细信息:</h4>")
        html_parts.append(f"<p>{explanation['original_message']}</p>")
        html_parts.append("</div>")
        
        html_parts.append("</div>")
        
        return "\n".join(html_parts)
    
    @staticmethod
    def format_json(explanation: Dict) -> str:
        """
        格式化为JSON形式
        
        Args:
            explanation: 错误解释信息
            
        Returns:
            str: 格式化后的JSON
        """
        return json.dumps(explanation, ensure_ascii=False, indent=2)
    
    @staticmethod
    def format_color_text(explanation: Dict) -> str:
        """
        格式化为带颜色的终端文本
        
        Args:
            explanation: 错误解释信息
            
        Returns:
            str: 格式化后的彩色文本
        """
        # ANSI颜色代码
        COLORS = {
            'HEADER': '\033[95m',
            'BLUE': '\033[94m',
            'GREEN': '\033[92m',
            'WARNING': '\033[93m',
            'FAIL': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
        }
        
        # 根据严重程度选择颜色
        severity_color = COLORS['BLUE']
        if explanation['severity'] == 'HIGH':
            severity_color = COLORS['FAIL']
        elif explanation['severity'] == 'MEDIUM':
            severity_color = COLORS['WARNING']
        
        lines = []
        lines.append(f"{COLORS['HEADER']}=" * 60 + f"{COLORS['ENDC']}")
        lines.append(f"{COLORS['BOLD']}{COLORS['WARNING']}错误提示{COLORS['ENDC']}")
        lines.append(f"{COLORS['HEADER']}=" * 60 + f"{COLORS['ENDC']}")
        lines.append(f"{COLORS['BLUE']}错误类型:{COLORS['ENDC']} {explanation['error_type']}")
        lines.append(f"{COLORS['GREEN']}友好提示:{COLORS['ENDC']} {explanation['user_friendly_message']}")
        lines.append(f"{severity_color}严重程度:{COLORS['ENDC']} {explanation['severity']}")
        
        if 'category' in explanation:
            lines.append(f"{COLORS['BLUE']}错误类别:{COLORS['ENDC']} {explanation['category']}")
        if 'error_code' in explanation:
            lines.append(f"{COLORS['BLUE']}错误代码:{COLORS['ENDC']} {explanation['error_code']}")
        
        lines.append(f"\n{COLORS['BOLD']}建议解决方案:{COLORS['ENDC']}")
        for i, solution in enumerate(explanation['solutions'], 1):
            lines.append(f"  {i}. {COLORS['GREEN']}{solution}{COLORS['ENDC']}")
        
        lines.append(f"\n{COLORS['BOLD']}原始错误信息:{COLORS['ENDC']}")
        lines.append(f"  {explanation['original_message']}")
        lines.append(f"{COLORS['HEADER']}=" * 60 + f"{COLORS['ENDC']}")
        
        return "\n".join(lines)


class UserFriendlyErrorHandler:
    """
    用户友好错误处理器类，整合所有功能
    """
    
    def __init__(self, default_language: str = "zh_CN"):
        """
        初始化用户友好错误处理器
        
        Args:
            default_language: 默认语言
        """
        self.localization = ErrorLocalization(default_language)
        self.explainer = ErrorExplainer(self.localization)
        self.formatter = ErrorFormatter()
        self.output_handlers: List[Callable] = []
        
        # 注册默认输出处理器
        self.register_output_handler(self._log_error)
    
    def register_output_handler(self, handler: Callable) -> bool:
        """
        注册错误输出处理器
        
        Args:
            handler: 处理函数，接收错误解释字典
            
        Returns:
            bool: 是否注册成功
        """
        try:
            if handler not in self.output_handlers:
                self.output_handlers.append(handler)
                logger.info(f"已注册错误输出处理器: {handler.__name__}")
            return True
        except Exception as e:
            logger.error(f"注册错误输出处理器失败: {str(e)}")
            return False
    
    def unregister_output_handler(self, handler: Callable) -> bool:
        """
        注销错误输出处理器
        
        Args:
            handler: 处理函数
            
        Returns:
            bool: 是否注销成功
        """
        try:
            if handler in self.output_handlers:
                self.output_handlers.remove(handler)
                logger.info(f"已注销错误输出处理器: {handler.__name__}")
                return True
            return False
        except Exception as e:
            logger.error(f"注销错误输出处理器失败: {str(e)}")
            return False
    
    def _log_error(self, explanation: Dict) -> None:
        """
        默认的错误日志处理器
        
        Args:
            explanation: 错误解释信息
        """
        # 根据严重程度选择日志级别
        if explanation['severity'] == 'HIGH':
            logger.error(explanation['user_friendly_message'])
        elif explanation['severity'] == 'MEDIUM':
            logger.warning(explanation['user_friendly_message'])
        else:
            logger.info(explanation['user_friendly_message'])
    
    def handle_error(self, error: Exception, context: Optional[Dict] = None, 
                    output_format: str = "text") -> str:
        """
        处理错误并返回友好提示
        
        Args:
            error: 错误对象
            context: 上下文信息
            output_format: 输出格式 (text, html, json, color)
            
        Returns:
            str: 格式化后的错误提示
        """
        if context is None:
            context = {}
        
        # 获取错误解释
        explanation = self.explainer.get_error_explanation(error)
        
        # 添加上下文特定的建议
        context_advice = self.explainer.generate_context_specific_advice(error, context)
        explanation['context_advice'] = context_advice
        
        # 格式化输出
        if output_format == 'html':
            formatted_output = self.formatter.format_html(explanation)
        elif output_format == 'json':
            formatted_output = self.formatter.format_json(explanation)
        elif output_format == 'color':
            formatted_output = self.formatter.format_color_text(explanation)
        else:
            formatted_output = self.formatter.format_text(explanation)
        
        # 调用所有输出处理器
        for handler in self.output_handlers:
            try:
                handler(explanation)
            except Exception as e:
                logger.error(f"执行错误输出处理器失败: {str(e)}")
        
        return formatted_output
    
    def set_language(self, language_code: str) -> bool:
        """
        设置语言
        
        Args:
            language_code: 语言代码
            
        Returns:
            bool: 是否设置成功
        """
        return self.localization.set_language(language_code)
    
    def load_custom_messages(self, language_code: str, catalog: Dict[str, str]) -> bool:
        """
        加载自定义错误消息
        
        Args:
            language_code: 语言代码
            catalog: 消息目录
            
        Returns:
            bool: 是否加载成功
        """
        return self.localization.load_catalog(language_code, catalog)
    
    def register_error_mapping(self, error_type: str, mapping: Dict) -> bool:
        """
        注册自定义错误映射
        
        Args:
            error_type: 错误类型名称
            mapping: 映射信息
            
        Returns:
            bool: 是否注册成功
        """
        return self.explainer.register_error_mapping(error_type, mapping)


class ErrorDisplayManager:
    """
    错误显示管理器，用于在不同界面中显示错误
    """
    
    def __init__(self, error_handler: Optional[UserFriendlyErrorHandler] = None):
        """
        初始化错误显示管理器
        
        Args:
            error_handler: 用户友好错误处理器
        """
        self.error_handler = error_handler or UserFriendlyErrorHandler()
        self.last_error = None
        self.error_history: List[Dict] = []
        self.max_history_size = 50
    
    def show_error(self, error: Exception, context: Optional[Dict] = None, 
                  show_in_console: bool = True) -> str:
        """
        显示错误
        
        Args:
            error: 错误对象
            context: 上下文信息
            show_in_console: 是否在控制台显示
            
        Returns:
            str: 错误提示
        """
        # 处理错误
        formatted_error = self.error_handler.handle_error(
            error, 
            context, 
            output_format="color" if show_in_console else "text"
        )
        
        # 保存到历史记录
        explanation = self.error_handler.explainer.get_error_explanation(error)
        self._add_to_history(explanation)
        self.last_error = explanation
        
        # 在控制台显示
        if show_in_console:
            print(formatted_error)
        
        return formatted_error
    
    def _add_to_history(self, explanation: Dict) -> None:
        """
        添加错误到历史记录
        
        Args:
            explanation: 错误解释信息
        """
        self.error_history.append(explanation)
        # 限制历史记录大小
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def get_error_history(self) -> List[Dict]:
        """
        获取错误历史记录
        
        Returns:
            List[Dict]: 错误历史
        """
        return self.error_history.copy()
    
    def clear_history(self) -> None:
        """
        清除错误历史记录
        """
        self.error_history.clear()
    
    def get_last_error(self) -> Optional[Dict]:
        """
        获取最后一个错误
        
        Returns:
            Optional[Dict]: 最后一个错误的解释信息
        """
        return self.last_error
    
    def export_history_to_file(self, file_path: str, format_type: str = "json") -> bool:
        """
        导出错误历史到文件
        
        Args:
            file_path: 文件路径
            format_type: 格式类型 (json, text)
            
        Returns:
            bool: 是否导出成功
        """
        try:
            if format_type == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.error_history, f, ensure_ascii=False, indent=2)
            elif format_type == "text":
                with open(file_path, 'w', encoding='utf-8') as f:
                    for error in self.error_history:
                        f.write(self.error_handler.formatter.format_text(error))
                        f.write("\n\n")
            else:
                logger.error(f"不支持的导出格式: {format_type}")
                return False
            
            logger.info(f"已导出错误历史到文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出错误历史失败: {str(e)}")
            return False


# 创建全局实例
_global_error_handler = None
_global_display_manager = None


def get_error_handler() -> UserFriendlyErrorHandler:
    """
    获取全局错误处理器
    
    Returns:
        UserFriendlyErrorHandler: 错误处理器实例
    """
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = UserFriendlyErrorHandler()
    return _global_error_handler


def get_display_manager() -> ErrorDisplayManager:
    """
    获取全局显示管理器
    
    Returns:
        ErrorDisplayManager: 显示管理器实例
    """
    global _global_display_manager
    if _global_display_manager is None:
        _global_display_manager = ErrorDisplayManager(get_error_handler())
    return _global_display_manager


def display_error(error: Exception, context: Optional[Dict] = None) -> str:
    """
    便捷函数：显示错误
    
    Args:
        error: 错误对象
        context: 上下文信息
        
    Returns:
        str: 错误提示
    """
    manager = get_display_manager()
    return manager.show_error(error, context)


def set_error_language(language_code: str) -> bool:
    """
    便捷函数：设置错误消息语言
    
    Args:
        language_code: 语言代码
        
    Returns:
        bool: 是否设置成功
    """
    handler = get_error_handler()
    return handler.set_language(language_code)


# 示例用法
if __name__ == '__main__':
    from URBasic.error_handling import CommunicationError
    
    # 创建错误处理器
    error_handler = get_error_handler()
    display_manager = get_display_manager()
    
    # 测试通信错误
    try:
        # 模拟一个通信错误
        raise CommunicationError(
            message="Failed to connect to robot at 192.168.1.100",
            error_code="COM001",
            severity=ErrorSeverity.HIGH
        )
    except Exception as e:
        # 显示错误
        context = {
            'robot_name': 'UR5机器人',
            'robot_ip': '192.168.1.100',
            'current_task': '连接操作'
        }
        display_manager.show_error(e, context)
    
    # 测试普通错误
    try:
        # 模拟一个普通错误
        1 / 0
    except Exception as e:
        display_manager.show_error(e)
    
    # 测试设置语言
    print("\n切换到英文错误消息:")
    set_error_language('en_US')
    
    try:
        raise CommunicationError(
            message="Connection timeout",
            error_code="COM002"
        )
    except Exception as e:
        display_manager.show_error(e)
    
    # 导出错误历史
    display_manager.export_history_to_file('error_history.json')
    display_manager.export_history_to_file('error_history.txt', 'text')
    
    print("\n错误历史记录数量:", len(display_manager.get_error_history()))
