#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态监控仪表板模块

此模块提供了机器人状态的实时监控功能，包括数据收集、存储、可视化和报警系统，
帮助用户实时了解机器人的工作状态并及时发现潜在问题。

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
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Union, Callable, Any, Tuple
from collections import deque

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入必要的可视化库
try:
    import matplotlib.animation as animation
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


class DataCollector:
    """
    数据收集器类，负责从机器人收集各种状态数据
    """
    
    def __init__(self, max_data_points: int = 1000):
        """
        初始化数据收集器
        
        Args:
            max_data_points: 最大数据点数量，超过后会自动移除最早的数据
        """
        self.max_data_points = max_data_points
        self.data_buffers: Dict[str, deque] = {}
        self.timestamps: deque = deque(maxlen=max_data_points)
        self.lock = threading.RLock()  # 可重入锁，保护数据访问
        self.running = False
        self.collection_thread = None
        self.collection_interval = 0.1  # 默认收集间隔为100ms
    
    def register_data_source(self, source_name: str) -> None:
        """
        注册数据源
        
        Args:
            source_name: 数据源名称
        """
        with self.lock:
            if source_name not in self.data_buffers:
                self.data_buffers[source_name] = deque(maxlen=self.max_data_points)
                logger.info(f"已注册数据源: {source_name}")
    
    def add_data_point(self, source_name: str, value: Any) -> None:
        """
        添加数据点
        
        Args:
            source_name: 数据源名称
            value: 数据值
        """
        with self.lock:
            # 如果数据源未注册，自动注册
            if source_name not in self.data_buffers:
                self.register_data_source(source_name)
            
            # 添加时间戳和数据
            current_time = datetime.datetime.now()
            self.timestamps.append(current_time)
            self.data_buffers[source_name].append(value)
    
    def get_data(self, source_name: str, start_time: Optional[datetime.datetime] = None, 
                 end_time: Optional[datetime.datetime] = None) -> List[Any]:
        """
        获取数据
        
        Args:
            source_name: 数据源名称
            start_time: 起始时间
            end_time: 结束时间
            
        Returns:
            List[Any]: 数据列表
        """
        with self.lock:
            if source_name not in self.data_buffers:
                logger.warning(f"数据源 {source_name} 不存在")
                return []
            
            data = list(self.data_buffers[source_name])
            
            # 如果指定了时间范围，进行过滤
            if start_time or end_time:
                filtered_data = []
                for i, timestamp in enumerate(self.timestamps):
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue
                    if i < len(data):
                        filtered_data.append(data[i])
                return filtered_data
            
            return data
    
    def get_timestamps(self, start_time: Optional[datetime.datetime] = None, 
                      end_time: Optional[datetime.datetime] = None) -> List[datetime.datetime]:
        """
        获取时间戳
        
        Args:
            start_time: 起始时间
            end_time: 结束时间
            
        Returns:
            List[datetime.datetime]: 时间戳列表
        """
        with self.lock:
            timestamps = list(self.timestamps)
            
            # 如果指定了时间范围，进行过滤
            if start_time or end_time:
                filtered_timestamps = []
                for timestamp in timestamps:
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue
                    filtered_timestamps.append(timestamp)
                return filtered_timestamps
            
            return timestamps
    
    def get_all_sources(self) -> List[str]:
        """
        获取所有数据源名称
        
        Returns:
            List[str]: 数据源名称列表
        """
        with self.lock:
            return list(self.data_buffers.keys())
    
    def start_continuous_collection(self, collection_func: Callable, interval: float = None) -> bool:
        """
        开始连续数据收集
        
        Args:
            collection_func: 收集函数，负责获取数据并调用add_data_point
            interval: 收集间隔（秒）
            
        Returns:
            bool: 是否启动成功
        """
        if self.running:
            logger.warning("数据收集已经在运行中")
            return False
        
        self.running = True
        if interval is not None:
            self.collection_interval = interval
            
        def collection_loop():
            while self.running:
                try:
                    collection_func()
                except Exception as e:
                    logger.error(f"数据收集出错: {str(e)}")
                time.sleep(self.collection_interval)
        
        self.collection_thread = threading.Thread(target=collection_loop, daemon=True)
        self.collection_thread.start()
        logger.info(f"已启动连续数据收集，间隔: {self.collection_interval}秒")
        return True
    
    def stop_continuous_collection(self) -> bool:
        """
        停止连续数据收集
        
        Returns:
            bool: 是否停止成功
        """
        if not self.running:
            logger.warning("数据收集未在运行中")
            return False
        
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=1.0)
            logger.info("已停止连续数据收集")
        return True
    
    def clear_data(self, source_name: Optional[str] = None) -> None:
        """
        清除数据
        
        Args:
            source_name: 数据源名称，如果为None则清除所有数据源
        """
        with self.lock:
            if source_name is None:
                # 清除所有数据源
                self.data_buffers.clear()
                self.timestamps.clear()
                logger.info("已清除所有数据")
            elif source_name in self.data_buffers:
                # 清除特定数据源
                self.data_buffers[source_name].clear()
                # 注意：时间戳不会单独清除，因为它们是共享的
                logger.info(f"已清除数据源 {source_name} 的数据")
    
    def export_data(self, file_path: str, source_name: Optional[str] = None, 
                    format_type: str = "json") -> bool:
        """
        导出数据
        
        Args:
            file_path: 文件路径
            source_name: 数据源名称，如果为None则导出所有数据源
            format_type: 格式类型 (json, csv)
            
        Returns:
            bool: 是否导出成功
        """
        try:
            with self.lock:
                # 准备导出数据
                export_data = {
                    'export_time': datetime.datetime.now().isoformat(),
                    'timestamps': [ts.isoformat() for ts in self.timestamps],
                    'data': {}
                }
                
                # 选择要导出的数据源
                if source_name is not None:
                    if source_name not in self.data_buffers:
                        logger.error(f"数据源 {source_name} 不存在")
                        return False
                    sources = [source_name]
                else:
                    sources = list(self.data_buffers.keys())
                
                # 添加数据
                for src in sources:
                    # 转换为可JSON序列化的格式
                    data_list = []
                    for item in self.data_buffers[src]:
                        if isinstance(item, np.ndarray):
                            data_list.append(item.tolist())
                        elif isinstance(item, (np.int64, np.int32, np.float64, np.float32)):
                            data_list.append(float(item))
                        else:
                            data_list.append(item)
                    export_data['data'][src] = data_list
                
                # 确保目录存在
                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                
                # 导出数据
                if format_type.lower() == "json":
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                elif format_type.lower() == "csv" and HAS_PANDAS:
                    # 转换为pandas DataFrame并导出为CSV
                    df_data = {'timestamp': self.timestamps}
                    for src in sources:
                        if len(self.data_buffers[src]) == len(self.timestamps):
                            df_data[src] = list(self.data_buffers[src])
                    
                    df = pd.DataFrame(df_data)
                    df.to_csv(file_path, index=False, encoding='utf-8')
                else:
                    logger.error(f"不支持的导出格式: {format_type}")
                    return False
                
                logger.info(f"数据已导出到 {file_path}")
                return True
        except Exception as e:
            logger.error(f"导出数据失败: {str(e)}")
            return False


class ThresholdMonitor:
    """
    阈值监控器，用于监控数据是否超出设定的阈值
    """
    
    class Threshold:
        """阈值类，定义监控阈值"""
        
        def __init__(self, lower_bound: Optional[float] = None,
                     upper_bound: Optional[float] = None,
                     duration: float = 0.0):
            """
            初始化阈值
            
            Args:
                lower_bound: 下界阈值
                upper_bound: 上界阈值
                duration: 超阈值持续时间(秒)，超过此时间才触发报警
            """
            self.lower_bound = lower_bound
            self.upper_bound = upper_bound
            self.duration = duration
            self.violation_start_time = None
    
    def __init__(self):
        """初始化阈值监控器"""
        self.thresholds: Dict[str, ThresholdMonitor.Threshold] = {}
        self.alarm_handlers: List[Callable] = []
        self.alarm_history: List[Dict] = []
        self.lock = threading.RLock()
    
    def set_threshold(self, data_source: str, lower_bound: Optional[float] = None,
                     upper_bound: Optional[float] = None, duration: float = 0.0) -> None:
        """
        设置数据阈值
        
        Args:
            data_source: 数据源名称
            lower_bound: 下界阈值
            upper_bound: 上界阈值
            duration: 超阈值持续时间(秒)
        """
        with self.lock:
            self.thresholds[data_source] = ThresholdMonitor.Threshold(
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                duration=duration
            )
            logger.info(f"已设置数据源 {data_source} 的阈值: 下界={lower_bound}, 上界={upper_bound}, 持续时间={duration}秒")
    
    def remove_threshold(self, data_source: str) -> bool:
        """
        移除数据阈值
        
        Args:
            data_source: 数据源名称
            
        Returns:
            bool: 是否移除成功
        """
        with self.lock:
            if data_source in self.thresholds:
                del self.thresholds[data_source]
                logger.info(f"已移除数据源 {data_source} 的阈值")
                return True
            return False
    
    def register_alarm_handler(self, handler: Callable) -> bool:
        """
        注册报警处理函数
        
        Args:
            handler: 处理函数，接收报警信息字典
            
        Returns:
            bool: 是否注册成功
        """
        try:
            if handler not in self.alarm_handlers:
                self.alarm_handlers.append(handler)
                logger.info(f"已注册报警处理函数: {handler.__name__}")
            return True
        except Exception as e:
            logger.error(f"注册报警处理函数失败: {str(e)}")
            return False
    
    def check_value(self, data_source: str, value: float, 
                   timestamp: Optional[datetime.datetime] = None) -> Optional[Dict]:
        """
        检查值是否超出阈值
        
        Args:
            data_source: 数据源名称
            value: 要检查的值
            timestamp: 时间戳，如果为None则使用当前时间
            
        Returns:
            Optional[Dict]: 报警信息，如果没有报警则返回None
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()
        
        with self.lock:
            if data_source not in self.thresholds:
                return None
            
            threshold = self.thresholds[data_source]
            is_violation = False
            violation_type = None
            
            # 检查是否超出阈值
            if threshold.lower_bound is not None and value < threshold.lower_bound:
                is_violation = True
                violation_type = "below_lower"
            elif threshold.upper_bound is not None and value > threshold.upper_bound:
                is_violation = True
                violation_type = "above_upper"
            
            # 处理违规情况
            if is_violation:
                # 如果是新的违规，记录开始时间
                if threshold.violation_start_time is None:
                    threshold.violation_start_time = timestamp
                
                # 检查是否超过持续时间
                duration = (timestamp - threshold.violation_start_time).total_seconds()
                if duration >= threshold.duration:
                    # 触发报警
                    alarm_info = {
                        'timestamp': timestamp,
                        'data_source': data_source,
                        'value': value,
                        'threshold': {
                            'lower_bound': threshold.lower_bound,
                            'upper_bound': threshold.upper_bound
                        },
                        'violation_type': violation_type,
                        'duration': duration
                    }
                    
                    # 添加到历史记录
                    self.alarm_history.append(alarm_info)
                    
                    # 触发所有报警处理函数
                    for handler in self.alarm_handlers:
                        try:
                            handler(alarm_info)
                        except Exception as e:
                            logger.error(f"执行报警处理函数失败: {str(e)}")
                    
                    return alarm_info
            else:
                # 没有违规，重置开始时间
                threshold.violation_start_time = None
            
            return None
    
    def get_alarm_history(self) -> List[Dict]:
        """
        获取报警历史记录
        
        Returns:
            List[Dict]: 报警历史记录
        """
        with self.lock:
            return self.alarm_history.copy()
    
    def clear_alarm_history(self) -> None:
        """
        清除报警历史记录
        """
        with self.lock:
            self.alarm_history.clear()
            logger.info("已清除报警历史记录")


class DataVisualizer:
    """
    数据可视化器，用于将收集的数据可视化
    """
    
    def __init__(self, data_collector: DataCollector):
        """
        初始化数据可视化器
        
        Args:
            data_collector: 数据收集器实例
        """
        if not HAS_MATPLOTLIB:
            raise ImportError("Matplotlib未安装，无法使用可视化功能")
            
        self.data_collector = data_collector
        self.figures: Dict[str, plt.Figure] = {}
        self.axes: Dict[str, plt.Axes] = {}
        self.lines: Dict[str, Dict[str, plt.Line2D]] = {}
        self.lock = threading.RLock()
    
    def create_figure(self, figure_id: str, title: str, 
                     xlabel: str = "时间", ylabel: str = "值") -> bool:
        """
        创建图表
        
        Args:
            figure_id: 图表ID
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            
        Returns:
            bool: 是否创建成功
        """
        try:
            with self.lock:
                if figure_id in self.figures:
                    logger.warning(f"图表 {figure_id} 已存在")
                    return False
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.set_title(title)
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)
                ax.grid(True)
                
                self.figures[figure_id] = fig
                self.axes[figure_id] = ax
                self.lines[figure_id] = {}
                
                logger.info(f"已创建图表: {figure_id}")
                return True
        except Exception as e:
            logger.error(f"创建图表失败: {str(e)}")
            return False
    
    def add_line(self, figure_id: str, data_source: str, label: str = None,
                color: str = None, linestyle: str = '-', marker: str = '') -> bool:
        """
        在图表中添加数据线
        
        Args:
            figure_id: 图表ID
            data_source: 数据源名称
            label: 图例标签，如果为None则使用数据源名称
            color: 线条颜色
            linestyle: 线条样式
            marker: 标记样式
            
        Returns:
            bool: 是否添加成功
        """
        try:
            with self.lock:
                if figure_id not in self.figures:
                    logger.error(f"图表 {figure_id} 不存在")
                    return False
                
                if data_source in self.lines[figure_id]:
                    logger.warning(f"数据线 {data_source} 已存在于图表 {figure_id} 中")
                    return False
                
                ax = self.axes[figure_id]
                line_label = label if label is not None else data_source
                
                # 创建空线条
                line, = ax.plot([], [], label=line_label, 
                               color=color, linestyle=linestyle, marker=marker)
                
                self.lines[figure_id][data_source] = line
                ax.legend()
                
                logger.info(f"已在图表 {figure_id} 中添加数据线: {data_source}")
                return True
        except Exception as e:
            logger.error(f"添加数据线失败: {str(e)}")
            return False
    
    def update_plot(self, figure_id: str) -> bool:
        """
        更新图表
        
        Args:
            figure_id: 图表ID
            
        Returns:
            bool: 是否更新成功
        """
        try:
            with self.lock:
                if figure_id not in self.figures:
                    logger.error(f"图表 {figure_id} 不存在")
                    return False
                
                ax = self.axes[figure_id]
                timestamps = self.data_collector.get_timestamps()
                
                # 更新每条线的数据
                for data_source, line in self.lines[figure_id].items():
                    data = self.data_collector.get_data(data_source)
                    
                    # 确保时间戳和数据长度匹配
                    min_length = min(len(timestamps), len(data))
                    if min_length > 0:
                        # 更新线条数据
                        line.set_data(timestamps[:min_length], data[:min_length])
                
                # 自动调整坐标轴范围
                ax.relim()
                ax.autoscale_view()
                
                # 调整X轴，使其更好地显示时间
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                self.figures[figure_id].tight_layout()
                
                return True
        except Exception as e:
            logger.error(f"更新图表失败: {str(e)}")
            return False
    
    def save_figure(self, figure_id: str, file_path: str, dpi: int = 100) -> bool:
        """
        保存图表到文件
        
        Args:
            figure_id: 图表ID
            file_path: 文件路径
            dpi: 分辨率
            
        Returns:
            bool: 是否保存成功
        """
        try:
            with self.lock:
                if figure_id not in self.figures:
                    logger.error(f"图表 {figure_id} 不存在")
                    return False
                
                # 确保目录存在
                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                
                # 更新图表
                self.update_plot(figure_id)
                
                # 保存图表
                self.figures[figure_id].savefig(file_path, dpi=dpi, bbox_inches='tight')
                logger.info(f"已将图表 {figure_id} 保存到: {file_path}")
                return True
        except Exception as e:
            logger.error(f"保存图表失败: {str(e)}")
            return False
    
    def close_figure(self, figure_id: str) -> bool:
        """
        关闭图表
        
        Args:
            figure_id: 图表ID
            
        Returns:
            bool: 是否关闭成功
        """
        try:
            with self.lock:
                if figure_id not in self.figures:
                    logger.error(f"图表 {figure_id} 不存在")
                    return False
                
                plt.close(self.figures[figure_id])
                del self.figures[figure_id]
                del self.axes[figure_id]
                del self.lines[figure_id]
                
                logger.info(f"已关闭图表: {figure_id}")
                return True
        except Exception as e:
            logger.error(f"关闭图表失败: {str(e)}")
            return False
    
    def create_robot_status_visualization(self, file_path: str, show_joints: bool = True,
                                         show_force: bool = False, show_temperature: bool = False) -> bool:
        """
        创建机器人状态可视化报告
        
        Args:
            file_path: 文件路径
            show_joints: 是否显示关节信息
            show_force: 是否显示力传感器信息
            show_temperature: 是否显示温度信息
            
        Returns:
            bool: 是否创建成功
        """
        try:
            # 创建一个包含多个子图的图表
            fig = plt.figure(figsize=(15, 10))
            subplot_idx = 1
            
            # 关节位置图
            if show_joints and 'joint_positions' in self.data_collector.get_all_sources():
                ax_joints = fig.add_subplot(2, 2, subplot_idx)
                subplot_idx += 1
                
                timestamps = self.data_collector.get_timestamps()
                joint_data = self.data_collector.get_data('joint_positions')
                
                if joint_data and isinstance(joint_data[0], (list, tuple)):
                    # 假设joint_data中的每个元素是包含6个关节值的列表
                    for i in range(min(6, len(joint_data[0]))):
                        joint_values = [data[i] for data in joint_data]
                        ax_joints.plot(timestamps, joint_values, label=f'关节 {i+1}')
                
                ax_joints.set_title('关节位置')
                ax_joints.set_xlabel('时间')
                ax_joints.set_ylabel('位置 (rad)')
                ax_joints.grid(True)
                ax_joints.legend()
                plt.setp(ax_joints.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # 力传感器图
            if show_force and 'force_data' in self.data_collector.get_all_sources():
                ax_force = fig.add_subplot(2, 2, subplot_idx)
                subplot_idx += 1
                
                timestamps = self.data_collector.get_timestamps()
                force_data = self.data_collector.get_data('force_data')
                
                if force_data and isinstance(force_data[0], (list, tuple)):
                    # 假设force_data中的每个元素是包含6个力/力矩值的列表
                    for i in range(min(6, len(force_data[0]))):
                        force_values = [data[i] for data in force_data]
                        ax_force.plot(timestamps, force_values, label=f'力/力矩 {i+1}')
                
                ax_force.set_title('力传感器数据')
                ax_force.set_xlabel('时间')
                ax_force.set_ylabel('力/力矩 (N/Nm)')
                ax_force.grid(True)
                ax_force.legend()
                plt.setp(ax_force.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # 温度图
            if show_temperature and 'temperature_data' in self.data_collector.get_all_sources():
                ax_temp = fig.add_subplot(2, 2, subplot_idx)
                subplot_idx += 1
                
                timestamps = self.data_collector.get_timestamps()
                temp_data = self.data_collector.get_data('temperature_data')
                
                if temp_data and isinstance(temp_data[0], (list, tuple)):
                    # 假设temperature_data中的每个元素是包含各部件温度的列表
                    for i in range(min(6, len(temp_data[0]))):
                        temp_values = [data[i] for data in temp_data]
                        ax_temp.plot(timestamps, temp_values, label=f'温度 {i+1}')
                
                ax_temp.set_title('温度数据')
                ax_temp.set_xlabel('时间')
                ax_temp.set_ylabel('温度 (°C)')
                ax_temp.grid(True)
                ax_temp.legend()
                plt.setp(ax_temp.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # 完成布局并保存
            fig.suptitle('机器人状态监控报告', fontsize=16)
            fig.tight_layout(rect=[0, 0, 1, 0.96])
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            fig.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"已创建机器人状态可视化报告: {file_path}")
            return True
        except Exception as e:
            logger.error(f"创建机器人状态可视化报告失败: {str(e)}")
            return False


class StatusDashboard:
    """
    状态监控仪表板，整合数据收集、监控和可视化功能
    """
    
    def __init__(self, max_data_points: int = 1000):
        """
        初始化状态监控仪表板
        
        Args:
            max_data_points: 最大数据点数量
        """
        self.data_collector = DataCollector(max_data_points)
        self.threshold_monitor = ThresholdMonitor()
        self.visualizer = None
        
        # 如果有matplotlib，创建可视化器
        if HAS_MATPLOTLIB:
            try:
                self.visualizer = DataVisualizer(self.data_collector)
            except Exception as e:
                logger.error(f"创建可视化器失败: {str(e)}")
                self.visualizer = None
        
        # 事件回调
        self.callbacks: Dict[str, List[Callable]] = {
            'data_added': [],
            'alarm_triggered': [],
            'status_changed': []
        }
        
        # 机器人状态信息
        self.robot_state: Dict[str, Any] = {
            'connected': False,
            'operating_mode': 'unknown',
            'power_state': 'off',
            'safety_mode': 'unknown',
            'current_task': None,
            'error_state': None,
            'timestamp': None
        }
        
        self.running = False
        self.update_thread = None
        self.update_interval = 1.0  # 默认更新间隔为1秒
    
    def register_callback(self, event_type: str, callback: Callable) -> bool:
        """
        注册事件回调函数
        
        Args:
            event_type: 事件类型 (data_added, alarm_triggered, status_changed)
            callback: 回调函数
            
        Returns:
            bool: 是否注册成功
        """
        if event_type not in self.callbacks:
            logger.error(f"未知的事件类型: {event_type}")
            return False
        
        try:
            if callback not in self.callbacks[event_type]:
                self.callbacks[event_type].append(callback)
                logger.info(f"已注册回调函数到事件 {event_type}: {callback.__name__}")
            return True
        except Exception as e:
            logger.error(f"注册回调函数失败: {str(e)}")
            return False
    
    def update_robot_state(self, **kwargs) -> None:
        """
        更新机器人状态信息
        
        Args:
            **kwargs: 要更新的状态信息
        """
        old_state = self.robot_state.copy()
        self.robot_state.update(kwargs)
        self.robot_state['timestamp'] = datetime.datetime.now()
        
        # 触发状态变化回调
        for callback in self.callbacks['status_changed']:
            try:
                callback(old_state, self.robot_state)
            except Exception as e:
                logger.error(f"执行状态变化回调失败: {str(e)}")
    
    def add_data_point(self, source_name: str, value: Any) -> None:
        """
        添加数据点
        
        Args:
            source_name: 数据源名称
            value: 数据值
        """
        self.data_collector.add_data_point(source_name, value)
        
        # 如果是数值类型，检查阈值
        if isinstance(value, (int, float)):
            alarm_info = self.threshold_monitor.check_value(source_name, value)
            if alarm_info:
                # 触发报警回调
                for callback in self.callbacks['alarm_triggered']:
                    try:
                        callback(alarm_info)
                    except Exception as e:
                        logger.error(f"执行报警回调失败: {str(e)}")
        
        # 触发数据添加回调
        for callback in self.callbacks['data_added']:
            try:
                callback(source_name, value)
            except Exception as e:
                logger.error(f"执行数据添加回调失败: {str(e)}")
    
    def add_robot_data(self, joint_positions: Optional[List[float]] = None,
                      joint_velocities: Optional[List[float]] = None,
                      joint_torques: Optional[List[float]] = None,
                      tcp_pose: Optional[List[float]] = None,
                      tcp_force: Optional[List[float]] = None,
                      temperatures: Optional[List[float]] = None,
                      current: Optional[List[float]] = None) -> None:
        """
        添加机器人数据
        
        Args:
            joint_positions: 关节位置
            joint_velocities: 关节速度
            joint_torques: 关节力矩
            tcp_pose: TCP位姿
            tcp_force: TCP力
            temperatures: 温度数据
            current: 电流数据
        """
        if joint_positions is not None:
            self.add_data_point('joint_positions', joint_positions)
        if joint_velocities is not None:
            self.add_data_point('joint_velocities', joint_velocities)
        if joint_torques is not None:
            self.add_data_point('joint_torques', joint_torques)
        if tcp_pose is not None:
            self.add_data_point('tcp_pose', tcp_pose)
        if tcp_force is not None:
            self.add_data_point('tcp_force', tcp_force)
        if temperatures is not None:
            self.add_data_point('temperatures', temperatures)
        if current is not None:
            self.add_data_point('current', current)
    
    def start_monitoring(self, update_interval: float = None) -> bool:
        """
        开始监控
        
        Args:
            update_interval: 更新间隔（秒）
            
        Returns:
            bool: 是否启动成功
        """
        if self.running:
            logger.warning("监控已经在运行中")
            return False
        
        self.running = True
        if update_interval is not None:
            self.update_interval = update_interval
            
        # 可以在这里启动周期性更新任务
        logger.info(f"已启动状态监控，更新间隔: {self.update_interval}秒")
        return True
    
    def stop_monitoring(self) -> bool:
        """
        停止监控
        
        Returns:
            bool: 是否停止成功
        """
        if not self.running:
            logger.warning("监控未在运行中")
            return False
        
        self.running = False
        logger.info("已停止状态监控")
        return True
    
    def generate_status_report(self, file_path: str) -> bool:
        """
        生成状态报告
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否生成成功
        """
        try:
            # 创建报告数据
            report = {
                'report_time': datetime.datetime.now().isoformat(),
                'robot_state': self.robot_state,
                'available_data_sources': self.data_collector.get_all_sources(),
                'alarm_history': self.threshold_monitor.get_alarm_history(),
                'data_summary': {}
            }
            
            # 添加数据摘要
            for source in report['available_data_sources']:
                data = self.data_collector.get_data(source)
                if data and all(isinstance(x, (int, float)) for x in data):
                    report['data_summary'][source] = {
                        'count': len(data),
                        'min': min(data),
                        'max': max(data),
                        'mean': float(np.mean(data)),
                        'std': float(np.std(data))
                    }
                elif data:
                    report['data_summary'][source] = {
                        'count': len(data),
                        'sample': data[0] if data else None
                    }
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # 保存报告
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已生成状态报告: {file_path}")
            
            # 如果有可视化器，也生成可视化报告
            if self.visualizer:
                viz_file = os.path.splitext(file_path)[0] + '_visualization.png'
                self.visualizer.create_robot_status_visualization(viz_file)
            
            return True
        except Exception as e:
            logger.error(f"生成状态报告失败: {str(e)}")
            return False
    
    def clear_all_data(self) -> None:
        """
        清除所有数据
        """
        self.data_collector.clear_data()
        self.threshold_monitor.clear_alarm_history()
        logger.info("已清除所有监控数据")


class RobotStatusMonitor:
    """
    机器人状态监控器，提供更高级的监控功能
    """
    
    def __init__(self):
        """
        初始化机器人状态监控器
        """
        self.dashboard = StatusDashboard()
        self.alarm_log_file = None
        self.status_log_file = None
        
        # 注册默认的报警处理函数
        self.dashboard.threshold_monitor.register_alarm_handler(self._log_alarm)
        self.dashboard.register_callback('status_changed', self._log_status_change)
    
    def set_alarm_log_file(self, file_path: str) -> bool:
        """
        设置报警日志文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否设置成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            self.alarm_log_file = file_path
            logger.info(f"已设置报警日志文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"设置报警日志文件失败: {str(e)}")
            return False
    
    def set_status_log_file(self, file_path: str) -> bool:
        """
        设置状态日志文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否设置成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            self.status_log_file = file_path
            logger.info(f"已设置状态日志文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"设置状态日志文件失败: {str(e)}")
            return False
    
    def _log_alarm(self, alarm_info: Dict) -> None:
        """
        记录报警信息
        
        Args:
            alarm_info: 报警信息
        """
        # 记录到日志文件
        if self.alarm_log_file:
            try:
                with open(self.alarm_log_file, 'a', encoding='utf-8') as f:
                    log_entry = {
                        'timestamp': alarm_info['timestamp'].isoformat(),
                        'data_source': alarm_info['data_source'],
                        'value': alarm_info['value'],
                        'threshold': alarm_info['threshold'],
                        'violation_type': alarm_info['violation_type'],
                        'duration': alarm_info['duration']
                    }
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            except Exception as e:
                logger.error(f"写入报警日志失败: {str(e)}")
        
        # 同时记录到系统日志
        logger.warning(f"报警: {alarm_info['data_source']} = {alarm_info['value']}, "
                      f"类型: {alarm_info['violation_type']}, "
                      f"持续时间: {alarm_info['duration']}秒")
    
    def _log_status_change(self, old_state: Dict, new_state: Dict) -> None:
        """
        记录状态变化
        
        Args:
            old_state: 旧状态
            new_state: 新状态
        """
        # 找出变化的状态字段
        changed_fields = {}
        for key, value in new_state.items():
            if key not in old_state or old_state[key] != value:
                changed_fields[key] = {'old': old_state.get(key), 'new': value}
        
        # 如果有变化，记录到日志
        if changed_fields:
            # 记录到日志文件
            if self.status_log_file:
                try:
                    with open(self.status_log_file, 'a', encoding='utf-8') as f:
                        log_entry = {
                            'timestamp': datetime.datetime.now().isoformat(),
                            'changes': changed_fields
                        }
                        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                except Exception as e:
                    logger.error(f"写入状态日志失败: {str(e)}")
            
            # 同时记录到系统日志
            change_strings = []
            for field, values in changed_fields.items():
                change_strings.append(f"{field}: {values['old']} -> {values['new']}")
            logger.info(f"状态变化: {', '.join(change_strings)}")
    
    def setup_joint_monitoring(self, joint_limits: List[Tuple[float, float]], 
                             velocity_limits: Optional[List[Tuple[float, float]]] = None,
                             torque_limits: Optional[List[Tuple[float, float]]] = None) -> None:
        """
        设置关节监控
        
        Args:
            joint_limits: 关节位置限制 [(min, max)]
            velocity_limits: 关节速度限制 [(min, max)]
            torque_limits: 关节力矩限制 [(min, max)]
        """
        # 设置关节位置阈值
        for i, (lower, upper) in enumerate(joint_limits):
            self.dashboard.threshold_monitor.set_threshold(
                f'joint_{i+1}_position', 
                lower_bound=lower, 
                upper_bound=upper,
                duration=1.0  # 1秒超阈值触发报警
            )
        
        # 设置关节速度阈值
        if velocity_limits:
            for i, (lower, upper) in enumerate(velocity_limits):
                self.dashboard.threshold_monitor.set_threshold(
                    f'joint_{i+1}_velocity', 
                    lower_bound=lower, 
                    upper_bound=upper,
                    duration=1.0
                )
        
        # 设置关节力矩阈值
        if torque_limits:
            for i, (lower, upper) in enumerate(torque_limits):
                self.dashboard.threshold_monitor.set_threshold(
                    f'joint_{i+1}_torque', 
                    lower_bound=lower, 
                    upper_bound=upper,
                    duration=0.5  # 力矩超阈值0.5秒触发报警
                )
    
    def setup_visualization(self) -> bool:
        """
        设置可视化
        
        Returns:
            bool: 是否设置成功
        """
        if not self.dashboard.visualizer:
            logger.error("可视化器不可用，无法设置可视化")
            return False
        
        try:
            # 创建关节位置图表
            self.dashboard.visualizer.create_figure(
                'joint_positions', 
                title='关节位置监控',
                xlabel='时间',
                ylabel='位置 (rad)'
            )
            
            # 创建关节速度图表
            self.dashboard.visualizer.create_figure(
                'joint_velocities', 
                title='关节速度监控',
                xlabel='时间',
                ylabel='速度 (rad/s)'
            )
            
            # 创建TCP力图表
            self.dashboard.visualizer.create_figure(
                'tcp_force', 
                title='TCP力监控',
                xlabel='时间',
                ylabel='力 (N)'
            )
            
            return True
        except Exception as e:
            logger.error(f"设置可视化失败: {str(e)}")
            return False


# 创建全局实例
_global_monitor = None


def get_monitor() -> RobotStatusMonitor:
    """
    获取全局监控器实例
    
    Returns:
        RobotStatusMonitor: 监控器实例
    """
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = RobotStatusMonitor()
    return _global_monitor


def start_monitoring() -> bool:
    """
    便捷函数：开始监控
    
    Returns:
        bool: 是否启动成功
    """
    monitor = get_monitor()
    return monitor.dashboard.start_monitoring()


def stop_monitoring() -> bool:
    """
    便捷函数：停止监控
    
    Returns:
        bool: 是否停止成功
    """
    monitor = get_monitor()
    return monitor.dashboard.stop_monitoring()


def add_robot_data(**kwargs) -> None:
    """
    便捷函数：添加机器人数据
    
    Args:
        **kwargs: 机器人数据
    """
    monitor = get_monitor()
    monitor.dashboard.add_robot_data(**kwargs)


# 示例用法
if __name__ == '__main__':
    # 创建监控器
    monitor = get_monitor()
    
    # 设置日志文件
    monitor.set_alarm_log_file('logs/alarm.log')
    monitor.set_status_log_file('logs/status.log')
    
    # 设置关节监控阈值
    # 假设UR5机器人的关节限制
    joint_limits = [
        (-2.9, 2.9),   # 关节1
        (-1.8, 1.8),   # 关节2
        (-2.9, 2.9),   # 关节3
        (-3.1, 3.1),   # 关节4
        (-2.9, 2.9),   # 关节5
        (-3.2, 3.2)    # 关节6
    ]
    monitor.setup_joint_monitoring(joint_limits)
    
    # 设置可视化（如果可用）
    monitor.setup_visualization()
    
    # 开始监控
    monitor.dashboard.start_monitoring()
    
    # 模拟机器人数据
    try:
        print("开始模拟数据收集，按Ctrl+C停止...")
        
        # 更新机器人状态
        monitor.dashboard.update_robot_state(
            connected=True,
            operating_mode='normal',
            power_state='on',
            safety_mode='normal',
            current_task='测试任务'
        )
        
        # 模拟添加数据
        for i in range(100):
            # 生成模拟的关节位置（带噪声的正弦曲线）
            joint_positions = [
                0.5 * np.sin(i * 0.1) + np.random.normal(0, 0.05),
                0.3 * np.sin(i * 0.1 + 0.5) + np.random.normal(0, 0.05),
                0.4 * np.sin(i * 0.1 + 1.0) + np.random.normal(0, 0.05),
                0.2 * np.sin(i * 0.1 + 1.5) + np.random.normal(0, 0.05),
                0.3 * np.sin(i * 0.1 + 2.0) + np.random.normal(0, 0.05),
                0.4 * np.sin(i * 0.1 + 2.5) + np.random.normal(0, 0.05)
            ]
            
            # 模拟关节速度
            joint_velocities = [
                0.5 * np.cos(i * 0.1) + np.random.normal(0, 0.02),
                0.3 * np.cos(i * 0.1 + 0.5) + np.random.normal(0, 0.02),
                0.4 * np.cos(i * 0.1 + 1.0) + np.random.normal(0, 0.02),
                0.2 * np.cos(i * 0.1 + 1.5) + np.random.normal(0, 0.02),
                0.3 * np.cos(i * 0.1 + 2.0) + np.random.normal(0, 0.02),
                0.4 * np.cos(i * 0.1 + 2.5) + np.random.normal(0, 0.02)
            ]
            
            # 模拟TCP力
            tcp_force = [
                5.0 + 2.0 * np.sin(i * 0.2) + np.random.normal(0, 0.5),
                3.0 + 1.5 * np.sin(i * 0.2 + 0.5) + np.random.normal(0, 0.5),
                10.0 + 3.0 * np.sin(i * 0.2 + 1.0) + np.random.normal(0, 0.5),
                0.5 * np.sin(i * 0.2 + 1.5) + np.random.normal(0, 0.1),
                0.3 * np.sin(i * 0.2 + 2.0) + np.random.normal(0, 0.1),
                0.2 * np.sin(i * 0.2 + 2.5) + np.random.normal(0, 0.1)
            ]
            
            # 添加数据
            monitor.dashboard.add_robot_data(
                joint_positions=joint_positions,
                joint_velocities=joint_velocities,
                tcp_force=tcp_force
            )
            
            # 添加单个关节数据（用于阈值监控）
            for j in range(6):
                monitor.dashboard.add_data_point(f'joint_{j+1}_position', joint_positions[j])
                monitor.dashboard.add_data_point(f'joint_{j+1}_velocity', joint_velocities[j])
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n停止模拟数据收集")
    finally:
        # 停止监控
        monitor.dashboard.stop_monitoring()
        
        # 生成状态报告
        monitor.dashboard.generate_status_report('reports/robot_status_report.json')
        
        # 导出数据
        monitor.dashboard.data_collector.export_data('data/robot_data.json')
        
        print("监控已停止，报告已生成")
