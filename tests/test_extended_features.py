#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试扩展功能模块

此文件包含对所有扩展功能模块的单元测试和集成测试
"""

import unittest
import sys
import os
import numpy as np

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入需要测试的模块
from URBasic.advanced_multi_robot_coordinator import AdvancedMultiRobotCoordinator, CollaborationMode
from URBasic.advanced_trajectory_planner import AdvancedTrajectoryPlanner
from URBasic.advanced_data_recorder import AdvancedDataRecorder, RecordType
from URBasic.advanced_data_analyzer import get_data_analyzer, AnalysisType


class TestAdvancedMultiRobotCoordinator(unittest.TestCase):
    """测试高级多机器人协调器"""

    def setUp(self):
        """设置测试环境"""
        self.coordinator = AdvancedMultiRobotCoordinator()
    
    def test_initialization(self):
        """测试协调器初始化"""
        self.assertIsInstance(self.coordinator, AdvancedMultiRobotCoordinator)
        self.assertEqual(self.coordinator.get_registered_robots(), [])
    
    def test_robot_registration(self):
        """测试机器人注册"""
        # 模拟机器人ID
        robot_ids = ["robot1", "robot2"]
        
        # 注册机器人
        for robot_id in robot_ids:
            self.coordinator.register_robot(robot_id)
        
        # 验证注册结果
        registered_robots = self.coordinator.get_registered_robots()
        self.assertEqual(len(registered_robots), 2)
        self.assertIn("robot1", registered_robots)
        self.assertIn("robot2", registered_robots)
    
    def test_collaboration_mode(self):
        """测试协作模式设置"""
        # 测试设置各种协作模式
        modes = [
            CollaborationMode.SEQUENTIAL,
            CollaborationMode.PARALLEL,
            CollaborationMode.SYNCHRONOUS,
            CollaborationMode.HIERARCHICAL
        ]
        
        for mode in modes:
            self.coordinator.set_collaboration_mode(mode)
            self.assertEqual(self.coordinator.get_collaboration_mode(), mode)
    
    def test_create_task(self):
        """测试创建协同任务"""
        # 首先注册一些机器人
        robot_ids = ["robot1", "robot2"]
        for robot_id in robot_ids:
            self.coordinator.register_robot(robot_id)
        
        # 创建任务分配
        robot_assignments = {
            "robot1": {"operation": "move", "params": {"x": 0.1, "y": 0.2, "z": 0.3}},
            "robot2": {"operation": "pick", "params": {"target": "object1"}}
        }
        
        # 创建任务
        task_id = self.coordinator.create_collaboration_task(
            task_name="测试任务",
            robot_assignments=robot_assignments
        )
        
        # 验证任务创建
        self.assertIsNotNone(task_id)
        
        # 尝试获取任务
        task = self.coordinator._tasks.get(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["name"], "测试任务")


class TestAdvancedTrajectoryPlanner(unittest.TestCase):
    """测试高级轨迹规划器"""
    
    def setUp(self):
        """设置测试环境"""
        self.planner = AdvancedTrajectoryPlanner()
    
    def test_bezier_curve_generation(self):
        """测试贝塞尔曲线生成"""
        # 定义控制点
        control_points = [
            [0.0, 0.0, 0.5, 0.0, 0.0, 0.0],
            [0.1, 0.1, 0.5, 0.0, 0.0, 0.0],
            [0.2, 0.0, 0.5, 0.0, 0.0, 0.0]
        ]
        
        # 生成贝塞尔曲线
        curve_points = self.planner.generate_bezier_curve(
            control_points=control_points,
            num_points=10
        )
        
        # 验证生成的点数
        self.assertEqual(len(curve_points), 10)
        
        # 验证起点和终点
        np.testing.assert_allclose(curve_points[0], control_points[0], atol=1e-6)
        np.testing.assert_allclose(curve_points[-1], control_points[-1], atol=1e-6)
    
    def test_trajectory_optimization(self):
        """测试轨迹优化"""
        # 定义路径点
        waypoints = [
            [0.0, 0.0, 0.5, 0.0, 0.0, 0.0],
            [0.1, 0.1, 0.5, 0.0, 0.0, 0.0],
            [0.2, 0.0, 0.5, 0.0, 0.0, 0.0]
        ]
        
        # 测试时间优化
        optimized_waypoints = self.planner.optimize_trajectory(
            waypoints=waypoints,
            optimization_type="time"
        )
        
        # 验证起点和终点不变
        np.testing.assert_allclose(optimized_waypoints[0], waypoints[0], atol=1e-6)
        np.testing.assert_allclose(optimized_waypoints[-1], waypoints[-1], atol=1e-6)
        
        # 测试能耗优化
        optimized_waypoints = self.planner.optimize_trajectory(
            waypoints=waypoints,
            optimization_type="energy"
        )
        
        # 验证起点和终点不变
        np.testing.assert_allclose(optimized_waypoints[0], waypoints[0], atol=1e-6)
        np.testing.assert_allclose(optimized_waypoints[-1], waypoints[-1], atol=1e-6)


class TestAdvancedDataRecorder(unittest.TestCase):
    """测试高级数据记录器"""
    
    def setUp(self):
        """设置测试环境"""
        self.recorder = AdvancedDataRecorder()
    
    def test_start_recording(self):
        """测试开始记录"""
        # 定义记录类型
        record_types = [RecordType.ROBOT_STATE, RecordType.JOINT_DATA]
        
        # 启动记录
        session_id = self.recorder.start_recording(
            robot_id="test_robot",
            record_types=record_types,
            duration=5.0  # 短时间记录用于测试
        )
        
        # 验证会话ID生成
        self.assertIsNotNone(session_id)
        
        # 验证会话在活跃列表中
        active_sessions = self.recorder.get_active_sessions()
        self.assertIn(session_id, active_sessions)
    
    def test_stop_recording(self):
        """测试停止记录"""
        # 首先启动一个记录会话
        session_id = self.recorder.start_recording(
            robot_id="test_robot",
            record_types=[RecordType.ROBOT_STATE],
            duration=0  # 持续记录
        )
        
        # 停止记录
        success = self.recorder.stop_recording(session_id)
        
        # 验证停止成功
        self.assertTrue(success)
        
        # 验证会话不再在活跃列表中
        active_sessions = self.recorder.get_active_sessions()
        self.assertNotIn(session_id, active_sessions)
    
    def test_get_recorded_sessions(self):
        """测试获取已记录的会话列表"""
        # 记录当前已有的会话数量
        initial_count = len(self.recorder.get_recorded_sessions())
        
        # 启动并停止一个会话
        session_id = self.recorder.start_recording(
            robot_id="test_robot",
            record_types=[RecordType.ROBOT_STATE]
        )
        self.recorder.stop_recording(session_id)
        
        # 验证会话数量增加
        new_count = len(self.recorder.get_recorded_sessions())
        self.assertEqual(new_count, initial_count + 1)


class TestAdvancedDataAnalyzer(unittest.TestCase):
    """测试高级数据分析器"""
    
    def setUp(self):
        """设置测试环境"""
        self.analyzer = get_data_analyzer()
        
        # 创建模拟数据
        self._create_test_data()
    
    def _create_test_data(self):
        """创建测试数据"""
        # 为了测试，我们需要模拟一些数据
        # 注意：这只是一个示例，实际测试中可能需要更复杂的数据生成
        self.analyzer._test_data = {
            'test_robot': {
                'timestamp': [1000, 1001, 1002, 1003, 1004],
                'joint_position_0': [0.1, 0.2, 0.3, 0.4, 0.5],
                'joint_position_1': [0.5, 0.6, 0.7, 0.8, 0.9],
                'tcp_x': [0.1, 0.2, 0.3, 0.4, 0.5],
                'tcp_y': [0.2, 0.3, 0.4, 0.5, 0.6],
                'tcp_z': [0.5, 0.5, 0.5, 0.5, 0.5],
                'robot_mode': [4, 4, 4, 4, 4]
            }
        }
    
    def test_statistical_analysis(self):
        """测试统计分析"""
        # 模拟加载数据
        import pandas as pd
        df = pd.DataFrame(self.analyzer._test_data['test_robot'])
        
        # 执行统计分析
        result = self.analyzer.analyze(df, AnalysisType.STATISTICAL)
        
        # 验证结果包含必要的统计信息
        self.assertIn('mean', result)
        self.assertIn('std', result)
        self.assertIn('min', result)
        self.assertIn('max', result)
    
    def test_trend_analysis(self):
        """测试趋势分析"""
        # 模拟加载数据
        import pandas as pd
        df = pd.DataFrame(self.analyzer._test_data['test_robot'])
        
        # 执行趋势分析
        result = self.analyzer.analyze(
            df,
            AnalysisType.TREND,
            {'x_column': 'timestamp', 'y_column': 'tcp_x'}
        )
        
        # 验证结果包含趋势信息
        self.assertIn('slope', result)
        self.assertIn('intercept', result)
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        # 获取另一个实例
        another_analyzer = get_data_analyzer()
        
        # 验证是同一个实例
        self.assertIs(self.analyzer, another_analyzer)


if __name__ == '__main__':
    unittest.main()
