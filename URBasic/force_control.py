#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
力控制功能模块

此模块提供机器人的力控制功能，包括：
- 阻抗控制
- 力/力矩监控
- 接触检测
- 恒力控制
- 力引导运动
"""

import numpy as np
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('force_control')

class ForceController:
    """
    力控制器类，负责机器人的力控制功能
    """
    
    def __init__(self, robot_model=None):
        """
        初始化力控制器
        
        Args:
            robot_model: 机器人模型对象
        """
        self.robot_model = robot_model
        self.force_threshold = 5.0  # 默认力阈值（牛顿）
        self.torque_threshold = 2.0  # 默认力矩阈值（牛顿·米）
        self.kp = np.diag([100.0, 100.0, 100.0, 10.0, 10.0, 10.0])  # 比例增益
        self.kd = np.diag([10.0, 10.0, 10.0, 1.0, 1.0, 1.0])  # 微分增益
        self.current_force = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 当前力/力矩值
        self.target_force = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 目标力/力矩值
        self.active_axes = [True, True, True, False, False, False]  # 激活的控制轴
    
    def set_force_threshold(self, threshold):
        """
        设置力阈值
        
        Args:
            threshold: 力阈值（牛顿）
        """
        self.force_threshold = threshold
        logger.info(f"力阈值已设置为: {threshold} N")
    
    def set_torque_threshold(self, threshold):
        """
        设置力矩阈值
        
        Args:
            threshold: 力矩阈值（牛顿·米）
        """
        self.torque_threshold = threshold
        logger.info(f"力矩阈值已设置为: {threshold} Nm")
    
    def set_impedance_params(self, kp, kd):
        """
        设置阻抗控制参数
        
        Args:
            kp: 比例增益，可以是标量或6维数组
            kd: 微分增益，可以是标量或6维数组
        """
        # 如果是标量，转换为对角矩阵
        if np.isscalar(kp):
            self.kp = np.diag([kp] * 6)
        else:
            self.kp = np.diag(kp)
        
        if np.isscalar(kd):
            self.kd = np.diag([kd] * 6)
        else:
            self.kd = np.diag(kd)
        
        logger.info("阻抗控制参数已更新")
    
    def set_active_axes(self, axes):
        """
        设置激活的控制轴
        
        Args:
            axes: 6元素布尔数组，指示哪些轴处于活动状态
        """
        self.active_axes = axes
        logger.info(f"激活的控制轴已设置为: {axes}")
    
    def get_force_torque(self, robot_client):
        """
        获取当前力/力矩值
        
        Args:
            robot_client: 机器人客户端对象
            
        Returns:
            list: 当前力/力矩值 [fx, fy, fz, tx, ty, tz]
        """
        try:
            # 这里应该调用机器人客户端的方法获取实际的力/力矩值
            # 暂时返回模拟值
            # 实际实现时需要替换为真实的传感器读数
            self.current_force = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 模拟值
            return self.current_force
            
        except Exception as e:
            logger.error(f"获取力/力矩值失败: {str(e)}")
            raise
    
    def detect_contact(self, force_values=None, robot_client=None):
        """
        检测是否发生接触
        
        Args:
            force_values: 可选，力/力矩值
            robot_client: 可选，机器人客户端对象
            
        Returns:
            bool: True表示检测到接触
        """
        try:
            # 获取力/力矩值
            if force_values is None:
                if robot_client is None:
                    raise ValueError("必须提供force_values或robot_client")
                force_values = self.get_force_torque(robot_client)
            
            # 检查力阈值
            forces = np.abs(force_values[:3])
            if np.any(forces > self.force_threshold):
                logger.info(f"检测到力接触: {forces}")
                return True
            
            # 检查力矩阈值
            torques = np.abs(force_values[3:])
            if np.any(torques > self.torque_threshold):
                logger.info(f"检测到力矩接触: {torques}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"接触检测失败: {str(e)}")
            raise
    
    def impedance_control(self, target_pose, current_pose, current_velocity, 
                         current_force=None, robot_client=None):
        """
        执行阻抗控制
        
        Args:
            target_pose: 目标位姿 [x, y, z, rx, ry, rz]
            current_pose: 当前位姿 [x, y, z, rx, ry, rz]
            current_velocity: 当前速度 [vx, vy, vz, wx, wy, wz]
            current_force: 可选，当前力/力矩值
            robot_client: 可选，机器人客户端对象
            
        Returns:
            list: 计算得到的控制力
        """
        try:
            # 获取力/力矩值
            if current_force is None:
                if robot_client is None:
                    raise ValueError("必须提供current_force或robot_client")
                current_force = self.get_force_torque(robot_client)
            
            # 计算位置误差
            pose_error = np.array(target_pose) - np.array(current_pose)
            
            # 计算控制力
            control_force = np.dot(self.kp, pose_error) - np.dot(self.kd, current_velocity)
            
            # 根据激活的轴过滤控制力
            for i in range(6):
                if not self.active_axes[i]:
                    control_force[i] = 0.0
            
            logger.debug(f"阻抗控制计算完成: 控制力 = {control_force}")
            return control_force.tolist()
            
        except Exception as e:
            logger.error(f"阻抗控制计算失败: {str(e)}")
            raise
    
    def constant_force_control(self, target_force, current_force=None, robot_client=None, 
                              control_gain=0.1):
        """
        执行恒力控制
        
        Args:
            target_force: 目标力/力矩值 [fx, fy, fz, tx, ty, tz]
            current_force: 可选，当前力/力矩值
            robot_client: 可选，机器人客户端对象
            control_gain: 控制增益
            
        Returns:
            list: 计算得到的位置调整量
        """
        try:
            # 保存目标力
            self.target_force = target_force
            
            # 获取当前力/力矩值
            if current_force is None:
                if robot_client is None:
                    raise ValueError("必须提供current_force或robot_client")
                current_force = self.get_force_torque(robot_client)
            
            # 计算力误差
            force_error = np.array(target_force) - np.array(current_force)
            
            # 计算位置调整量
            position_adjustment = control_gain * force_error
            
            # 根据激活的轴过滤调整量
            for i in range(6):
                if not self.active_axes[i]:
                    position_adjustment[i] = 0.0
            
            logger.debug(f"恒力控制计算完成: 位置调整量 = {position_adjustment}")
            return position_adjustment.tolist()
            
        except Exception as e:
            logger.error(f"恒力控制计算失败: {str(e)}")
            raise
    
    def force_guided_motion(self, direction, speed, max_force, robot_client=None):
        """
        执行力引导运动
        
        Args:
            direction: 运动方向向量 [dx, dy, dz]
            speed: 运动速度
            max_force: 最大允许力
            robot_client: 机器人客户端对象
            
        Returns:
            dict: 运动结果信息
        """
        try:
            logger.info(f"开始力引导运动: 方向={direction}, 速度={speed}, 最大力={max_force}")
            
            # 归一化方向向量
            direction_norm = np.linalg.norm(direction)
            if direction_norm == 0:
                raise ValueError("方向向量不能为零")
            normalized_direction = np.array(direction) / direction_norm
            
            # 设置临时力阈值
            original_threshold = self.force_threshold
            self.force_threshold = max_force
            
            # 这里应该实现力引导运动的逻辑
            # 实际应用中，需要循环读取力传感器并调整运动
            
            # 模拟力引导运动
            success = True
            contact_detected = False
            
            # 恢复原始阈值
            self.force_threshold = original_threshold
            
            result = {
                'success': success,
                'contact_detected': contact_detected,
                'message': '力引导运动完成'
            }
            
            logger.info(f"力引导运动结束: {result}")
            return result
            
        except Exception as e:
            logger.error(f"力引导运动失败: {str(e)}")
            # 恢复原始阈值
            self.force_threshold = original_threshold
            raise
    
    def teach_by_demonstration(self, robot_client=None, record_duration=10.0):
        """
        示教学习功能
        
        Args:
            robot_client: 机器人客户端对象
            record_duration: 记录时长（秒）
            
        Returns:
            list: 记录的轨迹点列表
        """
        try:
            logger.info(f"开始示教学习，记录时长: {record_duration}秒")
            
            recorded_path = []
            start_time = time.time()
            
            # 这里应该实现示教学习的逻辑
            # 实际应用中，需要循环读取机器人位置并记录
            
            # 模拟示教学习
            # 实际实现时需要替换为真实的记录逻辑
            
            logger.info(f"示教学习结束，记录了{len(recorded_path)}个轨迹点")
            return recorded_path
            
        except Exception as e:
            logger.error(f"示教学习失败: {str(e)}")
            raise

class ForceMonitoring:
    """
    力监控类，用于监控和分析力传感器数据
    """
    
    def __init__(self):
        """
        初始化力监控器
        """
        self.history_size = 1000  # 历史数据大小
        self.force_history = []  # 力历史数据
        self.torque_history = []  # 力矩历史数据
        self.timestamps = []  # 时间戳
    
    def record_data(self, force_values, timestamp=None):
        """
        记录力/力矩数据
        
        Args:
            force_values: 力/力矩值 [fx, fy, fz, tx, ty, tz]
            timestamp: 可选，时间戳
        """
        if timestamp is None:
            timestamp = time.time()
        
        # 分离力和力矩
        forces = force_values[:3]
        torques = force_values[3:]
        
        # 添加到历史记录
        self.force_history.append(forces)
        self.torque_history.append(torques)
        self.timestamps.append(timestamp)
        
        # 保持历史记录大小
        if len(self.force_history) > self.history_size:
            self.force_history.pop(0)
            self.torque_history.pop(0)
            self.timestamps.pop(0)
    
    def get_statistics(self):
        """
        获取力/力矩统计信息
        
        Returns:
            dict: 统计信息
        """
        if not self.force_history:
            return {
                'force_mean': [0.0, 0.0, 0.0],
                'force_std': [0.0, 0.0, 0.0],
                'force_max': [0.0, 0.0, 0.0],
                'torque_mean': [0.0, 0.0, 0.0],
                'torque_std': [0.0, 0.0, 0.0],
                'torque_max': [0.0, 0.0, 0.0]
            }
        
        force_array = np.array(self.force_history)
        torque_array = np.array(self.torque_history)
        
        return {
            'force_mean': np.mean(force_array, axis=0).tolist(),
            'force_std': np.std(force_array, axis=0).tolist(),
            'force_max': np.max(np.abs(force_array), axis=0).tolist(),
            'torque_mean': np.mean(torque_array, axis=0).tolist(),
            'torque_std': np.std(torque_array, axis=0).tolist(),
            'torque_max': np.max(np.abs(torque_array), axis=0).tolist()
        }
    
    def detect_anomalies(self, threshold=3.0):
        """
        检测异常力/力矩值
        
        Args:
            threshold: 标准差阈值
            
        Returns:
            list: 异常数据索引列表
        """
        anomalies = []
        
        if len(self.force_history) < 10:  # 需要足够的数据进行统计
            return anomalies
        
        stats = self.get_statistics()
        
        # 检查每个数据点
        for i, (forces, torques) in enumerate(zip(self.force_history, self.torque_history)):
            # 检查力异常
            for j in range(3):
                if abs(forces[j] - stats['force_mean'][j]) > threshold * stats['force_std'][j]:
                    anomalies.append(i)
                    break
            
            # 检查力矩异常
            if i not in anomalies:
                for j in range(3):
                    if abs(torques[j] - stats['torque_mean'][j]) > threshold * stats['torque_std'][j]:
                        anomalies.append(i)
                        break
        
        return anomalies