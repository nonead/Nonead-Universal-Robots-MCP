#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
操作历史记录和回放功能模块

此模块提供了机器人操作历史的记录、存储、搜索、过滤和回放功能，
帮助用户追踪机器人的操作过程、分析操作序列、排查问题以及重现操作。

作者: Nonead
日期: 2024
版本: 1.0
"""

import os
import time
import json
import logging
import threading
import datetime
import uuid
import copy
from typing import Dict, List, Optional, Union, Callable, Any, Tuple
from enum import Enum, auto
from collections import deque, OrderedDict
from dataclasses import dataclass, asdict

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入必要的可视化库
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import numpy as np
    HAS_MATPLOTLIB = True
    # 非交互式后端配置
    plt.switch_backend('Agg')
except ImportError:
    logger.warning("Matplotlib未安装，将无法使用可视化功能")
    HAS_MATPLOTLIB = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    logger.warning("Pandas未安装，将无法使用高级数据分析功能")
    HAS_PANDAS = False


class OperationType(Enum):
    """操作类型枚举"""
    # 基本操作
    MOVE_JOINT = auto()           # 关节空间运动
    MOVE_LINEAR = auto()          # 线性运动
    MOVE_CIRCULAR = auto()        # 圆弧运动
    SET_IO = auto()               # 设置IO
    READ_IO = auto()              # 读取IO
    SET_TOOL = auto()             # 设置工具
    SET_PAYLOAD = auto()          # 设置负载
    PAUSE = auto()                # 暂停
    RESUME = auto()               # 恢复
    STOP = auto()                 # 停止
    
    # 高级操作
    EXECUTE_SCRIPT = auto()       # 执行脚本
    CALL_PROGRAM = auto()         # 调用程序
    EXECUTE_TASK = auto()         # 执行任务
    
    # 系统操作
    SYSTEM_START = auto()         # 系统启动
    SYSTEM_SHUTDOWN = auto()      # 系统关闭
    CONNECT_ROBOT = auto()        # 连接机器人
    DISCONNECT_ROBOT = auto()     # 断开连接
    MODE_CHANGE = auto()          # 模式切换
    ERROR_HANDLING = auto()       # 错误处理
    RECOVERY_ACTION = auto()      # 恢复操作
    
    # 其他操作
    USER_ACTION = auto()          # 用户操作
    UNKNOWN = auto()              # 未知操作


class OperationStatus(Enum):
    """操作状态枚举"""
    SUCCESS = auto()              # 成功
    FAILED = auto()               # 失败
    IN_PROGRESS = auto()          # 进行中
    CANCELLED = auto()            # 已取消
    PARTIALLY_COMPLETED = auto()  # 部分完成


@dataclass
class OperationRecord:
    """操作记录数据类"""
    # 基本信息
    record_id: str                # 记录ID
    timestamp: datetime.datetime  # 时间戳
    operation_type: OperationType # 操作类型
    
    # 操作详情
    description: str              # 操作描述
    parameters: Dict[str, Any]    # 操作参数
    status: OperationStatus       # 操作状态
    
    # 结果信息
    result: Optional[Dict[str, Any]] = None  # 操作结果
    error_info: Optional[Dict[str, Any]] = None  # 错误信息
    
    # 机器人状态信息
    robot_state_before: Optional[Dict[str, Any]] = None  # 操作前机器人状态
    robot_state_after: Optional[Dict[str, Any]] = None  # 操作后机器人状态
    
    # 关联信息
    user_id: Optional[str] = None  # 用户ID
    session_id: Optional[str] = None  # 会话ID
    parent_record_id: Optional[str] = None  # 父记录ID
    child_record_ids: Optional[List[str]] = None  # 子记录ID列表
    
    # 元数据
    metadata: Optional[Dict[str, Any]] = None  # 元数据
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        result = asdict(self)
        # 转换枚举类型为字符串
        result['operation_type'] = self.operation_type.name
        result['status'] = self.status.name
        # 转换时间戳为字符串
        result['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OperationRecord':
        """
        从字典创建实例
        
        Args:
            data: 字典数据
            
        Returns:
            OperationRecord: 操作记录实例
        """
        # 复制数据以避免修改原始数据
        data_copy = copy.deepcopy(data)
        
        # 转换字符串为枚举
        if 'operation_type' in data_copy:
            data_copy['operation_type'] = OperationType[data_copy['operation_type']]
        
        if 'status' in data_copy:
            data_copy['status'] = OperationStatus[data_copy['status']]
        
        # 转换字符串为时间戳
        if 'timestamp' in data_copy and data_copy['timestamp']:
            data_copy['timestamp'] = datetime.datetime.fromisoformat(data_copy['timestamp'])
        
        # 创建并返回实例
        return cls(**data_copy)


class OperationHistory:
    """
    操作历史记录类，负责记录和管理操作历史
    """
    
    def __init__(self, max_in_memory_records: int = 1000, 
                 auto_save_interval: Optional[int] = None,
                 save_directory: str = 'history'):
        """
        初始化操作历史记录
        
        Args:
            max_in_memory_records: 内存中最大记录数
            auto_save_interval: 自动保存间隔（秒），为None则不自动保存
            save_directory: 保存目录
        """
        self.max_in_memory_records = max_in_memory_records
        self.auto_save_interval = auto_save_interval
        self.save_directory = save_directory
        
        # 创建保存目录
        os.makedirs(self.save_directory, exist_ok=True)
        
        # 内存中的记录
        self.records: deque = deque(maxlen=max_in_memory_records)
        self.records_dict: Dict[str, OperationRecord] = {}
        
        # 会话信息
        self.current_session_id = str(uuid.uuid4())
        self.current_user_id = None
        
        # 锁，保护并发访问
        self.lock = threading.RLock()
        
        # 自动保存相关
        self.running = False
        self.auto_save_thread = None
        self.last_save_time = time.time()
    
    def start_auto_save(self) -> bool:
        """
        开始自动保存
        
        Returns:
            bool: 是否启动成功
        """
        if self.auto_save_interval is None:
            logger.warning("未设置自动保存间隔")
            return False
        
        if self.running:
            logger.warning("自动保存已经在运行中")
            return False
        
        self.running = True
        
        def auto_save_loop():
            while self.running:
                time.sleep(self.auto_save_interval)
                try:
                    self.save_history()
                except Exception as e:
                    logger.error(f"自动保存失败: {str(e)}")
        
        self.auto_save_thread = threading.Thread(target=auto_save_loop, daemon=True)
        self.auto_save_thread.start()
        logger.info(f"已启动自动保存，间隔: {self.auto_save_interval}秒")
        return True
    
    def stop_auto_save(self) -> bool:
        """
        停止自动保存
        
        Returns:
            bool: 是否停止成功
        """
        if not self.running:
            logger.warning("自动保存未在运行中")
            return False
        
        self.running = False
        if self.auto_save_thread:
            self.auto_save_thread.join(timeout=1.0)
            logger.info("已停止自动保存")
        return True
    
    def set_current_user(self, user_id: str) -> None:
        """
        设置当前用户
        
        Args:
            user_id: 用户ID
        """
        self.current_user_id = user_id
    
    def start_new_session(self) -> str:
        """
        开始新会话
        
        Returns:
            str: 新会话ID
        """
        self.current_session_id = str(uuid.uuid4())
        return self.current_session_id
    
    def add_record(self, operation_type: OperationType, description: str,
                  parameters: Dict[str, Any], status: OperationStatus,
                  result: Optional[Dict[str, Any]] = None,
                  error_info: Optional[Dict[str, Any]] = None,
                  robot_state_before: Optional[Dict[str, Any]] = None,
                  robot_state_after: Optional[Dict[str, Any]] = None,
                  parent_record_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        添加操作记录
        
        Args:
            operation_type: 操作类型
            description: 操作描述
            parameters: 操作参数
            status: 操作状态
            result: 操作结果
            error_info: 错误信息
            robot_state_before: 操作前机器人状态
            robot_state_after: 操作后机器人状态
            parent_record_id: 父记录ID
            metadata: 元数据
            
        Returns:
            str: 记录ID
        """
        # 创建操作记录
        record = OperationRecord(
            record_id=str(uuid.uuid4()),
            timestamp=datetime.datetime.now(),
            operation_type=operation_type,
            description=description,
            parameters=parameters,
            status=status,
            result=result,
            error_info=error_info,
            robot_state_before=robot_state_before,
            robot_state_after=robot_state_after,
            user_id=self.current_user_id,
            session_id=self.current_session_id,
            parent_record_id=parent_record_id,
            child_record_ids=[],
            metadata=metadata
        )
        
        with self.lock:
            # 添加记录
            self.records.append(record)
            self.records_dict[record.record_id] = record
            
            # 如果有父记录，更新父记录的子记录列表
            if parent_record_id and parent_record_id in self.records_dict:
                parent_record = self.records_dict[parent_record_id]
                if parent_record.child_record_ids is None:
                    parent_record.child_record_ids = []
                parent_record.child_record_ids.append(record.record_id)
            
            logger.debug(f"已添加操作记录: {record.record_id}, 类型: {operation_type.name}")
            return record.record_id
    
    def update_record(self, record_id: str, **kwargs) -> bool:
        """
        更新操作记录
        
        Args:
            record_id: 记录ID
            **kwargs: 要更新的字段
            
        Returns:
            bool: 是否更新成功
        """
        with self.lock:
            if record_id not in self.records_dict:
                logger.warning(f"记录 {record_id} 不存在")
                return False
            
            record = self.records_dict[record_id]
            
            # 更新记录字段
            for key, value in kwargs.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            
            logger.debug(f"已更新操作记录: {record_id}")
            return True
    
    def get_record(self, record_id: str) -> Optional[OperationRecord]:
        """
        获取操作记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            Optional[OperationRecord]: 操作记录，如果不存在则返回None
        """
        with self.lock:
            return self.records_dict.get(record_id)
    
    def get_records(self, start_time: Optional[datetime.datetime] = None,
                   end_time: Optional[datetime.datetime] = None,
                   operation_types: Optional[List[OperationType]] = None,
                   statuses: Optional[List[OperationStatus]] = None,
                   limit: Optional[int] = None,
                   reverse: bool = True) -> List[OperationRecord]:
        """
        获取操作记录列表
        
        Args:
            start_time: 起始时间
            end_time: 结束时间
            operation_types: 操作类型列表
            statuses: 状态列表
            limit: 限制返回数量
            reverse: 是否按时间倒序排列
            
        Returns:
            List[OperationRecord]: 操作记录列表
        """
        with self.lock:
            # 获取所有记录的副本
            all_records = list(self.records)
            
            # 按时间排序
            all_records.sort(key=lambda r: r.timestamp, reverse=reverse)
            
            # 过滤记录
            filtered_records = []
            for record in all_records:
                # 时间过滤
                if start_time and record.timestamp < start_time:
                    if reverse:  # 如果是倒序，一旦遇到早于开始时间的记录，就可以停止了
                        continue
                    else:
                        continue
                
                if end_time and record.timestamp > end_time:
                    if reverse:  # 如果是倒序，跳过
                        continue
                    else:  # 如果是正序，一旦遇到晚于结束时间的记录，就可以停止了
                        break
                
                # 操作类型过滤
                if operation_types and record.operation_type not in operation_types:
                    continue
                
                # 状态过滤
                if statuses and record.status not in statuses:
                    continue
                
                filtered_records.append(record)
                
                # 限制数量
                if limit and len(filtered_records) >= limit:
                    break
            
            return filtered_records
    
    def get_session_records(self, session_id: str) -> List[OperationRecord]:
        """
        获取指定会话的所有记录
        
        Args:
            session_id: 会话ID
            
        Returns:
            List[OperationRecord]: 操作记录列表
        """
        with self.lock:
            return [r for r in self.records if r.session_id == session_id]
    
    def get_user_records(self, user_id: str) -> List[OperationRecord]:
        """
        获取指定用户的所有记录
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[OperationRecord]: 操作记录列表
        """
        with self.lock:
            return [r for r in self.records if r.user_id == user_id]
    
    def get_child_records(self, record_id: str) -> List[OperationRecord]:
        """
        获取指定记录的所有子记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            List[OperationRecord]: 子记录列表
        """
        with self.lock:
            record = self.records_dict.get(record_id)
            if not record or not record.child_record_ids:
                return []
            
            child_records = []
            for child_id in record.child_record_ids:
                if child_id in self.records_dict:
                    child_records.append(self.records_dict[child_id])
            
            return child_records
    
    def get_parent_record(self, record_id: str) -> Optional[OperationRecord]:
        """
        获取指定记录的父记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            Optional[OperationRecord]: 父记录，如果不存在则返回None
        """
        with self.lock:
            record = self.records_dict.get(record_id)
            if not record or not record.parent_record_id:
                return None
            
            return self.records_dict.get(record.parent_record_id)
    
    def search_records(self, keyword: str) -> List[OperationRecord]:
        """
        搜索操作记录
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            List[OperationRecord]: 匹配的操作记录列表
        """
        with self.lock:
            keyword_lower = keyword.lower()
            matched_records = []
            
            for record in self.records:
                # 在描述中搜索
                if keyword_lower in record.description.lower():
                    matched_records.append(record)
                    continue
                
                # 在参数中搜索
                if any(keyword_lower in str(value).lower() for value in record.parameters.values()):
                    matched_records.append(record)
                    continue
                
                # 在结果中搜索
                if record.result and any(keyword_lower in str(value).lower() for value in record.result.values()):
                    matched_records.append(record)
                    continue
            
            return matched_records
    
    def save_history(self, filename: Optional[str] = None) -> bool:
        """
        保存操作历史
        
        Args:
            filename: 文件名，如果为None则使用当前日期时间作为文件名
            
        Returns:
            bool: 是否保存成功
        """
        try:
            with self.lock:
                if filename is None:
                    # 使用当前日期时间作为文件名
                    filename = f"history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                # 构建完整路径
                filepath = os.path.join(self.save_directory, filename)
                
                # 转换记录为字典
                records_data = [record.to_dict() for record in self.records]
                
                # 保存数据
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(records_data, f, ensure_ascii=False, indent=2)
                
                self.last_save_time = time.time()
                logger.info(f"已保存 {len(records_data)} 条操作记录到: {filepath}")
                return True
        except Exception as e:
            logger.error(f"保存操作历史失败: {str(e)}")
            return False
    
    def load_history(self, filename: str) -> bool:
        """
        加载操作历史
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否加载成功
        """
        try:
            # 构建完整路径
            filepath = os.path.join(self.save_directory, filename)
            
            # 读取数据
            with open(filepath, 'r', encoding='utf-8') as f:
                records_data = json.load(f)
            
            with self.lock:
                # 清空现有记录
                self.records.clear()
                self.records_dict.clear()
                
                # 加载记录
                for data in records_data:
                    record = OperationRecord.from_dict(data)
                    self.records.append(record)
                    self.records_dict[record.record_id] = record
                
                logger.info(f"已从 {filepath} 加载 {len(records_data)} 条操作记录")
                return True
        except Exception as e:
            logger.error(f"加载操作历史失败: {str(e)}")
            return False
    
    def clear_history(self) -> bool:
        """
        清空操作历史
        
        Returns:
            bool: 是否清空成功
        """
        try:
            with self.lock:
                self.records.clear()
                self.records_dict.clear()
                logger.info("已清空操作历史")
                return True
        except Exception as e:
            logger.error(f"清空操作历史失败: {str(e)}")
            return False
    
    def get_history_summary(self) -> Dict[str, Any]:
        """
        获取历史记录摘要
        
        Returns:
            Dict[str, Any]: 历史记录摘要
        """
        with self.lock:
            if not self.records:
                return {
                    'total_records': 0,
                    'first_record_time': None,
                    'last_record_time': None,
                    'operation_type_count': {},
                    'status_count': {},
                    'sessions': set(),
                    'users': set()
                }
            
            # 统计操作类型数量
            operation_type_count = {}
            status_count = {}
            sessions = set()
            users = set()
            
            for record in self.records:
                # 统计操作类型
                type_name = record.operation_type.name
                operation_type_count[type_name] = operation_type_count.get(type_name, 0) + 1
                
                # 统计状态
                status_name = record.status.name
                status_count[status_name] = status_count.get(status_name, 0) + 1
                
                # 收集会话
                if record.session_id:
                    sessions.add(record.session_id)
                
                # 收集用户
                if record.user_id:
                    users.add(record.user_id)
            
            # 获取第一条和最后一条记录的时间
            sorted_records = sorted(self.records, key=lambda r: r.timestamp)
            first_record_time = sorted_records[0].timestamp if sorted_records else None
            last_record_time = sorted_records[-1].timestamp if sorted_records else None
            
            return {
                'total_records': len(self.records),
                'first_record_time': first_record_time,
                'last_record_time': last_record_time,
                'operation_type_count': operation_type_count,
                'status_count': status_count,
                'sessions': list(sessions),
                'users': list(users)
            }


class OperationReplay:
    """
    操作回放类，负责回放操作历史
    """
    
    def __init__(self, history: OperationHistory):
        """
        初始化操作回放
        
        Args:
            history: 操作历史记录实例
        """
        self.history = history
        self.replay_callbacks: Dict[OperationType, List[Callable]] = {}
        self.generic_callbacks: List[Callable] = []
        self.replay_speed = 1.0  # 回放速度倍率
        self.paused = False
        self.current_record_index = 0
        self.replay_thread = None
        self.running = False
    
    def register_replay_callback(self, operation_type: OperationType,
                               callback: Callable) -> bool:
        """
        注册操作回放回调函数
        
        Args:
            operation_type: 操作类型
            callback: 回调函数，接收操作记录作为参数
            
        Returns:
            bool: 是否注册成功
        """
        try:
            if operation_type not in self.replay_callbacks:
                self.replay_callbacks[operation_type] = []
            
            if callback not in self.replay_callbacks[operation_type]:
                self.replay_callbacks[operation_type].append(callback)
            
            logger.info(f"已注册操作类型 {operation_type.name} 的回放回调函数")
            return True
        except Exception as e:
            logger.error(f"注册回放回调函数失败: {str(e)}")
            return False
    
    def register_generic_callback(self, callback: Callable) -> bool:
        """
        注册通用回放回调函数
        
        Args:
            callback: 回调函数，接收操作记录作为参数
            
        Returns:
            bool: 是否注册成功
        """
        try:
            if callback not in self.generic_callbacks:
                self.generic_callbacks.append(callback)
            
            logger.info("已注册通用回放回调函数")
            return True
        except Exception as e:
            logger.error(f"注册通用回放回调函数失败: {str(e)}")
            return False
    
    def set_replay_speed(self, speed: float) -> None:
        """
        设置回放速度
        
        Args:
            speed: 速度倍率，大于0
        """
        if speed <= 0:
            logger.warning("回放速度必须大于0")
            return
        
        self.replay_speed = speed
        logger.info(f"已设置回放速度: {speed}x")
    
    def pause_replay(self) -> bool:
        """
        暂停回放
        
        Returns:
            bool: 是否暂停成功
        """
        if not self.running:
            logger.warning("回放未在运行中")
            return False
        
        self.paused = True
        logger.info("已暂停回放")
        return True
    
    def resume_replay(self) -> bool:
        """
        恢复回放
        
        Returns:
            bool: 是否恢复成功
        """
        if not self.running:
            logger.warning("回放未在运行中")
            return False
        
        self.paused = False
        logger.info("已恢复回放")
        return True
    
    def stop_replay(self) -> bool:
        """
        停止回放
        
        Returns:
            bool: 是否停止成功
        """
        if not self.running:
            logger.warning("回放未在运行中")
            return False
        
        self.running = False
        if self.replay_thread:
            self.replay_thread.join(timeout=1.0)
        
        logger.info("已停止回放")
        return True
    
    def replay_records(self, records: List[OperationRecord], 
                      real_time: bool = True) -> bool:
        """
        回放指定的记录列表
        
        Args:
            records: 要回放的记录列表
            real_time: 是否按照真实时间间隔回放
            
        Returns:
            bool: 是否回放成功
        """
        if not records:
            logger.warning("记录列表为空")
            return False
        
        if self.running:
            logger.warning("回放已经在运行中")
            return False
        
        self.running = True
        self.paused = False
        self.current_record_index = 0
        
        def replay_loop():
            try:
                # 按时间排序记录
                sorted_records = sorted(records, key=lambda r: r.timestamp)
                
                # 回放记录
                for i, record in enumerate(sorted_records):
                    # 检查是否应该停止
                    if not self.running:
                        break
                    
                    # 等待暂停状态
                    while self.paused and self.running:
                        time.sleep(0.1)
                    
                    # 检查是否应该停止
                    if not self.running:
                        break
                    
                    # 更新当前索引
                    self.current_record_index = i
                    
                    # 执行操作类型特定的回调
                    if record.operation_type in self.replay_callbacks:
                        for callback in self.replay_callbacks[record.operation_type]:
                            try:
                                callback(record)
                            except Exception as e:
                                logger.error(f"执行操作类型 {record.operation_type.name} 的回调失败: {str(e)}")
                    
                    # 执行通用回调
                    for callback in self.generic_callbacks:
                        try:
                            callback(record)
                        except Exception as e:
                                logger.error(f"执行通用回调失败: {str(e)}")
                    
                    # 如果是实时回放，并且不是最后一条记录，等待时间间隔
                    if real_time and i < len(sorted_records) - 1:
                        next_record = sorted_records[i + 1]
                        time_diff = (next_record.timestamp - record.timestamp).total_seconds()
                        
                        # 根据回放速度调整等待时间
                        adjusted_time = time_diff / self.replay_speed
                        
                        # 等待指定时间
                        if adjusted_time > 0:
                            time.sleep(adjusted_time)
            finally:
                self.running = False
                logger.info("回放已完成")
        
        self.replay_thread = threading.Thread(target=replay_loop)
        self.replay_thread.start()
        
        return True
    
    def replay_session(self, session_id: str, real_time: bool = True) -> bool:
        """
        回放指定会话的所有记录
        
        Args:
            session_id: 会话ID
            real_time: 是否按照真实时间间隔回放
            
        Returns:
            bool: 是否回放成功
        """
        # 获取会话记录
        records = self.history.get_session_records(session_id)
        if not records:
            logger.warning(f"会话 {session_id} 没有记录")
            return False
        
        return self.replay_records(records, real_time)
    
    def replay_time_range(self, start_time: datetime.datetime,
                         end_time: datetime.datetime,
                         real_time: bool = True) -> bool:
        """
        回放指定时间范围内的记录
        
        Args:
            start_time: 起始时间
            end_time: 结束时间
            real_time: 是否按照真实时间间隔回放
            
        Returns:
            bool: 是否回放成功
        """
        # 获取时间范围内的记录
        records = self.history.get_records(start_time=start_time, end_time=end_time)
        if not records:
            logger.warning(f"时间范围 {start_time} 到 {end_time} 内没有记录")
            return False
        
        return self.replay_records(records, real_time)
    
    def replay_operation_types(self, operation_types: List[OperationType],
                              limit: Optional[int] = None,
                              real_time: bool = True) -> bool:
        """
        回放指定操作类型的记录
        
        Args:
            operation_types: 操作类型列表
            limit: 限制回放数量
            real_time: 是否按照真实时间间隔回放
            
        Returns:
            bool: 是否回放成功
        """
        # 获取指定操作类型的记录
        records = self.history.get_records(operation_types=operation_types, limit=limit)
        if not records:
            logger.warning(f"没有找到指定操作类型的记录")
            return False
        
        return self.replay_records(records, real_time)
    
    def step_forward(self) -> Optional[OperationRecord]:
        """
        向前步进一条记录
        
        Returns:
            Optional[OperationRecord]: 执行的记录，如果没有更多记录则返回None
        """
        # 获取所有记录（按时间排序）
        all_records = sorted(self.history.records, key=lambda r: r.timestamp)
        
        if self.current_record_index < len(all_records):
            record = all_records[self.current_record_index]
            
            # 执行操作类型特定的回调
            if record.operation_type in self.replay_callbacks:
                for callback in self.replay_callbacks[record.operation_type]:
                    try:
                        callback(record)
                    except Exception as e:
                        logger.error(f"执行操作类型 {record.operation_type.name} 的回调失败: {str(e)}")
            
            # 执行通用回调
            for callback in self.generic_callbacks:
                try:
                    callback(record)
                except Exception as e:
                        logger.error(f"执行通用回调失败: {str(e)}")
            
            # 更新索引
            self.current_record_index += 1
            return record
        
        return None
    
    def step_backward(self) -> Optional[OperationRecord]:
        """
        向后步进一条记录
        
        Returns:
            Optional[OperationRecord]: 执行的记录，如果没有更多记录则返回None
        """
        # 获取所有记录（按时间排序）
        all_records = sorted(self.history.records, key=lambda r: r.timestamp)
        
        if self.current_record_index > 0:
            # 调整索引
            self.current_record_index -= 1
            record = all_records[self.current_record_index]
            
            # 执行操作类型特定的回调
            if record.operation_type in self.replay_callbacks:
                for callback in self.replay_callbacks[record.operation_type]:
                    try:
                        callback(record)
                    except Exception as e:
                        logger.error(f"执行操作类型 {record.operation_type.name} 的回调失败: {str(e)}")
            
            # 执行通用回调
            for callback in self.generic_callbacks:
                try:
                    callback(record)
                except Exception as e:
                        logger.error(f"执行通用回调失败: {str(e)}")
            
            return record
        
        return None


class HistoryVisualizer:
    """
    历史记录可视化类，用于可视化操作历史
    """
    
    def __init__(self, history: OperationHistory):
        """
        初始化历史记录可视化
        
        Args:
            history: 操作历史记录实例
        """
        if not HAS_MATPLOTLIB:
            raise ImportError("Matplotlib未安装，无法使用可视化功能")
        
        self.history = history
    
    def plot_operation_types(self, file_path: str, time_range: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> bool:
        """
        绘制操作类型分布图表
        
        Args:
            file_path: 文件路径
            time_range: 时间范围
            
        Returns:
            bool: 是否绘制成功
        """
        try:
            # 获取记录
            if time_range:
                records = self.history.get_records(start_time=time_range[0], end_time=time_range[1])
            else:
                records = list(self.history.records)
            
            if not records:
                logger.warning("没有找到记录")
                return False
            
            # 统计操作类型
            type_counts = {}
            for record in records:
                type_name = record.operation_type.name
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
            
            # 排序
            sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
            
            # 创建图表
            plt.figure(figsize=(12, 6))
            
            types = [item[0] for item in sorted_types]
            counts = [item[1] for item in sorted_types]
            
            plt.bar(types, counts)
            plt.xlabel('操作类型')
            plt.ylabel('次数')
            plt.title('操作类型分布')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # 保存图表
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"已保存操作类型分布图表到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"绘制操作类型分布图表失败: {str(e)}")
            return False
    
    def plot_status_distribution(self, file_path: str, time_range: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> bool:
        """
        绘制状态分布图表
        
        Args:
            file_path: 文件路径
            time_range: 时间范围
            
        Returns:
            bool: 是否绘制成功
        """
        try:
            # 获取记录
            if time_range:
                records = self.history.get_records(start_time=time_range[0], end_time=time_range[1])
            else:
                records = list(self.history.records)
            
            if not records:
                logger.warning("没有找到记录")
                return False
            
            # 统计状态
            status_counts = {}
            for record in records:
                status_name = record.status.name
                status_counts[status_name] = status_counts.get(status_name, 0) + 1
            
            # 创建图表
            plt.figure(figsize=(8, 8))
            
            plt.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
            plt.title('操作状态分布')
            
            # 保存图表
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"已保存状态分布图表到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"绘制状态分布图表失败: {str(e)}")
            return False
    
    def plot_operation_timeline(self, file_path: str, time_range: Optional[Tuple[datetime.datetime, datetime.datetime]] = None,
                               operation_types: Optional[List[OperationType]] = None) -> bool:
        """
        绘制操作时间线
        
        Args:
            file_path: 文件路径
            time_range: 时间范围
            operation_types: 操作类型列表
            
        Returns:
            bool: 是否绘制成功
        """
        try:
            # 获取记录
            records = self.history.get_records(start_time=time_range[0] if time_range else None,
                                             end_time=time_range[1] if time_range else None,
                                             operation_types=operation_types,
                                             reverse=False)  # 正序排列
            
            if not records:
                logger.warning("没有找到记录")
                return False
            
            # 创建图表
            plt.figure(figsize=(15, 8))
            
            # 为不同操作类型分配不同颜色
            type_colors = {}
            colors = plt.cm.tab20.colors
            for i, record in enumerate(records):
                type_name = record.operation_type.name
                if type_name not in type_colors:
                    type_colors[type_name] = colors[len(type_colors) % len(colors)]
            
            # 绘制时间线
            y_positions = []
            timestamps = []
            labels = []
            bar_colors = []
            
            # 按类型分组
            type_groups = {}
            for record in records:
                type_name = record.operation_type.name
                if type_name not in type_groups:
                    type_groups[type_name] = []
                type_groups[type_name].append(record)
            
            # 为每种类型分配Y轴位置
            y_offset = 0
            for type_name, type_records in sorted(type_groups.items()):
                type_y = []
                type_ts = []
                type_labels = []
                type_colors_list = []
                
                # 为同一类型的每个记录分配Y轴位置
                for i, record in enumerate(sorted(type_records, key=lambda r: r.timestamp)):
                    type_y.append(y_offset + i * 0.5)
                    type_ts.append(record.timestamp)
                    type_labels.append(f"{record.description[:20]}..." if len(record.description) > 20 else record.description)
                    type_colors_list.append(type_colors[type_name])
                
                y_positions.extend(type_y)
                timestamps.extend(type_ts)
                labels.extend(type_labels)
                bar_colors.extend(type_colors_list)
                
                y_offset += len(type_records) * 0.5 + 1
            
            # 绘制点
            plt.scatter(timestamps, y_positions, c=bar_colors, s=50)
            
            # 添加标签
            for i, label in enumerate(labels):
                plt.annotate(label, (timestamps[i], y_positions[i]), 
                            xytext=(5, 5), textcoords='offset points',
                            rotation=15, ha='left', va='bottom', fontsize=8)
            
            # 设置图表
            plt.xlabel('时间')
            plt.title('操作时间线')
            plt.grid(True, axis='y', linestyle='--', alpha=0.7)
            
            # 设置Y轴
            plt.yticks([])
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"已保存操作时间线到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"绘制操作时间线失败: {str(e)}")
            return False
    
    def create_history_report(self, output_dir: str, time_range: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> bool:
        """
        创建历史记录报告
        
        Args:
            output_dir: 输出目录
            time_range: 时间范围
            
        Returns:
            bool: 是否创建成功
        """
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成各种图表
            success = True
            
            # 操作类型分布
            success &= self.plot_operation_types(
                os.path.join(output_dir, 'operation_types.png'),
                time_range
            )
            
            # 状态分布
            success &= self.plot_status_distribution(
                os.path.join(output_dir, 'status_distribution.png'),
                time_range
            )
            
            # 操作时间线
            success &= self.plot_operation_timeline(
                os.path.join(output_dir, 'operation_timeline.png'),
                time_range
            )
            
            # 生成文字报告
            report_path = os.path.join(output_dir, 'history_report.txt')
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("机器人操作历史报告\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if time_range:
                    f.write(f"时间范围: {time_range[0].strftime('%Y-%m-%d %H:%M:%S')} - {time_range[1].strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 添加历史摘要
                summary = self.history.get_history_summary()
                f.write("历史记录摘要\n")
                f.write("-" * 30 + "\n")
                f.write(f"总记录数: {summary['total_records']}\n")
                
                if summary['first_record_time']:
                    f.write(f"第一条记录时间: {summary['first_record_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                if summary['last_record_time']:
                    f.write(f"最后一条记录时间: {summary['last_record_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                f.write(f"会话数: {len(summary['sessions'])}\n")
                f.write(f"用户数: {len(summary['users'])}\n\n")
                
                # 操作类型统计
                f.write("操作类型统计\n")
                f.write("-" * 30 + "\n")
                for type_name, count in sorted(summary['operation_type_count'].items(), key=lambda x: x[1], reverse=True):
                    f.write(f"{type_name}: {count}\n")
                f.write("\n")
                
                # 状态统计
                f.write("状态统计\n")
                f.write("-" * 30 + "\n")
                for status_name, count in sorted(summary['status_count'].items(), key=lambda x: x[1], reverse=True):
                    f.write(f"{status_name}: {count}\n")
                f.write("\n")
                
                # 最近10条记录
                f.write("最近10条记录\n")
                f.write("-" * 30 + "\n")
                recent_records = self.history.get_records(limit=10)
                for record in recent_records:
                    f.write(f"时间: {record.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                    f.write(f"类型: {record.operation_type.name}\n")
                    f.write(f"描述: {record.description}\n")
                    f.write(f"状态: {record.status.name}\n")
                    f.write("-" * 30 + "\n")
            
            logger.info(f"已生成历史记录报告到: {output_dir}")
            return success
        except Exception as e:
            logger.error(f"创建历史记录报告失败: {str(e)}")
            return False


class OperationHistoryManager:
    """
    操作历史管理类，整合历史记录、回放和可视化功能
    """
    
    def __init__(self, history_dir: str = 'history'):
        """
        初始化操作历史管理器
        
        Args:
            history_dir: 历史记录保存目录
        """
        self.history = OperationHistory(save_directory=history_dir)
        self.replay = OperationReplay(self.history)
        self.visualizer = None
        
        # 如果有matplotlib，创建可视化器
        if HAS_MATPLOTLIB:
            try:
                self.visualizer = HistoryVisualizer(self.history)
            except Exception as e:
                logger.error(f"创建历史记录可视化器失败: {str(e)}")
                self.visualizer = None
        
        # 开始自动保存（默认每60秒保存一次）
        self.history.start_auto_save()
    
    def add_operation(self, operation_type: Union[OperationType, str], description: str,
                     parameters: Dict[str, Any] = None,
                     robot_state_before: Optional[Dict[str, Any]] = None,
                     parent_record_id: Optional[str] = None) -> str:
        """
        添加操作（便捷方法）
        
        Args:
            operation_type: 操作类型
            description: 操作描述
            parameters: 操作参数
            robot_state_before: 操作前机器人状态
            parent_record_id: 父记录ID
            
        Returns:
            str: 记录ID
        """
        # 确保参数不为None
        if parameters is None:
            parameters = {}
        
        # 如果操作类型是字符串，转换为枚举
        if isinstance(operation_type, str):
            try:
                operation_type = OperationType[operation_type.upper()]
            except KeyError:
                logger.warning(f"未知的操作类型: {operation_type}，使用UNKNOWN")
                operation_type = OperationType.UNKNOWN
        
        # 添加操作记录（状态为进行中）
        return self.history.add_record(
            operation_type=operation_type,
            description=description,
            parameters=parameters,
            status=OperationStatus.IN_PROGRESS,
            robot_state_before=robot_state_before,
            parent_record_id=parent_record_id
        )
    
    def complete_operation(self, record_id: str, result: Dict[str, Any] = None,
                          robot_state_after: Optional[Dict[str, Any]] = None,
                          error_info: Optional[Dict[str, Any]] = None) -> bool:
        """
        完成操作（便捷方法）
        
        Args:
            record_id: 记录ID
            result: 操作结果
            robot_state_after: 操作后机器人状态
            error_info: 错误信息（如果有）
            
        Returns:
            bool: 是否完成成功
        """
        # 确定操作状态
        if error_info:
            status = OperationStatus.FAILED
        else:
            status = OperationStatus.SUCCESS
        
        # 更新记录
        return self.history.update_record(
            record_id=record_id,
            status=status,
            result=result,
            error_info=error_info,
            robot_state_after=robot_state_after
        )
    
    def create_operation_group(self, description: str) -> str:
        """
        创建操作组（用于将多个相关操作分组）
        
        Args:
            description: 操作组描述
            
        Returns:
            str: 操作组记录ID
        """
        return self.add_operation(
            operation_type=OperationType.EXECUTE_TASK,
            description=description,
            parameters={}
        )
    
    def end_operation_group(self, group_id: str) -> bool:
        """
        结束操作组
        
        Args:
            group_id: 操作组ID
            
        Returns:
            bool: 是否结束成功
        """
        # 检查是否所有子操作都已完成
        child_records = self.history.get_child_records(group_id)
        all_completed = all(record.status != OperationStatus.IN_PROGRESS for record in child_records)
        
        # 确定操作组状态
        if all_completed:
            # 检查是否有子操作失败
            any_failed = any(record.status == OperationStatus.FAILED for record in child_records)
            
            if any_failed:
                status = OperationStatus.FAILED
            else:
                status = OperationStatus.SUCCESS
        else:
            status = OperationStatus.PARTIALLY_COMPLETED
        
        # 更新操作组记录
        return self.history.update_record(
            record_id=group_id,
            status=status,
            result={
                'child_operations_count': len(child_records),
                'all_completed': all_completed
            }
        )
    
    def export_history(self, file_path: str, time_range: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> bool:
        """
        导出历史记录
        
        Args:
            file_path: 文件路径
            time_range: 时间范围
            
        Returns:
            bool: 是否导出成功
        """
        try:
            # 获取要导出的记录
            if time_range:
                records = self.history.get_records(start_time=time_range[0], end_time=time_range[1])
            else:
                records = list(self.history.records)
            
            # 转换为字典
            records_data = [record.to_dict() for record in records]
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(records_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已导出 {len(records_data)} 条记录到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出历史记录失败: {str(e)}")
            return False
    
    def import_history(self, file_path: str, clear_existing: bool = False) -> bool:
        """
        导入历史记录
        
        Args:
            file_path: 文件路径
            clear_existing: 是否清除现有记录
            
        Returns:
            bool: 是否导入成功
        """
        try:
            # 如果需要清除现有记录
            if clear_existing:
                self.history.clear_history()
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                records_data = json.load(f)
            
            # 导入记录
            imported_count = 0
            for data in records_data:
                try:
                    record = OperationRecord.from_dict(data)
                    
                    # 添加到历史记录中
                    with self.history.lock:
                        self.history.records.append(record)
                        self.history.records_dict[record.record_id] = record
                    
                    imported_count += 1
                except Exception as e:
                    logger.error(f"导入记录失败: {str(e)}")
            
            logger.info(f"已从 {file_path} 导入 {imported_count} 条记录")
            return True
        except Exception as e:
            logger.error(f"导入历史记录失败: {str(e)}")
            return False
    
    def generate_report(self, output_dir: str, time_range: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> bool:
        """
        生成报告
        
        Args:
            output_dir: 输出目录
            time_range: 时间范围
            
        Returns:
            bool: 是否生成成功
        """
        if not self.visualizer:
            logger.error("可视化器不可用，无法生成报告")
            return False
        
        return self.visualizer.create_history_report(output_dir, time_range)


# 创建全局实例
_global_history_manager = None


def get_history_manager() -> OperationHistoryManager:
    """
    获取全局历史记录管理器实例
    
    Returns:
        OperationHistoryManager: 历史记录管理器实例
    """
    global _global_history_manager
    if _global_history_manager is None:
        _global_history_manager = OperationHistoryManager()
    return _global_history_manager


def add_operation(operation_type: Union[OperationType, str], description: str,
                  parameters: Dict[str, Any] = None,
                  robot_state_before: Optional[Dict[str, Any]] = None,
                  parent_record_id: Optional[str] = None) -> str:
    """
    便捷函数：添加操作
    
    Args:
        operation_type: 操作类型
        description: 操作描述
        parameters: 操作参数
        robot_state_before: 操作前机器人状态
        parent_record_id: 父记录ID
        
    Returns:
        str: 记录ID
    """
    manager = get_history_manager()
    return manager.add_operation(operation_type, description, parameters,
                               robot_state_before, parent_record_id)


def complete_operation(record_id: str, result: Dict[str, Any] = None,
                       robot_state_after: Optional[Dict[str, Any]] = None,
                       error_info: Optional[Dict[str, Any]] = None) -> bool:
    """
    便捷函数：完成操作
    
    Args:
        record_id: 记录ID
        result: 操作结果
        robot_state_after: 操作后机器人状态
        error_info: 错误信息
        
    Returns:
        bool: 是否完成成功
    """
    manager = get_history_manager()
    return manager.complete_operation(record_id, result, robot_state_after, error_info)


def replay_records(records: List[OperationRecord], real_time: bool = True) -> bool:
    """
    便捷函数：回放记录
    
    Args:
        records: 记录列表
        real_time: 是否实时回放
        
    Returns:
        bool: 是否回放成功
    """
    manager = get_history_manager()
    return manager.replay.replay_records(records, real_time)


# 示例用法
if __name__ == '__main__':
    # 获取历史管理器
    history_manager = get_history_manager()
    
    # 设置当前用户
    history_manager.history.set_current_user("test_user")
    
    # 创建操作组
    group_id = history_manager.create_operation_group("测试操作组")
    
    try:
        print("开始模拟操作记录...")
        
        # 模拟一些操作
        # 1. 连接机器人
        record_id1 = history_manager.add_operation(
            operation_type=OperationType.CONNECT_ROBOT,
            description="连接到机器人",
            parameters={"ip_address": "192.168.1.100"},
            parent_record_id=group_id
        )
        
        # 完成操作
        history_manager.complete_operation(
            record_id=record_id1,
            result={"success": True, "robot_model": "UR5"},
            robot_state_after={"connected": True, "mode": "normal"}
        )
        
        # 模拟一点延迟
        time.sleep(0.5)
        
        # 2. 移动关节
        record_id2 = history_manager.add_operation(
            operation_type=OperationType.MOVE_JOINT,
            description="移动机器人关节",
            parameters={
                "joint_positions": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
                "speed": 0.1,
                "acceleration": 0.5
            },
            parent_record_id=group_id
        )
        
        # 模拟一点延迟
        time.sleep(0.5)
        
        # 完成操作
        history_manager.complete_operation(
            record_id=record_id2,
            result={"success": True, "time_taken": 2.5},
            robot_state_after={"joint_positions": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]}
        )
        
        # 3. 设置IO
        record_id3 = history_manager.add_operation(
            operation_type=OperationType.SET_IO,
            description="设置数字输出",
            parameters={"pin": 0, "value": True},
            parent_record_id=group_id
        )
        
        # 完成操作
        history_manager.complete_operation(
            record_id=record_id3,
            result={"success": True}
        )
        
        # 4. 线性移动（故意设置为失败）
        record_id4 = history_manager.add_operation(
            operation_type=OperationType.MOVE_LINEAR,
            description="线性移动TCP",
            parameters={
                "target_pose": [0.5, 0.2, 0.3, 0, 3.14, 0],
                "speed": 0.1,
                "acceleration": 0.5
            },
            parent_record_id=group_id
        )
        
        # 完成操作（失败）
        history_manager.complete_operation(
            record_id=record_id4,
            result={"success": False},
            error_info={
                "code": "PATH_PLANNING_ERROR",
                "message": "无法规划路径",
                "details": "目标位置超出机器人工作空间"
            }
        )
        
        # 结束操作组
        history_manager.end_operation_group(group_id)
        
        print("模拟操作完成，正在保存历史记录...")
        
        # 保存历史记录
        history_manager.history.save_history()
        
        # 导出历史记录
        history_manager.export_history("exports/operation_history.json")
        
        # 生成报告（如果可视化器可用）
        if history_manager.visualizer:
            print("正在生成历史记录报告...")
            history_manager.generate_report("reports/history_report")
        
        print("示例完成！")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        # 停止自动保存
        history_manager.history.stop_auto_save()
