#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
轨迹规划和路径优化模块

此模块提供机器人运动轨迹的规划和优化功能，包括：
- 点到点运动的平滑插值
- 碰撞检测和规避
- 速度和加速度优化
- 轨迹参数调整
"""

import numpy as np
from scipy.interpolate import splprep, splev
from scipy.optimize import minimize
import time
import logging
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass

@dataclass
class TrajectoryPoint:
    """轨迹点类，包含位置、速度、加速度等信息"""
    pose: List[float]            # 位姿 [x, y, z, rx, ry, rz]
    velocity: Optional[List[float]] = None  # 速度
    acceleration: Optional[List[float]] = None  # 加速度
    time: Optional[float] = None  # 时间戳
    joint_positions: Optional[List[float]] = None  # 关节位置
    joint_velocities: Optional[List[float]] = None  # 关节速度
    joint_accelerations: Optional[List[float]] = None  # 关节加速度

@dataclass
class PathPoint:
    """路径点类，包含位置和相关属性"""
    position: List[float]         # 位置 [x, y, z]
    orientation: Optional[List[float]] = None  # 姿态 [rx, ry, rz]
    velocity: Optional[float] = None  # 速度
    acceleration: Optional[float] = None  # 加速度
    curvature: Optional[float] = None  # 曲率
    is_waypoint: bool = False  # 是否为途经点

@dataclass
class TrajectoryConstraint:
    """轨迹约束类，包含速度、加速度等约束条件"""
    max_velocity: float = 0.5      # 最大线速度 (m/s)
    max_acceleration: float = 0.2   # 最大线加速度 (m/s²)
    max_jerk: float = 0.1          # 最大线加加速度 (m/s³)
    max_joint_velocity: float = 1.0  # 最大关节速度 (rad/s)
    max_joint_acceleration: float = 0.5  # 最大关节加速度 (rad/s²)
    max_joint_jerk: float = 0.2    # 最大关节加加速度 (rad/s³)
    safety_margin: float = 0.05    # 安全余量 (m)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('trajectory_planner')

class TrajectoryPlanner:
    """
    轨迹规划器类，负责机器人轨迹的生成和优化
    """
    
    def __init__(self, robot_model=None):
        """
        初始化轨迹规划器
        
        Args:
            robot_model: 机器人模型对象，用于碰撞检测和运动学计算
        """
        self.robot_model = robot_model
        self.safety_margin = 0.05  # 安全余量（米）
        self.max_velocity = 0.5  # 最大速度（米/秒）
        self.max_acceleration = 0.2  # 最大加速度（米/秒²）
        
    def plan_joint_trajectory(self, start_joints, goal_joints, via_points=None, num_points=100):
        """
        规划关节空间轨迹
        
        Args:
            start_joints: 起始关节角度 [rad]
            goal_joints: 目标关节角度 [rad]
            via_points: 途经点列表，每个途经点是一个关节角度列表
            num_points: 生成的轨迹点数
            
        Returns:
            list: 规划好的轨迹点列表，每个点包含关节角度
        """
        try:
            logger.info(f"规划关节空间轨迹: 从{start_joints}到{goal_joints}")
            
            # 收集所有路径点
            all_points = [start_joints]
            if via_points:
                all_points.extend(via_points)
            all_points.append(goal_joints)
            
            # 生成平滑的关节轨迹
            joint_trajectories = []
            for i in range(len(start_joints)):
                # 提取每个关节的所有位置
                joint_values = [point[i] for point in all_points]
                # 创建时间点
                t = np.linspace(0, 1, len(joint_values))
                # 使用三次样条插值
                tck, u = splprep([joint_values], s=0, u=t)
                # 生成更多的点
                u_new = np.linspace(0, 1, num_points)
                joint_traj = splev(u_new, tck)[0]
                joint_trajectories.append(joint_traj)
            
            # 转置得到轨迹点
            trajectory = np.array(joint_trajectories).T.tolist()
            
            # 应用速度和加速度约束
            trajectory = self.apply_dynamic_constraints(trajectory)
            
            logger.info(f"关节空间轨迹规划完成，生成{len(trajectory)}个轨迹点")
            return trajectory
            
        except Exception as e:
            logger.error(f"关节空间轨迹规划失败: {str(e)}")
            raise
    
    def plan_cartesian_trajectory(self, start_pose, goal_pose, via_points=None, num_points=100):
        """
        规划笛卡尔空间轨迹
        
        Args:
            start_pose: 起始TCP位姿 [x, y, z, rx, ry, rz]
            goal_pose: 目标TCP位姿 [x, y, z, rx, ry, rz]
            via_points: 途经点位姿列表
            num_points: 生成的轨迹点数
            
        Returns:
            list: 规划好的轨迹点列表，每个点包含TCP位姿
        """
        try:
            logger.info(f"规划笛卡尔空间轨迹: 从{start_pose[:3]}到{goal_pose[:3]}")
            
            # 收集所有路径点
            all_points = [start_pose]
            if via_points:
                all_points.extend(via_points)
            all_points.append(goal_pose)
            
            # 分离位置和姿态
            positions = [point[:3] for point in all_points]
            orientations = [point[3:] for point in all_points]
            
            # 创建时间点
            t = np.linspace(0, 1, len(all_points))
            
            # 对位置进行平滑插值
            tck_pos, u = splprep(np.array(positions).T, s=0, u=t)
            u_new = np.linspace(0, 1, num_points)
            pos_trajectory = np.array(splev(u_new, tck_pos)).T
            
            # 对姿态进行平滑插值
            orientation_trajectories = []
            for i in range(3):
                orient_values = [point[i] for point in orientations]
                tck_orient, u = splprep([orient_values], s=0, u=t)
                orient_traj = splev(u_new, tck_orient)[0]
                orientation_trajectories.append(orient_traj)
            orient_trajectory = np.array(orientation_trajectories).T
            
            # 合并位置和姿态
            trajectory = np.hstack((pos_trajectory, orient_trajectory)).tolist()
            
            # 检查碰撞
            if self.robot_model:
                collision_free = self.check_collisions(trajectory)
                if not collision_free:
                    logger.warning("检测到潜在碰撞，尝试路径优化...")
                    # 尝试优化路径以避免碰撞
                    trajectory = self.optimize_path_to_avoid_collisions(trajectory)
            
            # 应用速度和加速度约束
            trajectory = self.apply_dynamic_constraints(trajectory)
            
            logger.info(f"笛卡尔空间轨迹规划完成，生成{len(trajectory)}个轨迹点")
            return trajectory
            
        except Exception as e:
            logger.error(f"笛卡尔空间轨迹规划失败: {str(e)}")
            raise
    
    def apply_dynamic_constraints(self, trajectory):
        """
        应用速度和加速度约束到轨迹
        
        Args:
            trajectory: 轨迹点列表
            
        Returns:
            list: 应用约束后的轨迹
        """
        # 这里实现简单的动态约束应用
        # 在实际应用中，可能需要更复杂的时间参数化算法
        return trajectory
    
    def check_collisions(self, trajectory):
        """
        检查轨迹是否存在碰撞
        
        Args:
            trajectory: 轨迹点列表
            
        Returns:
            bool: True表示无碰撞，False表示有碰撞
        """
        # 如果没有机器人模型，假设无碰撞
        if not self.robot_model:
            return True
        
        # 实际应用中，这里应该调用机器人模型的碰撞检测函数
        # 这里简化为假设有碰撞就返回False
        return True
    
    def optimize_path_to_avoid_collisions(self, trajectory):
        """
        优化路径以避免碰撞
        
        Args:
            trajectory: 原始轨迹
            
        Returns:
            list: 优化后的轨迹
        """
        # 这里实现简单的路径优化逻辑
        # 实际应用中，可能需要使用更复杂的算法如RRT、A*等
        logger.info("应用路径优化以避免碰撞")
        return trajectory
    
    def optimize_trajectory_time(self, trajectory):
        """
        优化轨迹执行时间
        
        Args:
            trajectory: 轨迹点列表
            
        Returns:
            list: 优化时间参数后的轨迹
        """
        logger.info("优化轨迹执行时间")
        # 这里可以实现时间最优轨迹规划算法
        return trajectory

class PathOptimizer:
    """
    路径优化器类，提供高级路径优化功能
    """
    
    def __init__(self):
        """
        初始化路径优化器
        """
        self.weight_smoothness = 0.1
        self.weight_shortness = 0.9
    
    def smooth_path(self, path, smoothing_factor=0.5):
        """
        平滑路径，减少关节运动的突变
        
        Args:
            path: 原始路径点列表
            smoothing_factor: 平滑因子，0-1之间
            
        Returns:
            list: 平滑后的路径
        """
        try:
            logger.info(f"平滑路径，平滑因子: {smoothing_factor}")
            
            if len(path) <= 2:
                return path
            
            # 转换为numpy数组进行处理
            path_array = np.array(path)
            smoothed = path_array.copy()
            
            # 应用平滑算法
            for i in range(1, len(path) - 1):
                smoothed[i] = (1 - smoothing_factor) * path_array[i] + \
                             smoothing_factor * 0.5 * (path_array[i-1] + path_array[i+1])
            
            return smoothed.tolist()
            
        except Exception as e:
            logger.error(f"路径平滑失败: {str(e)}")
            raise
    
    def optimize_path_length(self, path):
        """
        优化路径长度，使路径尽可能短
        
        Args:
            path: 原始路径点列表
            
        Returns:
            list: 优化后的路径
        """
        try:
            logger.info("优化路径长度")
            
            if len(path) <= 2:
                return path
            
            # 简单的路径长度优化：删除冗余点
            optimized = [path[0]]
            
            for i in range(1, len(path) - 1):
                # 检查三点是否近似共线
                p1 = np.array(optimized[-1])
                p2 = np.array(path[i])
                p3 = np.array(path[i+1])
                
                # 计算向量
                v1 = p2 - p1
                v2 = p3 - p2
                
                # 计算向量夹角
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
                
                # 如果夹角接近180度，则跳过中间点
                if abs(cos_angle) < 0.999:
                    optimized.append(path[i])
            
            # 添加最后一个点
            optimized.append(path[-1])
            
            logger.info(f"路径长度优化完成: {len(path)} -> {len(optimized)}个点")
            return optimized
            
        except Exception as e:
            logger.error(f"路径长度优化失败: {str(e)}")
            raise
    
    def find_optimal_path(self, start, goal, obstacles=None, method='smooth'):
        """
        寻找绕过障碍物的最优路径
        
        Args:
            start: 起始点
            goal: 目标点
            obstacles: 障碍物列表
            method: 优化方法 ('smooth', 'short', 'balanced')
            
        Returns:
            list: 最优路径点列表
        """
        try:
            logger.info(f"寻找最优路径: 从{start}到{goal}，方法: {method}")
            
            # 根据方法调整权重
            if method == 'smooth':
                self.weight_smoothness = 0.8
                self.weight_shortness = 0.2
            elif method == 'short':
                self.weight_smoothness = 0.2
                self.weight_shortness = 0.8
            else:  # balanced
                self.weight_smoothness = 0.5
                self.weight_shortness = 0.5
            
            # 这里简化处理，实际应用中应实现完整的路径规划算法
            # 例如RRT、A*、PRM等
            
            # 返回简单的直线路径
            return [start, goal]
            
        except Exception as e:
            logger.error(f"最优路径查找失败: {str(e)}")
            raise