#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级数据记录系统

此模块提供全面的机器人运行数据记录功能，支持多种数据类型的捕获、
存储、查询和导出，为机器人的监控、分析和优化提供数据基础。

作者: Nonead
日期: 2024
版本: 1.0
"""

import json
import logging
import os
import time
import threading
import datetime
import sqlite3
import csv
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Union, Any, Callable
from collections import deque
import pickle
import zlib

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataRecordType(Enum):
    """数据记录类型枚举"""
    SYSTEM_INFO = "system_info"                  # 系统信息
    ROBOT_STATE = "robot_state"                  # 机器人状态
    JOINT_DATA = "joint_data"                    # 关节数据
    TCP_DATA = "tcp_data"                        # TCP数据
    TRAJECTORY = "trajectory"                    # 轨迹数据
    OPERATION = "operation"                      # 操作记录
    ERROR = "error"                              # 错误记录
    SENSOR = "sensor"                            # 传感器数据
    PERFORMANCE = "performance"                  # 性能数据
    ENERGY = "energy"                            # 能耗数据
    COLLISION = "collision"                      # 碰撞检测
    CUSTOM = "custom"                            # 自定义数据


class StorageFormat(Enum):
    """存储格式枚举"""
    JSON = "json"                                # JSON格式
    CSV = "csv"                                  # CSV格式
    SQLITE = "sqlite"                            # SQLite数据库
    PICKLE = "pickle"                            # Python Pickle
    COMPRESSED = "compressed"                    # 压缩格式


class RotationStrategy(Enum):
    """日志轮转策略枚举"""
    SIZE_BASED = "size_based"                    # 基于大小
    TIME_BASED = "time_based"                    # 基于时间
    COUNT_BASED = "count_based"                  # 基于记录数
    HYBRID = "hybrid"                            # 混合策略


class RecordPriority(Enum):
    """记录优先级枚举"""
    LOW = "low"                                  # 低优先级
    MEDIUM = "medium"                            # 中优先级
    HIGH = "high"                                # 高优先级
    CRITICAL = "critical"                        # 关键优先级


@dataclass
class DataRecord:
    """数据记录基类"""
    timestamp: float = field(default_factory=time.time)  # 时间戳
    record_id: str = field(default_factory=lambda: f"rec_{int(time.time() * 1000)}")  # 记录ID
    robot_id: Optional[str] = None  # 机器人ID
    record_type: Optional[DataRecordType] = None  # 记录类型
    priority: RecordPriority = RecordPriority.MEDIUM  # 优先级
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    data: Dict[str, Any] = field(default_factory=dict)  # 实际数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        # 处理枚举类型
        if result['record_type'] is not None:
            result['record_type'] = result['record_type'].value
        result['priority'] = result['priority'].value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataRecord':
        """从字典创建实例"""
        # 转换回枚举类型
        if 'record_type' in data and data['record_type'] is not None:
            data['record_type'] = DataRecordType(data['record_type'])
        if 'priority' in data:
            data['priority'] = RecordPriority(data['priority'])
        return cls(**data)


@dataclass
class RobotStateRecord(DataRecord):
    """机器人状态记录"""
    def __post_init__(self):
        self.record_type = DataRecordType.ROBOT_STATE


@dataclass
class JointDataRecord(DataRecord):
    """关节数据记录"""
    def __post_init__(self):
        self.record_type = DataRecordType.JOINT_DATA


@dataclass
class TCPDataRecord(DataRecord):
    """TCP数据记录"""
    def __post_init__(self):
        self.record_type = DataRecordType.TCP_DATA


@dataclass
class TrajectoryRecord(DataRecord):
    """轨迹数据记录"""
    def __post_init__(self):
        self.record_type = DataRecordType.TRAJECTORY


@dataclass
class OperationRecord(DataRecord):
    """操作记录"""
    def __post_init__(self):
        self.record_type = DataRecordType.OPERATION


@dataclass
class ErrorRecord(DataRecord):
    """错误记录"""
    def __post_init__(self):
        self.record_type = DataRecordType.ERROR
        self.priority = RecordPriority.HIGH


@dataclass
class SensorRecord(DataRecord):
    """传感器数据记录"""
    def __post_init__(self):
        self.record_type = DataRecordType.SENSOR


@dataclass
class PerformanceRecord(DataRecord):
    """性能数据记录"""
    def __post_init__(self):
        self.record_type = DataRecordType.PERFORMANCE


@dataclass
class StorageConfig:
    """存储配置"""
    storage_format: StorageFormat = StorageFormat.JSON  # 存储格式
    base_directory: str = "./robot_data"  # 基础存储目录
    file_prefix: str = "robot_log"  # 文件前缀
    rotation_strategy: RotationStrategy = RotationStrategy.SIZE_BASED  # 轮转策略
    max_file_size_mb: int = 100  # 最大文件大小(MB)
    rotation_interval_seconds: int = 3600  # 轮转间隔(秒)
    max_records_per_file: int = 10000  # 每个文件最大记录数
    compression: bool = False  # 是否压缩
    enable_backup: bool = True  # 是否启用备份
    backup_interval_days: int = 7  # 备份间隔(天)


@dataclass
class RecordingConfig:
    """记录配置"""
    enabled: bool = True  # 是否启用记录
    buffer_size: int = 10000  # 缓冲区大小
    flush_interval_seconds: int = 5  # 刷新间隔(秒)
    min_priority: RecordPriority = RecordPriority.LOW  # 最小记录优先级
    enabled_record_types: List[DataRecordType] = field(
        default_factory=lambda: list(DataRecordType))  # 启用的记录类型
    sampling_rate_hz: Dict[DataRecordType, float] = field(
        default_factory=lambda: {
            DataRecordType.ROBOT_STATE: 10.0,
            DataRecordType.JOINT_DATA: 100.0,
            DataRecordType.TCP_DATA: 50.0,
            DataRecordType.TRAJECTORY: 20.0,
            DataRecordType.OPERATION: 0.0,  # 事件触发
            DataRecordType.ERROR: 0.0,  # 事件触发
            DataRecordType.SENSOR: 50.0,
            DataRecordType.PERFORMANCE: 1.0,
            DataRecordType.ENERGY: 5.0,
            DataRecordType.COLLISION: 0.0,  # 事件触发
            DataRecordType.CUSTOM: 10.0
        })  # 采样率(Hz)
    custom_filters: Dict[str, Callable[[DataRecord], bool]] = field(
        default_factory=dict)  # 自定义过滤器


class SQLiteStorage:
    """SQLite存储管理器"""
    
    def __init__(self, db_path: str):
        """
        初始化SQLite存储
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建主记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    record_type TEXT,
                    robot_id TEXT,
                    priority TEXT,
                    metadata TEXT,
                    data TEXT
                )
            ''')
            
            # 创建索引以提高查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON records (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_record_type ON records (record_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_robot_id ON records (robot_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON records (priority)')
            
            conn.commit()
    
    def store_records(self, records: List[DataRecord]) -> bool:
        """
        存储记录到SQLite数据库
        
        Args:
            records: 记录列表
            
        Returns:
            bool: 是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for record in records:
                    record_dict = record.to_dict()
                    cursor.execute('''
                        INSERT OR REPLACE INTO records 
                        (id, timestamp, record_type, robot_id, priority, metadata, data) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record_dict['record_id'],
                        record_dict['timestamp'],
                        record_dict['record_type'],
                        record_dict['robot_id'],
                        record_dict['priority'],
                        json.dumps(record_dict['metadata']),
                        json.dumps(record_dict['data'])
                    ))
                
                conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"SQLite存储失败: {str(e)}")
            return False
    
    def query_records(self, 
                     start_time: Optional[float] = None,
                     end_time: Optional[float] = None,
                     record_type: Optional[DataRecordType] = None,
                     robot_id: Optional[str] = None,
                     priority: Optional[RecordPriority] = None,
                     limit: int = 1000,
                     offset: int = 0) -> List[DataRecord]:
        """
        查询记录
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            record_type: 记录类型
            robot_id: 机器人ID
            priority: 优先级
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[DataRecord]: 记录列表
        """
        records = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 构建查询
                query = "SELECT * FROM records WHERE 1=1"
                params = []
                
                if start_time is not None:
                    query += " AND timestamp >= ?"
                    params.append(start_time)
                
                if end_time is not None:
                    query += " AND timestamp <= ?"
                    params.append(end_time)
                
                if record_type is not None:
                    query += " AND record_type = ?"
                    params.append(record_type.value)
                
                if robot_id is not None:
                    query += " AND robot_id = ?"
                    params.append(robot_id)
                
                if priority is not None:
                    query += " AND priority = ?"
                    params.append(priority.value)
                
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                # 执行查询
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                for row in rows:
                    record_data = {
                        'record_id': row['id'],
                        'timestamp': row['timestamp'],
                        'record_type': row['record_type'],
                        'robot_id': row['robot_id'],
                        'priority': row['priority'],
                        'metadata': json.loads(row['metadata']),
                        'data': json.loads(row['data'])
                    }
                    records.append(DataRecord.from_dict(record_data))
                
        except Exception as e:
            logger.error(f"SQLite查询失败: {str(e)}")
        
        return records
    
    def delete_records(self, 
                     start_time: Optional[float] = None,
                     end_time: Optional[float] = None,
                     record_type: Optional[DataRecordType] = None,
                     robot_id: Optional[str] = None) -> bool:
        """
        删除记录
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            record_type: 记录类型
            robot_id: 机器人ID
            
        Returns:
            bool: 是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 构建删除语句
                query = "DELETE FROM records WHERE 1=1"
                params = []
                
                if start_time is not None:
                    query += " AND timestamp >= ?"
                    params.append(start_time)
                
                if end_time is not None:
                    query += " AND timestamp <= ?"
                    params.append(end_time)
                
                if record_type is not None:
                    query += " AND record_type = ?"
                    params.append(record_type.value)
                
                if robot_id is not None:
                    query += " AND robot_id = ?"
                    params.append(robot_id)
                
                # 执行删除
                cursor.execute(query, params)
                conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"SQLite删除失败: {str(e)}")
            return False
    
    def get_record_count(self) -> int:
        """
        获取记录总数
        
        Returns:
            int: 记录数量
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM records")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"获取记录数失败: {str(e)}")
            return 0


class JSONStorage:
    """JSON文件存储管理器"""
    
    def __init__(self, base_path: str, file_prefix: str):
        """
        初始化JSON存储
        
        Args:
            base_path: 基础路径
            file_prefix: 文件前缀
        """
        self.base_path = base_path
        self.file_prefix = file_prefix
        os.makedirs(base_path, exist_ok=True)
        
    def _get_current_filename(self) -> str:
        """获取当前文件名"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.base_path, f"{self.file_prefix}_{timestamp}.json")
    
    def store_records(self, records: List[DataRecord]) -> bool:
        """
        存储记录到JSON文件
        
        Args:
            records: 记录列表
            
        Returns:
            bool: 是否成功
        """
        try:
            filename = self._get_current_filename()
            
            # 读取现有数据（如果文件存在）
            existing_records = []
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_records = json.load(f)
            
            # 添加新记录
            for record in records:
                existing_records.append(record.to_dict())
            
            # 写入文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_records, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"JSON存储失败: {str(e)}")
            return False
    
    def query_records(self, 
                     start_time: Optional[float] = None,
                     end_time: Optional[float] = None,
                     record_type: Optional[DataRecordType] = None,
                     robot_id: Optional[str] = None,
                     priority: Optional[RecordPriority] = None,
                     limit: int = 1000,
                     offset: int = 0) -> List[DataRecord]:
        """
        查询记录
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            record_type: 记录类型
            robot_id: 机器人ID
            priority: 优先级
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[DataRecord]: 记录列表
        """
        records = []
        
        try:
            # 查找所有匹配的文件
            pattern = f"{self.file_prefix}_*.json"
            import glob
            json_files = glob.glob(os.path.join(self.base_path, pattern))
            json_files.sort(reverse=True)  # 最新的文件优先
            
            for file_path in json_files:
                if len(records) >= limit:
                    break
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_records = json.load(f)
                
                # 过滤记录
                for record_dict in file_records:
                    # 时间过滤
                    if start_time is not None and record_dict['timestamp'] < start_time:
                        continue
                    if end_time is not None and record_dict['timestamp'] > end_time:
                        continue
                    
                    # 类型过滤
                    if record_type is not None and record_dict['record_type'] != record_type.value:
                        continue
                    
                    # 机器人ID过滤
                    if robot_id is not None and record_dict['robot_id'] != robot_id:
                        continue
                    
                    # 优先级过滤
                    if priority is not None and record_dict['priority'] != priority.value:
                        continue
                    
                    records.append(DataRecord.from_dict(record_dict))
            
            # 按时间戳排序
            records.sort(key=lambda x: x.timestamp, reverse=True)
            
            # 应用偏移和限制
            records = records[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"JSON查询失败: {str(e)}")
        
        return records


class CSVStorage:
    """CSV文件存储管理器"""
    
    def __init__(self, base_path: str, file_prefix: str):
        """
        初始化CSV存储
        
        Args:
            base_path: 基础路径
            file_prefix: 文件前缀
        """
        self.base_path = base_path
        self.file_prefix = file_prefix
        os.makedirs(base_path, exist_ok=True)
        self._file_headers = {}
    
    def _get_filename_by_type(self, record_type: DataRecordType) -> str:
        """根据记录类型获取文件名"""
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        return os.path.join(self.base_path, 
                          f"{self.file_prefix}_{record_type.value}_{date_str}.csv")
    
    def store_records(self, records: List[DataRecord]) -> bool:
        """
        存储记录到CSV文件
        
        Args:
            records: 记录列表
            
        Returns:
            bool: 是否成功
        """
        try:
            # 按记录类型分组
            records_by_type = {}
            for record in records:
                if record.record_type not in records_by_type:
                    records_by_type[record.record_type] = []
                records_by_type[record.record_type].append(record)
            
            # 存储每组记录
            for record_type, type_records in records_by_type.items():
                filename = self._get_filename_by_type(record_type)
                file_exists = os.path.exists(filename)
                
                with open(filename, 'a', newline='', encoding='utf-8') as f:
                    # 构建所有可能的字段
                    all_fields = ['record_id', 'timestamp', 'robot_id', 'priority']
                    data_fields = set()
                    
                    for record in type_records:
                        data_fields.update(record.data.keys())
                    
                    fieldnames = all_fields + sorted(list(data_fields))
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    # 写入头部（如果是新文件）
                    if not file_exists:
                        writer.writeheader()
                        self._file_headers[filename] = fieldnames
                    
                    # 写入记录
                    for record in type_records:
                        row = {
                            'record_id': record.record_id,
                            'timestamp': record.timestamp,
                            'robot_id': record.robot_id or '',
                            'priority': record.priority.value
                        }
                        row.update(record.data)
                        writer.writerow(row)
            
            return True
        except Exception as e:
            logger.error(f"CSV存储失败: {str(e)}")
            return False


class PickleStorage:
    """Pickle存储管理器"""
    
    def __init__(self, base_path: str, file_prefix: str, compression: bool = False):
        """
        初始化Pickle存储
        
        Args:
            base_path: 基础路径
            file_prefix: 文件前缀
            compression: 是否使用压缩
        """
        self.base_path = base_path
        self.file_prefix = file_prefix
        self.compression = compression
        os.makedirs(base_path, exist_ok=True)
    
    def _get_current_filename(self) -> str:
        """获取当前文件名"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "pklz" if self.compression else "pkl"
        return os.path.join(self.base_path, f"{self.file_prefix}_{timestamp}.{ext}")
    
    def store_records(self, records: List[DataRecord]) -> bool:
        """
        存储记录到Pickle文件
        
        Args:
            records: 记录列表
            
        Returns:
            bool: 是否成功
        """
        try:
            filename = self._get_current_filename()
            
            # 序列化记录
            records_data = [record.to_dict() for record in records]
            
            # 写入文件
            if self.compression:
                with open(filename, 'wb') as f:
                    compressed_data = zlib.compress(pickle.dumps(records_data))
                    f.write(compressed_data)
            else:
                with open(filename, 'wb') as f:
                    pickle.dump(records_data, f)
            
            return True
        except Exception as e:
            logger.error(f"Pickle存储失败: {str(e)}")
            return False
    
    def query_records(self, 
                     start_time: Optional[float] = None,
                     end_time: Optional[float] = None,
                     record_type: Optional[DataRecordType] = None,
                     robot_id: Optional[str] = None,
                     priority: Optional[RecordPriority] = None,
                     limit: int = 1000,
                     offset: int = 0) -> List[DataRecord]:
        """
        查询记录
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            record_type: 记录类型
            robot_id: 机器人ID
            priority: 优先级
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[DataRecord]: 记录列表
        """
        records = []
        
        try:
            # 查找所有匹配的文件
            import glob
            if self.compression:
                pattern = f"{self.file_prefix}_*.pklz"
            else:
                pattern = f"{self.file_prefix}_*.pkl"
            
            pickle_files = glob.glob(os.path.join(self.base_path, pattern))
            pickle_files.sort(reverse=True)  # 最新的文件优先
            
            for file_path in pickle_files:
                if len(records) >= limit:
                    break
                
                # 读取文件
                if file_path.endswith('.pklz'):
                    with open(file_path, 'rb') as f:
                        compressed_data = f.read()
                        file_records = pickle.loads(zlib.decompress(compressed_data))
                else:
                    with open(file_path, 'rb') as f:
                        file_records = pickle.load(f)
                
                # 过滤记录
                for record_dict in file_records:
                    # 时间过滤
                    if start_time is not None and record_dict['timestamp'] < start_time:
                        continue
                    if end_time is not None and record_dict['timestamp'] > end_time:
                        continue
                    
                    # 类型过滤
                    if record_type is not None and record_dict['record_type'] != record_type.value:
                        continue
                    
                    # 机器人ID过滤
                    if robot_id is not None and record_dict['robot_id'] != robot_id:
                        continue
                    
                    # 优先级过滤
                    if priority is not None and record_dict['priority'] != priority.value:
                        continue
                    
                    records.append(DataRecord.from_dict(record_dict))
            
            # 按时间戳排序
            records.sort(key=lambda x: x.timestamp, reverse=True)
            
            # 应用偏移和限制
            records = records[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Pickle查询失败: {str(e)}")
        
        return records


class DataStorageFactory:
    """数据存储工厂类"""
    
    @staticmethod
    def create_storage(config: StorageConfig) -> Union[SQLiteStorage, JSONStorage, CSVStorage, PickleStorage]:
        """
        创建存储实例
        
        Args:
            config: 存储配置
            
        Returns:
            Union[SQLiteStorage, JSONStorage, CSVStorage, PickleStorage]: 存储实例
        """
        os.makedirs(config.base_directory, exist_ok=True)
        
        if config.storage_format == StorageFormat.SQLITE:
            db_path = os.path.join(config.base_directory, f"{config.file_prefix}.db")
            return SQLiteStorage(db_path)
        elif config.storage_format == StorageFormat.JSON:
            return JSONStorage(config.base_directory, config.file_prefix)
        elif config.storage_format == StorageFormat.CSV:
            return CSVStorage(config.base_directory, config.file_prefix)
        elif config.storage_format == StorageFormat.PICKLE or config.storage_format == StorageFormat.COMPRESSED:
            return PickleStorage(config.base_directory, config.file_prefix, 
                               compression=config.storage_format == StorageFormat.COMPRESSED)
        else:
            raise ValueError(f"不支持的存储格式: {config.storage_format}")


class AdvancedDataRecorder:
    """高级数据记录器类"""
    
    def __init__(self, 
                 storage_config: Optional[StorageConfig] = None,
                 recording_config: Optional[RecordingConfig] = None):
        """
        初始化高级数据记录器
        
        Args:
            storage_config: 存储配置
            recording_config: 记录配置
        """
        self.storage_config = storage_config or StorageConfig()
        self.recording_config = recording_config or RecordingConfig()
        
        # 创建存储实例
        self.storage = DataStorageFactory.create_storage(self.storage_config)
        
        # 初始化缓冲区
        self.buffer = deque(maxlen=self.recording_config.buffer_size)
        self.buffer_lock = threading.RLock()
        
        # 状态标志
        self.running = False
        self.recording = self.recording_config.enabled
        
        # 记录统计信息
        self.stats = {
            'total_records': 0,
            'records_stored': 0,
            'records_dropped': 0,
            'last_flush_time': time.time(),
            'last_rotation_time': time.time()
        }
        
        # 记录最后采样时间（用于控制采样率）
        self.last_sampling_time = {}
        
        # 启动后台线程
        self.flush_thread = None
        if self.recording_config.flush_interval_seconds > 0:
            self._start_flush_thread()
    
    def _start_flush_thread(self):
        """启动刷新线程"""
        self.running = True
        self.flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flush_thread.start()
        logger.info("数据记录器刷新线程已启动")
    
    def _flush_loop(self):
        """刷新循环"""
        while self.running:
            try:
                # 检查是否需要刷新
                current_time = time.time()
                if current_time - self.stats['last_flush_time'] >= self.recording_config.flush_interval_seconds:
                    self.flush()
                
                # 检查是否需要轮转
                self._check_rotation()
                
                # 检查是否需要备份
                self._check_backup()
                
            except Exception as e:
                logger.error(f"刷新线程错误: {str(e)}")
            
            time.sleep(0.1)
    
    def start_recording(self):
        """
        开始记录
        """
        self.recording = True
        logger.info("数据记录已开始")
    
    def stop_recording(self):
        """
        停止记录
        """
        self.recording = False
        logger.info("数据记录已停止")
    
    def toggle_recording(self) -> bool:
        """
        切换记录状态
        
        Returns:
            bool: 切换后的状态
        """
        self.recording = not self.recording
        logger.info(f"数据记录已{'开始' if self.recording else '停止'}")
        return self.recording
    
    def record(self, 
              record_type: DataRecordType,
              data: Dict[str, Any],
              robot_id: Optional[str] = None,
              priority: Optional[RecordPriority] = None,
              metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        记录数据
        
        Args:
            record_type: 记录类型
            data: 记录数据
            robot_id: 机器人ID
            priority: 优先级
            metadata: 元数据
            
        Returns:
            bool: 是否成功
        """
        # 检查是否启用记录
        if not self.recording:
            return False
        
        # 检查记录类型是否启用
        if record_type not in self.recording_config.enabled_record_types:
            return False
        
        # 检查优先级
        if priority is None:
            priority = RecordPriority.MEDIUM
        
        if priority.value < self.recording_config.min_priority.value:
            return False
        
        # 检查采样率控制
        current_time = time.time()
        sampling_rate = self.recording_config.sampling_rate_hz.get(record_type, 0.0)
        
        if sampling_rate > 0:
            if record_type not in self.last_sampling_time:
                self.last_sampling_time[record_type] = current_time
            else:
                elapsed = current_time - self.last_sampling_time[record_type]
                if elapsed < 1.0 / sampling_rate:
                    return False
                self.last_sampling_time[record_type] = current_time
        
        # 创建记录
        record = DataRecord(
            record_id=f"{record_type.value}_{int(current_time * 1000)}",
            robot_id=robot_id,
            record_type=record_type,
            priority=priority,
            metadata=metadata or {},
            data=data
        )
        
        # 应用自定义过滤器
        filter_name = f"{record_type.value}_filter"
        if filter_name in self.recording_config.custom_filters:
            if not self.recording_config.custom_filters[filter_name](record):
                return False
        
        # 添加到缓冲区
        with self.buffer_lock:
            if len(self.buffer) >= self.buffer.maxlen:
                self.stats['records_dropped'] += 1
                return False
            
            self.buffer.append(record)
            self.stats['total_records'] += 1
        
        return True
    
    def record_robot_state(self, 
                          robot_id: str,
                          state_data: Dict[str, Any],
                          priority: RecordPriority = RecordPriority.MEDIUM) -> bool:
        """
        记录机器人状态
        
        Args:
            robot_id: 机器人ID
            state_data: 状态数据
            priority: 优先级
            
        Returns:
            bool: 是否成功
        """
        return self.record(
            record_type=DataRecordType.ROBOT_STATE,
            robot_id=robot_id,
            data=state_data,
            priority=priority
        )
    
    def record_joint_data(self, 
                         robot_id: str,
                         joint_data: Dict[str, Any],
                         priority: RecordPriority = RecordPriority.MEDIUM) -> bool:
        """
        记录关节数据
        
        Args:
            robot_id: 机器人ID
            joint_data: 关节数据
            priority: 优先级
            
        Returns:
            bool: 是否成功
        """
        return self.record(
            record_type=DataRecordType.JOINT_DATA,
            robot_id=robot_id,
            data=joint_data,
            priority=priority
        )
    
    def record_tcp_data(self, 
                       robot_id: str,
                       tcp_data: Dict[str, Any],
                       priority: RecordPriority = RecordPriority.MEDIUM) -> bool:
        """
        记录TCP数据
        
        Args:
            robot_id: 机器人ID
            tcp_data: TCP数据
            priority: 优先级
            
        Returns:
            bool: 是否成功
        """
        return self.record(
            record_type=DataRecordType.TCP_DATA,
            robot_id=robot_id,
            data=tcp_data,
            priority=priority
        )
    
    def record_trajectory(self, 
                         robot_id: str,
                         trajectory_data: Dict[str, Any],
                         priority: RecordPriority = RecordPriority.MEDIUM) -> bool:
        """
        记录轨迹数据
        
        Args:
            robot_id: 机器人ID
            trajectory_data: 轨迹数据
            priority: 优先级
            
        Returns:
            bool: 是否成功
        """
        return self.record(
            record_type=DataRecordType.TRAJECTORY,
            robot_id=robot_id,
            data=trajectory_data,
            priority=priority
        )
    
    def record_error(self, 
                    robot_id: str,
                    error_data: Dict[str, Any]) -> bool:
        """
        记录错误数据
        
        Args:
            robot_id: 机器人ID
            error_data: 错误数据
            
        Returns:
            bool: 是否成功
        """
        return self.record(
            record_type=DataRecordType.ERROR,
            robot_id=robot_id,
            data=error_data,
            priority=RecordPriority.CRITICAL
        )
    
    def record_operation(self, 
                        robot_id: str,
                        operation_data: Dict[str, Any],
                        priority: RecordPriority = RecordPriority.MEDIUM) -> bool:
        """
        记录操作数据
        
        Args:
            robot_id: 机器人ID
            operation_data: 操作数据
            priority: 优先级
            
        Returns:
            bool: 是否成功
        """
        return self.record(
            record_type=DataRecordType.OPERATION,
            robot_id=robot_id,
            data=operation_data,
            priority=priority
        )
    
    def record_custom(self, 
                     robot_id: str,
                     custom_type: str,
                     custom_data: Dict[str, Any],
                     priority: RecordPriority = RecordPriority.MEDIUM) -> bool:
        """
        记录自定义数据
        
        Args:
            robot_id: 机器人ID
            custom_type: 自定义类型
            custom_data: 自定义数据
            priority: 优先级
            
        Returns:
            bool: 是否成功
        """
        metadata = {'custom_type': custom_type}
        return self.record(
            record_type=DataRecordType.CUSTOM,
            robot_id=robot_id,
            data=custom_data,
            priority=priority,
            metadata=metadata
        )
    
    def flush(self) -> int:
        """
        刷新缓冲区到存储
        
        Returns:
            int: 刷新的记录数量
        """
        if not self.buffer:
            return 0
        
        with self.buffer_lock:
            # 获取所有记录
            records_to_store = list(self.buffer)
            self.buffer.clear()
        
        # 存储记录
        if records_to_store:
            success = self.storage.store_records(records_to_store)
            if success:
                self.stats['records_stored'] += len(records_to_store)
                self.stats['last_flush_time'] = time.time()
                logger.debug(f"刷新了 {len(records_to_store)} 条记录")
                return len(records_to_store)
            else:
                # 重新添加到缓冲区（如果有空间）
                with self.buffer_lock:
                    for record in reversed(records_to_store):
                        if len(self.buffer) < self.buffer.maxlen:
                            self.buffer.appendleft(record)
                        else:
                            self.stats['records_dropped'] += 1
                return 0
        
        return 0
    
    def query_records(self, 
                     start_time: Optional[float] = None,
                     end_time: Optional[float] = None,
                     record_type: Optional[DataRecordType] = None,
                     robot_id: Optional[str] = None,
                     priority: Optional[RecordPriority] = None,
                     limit: int = 1000,
                     offset: int = 0) -> List[DataRecord]:
        """
        查询记录
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            record_type: 记录类型
            robot_id: 机器人ID
            priority: 优先级
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            List[DataRecord]: 记录列表
        """
        # 先刷新缓冲区
        self.flush()
        
        # 查询存储
        return self.storage.query_records(
            start_time=start_time,
            end_time=end_time,
            record_type=record_type,
            robot_id=robot_id,
            priority=priority,
            limit=limit,
            offset=offset
        )
    
    def export_records(self, 
                      output_file: str,
                      format: StorageFormat = StorageFormat.JSON,
                      start_time: Optional[float] = None,
                      end_time: Optional[float] = None,
                      record_type: Optional[DataRecordType] = None,
                      robot_id: Optional[str] = None) -> bool:
        """
        导出记录
        
        Args:
            output_file: 输出文件路径
            format: 导出格式
            start_time: 开始时间
            end_time: 结束时间
            record_type: 记录类型
            robot_id: 机器人ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 查询记录
            records = self.query_records(
                start_time=start_time,
                end_time=end_time,
                record_type=record_type,
                robot_id=robot_id,
                limit=100000  # 设置一个较大的限制
            )
            
            if not records:
                logger.warning("没有找到匹配的记录")
                return False
            
            # 导出到指定格式
            if format == StorageFormat.JSON:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump([record.to_dict() for record in records], 
                             f, ensure_ascii=False, indent=2)
            
            elif format == StorageFormat.CSV:
                if records:
                    # 获取所有字段
                    fieldnames = ['record_id', 'timestamp', 'record_type', 
                                'robot_id', 'priority']
                    data_fields = set()
                    
                    for record in records:
                        data_fields.update(record.data.keys())
                    
                    fieldnames.extend(sorted(list(data_fields)))
                    
                    with open(output_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        for record in records:
                            row = {
                                'record_id': record.record_id,
                                'timestamp': record.timestamp,
                                'record_type': record.record_type.value if record.record_type else '',
                                'robot_id': record.robot_id or '',
                                'priority': record.priority.value
                            }
                            row.update(record.data)
                            writer.writerow(row)
            
            elif format == StorageFormat.PICKLE:
                with open(output_file, 'wb') as f:
                    pickle.dump([record.to_dict() for record in records], f)
            
            logger.info(f"成功导出 {len(records)} 条记录到 {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"导出记录失败: {str(e)}")
            return False
    
    def delete_records(self, 
                     start_time: Optional[float] = None,
                     end_time: Optional[float] = None,
                     record_type: Optional[DataRecordType] = None,
                     robot_id: Optional[str] = None) -> bool:
        """
        删除记录
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            record_type: 记录类型
            robot_id: 机器人ID
            
        Returns:
            bool: 是否成功
        """
        # 对于SQLite存储，可以直接调用其delete_records方法
        if isinstance(self.storage, SQLiteStorage):
            result = self.storage.delete_records(
                start_time=start_time,
                end_time=end_time,
                record_type=record_type,
                robot_id=robot_id
            )
            if result:
                logger.info("记录删除成功")
            return result
        else:
            logger.warning("删除操作仅支持SQLite存储")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            'total_records': self.stats['total_records'],
            'records_stored': self.stats['records_stored'],
            'records_dropped': self.stats['records_dropped'],
            'buffer_size': len(self.buffer),
            'max_buffer_size': self.recording_config.buffer_size,
            'recording_enabled': self.recording,
            'last_flush_time': self.stats['last_flush_time']
        }
    
    def set_sampling_rate(self, 
                         record_type: DataRecordType,
                         rate_hz: float) -> bool:
        """
        设置采样率
        
        Args:
            record_type: 记录类型
            rate_hz: 采样率(Hz)
            
        Returns:
            bool: 是否成功
        """
        if rate_hz < 0:
            return False
        
        self.recording_config.sampling_rate_hz[record_type] = rate_hz
        return True
    
    def add_custom_filter(self, 
                         filter_name: str,
                         filter_func: Callable[[DataRecord], bool]) -> bool:
        """
        添加自定义过滤器
        
        Args:
            filter_name: 过滤器名称
            filter_func: 过滤函数
            
        Returns:
            bool: 是否成功
        """
        if not callable(filter_func):
            return False
        
        self.recording_config.custom_filters[filter_name] = filter_func
        return True
    
    def _check_rotation(self):
        """
        检查是否需要文件轮转
        """
        current_time = time.time()
        
        # 基于时间的轮转
        if self.storage_config.rotation_strategy in [RotationStrategy.TIME_BASED, RotationStrategy.HYBRID]:
            if current_time - self.stats['last_rotation_time'] >= self.storage_config.rotation_interval_seconds:
                # 对于文件存储类型，轮转是自动的（通过文件名中的时间戳）
                self.stats['last_rotation_time'] = current_time
                logger.info("数据文件已轮转（时间触发）")
        
        # 其他轮转策略可以在这里实现
    
    def _check_backup(self):
        """
        检查是否需要备份
        """
        if not self.storage_config.enable_backup:
            return
        
        # 备份逻辑可以在这里实现
        # 例如：复制当前数据库文件到备份目录
    
    def shutdown(self):
        """
        关闭数据记录器
        """
        # 停止后台线程
        self.running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5.0)
        
        # 最后刷新一次缓冲区
        self.flush()
        
        logger.info("数据记录器已关闭")
    
    def __enter__(self):
        """
        上下文管理器入口
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器退出
        """
        self.shutdown()


# 全局记录器实例
_global_recorder = None


def get_data_recorder() -> AdvancedDataRecorder:
    """
    获取全局数据记录器实例
    
    Returns:
        AdvancedDataRecorder: 数据记录器实例
    """
    global _global_recorder
    
    if _global_recorder is None:
        _global_recorder = AdvancedDataRecorder()
    
    return _global_recorder


def reset_data_recorder() -> None:
    """
    重置全局数据记录器实例
    """
    global _global_recorder
    if _global_recorder:
        _global_recorder.shutdown()
    _global_recorder = None


# 便捷函数
def record_robot_state(robot_id: str, data: Dict[str, Any]) -> bool:
    """
    便捷函数：记录机器人状态
    """
    return get_data_recorder().record_robot_state(robot_id, data)

def record_joint_data(robot_id: str, data: Dict[str, Any]) -> bool:
    """
    便捷函数：记录关节数据
    """
    return get_data_recorder().record_joint_data(robot_id, data)

def record_tcp_data(robot_id: str, data: Dict[str, Any]) -> bool:
    """
    便捷函数：记录TCP数据
    """
    return get_data_recorder().record_tcp_data(robot_id, data)

def record_error(robot_id: str, error_data: Dict[str, Any]) -> bool:
    """
    便捷函数：记录错误
    """
    return get_data_recorder().record_error(robot_id, error_data)

def record_operation(robot_id: str, operation_data: Dict[str, Any]) -> bool:
    """
    便捷函数：记录操作
    """
    return get_data_recorder().record_operation(robot_id, operation_data)


if __name__ == '__main__':
    # 示例使用
    print("=== 高级数据记录器示例 ===")
    
    # 配置记录器
    storage_config = StorageConfig(
        storage_format=StorageFormat.SQLITE,
        base_directory="./robot_data_example",
        max_file_size_mb=50
    )
    
    recording_config = RecordingConfig(
        buffer_size=1000,
        flush_interval_seconds=2,
        sampling_rate_hz={
            DataRecordType.ROBOT_STATE: 5.0,
            DataRecordType.JOINT_DATA: 20.0,
            DataRecordType.TCP_DATA: 10.0
        }
    )
    
    # 创建记录器
    recorder = AdvancedDataRecorder(
        storage_config=storage_config,
        recording_config=recording_config
    )
    
    # 开始记录
    recorder.start_recording()
    
    # 模拟记录一些数据
    print("正在记录示例数据...")
    
    # 记录机器人状态
    for i in range(10):
        recorder.record_robot_state(
            robot_id="UR10_001",
            state_data={
                'mode': 'RUNNING',
                'safety_mode': 'NORMAL',
                'power_on': True,
                'program_running': True,
                'speed_scaling': 0.5 + i * 0.05
            }
        )
        time.sleep(0.1)
    
    # 记录关节数据
    for i in range(5):
        recorder.record_joint_data(
            robot_id="UR10_001",
            joint_data={
                'joint_positions': [i * 0.1, 0.5, 0.3, 0.1, 0.2, 0.0],
                'joint_velocities': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                'joint_temperatures': [35.1, 34.8, 34.5, 35.2, 35.0, 34.7],
                'joint_current': [1.2, 1.1, 0.9, 0.5, 0.4, 0.3]
            }
        )
        time.sleep(0.05)
    
    # 记录TCP数据
    for i in range(8):
        recorder.record_tcp_data(
            robot_id="UR10_001",
            tcp_data={
                'tcp_pose': [0.5, 0.2, 0.8, 0.0, 1.57, 0.0],
                'tcp_velocity': [0.01, 0.0, 0.0, 0.0, 0.0, 0.0],
                'tcp_force': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                'tool_temperature': 32.5
            }
        )
        time.sleep(0.02)
    
    # 记录错误
    recorder.record_error(
        robot_id="UR10_001",
        error_data={
            'error_code': 12345,
            'error_message': '示例错误信息',
            'error_level': 'WARNING',
            'error_source': 'SYSTEM',
            'error_timestamp': time.time(),
            'context': {'operation': 'movej', 'parameters': {'target': [0.5, 0.2, 0.8, 0.0, 1.57, 0.0]}}
        }
    )
    
    # 记录操作
    recorder.record_operation(
        robot_id="UR10_001",
        operation_data={
            'operation_type': 'MOVEJ',
            'parameters': {
                'target_joints': [0.5, -1.0, 1.0, -1.5, -1.5, 0.0],
                'speed': 0.5,
                'acceleration': 0.5
            },
            'result': 'SUCCESS',
            'execution_time': 2.5,
            'user': 'system'
        }
    )
    
    # 强制刷新
    recorder.flush()
    
    # 查询记录
    print("\n查询机器人状态记录:")
    state_records = recorder.query_records(
        record_type=DataRecordType.ROBOT_STATE,
        robot_id="UR10_001",
        limit=5
    )
    
    for record in state_records[:3]:  # 只显示前3条
        print(f"  时间: {datetime.datetime.fromtimestamp(record.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')}")
        print(f"  模式: {record.data.get('mode')}")
        print(f"  安全模式: {record.data.get('safety_mode')}")
        print(f"  速度缩放: {record.data.get('speed_scaling')}")
        print()
    
    # 获取统计信息
    stats = recorder.get_statistics()
    print("\n统计信息:")
    print(f"  总记录数: {stats['total_records']}")
    print(f"  已存储: {stats['records_stored']}")
    print(f"  已丢弃: {stats['records_dropped']}")
    print(f"  当前缓冲区大小: {stats['buffer_size']}/{stats['max_buffer_size']}")
    print(f"  记录状态: {'开启' if stats['recording_enabled'] else '关闭'}")
    
    # 导出记录
    export_file = "./robot_data_example/export.json"
    print(f"\n导出记录到: {export_file}")
    recorder.export_records(
        output_file=export_file,
        format=StorageFormat.JSON,
        robot_id="UR10_001"
    )
    
    # 关闭记录器
    recorder.shutdown()
    print("\n数据记录器已关闭")
