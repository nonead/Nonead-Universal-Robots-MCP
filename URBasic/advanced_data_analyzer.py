#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级数据分析模块

此模块提供全面的机器人运行数据分析功能，支持统计分析、趋势检测、
异常识别、性能评估和数据可视化，为机器人系统的监控、优化和决策提供支持。

作者: Nonead
日期: 2024
版本: 1.0
"""

import json
import logging
import os
import time
import datetime
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
import numpy as np
import pandas as pd
from enum import Enum, auto
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import warnings
from .advanced_data_recorder import (
    DataRecord, DataRecordType, RecordPriority, AdvancedDataRecorder,
    get_data_recorder, StorageFormat
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 忽略警告
warnings.filterwarnings('ignore')

# 设置matplotlib字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


class AnalysisType(Enum):
    """分析类型枚举"""
    STATISTICAL = "statistical"            # 统计分析
    TREND = "trend"                        # 趋势分析
    ANOMALY = "anomaly"                    # 异常检测
    PERFORMANCE = "performance"            # 性能分析
    ENERGY = "energy"                      # 能耗分析
    TRAJECTORY = "trajectory"              # 轨迹分析
    CORRELATION = "correlation"            # 相关性分析
    CLUSTERING = "clustering"              # 聚类分析
    CUSTOM = "custom"                      # 自定义分析


class VisualizationType(Enum):
    """可视化类型枚举"""
    LINE = "line"                          # 折线图
    SCATTER = "scatter"                    # 散点图
    BAR = "bar"                            # 柱状图
    HISTOGRAM = "histogram"                # 直方图
    HEATMAP = "heatmap"                    # 热力图
    BOX = "box"                            # 箱线图
    THREE_D_SCATTER = "3d_scatter"              # 3D散点图
    TRAJECTORY = "trajectory"              # 轨迹图
    PIE = "pie"                            # 饼图
    RADAR = "radar"                        # 雷达图


class AnomalyDetectionMethod(Enum):
    """异常检测方法枚举"""
    Z_SCORE = "z_score"                    # Z-score方法
    IQR = "iqr"                            # IQR方法
    ISOLATION_FOREST = "isolation_forest"  # 孤立森林
    LOF = "lof"                            # 局部离群因子
    DBSCAN = "dbscan"                      # DBSCAN聚类
    CUSTOM = "custom"                      # 自定义方法


class TrendAnalysisMethod(Enum):
    """趋势分析方法枚举"""
    LINEAR_REGRESSION = "linear_regression"  # 线性回归
    MOVING_AVERAGE = "moving_average"        # 移动平均
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"  # 指数平滑
    POLYNOMIAL_FIT = "polynomial_fit"        # 多项式拟合
    CUSTOM = "custom"                        # 自定义方法


@dataclass
class AnalysisConfig:
    """分析配置"""
    analysis_type: AnalysisType = AnalysisType.STATISTICAL  # 分析类型
    time_window_seconds: Optional[int] = None               # 时间窗口(秒)
    sampling_interval_seconds: Optional[float] = None       # 采样间隔(秒)
    filters: Dict[str, Any] = field(default_factory=dict)    # 过滤条件
    parameters: Dict[str, Any] = field(default_factory=dict)  # 分析参数


@dataclass
class VisualizationConfig:
    """可视化配置"""
    visualization_type: VisualizationType = VisualizationType.LINE  # 可视化类型
    title: Optional[str] = None                                     # 图表标题
    x_label: Optional[str] = None                                   # X轴标签
    y_label: Optional[str] = None                                   # Y轴标签
    figsize: Tuple[int, int] = (10, 6)                              # 图表大小
    dpi: int = 100                                                  # 图表DPI
    save_path: Optional[str] = None                                 # 保存路径
    show_plot: bool = True                                          # 是否显示图表
    theme: str = "default"                                          # 主题
    custom_style: Dict[str, Any] = field(default_factory=dict)       # 自定义样式


@dataclass
class AnomalyConfig:
    """异常检测配置"""
    method: AnomalyDetectionMethod = AnomalyDetectionMethod.Z_SCORE  # 检测方法
    threshold: float = 3.0                                            # 阈值
    window_size: int = 100                                            # 窗口大小
    custom_function: Optional[Callable] = None                        # 自定义函数


@dataclass
class TrendConfig:
    """趋势分析配置"""
    method: TrendAnalysisMethod = TrendAnalysisMethod.LINEAR_REGRESSION  # 分析方法
    window_size: int = 10                                                # 窗口大小
    degree: int = 2                                                      # 多项式次数
    smoothing_level: float = 0.1                                         # 平滑级别
    custom_function: Optional[Callable] = None                           # 自定义函数


class DataAnalyzer:
    """数据分析师基类"""
    
    def __init__(self, recorder: Optional[AdvancedDataRecorder] = None):
        """
        初始化数据分析师
        
        Args:
            recorder: 数据记录器实例
        """
        self.recorder = recorder or get_data_recorder()
    
    def _records_to_dataframe(self, records: List[DataRecord]) -> pd.DataFrame:
        """
        将记录列表转换为DataFrame
        
        Args:
            records: 记录列表
            
        Returns:
            pd.DataFrame: 转换后的DataFrame
        """
        data_list = []
        
        for record in records:
            # 基础信息
            data_dict = {
                'timestamp': record.timestamp,
                'record_id': record.record_id,
                'robot_id': record.robot_id,
                'record_type': record.record_type.value if record.record_type else None,
                'priority': record.priority.value
            }
            
            # 添加记录数据
            data_dict.update(record.data)
            
            # 添加元数据（带前缀避免冲突）
            for key, value in record.metadata.items():
                data_dict[f'metadata_{key}'] = value
            
            data_list.append(data_dict)
        
        if not data_list:
            return pd.DataFrame()
        
        df = pd.DataFrame(data_list)
        
        # 转换时间戳为DatetimeIndex
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('datetime', inplace=True)
        
        return df
    
    def _get_records(self, 
                    start_time: Optional[float] = None,
                    end_time: Optional[float] = None,
                    record_type: Optional[DataRecordType] = None,
                    robot_id: Optional[str] = None,
                    priority: Optional[RecordPriority] = None,
                    limit: int = 10000) -> List[DataRecord]:
        """
        获取记录
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            record_type: 记录类型
            robot_id: 机器人ID
            priority: 优先级
            limit: 限制数量
            
        Returns:
            List[DataRecord]: 记录列表
        """
        return self.recorder.query_records(
            start_time=start_time,
            end_time=end_time,
            record_type=record_type,
            robot_id=robot_id,
            priority=priority,
            limit=limit
        )
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据预处理
        
        Args:
            df: 原始数据
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        # 复制数据
        processed_df = df.copy()
        
        # 填充缺失值（数值列）
        numeric_cols = processed_df.select_dtypes(include=['float64', 'int64']).columns
        processed_df[numeric_cols] = processed_df[numeric_cols].fillna(method='ffill').fillna(method='bfill')
        
        # 删除仍有缺失值的行
        processed_df.dropna(subset=numeric_cols, inplace=True)
        
        return processed_df


class StatisticalAnalyzer(DataAnalyzer):
    """统计分析师"""
    
    def analyze(self, 
               df: pd.DataFrame,
               columns: Optional[List[str]] = None,
               group_by: Optional[str] = None) -> Dict[str, Any]:
        """
        执行统计分析
        
        Args:
            df: 数据
            columns: 要分析的列
            group_by: 分组列
            
        Returns:
            Dict[str, Any]: 统计结果
        """
        if df.empty:
            return {'error': '数据为空'}
        
        # 获取数值列
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        
        if columns:
            numeric_cols = [col for col in columns if col in numeric_cols]
        
        if not numeric_cols:
            return {'error': '没有找到数值列'}
        
        results = {}
        
        if group_by and group_by in df.columns:
            # 分组统计
            grouped = df.groupby(group_by)
            
            for group_name, group_data in grouped:
                results[group_name] = {}
                
                # 基本统计
                stats_df = group_data[numeric_cols].describe()
                for col in numeric_cols:
                    results[group_name][col] = {
                        'count': stats_df.loc['count', col],
                        'mean': stats_df.loc['mean', col],
                        'std': stats_df.loc['std', col],
                        'min': stats_df.loc['min', col],
                        '25%': stats_df.loc['25%', col],
                        '50%': stats_df.loc['50%', col],
                        '75%': stats_df.loc['75%', col],
                        'max': stats_df.loc['max', col]
                    }
                    
                    # 额外统计量
                    results[group_name][col]['median'] = group_data[col].median()
                    results[group_name][col]['skew'] = group_data[col].skew()
                    results[group_name][col]['kurtosis'] = group_data[col].kurtosis()
                    results[group_name][col]['iqr'] = stats.iqr(group_data[col])
        else:
            # 整体统计
            for col in numeric_cols:
                results[col] = {
                    'count': df[col].count(),
                    'mean': df[col].mean(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'median': df[col].median(),
                    'skew': df[col].skew(),
                    'kurtosis': df[col].kurtosis(),
                    'iqr': stats.iqr(df[col]),
                    'sum': df[col].sum(),
                    'var': df[col].var(),
                    'sem': stats.sem(df[col])  # 标准误差
                }
        
        return results
    
    def get_time_series_stats(self, 
                             df: pd.DataFrame,
                             column: str,
                             window_size: int = 10) -> pd.DataFrame:
        """
        获取时间序列统计
        
        Args:
            df: 数据
            column: 列名
            window_size: 窗口大小
            
        Returns:
            pd.DataFrame: 时间序列统计结果
        """
        if df.empty or column not in df.columns:
            return pd.DataFrame()
        
        # 计算滑动窗口统计
        rolling = df[column].rolling(window=window_size)
        
        result = pd.DataFrame({
            'timestamp': df['timestamp'],
            'value': df[column],
            'rolling_mean': rolling.mean(),
            'rolling_std': rolling.std(),
            'rolling_min': rolling.min(),
            'rolling_max': rolling.max()
        })
        
        return result


class TrendAnalyzer(DataAnalyzer):
    """趋势分析师"""
    
    def analyze(self, 
               df: pd.DataFrame,
               x_column: str,
               y_column: str,
               config: TrendConfig = TrendConfig()) -> Dict[str, Any]:
        """
        执行趋势分析
        
        Args:
            df: 数据
            x_column: X轴列
            y_column: Y轴列
            config: 趋势分析配置
            
        Returns:
            Dict[str, Any]: 趋势分析结果
        """
        if df.empty or x_column not in df.columns or y_column not in df.columns:
            return {'error': '数据不完整'}
        
        # 准备数据
        X = df[x_column].values.reshape(-1, 1)
        y = df[y_column].values
        
        results = {
            'method': config.method.value,
            'x_column': x_column,
            'y_column': y_column
        }
        
        if config.method == TrendAnalysisMethod.LINEAR_REGRESSION:
            # 线性回归
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)
            
            results['slope'] = model.coef_[0]
            results['intercept'] = model.intercept_
            results['r2_score'] = r2_score(y, y_pred)
            results['mse'] = mean_squared_error(y, y_pred)
            results['predictions'] = y_pred.tolist()
            
            # 趋势方向
            if results['slope'] > 0:
                results['trend_direction'] = 'increasing'
            elif results['slope'] < 0:
                results['trend_direction'] = 'decreasing'
            else:
                results['trend_direction'] = 'stable'
        
        elif config.method == TrendAnalysisMethod.MOVING_AVERAGE:
            # 移动平均
            df_sorted = df.sort_values(x_column)
            rolling_mean = df_sorted[y_column].rolling(window=config.window_size).mean()
            
            results['window_size'] = config.window_size
            results['moving_averages'] = rolling_mean.dropna().tolist()
            results['timestamps'] = df_sorted.loc[rolling_mean.dropna().index, x_column].tolist()
        
        elif config.method == TrendAnalysisMethod.POLYNOMIAL_FIT:
            # 多项式拟合
            coeffs = np.polyfit(X.flatten(), y, deg=config.degree)
            y_pred = np.polyval(coeffs, X.flatten())
            
            results['coefficients'] = coeffs.tolist()
            results['degree'] = config.degree
            results['r2_score'] = r2_score(y, y_pred)
            results['predictions'] = y_pred.tolist()
        
        elif config.method == TrendAnalysisMethod.CUSTOM and config.custom_function:
            # 自定义方法
            results['custom_results'] = config.custom_function(df, x_column, y_column)
        
        return results
    
    def detect_seasonality(self, 
                         df: pd.DataFrame,
                         column: str,
                         period: int) -> Dict[str, Any]:
        """
        检测季节性
        
        Args:
            df: 数据
            column: 列名
            period: 周期
            
        Returns:
            Dict[str, Any]: 季节性分析结果
        """
        if df.empty or column not in df.columns or len(df) < 2 * period:
            return {'error': '数据不足或不完整'}
        
        # 计算自相关
        values = df[column].dropna().values
        acf = self._autocorrelation(values, period)
        
        # 计算周期图
        fft_values = np.fft.fft(values)
        frequencies = np.fft.fftfreq(len(values))
        power_spectrum = np.abs(fft_values) ** 2
        
        # 找到主要频率
        positive_freq_idx = frequencies > 0
        main_freq_idx = np.argmax(power_spectrum[positive_freq_idx])
        main_freq = frequencies[positive_freq_idx][main_freq_idx]
        main_period = 1.0 / main_freq if main_freq > 0 else 0
        
        results = {
            'autocorrelation_at_period': acf,
            'has_seasonality': abs(acf) > 0.3,  # 阈值判断
            'main_frequency': main_freq,
            'main_period': main_period,
            'recommended_period': period
        }
        
        return results
    
    def _autocorrelation(self, values: np.ndarray, lag: int) -> float:
        """
        计算自相关
        
        Args:
            values: 数据值
            lag: 滞后阶数
            
        Returns:
            float: 自相关系数
        """
        if lag >= len(values):
            return 0.0
        
        # 标准化数据
        values_std = (values - np.mean(values)) / np.std(values)
        
        # 计算自相关
        return np.correlate(values_std[lag:], values_std[:-lag], mode='valid')[0] / (len(values) - lag)


class AnomalyDetector(DataAnalyzer):
    """异常检测器"""
    
    def detect(self, 
              df: pd.DataFrame,
              columns: List[str],
              config: AnomalyConfig = AnomalyConfig()) -> pd.DataFrame:
        """
        检测异常
        
        Args:
            df: 数据
            columns: 要检测的列
            config: 异常检测配置
            
        Returns:
            pd.DataFrame: 包含异常标记的数据
        """
        if df.empty:
            return pd.DataFrame()
        
        result_df = df.copy()
        
        for column in columns:
            if column not in result_df.columns:
                continue
            
            anomaly_column = f"{column}_anomaly"
            score_column = f"{column}_anomaly_score"
            
            if config.method == AnomalyDetectionMethod.Z_SCORE:
                # Z-score方法
                z_scores = np.abs(stats.zscore(result_df[column]))
                result_df[anomaly_column] = z_scores > config.threshold
                result_df[score_column] = z_scores
            
            elif config.method == AnomalyDetectionMethod.IQR:
                # IQR方法
                Q1 = result_df[column].quantile(0.25)
                Q3 = result_df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - config.threshold * IQR
                upper_bound = Q3 + config.threshold * IQR
                
                is_outlier = (result_df[column] < lower_bound) | (result_df[column] > upper_bound)
                result_df[anomaly_column] = is_outlier
                
                # 计算异常分数
                scores = np.zeros_like(result_df[column])
                below = result_df[column] < lower_bound
                above = result_df[column] > upper_bound
                scores[below] = (lower_bound - result_df.loc[below, column]) / IQR
                scores[above] = (result_df.loc[above, column] - upper_bound) / IQR
                result_df[score_column] = scores
            
            elif config.method == AnomalyDetectionMethod.DBSCAN:
                # DBSCAN聚类
                X = result_df[[column]].values
                X_scaled = StandardScaler().fit_transform(X)
                
                dbscan = DBSCAN(eps=0.3, min_samples=10)
                labels = dbscan.fit_predict(X_scaled)
                
                result_df[anomaly_column] = labels == -1  # -1表示离群点
                result_df[score_column] = 1.0 / (1.0 + np.abs(labels))
            
            elif config.method == AnomalyDetectionMethod.CUSTOM and config.custom_function:
                # 自定义方法
                anomalies, scores = config.custom_function(result_df[column], config)
                result_df[anomaly_column] = anomalies
                result_df[score_column] = scores
        
        # 添加总体异常标记
        anomaly_columns = [col for col in result_df.columns if col.endswith('_anomaly')]
        if anomaly_columns:
            result_df['is_anomaly'] = result_df[anomaly_columns].any(axis=1)
        
        return result_df
    
    def detect_time_series_anomalies(self, 
                                   df: pd.DataFrame,
                                   column: str,
                                   config: AnomalyConfig = AnomalyConfig()) -> pd.DataFrame:
        """
        检测时间序列异常
        
        Args:
            df: 数据
            column: 列名
            config: 异常检测配置
            
        Returns:
            pd.DataFrame: 包含异常标记的数据
        """
        if df.empty or column not in df.columns:
            return pd.DataFrame()
        
        result_df = df.copy()
        
        # 计算滑动窗口统计
        rolling = result_df[column].rolling(window=config.window_size)
        result_df['rolling_mean'] = rolling.mean()
        result_df['rolling_std'] = rolling.std()
        
        # 计算Z-score
        z_scores = np.abs((result_df[column] - result_df['rolling_mean']) / result_df['rolling_std'])
        z_scores = z_scores.fillna(0)
        
        result_df[f"{column}_anomaly"] = z_scores > config.threshold
        result_df[f"{column}_anomaly_score"] = z_scores
        result_df['is_anomaly'] = result_df[f"{column}_anomaly"]
        
        return result_df
    
    def get_anomaly_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        获取异常统计摘要
        
        Args:
            df: 包含异常标记的数据
            
        Returns:
            Dict[str, Any]: 异常统计摘要
        """
        if df.empty:
            return {'error': '数据为空'}
        
        summary = {}
        
        # 总体异常统计
        if 'is_anomaly' in df.columns:
            anomalies = df[df['is_anomaly']]
            summary['total_records'] = len(df)
            summary['total_anomalies'] = len(anomalies)
            summary['anomaly_percentage'] = (len(anomalies) / len(df)) * 100 if len(df) > 0 else 0
            
            if len(anomalies) > 0:
                summary['first_anomaly_timestamp'] = anomalies['timestamp'].min()
                summary['last_anomaly_timestamp'] = anomalies['timestamp'].max()
        
        # 各列异常统计
        anomaly_columns = [col for col in df.columns if col.endswith('_anomaly')]
        for col in anomaly_columns:
            original_col = col.replace('_anomaly', '')
            anomaly_count = df[col].sum()
            
            summary[original_col] = {
                'anomaly_count': int(anomaly_count),
                'anomaly_percentage': (anomaly_count / len(df)) * 100 if len(df) > 0 else 0
            }
            
            # 异常值的统计
            if anomaly_count > 0:
                anomaly_values = df.loc[df[col], original_col]
                summary[original_col]['anomaly_min'] = anomaly_values.min()
                summary[original_col]['anomaly_max'] = anomaly_values.max()
                summary[original_col]['anomaly_mean'] = anomaly_values.mean()
        
        return summary


class PerformanceAnalyzer(DataAnalyzer):
    """性能分析师"""
    
    def analyze_robot_performance(self, 
                                 df: pd.DataFrame,
                                 operation_column: str,
                                 duration_column: str,
                                 robot_id_column: str = 'robot_id') -> Dict[str, Any]:
        """
        分析机器人性能
        
        Args:
            df: 数据
            operation_column: 操作类型列
            duration_column: 持续时间列
            robot_id_column: 机器人ID列
            
        Returns:
            Dict[str, Any]: 性能分析结果
        """
        if df.empty or operation_column not in df.columns or duration_column not in df.columns:
            return {'error': '数据不完整'}
        
        results = {}
        
        # 按机器人分组
        if robot_id_column in df.columns:
            for robot_id, robot_data in df.groupby(robot_id_column):
                results[robot_id] = self._analyze_single_robot_performance(
                    robot_data, operation_column, duration_column
                )
        else:
            # 整体分析
            results['overall'] = self._analyze_single_robot_performance(
                df, operation_column, duration_column
            )
        
        return results
    
    def _analyze_single_robot_performance(self, 
                                         df: pd.DataFrame,
                                         operation_column: str,
                                         duration_column: str) -> Dict[str, Any]:
        """
        分析单个机器人性能
        
        Args:
            df: 数据
            operation_column: 操作类型列
            duration_column: 持续时间列
            
        Returns:
            Dict[str, Any]: 性能分析结果
        """
        robot_results = {}
        
        # 按操作类型分析
        for operation_type, operation_data in df.groupby(operation_column):
            durations = operation_data[duration_column]
            
            robot_results[operation_type] = {
                'count': len(durations),
                'mean_duration': durations.mean(),
                'median_duration': durations.median(),
                'std_duration': durations.std(),
                'min_duration': durations.min(),
                'max_duration': durations.max(),
                'total_duration': durations.sum()
            }
        
        # 总体性能
        all_durations = df[duration_column]
        robot_results['overall'] = {
            'total_operations': len(df),
            'mean_duration': all_durations.mean(),
            'median_duration': all_durations.median(),
            'throughput': len(df) / (all_durations.sum() or 1),  # 每秒操作数
            'total_duration': all_durations.sum()
        }
        
        return robot_results
    
    def analyze_cycle_time(self, 
                          df: pd.DataFrame,
                          cycle_id_column: str,
                          timestamp_column: str = 'timestamp') -> pd.DataFrame:
        """
        分析循环时间
        
        Args:
            df: 数据
            cycle_id_column: 循环ID列
            timestamp_column: 时间戳列
            
        Returns:
            pd.DataFrame: 循环时间分析结果
        """
        if df.empty or cycle_id_column not in df.columns:
            return pd.DataFrame()
        
        # 按循环ID分组计算循环时间
        cycle_times = []
        
        for cycle_id, cycle_data in df.groupby(cycle_id_column):
            if len(cycle_data) > 1:
                start_time = cycle_data[timestamp_column].min()
                end_time = cycle_data[timestamp_column].max()
                cycle_time = end_time - start_time
                
                cycle_times.append({
                    'cycle_id': cycle_id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'cycle_time': cycle_time,
                    'operation_count': len(cycle_data)
                })
        
        return pd.DataFrame(cycle_times)


class EnergyAnalyzer(DataAnalyzer):
    """能耗分析师"""
    
    def analyze_energy_consumption(self, 
                                  df: pd.DataFrame,
                                  voltage_column: str,
                                  current_column: str,
                                  timestamp_column: str = 'timestamp',
                                  robot_id_column: str = 'robot_id') -> Dict[str, Any]:
        """
        分析能耗
        
        Args:
            df: 数据
            voltage_column: 电压列
            current_column: 电流列
            timestamp_column: 时间戳列
            robot_id_column: 机器人ID列
            
        Returns:
            Dict[str, Any]: 能耗分析结果
        """
        if (df.empty or voltage_column not in df.columns or 
            current_column not in df.columns or timestamp_column not in df.columns):
            return {'error': '数据不完整'}
        
        results = {}
        
        # 计算功率 (P = V * I)
        df['power'] = df[voltage_column] * df[current_column]
        
        # 按机器人分组
        if robot_id_column in df.columns:
            for robot_id, robot_data in df.groupby(robot_id_column):
                results[robot_id] = self._analyze_single_robot_energy(
                    robot_data.sort_values(timestamp_column), timestamp_column
                )
        else:
            # 整体分析
            results['overall'] = self._analyze_single_robot_energy(
                df.sort_values(timestamp_column), timestamp_column
            )
        
        return results
    
    def _analyze_single_robot_energy(self, 
                                    df: pd.DataFrame,
                                    timestamp_column: str) -> Dict[str, Any]:
        """
        分析单个机器人能耗
        
        Args:
            df: 数据
            timestamp_column: 时间戳列
            
        Returns:
            Dict[str, Any]: 能耗分析结果
        """
        # 计算能耗（积分近似）
        timestamps = df[timestamp_column].values
        power = df['power'].values
        
        # 使用梯形法则计算能耗（千瓦时）
        energy_kwh = 0
        if len(timestamps) > 1:
            for i in range(1, len(timestamps)):
                duration_hours = (timestamps[i] - timestamps[i-1]) / 3600.0
                avg_power_kW = (power[i] + power[i-1]) / 2000.0  # 转换为千瓦
                energy_kwh += avg_power_kW * duration_hours
        
        # 计算统计数据
        analysis = {
            'total_energy_kwh': energy_kwh,
            'mean_power_w': df['power'].mean(),
            'max_power_w': df['power'].max(),
            'min_power_w': df['power'].min(),
            'median_power_w': df['power'].median(),
            'std_power_w': df['power'].std(),
            'total_duration_hours': (timestamps[-1] - timestamps[0]) / 3600.0 if len(timestamps) > 1 else 0,
            'samples_count': len(df)
        }
        
        # 计算能耗效率
        if analysis['total_duration_hours'] > 0:
            analysis['average_power_kW'] = analysis['total_energy_kwh'] / analysis['total_duration_hours']
        
        return analysis
    
    def analyze_energy_by_operation(self, 
                                   energy_df: pd.DataFrame,
                                   operation_df: pd.DataFrame,
                                   timestamp_column: str = 'timestamp',
                                   robot_id_column: str = 'robot_id') -> Dict[str, Any]:
        """
        按操作分析能耗
        
        Args:
            energy_df: 能耗数据
            operation_df: 操作数据
            timestamp_column: 时间戳列
            robot_id_column: 机器人ID列
            
        Returns:
            Dict[str, Any]: 按操作的能耗分析结果
        """
        if energy_df.empty or operation_df.empty:
            return {'error': '数据为空'}
        
        results = {}
        
        # 确保两个DataFrame都有序
        energy_df = energy_df.sort_values(timestamp_column)
        operation_df = operation_df.sort_values(timestamp_column)
        
        # 按机器人分组
        if robot_id_column in energy_df.columns and robot_id_column in operation_df.columns:
            for robot_id in set(energy_df[robot_id_column]).intersection(operation_df[robot_id_column]):
                robot_energy = energy_df[energy_df[robot_id_column] == robot_id]
                robot_operations = operation_df[operation_df[robot_id_column] == robot_id]
                
                if not robot_energy.empty and not robot_operations.empty:
                    results[robot_id] = self._analyze_robot_energy_by_operation(
                        robot_energy, robot_operations, timestamp_column
                    )
        
        return results
    
    def _analyze_robot_energy_by_operation(self, 
                                         energy_df: pd.DataFrame,
                                         operation_df: pd.DataFrame,
                                         timestamp_column: str) -> Dict[str, Any]:
        """
        分析单个机器人按操作的能耗
        
        Args:
            energy_df: 能耗数据
            operation_df: 操作数据
            timestamp_column: 时间戳列
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        # 对每个操作找到对应的能耗数据
        operation_energy = {}
        
        for _, operation in operation_df.iterrows():
            operation_time = operation[timestamp_column]
            
            # 找到操作时间附近的能耗数据
            time_window = 1.0  # 1秒窗口
            nearby_energy = energy_df[
                (energy_df[timestamp_column] >= operation_time - time_window/2) &
                (energy_df[timestamp_column] <= operation_time + time_window/2)
            ]
            
            if not nearby_energy.empty:
                operation_type = operation.get('operation_type', 'unknown')
                
                if operation_type not in operation_energy:
                    operation_energy[operation_type] = []
                
                # 使用平均功率作为该操作的功率
                operation_energy[operation_type].append(nearby_energy['power'].mean())
        
        # 计算统计数据
        results = {}
        for op_type, powers in operation_energy.items():
            powers_array = np.array(powers)
            results[op_type] = {
                'count': len(powers),
                'mean_power_w': powers_array.mean(),
                'median_power_w': np.median(powers_array),
                'std_power_w': powers_array.std(),
                'min_power_w': powers_array.min(),
                'max_power_w': powers_array.max()
            }
        
        return results


class TrajectoryAnalyzer(DataAnalyzer):
    """轨迹分析师"""
    
    def analyze_trajectory(self, 
                          df: pd.DataFrame,
                          x_column: str,
                          y_column: str,
                          z_column: Optional[str] = None,
                          timestamp_column: str = 'timestamp') -> Dict[str, Any]:
        """
        分析轨迹
        
        Args:
            df: 数据
            x_column: X坐标列
            y_column: Y坐标列
            z_column: Z坐标列（可选）
            timestamp_column: 时间戳列
            
        Returns:
            Dict[str, Any]: 轨迹分析结果
        """
        if df.empty or x_column not in df.columns or y_column not in df.columns:
            return {'error': '数据不完整'}
        
        # 按时间排序
        df_sorted = df.sort_values(timestamp_column)
        
        # 计算距离和速度
        positions = df_sorted[[x_column, y_column]].values
        if z_column and z_column in df_sorted.columns:
            positions = np.column_stack((positions, df_sorted[z_column].values))
        
        timestamps = df_sorted[timestamp_column].values
        
        # 计算移动距离
        distances = np.zeros(len(positions))
        speeds = np.zeros(len(positions))
        accelerations = np.zeros(len(positions))
        
        if len(positions) > 1:
            # 计算每段距离
            segment_distances = np.sqrt(np.sum(np.diff(positions, axis=0)**2, axis=1))
            distances[1:] = np.cumsum(segment_distances)
            
            # 计算速度
            time_diffs = np.diff(timestamps)
            speeds[1:] = segment_distances / time_diffs
            
            # 计算加速度
            if len(speeds) > 2:
                acceleration_time_diffs = time_diffs[:-1]
                speed_diffs = np.diff(speeds[1:])
                accelerations[2:] = speed_diffs / acceleration_time_diffs
        
        # 计算统计数据
        results = {
            'total_distance': distances[-1] if len(distances) > 0 else 0,
            'mean_speed': np.mean(speeds[1:]) if len(speeds) > 1 else 0,
            'max_speed': np.max(speeds) if len(speeds) > 0 else 0,
            'min_speed': np.min(speeds[speeds > 0]) if np.any(speeds > 0) else 0,
            'duration': timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0,
            'start_position': positions[0].tolist() if len(positions) > 0 else [],
            'end_position': positions[-1].tolist() if len(positions) > 0 else [],
            'straight_line_distance': np.linalg.norm(positions[-1] - positions[0]) if len(positions) > 1 else 0,
            'path_efficiency': np.linalg.norm(positions[-1] - positions[0]) / distances[-1] if distances[-1] > 0 else 0,
            'points_count': len(positions)
        }
        
        # 如果有加速度数据
        if np.any(accelerations):
            results['mean_acceleration'] = np.mean(np.abs(accelerations[2:]))
            results['max_acceleration'] = np.max(np.abs(accelerations))
        
        return results
    
    def analyze_trajectory_smoothness(self, 
                                    df: pd.DataFrame,
                                    x_column: str,
                                    y_column: str,
                                    z_column: Optional[str] = None) -> float:
        """
        分析轨迹平滑度（使用曲率的标准差）
        
        Args:
            df: 数据
            x_column: X坐标列
            y_column: Y坐标列
            z_column: Z坐标列（可选）
            
        Returns:
            float: 平滑度指标（值越小越平滑）
        """
        if df.empty or len(df) < 3:
            return 0.0
        
        # 获取位置数据
        positions = df[[x_column, y_column]].values
        if z_column and z_column in df.columns:
            positions = np.column_stack((positions, df[z_column].values))
        
        # 计算曲率
        curvatures = []
        for i in range(1, len(positions) - 1):
            # 三点计算曲率
            p0 = positions[i-1]
            p1 = positions[i]
            p2 = positions[i+1]
            
            # 计算向量
            v1 = p1 - p0
            v2 = p2 - p1
            
            # 计算曲率 (对于2D)
            if len(p0) == 2:
                # 叉积的大小 (z分量)
                cross_product = v1[0] * v2[1] - v1[1] * v2[0]
                # 曲率
                curvature = 2 * abs(cross_product) / (np.linalg.norm(v1) * np.linalg.norm(v2) * np.linalg.norm(v1 + v2))
                curvatures.append(curvature)
            else:
                # 3D情况简化处理
                # 计算v1和v2的叉积
                cross_product = np.cross(v1, v2)
                denominator = np.linalg.norm(v1) * np.linalg.norm(v2)
                if denominator > 0:
                    sin_theta = np.linalg.norm(cross_product) / denominator
                    curvature = sin_theta / np.linalg.norm(v1)
                    curvatures.append(curvature)
        
        # 计算曲率的标准差作为平滑度指标
        if curvatures:
            return np.std(curvatures)
        else:
            return 0.0


class DataVisualizer:
    """数据可视化器"""
    
    def __init__(self):
        """
        初始化数据可视化器
        """
        self._setup_style()
    
    def _setup_style(self, theme: str = "default"):
        """
        设置可视化风格
        
        Args:
            theme: 主题名称
        """
        if theme == "dark":
            plt.style.use('dark_background')
        elif theme == "seaborn":
            plt.style.use('seaborn-v0_8-whitegrid')
        elif theme == "ggplot":
            plt.style.use('ggplot')
        else:
            plt.style.use('default')
    
    def plot_time_series(self, 
                        df: pd.DataFrame,
                        columns: List[str],
                        config: VisualizationConfig = VisualizationConfig()) -> plt.Figure:
        """
        绘制时间序列图
        
        Args:
            df: 数据
            columns: 要绘制的列
            config: 可视化配置
            
        Returns:
            plt.Figure: 图表对象
        """
        if df.empty:
            return None
        
        self._setup_style(config.theme)
        
        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
        
        # 检查是否有datetime索引
        if isinstance(df.index, pd.DatetimeIndex):
            x_data = df.index
        elif 'datetime' in df.columns:
            x_data = df['datetime']
        elif 'timestamp' in df.columns:
            x_data = pd.to_datetime(df['timestamp'], unit='s')
        else:
            x_data = np.arange(len(df))
        
        # 绘制每条线
        for column in columns:
            if column in df.columns:
                ax.plot(x_data, df[column], label=column)
        
        # 设置标题和标签
        if config.title:
            ax.set_title(config.title)
        if config.x_label:
            ax.set_xlabel(config.x_label)
        else:
            ax.set_xlabel('时间')
        if config.y_label:
            ax.set_ylabel(config.y_label)
        else:
            ax.set_ylabel('值')
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 应用自定义样式
        for key, value in config.custom_style.items():
            if hasattr(ax, key):
                setattr(ax, key, value)
        
        # 保存图表
        if config.save_path:
            os.makedirs(os.path.dirname(config.save_path), exist_ok=True)
            plt.savefig(config.save_path, dpi=config.dpi, bbox_inches='tight')
        
        # 显示图表
        if config.show_plot:
            plt.show()
        
        return fig
    
    def plot_scatter(self, 
                    df: pd.DataFrame,
                    x_column: str,
                    y_column: str,
                    hue_column: Optional[str] = None,
                    config: VisualizationConfig = VisualizationConfig()) -> plt.Figure:
        """
        绘制散点图
        
        Args:
            df: 数据
            x_column: X轴列
            y_column: Y轴列
            hue_column: 颜色分组列
            config: 可视化配置
            
        Returns:
            plt.Figure: 图表对象
        """
        if df.empty or x_column not in df.columns or y_column not in df.columns:
            return None
        
        self._setup_style(config.theme)
        
        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
        
        if hue_column and hue_column in df.columns:
            # 分组绘制
            unique_values = df[hue_column].unique()
            for value in unique_values:
                subset = df[df[hue_column] == value]
                ax.scatter(subset[x_column], subset[y_column], label=str(value), alpha=0.7)
            ax.legend(title=hue_column)
        else:
            ax.scatter(df[x_column], df[y_column], alpha=0.7)
        
        # 设置标题和标签
        if config.title:
            ax.set_title(config.title)
        ax.set_xlabel(config.x_label or x_column)
        ax.set_ylabel(config.y_label or y_column)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 保存图表
        if config.save_path:
            os.makedirs(os.path.dirname(config.save_path), exist_ok=True)
            plt.savefig(config.save_path, dpi=config.dpi, bbox_inches='tight')
        
        # 显示图表
        if config.show_plot:
            plt.show()
        
        return fig
    
    def plot_histogram(self, 
                      df: pd.DataFrame,
                      column: str,
                      bins: int = 30,
                      config: VisualizationConfig = VisualizationConfig()) -> plt.Figure:
        """
        绘制直方图
        
        Args:
            df: 数据
            column: 列名
            bins: 分箱数量
            config: 可视化配置
            
        Returns:
            plt.Figure: 图表对象
        """
        if df.empty or column not in df.columns:
            return None
        
        self._setup_style(config.theme)
        
        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
        
        ax.hist(df[column].dropna(), bins=bins, alpha=0.7, edgecolor='black')
        
        # 设置标题和标签
        if config.title:
            ax.set_title(config.title)
        ax.set_xlabel(config.x_label or column)
        ax.set_ylabel(config.y_label or '频率')
        
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # 保存图表
        if config.save_path:
            os.makedirs(os.path.dirname(config.save_path), exist_ok=True)
            plt.savefig(config.save_path, dpi=config.dpi, bbox_inches='tight')
        
        # 显示图表
        if config.show_plot:
            plt.show()
        
        return fig
    
    def plot_heatmap(self, 
                    df: pd.DataFrame,
                    config: VisualizationConfig = VisualizationConfig()) -> plt.Figure:
        """
        绘制热力图
        
        Args:
            df: 数据（相关性矩阵或类似数据）
            config: 可视化配置
            
        Returns:
            plt.Figure: 图表对象
        """
        if df.empty:
            return None
        
        self._setup_style(config.theme)
        
        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
        
        sns.heatmap(df, annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
        
        # 设置标题
        if config.title:
            ax.set_title(config.title)
        
        plt.tight_layout()
        
        # 保存图表
        if config.save_path:
            os.makedirs(os.path.dirname(config.save_path), exist_ok=True)
            plt.savefig(config.save_path, dpi=config.dpi, bbox_inches='tight')
        
        # 显示图表
        if config.show_plot:
            plt.show()
        
        return fig
    
    def plot_trajectory_2d(self, 
                          df: pd.DataFrame,
                          x_column: str,
                          y_column: str,
                          color_column: Optional[str] = None,
                          config: VisualizationConfig = VisualizationConfig()) -> plt.Figure:
        """
        绘制2D轨迹图
        
        Args:
            df: 数据
            x_column: X坐标列
            y_column: Y坐标列
            color_column: 颜色映射列
            config: 可视化配置
            
        Returns:
            plt.Figure: 图表对象
        """
        if df.empty or x_column not in df.columns or y_column not in df.columns:
            return None
        
        self._setup_style(config.theme)
        
        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
        
        if color_column and color_column in df.columns:
            # 带颜色映射的轨迹
            scatter = ax.scatter(
                df[x_column], df[y_column], 
                c=df[color_column], 
                cmap='viridis', 
                alpha=0.7,
                s=50
            )
            plt.colorbar(scatter, ax=ax, label=color_column)
        else:
            # 简单轨迹
            ax.plot(df[x_column], df[y_column], 'b-', alpha=0.7)
            ax.scatter(df[x_column].iloc[0], df[y_column].iloc[0], color='green', s=100, label='Start')
            ax.scatter(df[x_column].iloc[-1], df[y_column].iloc[-1], color='red', s=100, label='End')
            ax.legend()
        
        # 设置标题和标签
        if config.title:
            ax.set_title(config.title)
        ax.set_xlabel(config.x_label or x_column)
        ax.set_ylabel(config.y_label or y_column)
        
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')
        plt.tight_layout()
        
        # 保存图表
        if config.save_path:
            os.makedirs(os.path.dirname(config.save_path), exist_ok=True)
            plt.savefig(config.save_path, dpi=config.dpi, bbox_inches='tight')
        
        # 显示图表
        if config.show_plot:
            plt.show()
        
        return fig
    
    def plot_anomalies(self, 
                      df: pd.DataFrame,
                      value_column: str,
                      anomaly_column: str,
                      config: VisualizationConfig = VisualizationConfig()) -> plt.Figure:
        """
        绘制异常点
        
        Args:
            df: 数据
            value_column: 值列
            anomaly_column: 异常标记列
            config: 可视化配置
            
        Returns:
            plt.Figure: 图表对象
        """
        if df.empty or value_column not in df.columns or anomaly_column not in df.columns:
            return None
        
        self._setup_style(config.theme)
        
        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
        
        # 检查是否有datetime索引
        if isinstance(df.index, pd.DatetimeIndex):
            x_data = df.index
        elif 'datetime' in df.columns:
            x_data = df['datetime']
        elif 'timestamp' in df.columns:
            x_data = pd.to_datetime(df['timestamp'], unit='s')
        else:
            x_data = np.arange(len(df))
        
        # 绘制正常值
        normal_data = df[~df[anomaly_column]]
        ax.plot(x_data[~df[anomaly_column]], normal_data[value_column], 'b-', alpha=0.7, label='正常值')
        
        # 绘制异常值
        anomaly_data = df[df[anomaly_column]]
        if not anomaly_data.empty:
            ax.scatter(x_data[df[anomaly_column]], anomaly_data[value_column], 
                      color='red', s=100, alpha=0.8, label='异常值')
        
        # 设置标题和标签
        if config.title:
            ax.set_title(config.title)
        ax.set_xlabel(config.x_label or '时间')
        ax.set_ylabel(config.y_label or value_column)
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 保存图表
        if config.save_path:
            os.makedirs(os.path.dirname(config.save_path), exist_ok=True)
            plt.savefig(config.save_path, dpi=config.dpi, bbox_inches='tight')
        
        # 显示图表
        if config.show_plot:
            plt.show()
        
        return fig
    
    def plot_comparison(self, 
                       dfs: List[pd.DataFrame],
                       labels: List[str],
                       column: str,
                       config: VisualizationConfig = VisualizationConfig()) -> plt.Figure:
        """
        绘制比较图
        
        Args:
            dfs: 数据框列表
            labels: 标签列表
            column: 要比较的列
            config: 可视化配置
            
        Returns:
            plt.Figure: 图表对象
        """
        if not dfs or any(df.empty or column not in df.columns for df in dfs):
            return None
        
        self._setup_style(config.theme)
        
        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
        
        for i, (df, label) in enumerate(zip(dfs, labels)):
            # 检查是否有datetime索引
            if isinstance(df.index, pd.DatetimeIndex):
                x_data = df.index
            elif 'datetime' in df.columns:
                x_data = df['datetime']
            elif 'timestamp' in df.columns:
                x_data = pd.to_datetime(df['timestamp'], unit='s')
            else:
                x_data = np.arange(len(df))
            
            ax.plot(x_data, df[column], label=label)
        
        # 设置标题和标签
        if config.title:
            ax.set_title(config.title)
        ax.set_xlabel(config.x_label or '时间')
        ax.set_ylabel(config.y_label or column)
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 保存图表
        if config.save_path:
            os.makedirs(os.path.dirname(config.save_path), exist_ok=True)
            plt.savefig(config.save_path, dpi=config.dpi, bbox_inches='tight')
        
        # 显示图表
        if config.show_plot:
            plt.show()
        
        return fig


class AdvancedDataAnalyzer:
    """高级数据分析器集成类"""
    
    def __init__(self, recorder: Optional[AdvancedDataRecorder] = None):
        """
        初始化高级数据分析器
        
        Args:
            recorder: 数据记录器实例
        """
        self.recorder = recorder or get_data_recorder()
        self.statistical_analyzer = StatisticalAnalyzer(recorder)
        self.trend_analyzer = TrendAnalyzer(recorder)
        self.anomaly_detector = AnomalyDetector(recorder)
        self.performance_analyzer = PerformanceAnalyzer(recorder)
        self.energy_analyzer = EnergyAnalyzer(recorder)
        self.trajectory_analyzer = TrajectoryAnalyzer(recorder)
        self.visualizer = DataVisualizer()
    
    def load_data(self, 
                 start_time: Optional[float] = None,
                 end_time: Optional[float] = None,
                 record_type: Optional[DataRecordType] = None,
                 robot_id: Optional[str] = None,
                 priority: Optional[RecordPriority] = None,
                 limit: int = 10000) -> pd.DataFrame:
        """
        加载数据
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            record_type: 记录类型
            robot_id: 机器人ID
            priority: 优先级
            limit: 限制数量
            
        Returns:
            pd.DataFrame: 加载的数据
        """
        # 获取记录
        records = self._get_records(
            start_time=start_time,
            end_time=end_time,
            record_type=record_type,
            robot_id=robot_id,
            priority=priority,
            limit=limit
        )
        
        # 转换为DataFrame
        df = self._records_to_dataframe(records)
        
        # 数据预处理
        return self._preprocess_data(df)
    
    def analyze(self, 
               df: pd.DataFrame,
               analysis_type: AnalysisType,
               config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行分析
        
        Args:
            df: 数据
            analysis_type: 分析类型
            config: 分析配置
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        config = config or {}
        
        if analysis_type == AnalysisType.STATISTICAL:
            return self.statistical_analyzer.analyze(
                df, 
                columns=config.get('columns'),
                group_by=config.get('group_by')
            )
        
        elif analysis_type == AnalysisType.TREND:
            trend_config = TrendConfig(
                method=config.get('method', TrendAnalysisMethod.LINEAR_REGRESSION),
                window_size=config.get('window_size', 10),
                degree=config.get('degree', 2)
            )
            return self.trend_analyzer.analyze(
                df,
                x_column=config.get('x_column', 'timestamp'),
                y_column=config.get('y_column'),
                config=trend_config
            )
        
        elif analysis_type == AnalysisType.ANOMALY:
            anomaly_config = AnomalyConfig(
                method=config.get('method', AnomalyDetectionMethod.Z_SCORE),
                threshold=config.get('threshold', 3.0)
            )
            result_df = self.anomaly_detector.detect(
                df,
                columns=config.get('columns', []),
                config=anomaly_config
            )
            # 返回异常统计和标记的数据
            return {
                'anomaly_summary': self.anomaly_detector.get_anomaly_summary(result_df),
                'data_with_anomalies': result_df.to_dict('records')
            }
        
        elif analysis_type == AnalysisType.PERFORMANCE:
            return self.performance_analyzer.analyze_robot_performance(
                df,
                operation_column=config.get('operation_column', 'operation_type'),
                duration_column=config.get('duration_column', 'execution_time')
            )
        
        elif analysis_type == AnalysisType.ENERGY:
            return self.energy_analyzer.analyze_energy_consumption(
                df,
                voltage_column=config.get('voltage_column', 'voltage'),
                current_column=config.get('current_column', 'current')
            )
        
        elif analysis_type == AnalysisType.TRAJECTORY:
            return self.trajectory_analyzer.analyze_trajectory(
                df,
                x_column=config.get('x_column', 'x'),
                y_column=config.get('y_column', 'y'),
                z_column=config.get('z_column')
            )
        
        elif analysis_type == AnalysisType.CORRELATION:
            # 计算相关性矩阵
            numeric_df = df.select_dtypes(include=['float64', 'int64'])
            return {
                'correlation_matrix': numeric_df.corr().to_dict(),
                'strongest_correlations': self._find_strongest_correlations(numeric_df)
            }
        
        elif analysis_type == AnalysisType.CLUSTERING:
            return self._perform_clustering(
                df,
                columns=config.get('columns', []),
                n_clusters=config.get('n_clusters', 3)
            )
        
        else:
            return {'error': f'不支持的分析类型: {analysis_type}'}
    
    def visualize(self, 
                 df: pd.DataFrame,
                 visualization_type: VisualizationType,
                 config: Optional[Dict[str, Any]] = None) -> plt.Figure:
        """
        数据可视化
        
        Args:
            df: 数据
            visualization_type: 可视化类型
            config: 可视化配置
            
        Returns:
            plt.Figure: 图表对象
        """
        config = config or {}
        viz_config = VisualizationConfig(
            title=config.get('title'),
            x_label=config.get('x_label'),
            y_label=config.get('y_label'),
            figsize=config.get('figsize', (10, 6)),
            dpi=config.get('dpi', 100),
            save_path=config.get('save_path'),
            show_plot=config.get('show_plot', True),
            theme=config.get('theme', 'default')
        )
        
        if visualization_type == VisualizationType.LINE:
            return self.visualizer.plot_time_series(
                df,
                columns=config.get('columns', []),
                config=viz_config
            )
        
        elif visualization_type == VisualizationType.SCATTER:
            return self.visualizer.plot_scatter(
                df,
                x_column=config.get('x_column'),
                y_column=config.get('y_column'),
                hue_column=config.get('hue_column'),
                config=viz_config
            )
        
        elif visualization_type == VisualizationType.HISTOGRAM:
            return self.visualizer.plot_histogram(
                df,
                column=config.get('column'),
                bins=config.get('bins', 30),
                config=viz_config
            )
        
        elif visualization_type == VisualizationType.HEATMAP:
            # 对于热力图，计算相关性矩阵
            numeric_df = df.select_dtypes(include=['float64', 'int64'])
            corr_matrix = numeric_df.corr()
            return self.visualizer.plot_heatmap(corr_matrix, config=viz_config)
        
        elif visualization_type == VisualizationType.TRAJECTORY:
            return self.visualizer.plot_trajectory_2d(
                df,
                x_column=config.get('x_column'),
                y_column=config.get('y_column'),
                color_column=config.get('color_column'),
                config=viz_config
            )
        
        elif visualization_type == VisualizationType.BOX:
            # 绘制箱线图
            self._setup_style(viz_config.theme)
            fig, ax = plt.subplots(figsize=viz_config.figsize, dpi=viz_config.dpi)
            
            columns = config.get('columns', [])
            if columns:
                df[columns].boxplot(ax=ax)
            else:
                df.select_dtypes(include=['float64', 'int64']).boxplot(ax=ax)
            
            if viz_config.title:
                ax.set_title(viz_config.title)
            ax.set_xlabel(viz_config.x_label or '变量')
            ax.set_ylabel(viz_config.y_label or '值')
            
            plt.tight_layout()
            
            if viz_config.save_path:
                os.makedirs(os.path.dirname(viz_config.save_path), exist_ok=True)
                plt.savefig(viz_config.save_path, dpi=viz_config.dpi, bbox_inches='tight')
            
            if viz_config.show_plot:
                plt.show()
            
            return fig
        
        else:
            logger.error(f'不支持的可视化类型: {visualization_type}')
            return None
    
    def generate_report(self, 
                       start_time: Optional[float] = None,
                       end_time: Optional[float] = None,
                       robot_id: Optional[str] = None,
                       report_path: Optional[str] = None) -> Dict[str, Any]:
        """
        生成综合分析报告
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            robot_id: 机器人ID
            report_path: 报告保存路径
            
        Returns:
            Dict[str, Any]: 报告内容
        """
        # 加载数据
        df = self.load_data(
            start_time=start_time,
            end_time=end_time,
            robot_id=robot_id
        )
        
        if df.empty:
            return {'error': '没有找到数据'}
        
        report = {
            'metadata': {
                'generated_at': time.time(),
                'generated_at_str': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'robot_id': robot_id,
                'time_range': {
                    'start': start_time,
                    'end': end_time
                },
                'data_points': len(df)
            },
            'analyses': {}
        }
        
        # 执行各种分析
        
        # 1. 统计分析
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if numeric_cols:
            report['analyses']['statistical'] = self.analyze(
                df,
                AnalysisType.STATISTICAL,
                {'columns': numeric_cols[:5]}  # 分析前5个数值列
            )
        
        # 2. 性能分析（如果有相关列）
        if 'operation_type' in df.columns and 'execution_time' in df.columns:
            report['analyses']['performance'] = self.analyze(
                df,
                AnalysisType.PERFORMANCE,
                {'operation_column': 'operation_type', 'duration_column': 'execution_time'}
            )
        
        # 3. 能耗分析（如果有相关列）
        if 'voltage' in df.columns and 'current' in df.columns:
            report['analyses']['energy'] = self.analyze(
                df,
                AnalysisType.ENERGY,
                {'voltage_column': 'voltage', 'current_column': 'current'}
            )
        
        # 4. 异常检测（对温度等关键参数）
        temperature_cols = [col for col in df.columns if 'temp' in col.lower() or 'temperature' in col.lower()]
        if temperature_cols:
            report['analyses']['anomalies'] = self.analyze(
                df,
                AnalysisType.ANOMALY,
                {'columns': temperature_cols}
            )
        
        # 5. 相关性分析
        report['analyses']['correlation'] = self.analyze(
            df,
            AnalysisType.CORRELATION
        )
        
        # 保存报告
        if report_path:
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"分析报告已保存到: {report_path}")
        
        return report
    
    def compare_robots(self, 
                      robot_ids: List[str],
                      start_time: Optional[float] = None,
                      end_time: Optional[float] = None,
                      metric_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        比较多个机器人的性能
        
        Args:
            robot_ids: 机器人ID列表
            start_time: 开始时间
            end_time: 结束时间
            metric_columns: 要比较的指标列
            
        Returns:
            Dict[str, Any]: 比较结果
        """
        comparison_results = {
            'robots': {},
            'summary': {}
        }
        
        all_data = []
        
        # 收集每个机器人的数据
        for robot_id in robot_ids:
            df = self.load_data(
                start_time=start_time,
                end_time=end_time,
                robot_id=robot_id
            )
            
            if not df.empty:
                comparison_results['robots'][robot_id] = {
                    'data_points': len(df),
                    'metrics': {}
                }
                
                # 计算指标
                if metric_columns:
                    for col in metric_columns:
                        if col in df.columns:
                            comparison_results['robots'][robot_id]['metrics'][col] = {
                                'mean': df[col].mean(),
                                'median': df[col].median(),
                                'std': df[col].std(),
                                'min': df[col].min(),
                                'max': df[col].max()
                            }
                
                all_data.append((robot_id, df))
        
        # 生成比较摘要
        if metric_columns and all_data:
            for col in metric_columns:
                values = []
                valid_robots = []
                
                for robot_id, df in all_data:
                    if col in df.columns:
                        values.append(df[col].mean())
                        valid_robots.append(robot_id)
                
                if values:
                    best_idx = np.argmin(values) if 'error' in col.lower() or 'temperature' in col.lower() else np.argmax(values)
                    comparison_results['summary'][col] = {
                        'best_robot': valid_robots[best_idx],
                        'best_value': values[best_idx],
                        'average_value': np.mean(values),
                        'range': {'min': min(values), 'max': max(values)},
                        'variation': np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
                    }
        
        return comparison_results
    
    def _find_strongest_correlations(self, df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        找到最强的相关性
        
        Args:
            df: 数据
            top_n: 返回前N个
            
        Returns:
            List[Dict[str, Any]]: 相关性列表
        """
        corr_matrix = df.corr().abs()
        
        # 提取上三角矩阵（排除对角线）
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # 找到强相关性
        strong_correlations = []
        
        for column in upper.columns:
            for idx in upper.index:
                correlation = upper.loc[idx, column]
                if not np.isnan(correlation) and correlation > 0.7:  # 强相关阈值
                    strong_correlations.append({
                        'variable1': idx,
                        'variable2': column,
                        'correlation': correlation
                    })
        
        # 按相关性强度排序
        strong_correlations.sort(key=lambda x: x['correlation'], reverse=True)
        
        return strong_correlations[:top_n]
    
    def _perform_clustering(self, 
                           df: pd.DataFrame,
                           columns: List[str],
                           n_clusters: int = 3) -> Dict[str, Any]:
        """
        执行聚类分析
        
        Args:
            df: 数据
            columns: 要聚类的列
            n_clusters: 聚类数量
            
        Returns:
            Dict[str, Any]: 聚类结果
        """
        if not columns:
            # 使用所有数值列
            numeric_df = df.select_dtypes(include=['float64', 'int64'])
            columns = numeric_df.columns.tolist()
        else:
            numeric_df = df[columns].select_dtypes(include=['float64', 'int64'])
        
        if numeric_df.empty:
            return {'error': '没有找到合适的数值列进行聚类'}
        
        # 标准化数据
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)
        
        # 执行K-means聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(scaled_data)
        
        # 计算聚类中心
        centers = scaler.inverse_transform(kmeans.cluster_centers_)
        
        # 计算每个聚类的统计信息
        cluster_stats = {}
        for i in range(n_clusters):
            cluster_data = numeric_df[labels == i]
            cluster_stats[i] = {
                'size': len(cluster_data),
                'center': centers[i].tolist(),
                'statistics': {}
            }
            
            for col_idx, col in enumerate(numeric_df.columns):
                cluster_stats[i]['statistics'][col] = {
                    'mean': cluster_data[col].mean(),
                    'std': cluster_data[col].std(),
                    'min': cluster_data[col].min(),
                    'max': cluster_data[col].max()
                }
        
        return {
            'n_clusters': n_clusters,
            'labels': labels.tolist(),
            'inertia': kmeans.inertia_,
            'cluster_centers': centers.tolist(),
            'cluster_statistics': cluster_stats,
            'feature_names': numeric_df.columns.tolist()
        }
    
    # 辅助方法
    def _get_records(self, **kwargs):
        """获取记录的辅助方法"""
        return self.statistical_analyzer._get_records(**kwargs)
    
    def _records_to_dataframe(self, records):
        """转换记录到DataFrame的辅助方法"""
        return self.statistical_analyzer._records_to_dataframe(records)
    
    def _preprocess_data(self, df):
        """数据预处理的辅助方法"""
        return self.statistical_analyzer._preprocess_data(df)
    
    def _setup_style(self, theme):
        """设置可视化风格的辅助方法"""
        self.visualizer._setup_style(theme)


# 全局分析器实例
_advanced_analyzer_instance = None

def get_data_analyzer() -> AdvancedDataAnalyzer:
    """
    获取高级数据分析器实例（单例模式）
    
    Returns:
        AdvancedDataAnalyzer: 高级数据分析器实例
    """
    global _advanced_analyzer_instance
    
    if _advanced_analyzer_instance is None:
        _advanced_analyzer_instance = AdvancedDataAnalyzer()
    
    return _advanced_analyzer_instance


# 示例用法
if __name__ == "__main__":
    # 初始化分析器
    analyzer = AdvancedDataAnalyzer()
    
    # 这里可以添加示例代码来演示功能
    print("高级数据分析器已初始化")
    print("可用分析类型:", [t.value for t in AnalysisType])
    print("可用可视化类型:", [v.value for v in VisualizationType])


"""
使用示例:

# 1. 初始化分析器
from URBasic.advanced_data_analyzer import AdvancedDataAnalyzer, AnalysisType, VisualizationType
analyzer = AdvancedDataAnalyzer()

# 2. 加载数据
import time
end_time = time.time()
start_time = end_time - 3600  # 过去1小时
df = analyzer.load_data(start_time=start_time, end_time=end_time)

# 3. 执行统计分析
stats = analyzer.analyze(
    df,
    AnalysisType.STATISTICAL,
    {'columns': ['temperature_joint_1', 'temperature_joint_2']}
)

# 4. 执行异常检测
anomalies = analyzer.analyze(
    df,
    AnalysisType.ANOMALY,
    {'columns': ['temperature_joint_1'], 'threshold': 2.5}
)

# 5. 执行趋势分析
trend = analyzer.analyze(
    df,
    AnalysisType.TREND,
    {'x_column': 'timestamp', 'y_column': 'temperature_joint_1'}
)

# 6. 数据可视化
analyzer.visualize(
    df,
    VisualizationType.LINE,
    {
        'columns': ['temperature_joint_1', 'temperature_joint_2'],
        'title': '关节温度趋势',
        'y_label': '温度 (°C)',
        'save_path': 'temperature_trend.png'
    }
)

# 7. 生成综合报告
report = analyzer.generate_report(
    start_time=start_time,
    end_time=end_time,
    report_path='robot_analysis_report.json'
)

# 8. 比较多个机器人
comparison = analyzer.compare_robots(
    robot_ids=['robot_1', 'robot_2'],
    start_time=start_time,
    end_time=end_time,
    metric_columns=['temperature_joint_1', 'execution_time']
)
"""
