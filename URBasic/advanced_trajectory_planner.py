#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级轨迹规划模块

此模块扩展了基础的轨迹规划功能，提供更复杂的路径生成、优化、
动态障碍物避让和能耗优化等高级功能。

作者: Nonead
日期: 2024
版本: 1.0
"""

import numpy as np
import logging
import math
from typing import Dict, List, Optional, Union, Tuple, Callable
from enum import Enum, auto
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 导入基础模块
from URBasic.trajectory_planner import (
    TrajectoryPlanner, PathOptimizer, 
    TrajectoryPoint, PathPoint, TrajectoryConstraint
)
from typing import Optional, Any
from URBasic.error_handling import RobotError, ErrorCategory

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PathType(Enum):
    """路径类型枚举"""
    LINEAR = "linear"                    # 直线
    CIRCULAR = "circular"                # 圆弧
    SPLINE = "spline"                    # 样条曲线
    BEZIER = "bezier"                    # 贝塞尔曲线
    SPIRAL = "spiral"                    # 螺旋线
    COMPOSITE = "composite"              # 组合路径
    PARAMETRIC = "parametric"            # 参数化路径
    FOLLOW_PATH = "follow_path"          # 跟随路径点


class OptimizationObjective(Enum):
    """优化目标枚举"""
    MINIMIZE_DISTANCE = "minimize_distance"        # 最小化距离
    MINIMIZE_TIME = "minimize_time"                # 最小化时间
    MINIMIZE_ENERGY = "minimize_energy"            # 最小化能耗
    MINIMIZE_JERK = "minimize_jerk"                # 最小化加加速度
    BALANCED = "balanced"                          # 平衡优化
    SMOOTHNESS = "smoothness"                      # 平滑度优化


class CollisionAvoidanceStrategy(Enum):
    """碰撞避免策略枚举"""
    AVOID_ALL = "avoid_all"                # 避免所有障碍物
    CONTOUR_FOLLOWING = "contour_following"  # 轮廓跟随
    DYNAMIC_REPLANNING = "dynamic_replanning"  # 动态重规划
    PRIORITY_BASED = "priority_based"        # 基于优先级
    REACTIVE = "reactive"                    # 反应式


class PathSmoothness(Enum):
    """路径平滑度枚举"""
    LOW = "low"        # 低平滑度
    MEDIUM = "medium"  # 中等平滑度
    HIGH = "high"      # 高平滑度
    VERY_HIGH = "very_high"  # 非常高的平滑度


@dataclass
class AdvancedTrajectoryConstraint(TrajectoryConstraint):
    """高级轨迹约束类"""
    # 能耗约束
    max_energy: Optional[float] = None  # 最大能耗 (J)
    energy_efficiency_factor: float = 1.0  # 能耗效率因子 (0.0-1.0)
    
    # 碰撞避免参数
    collision_avoidance_strategy: CollisionAvoidanceStrategy = \
        CollisionAvoidanceStrategy.AVOID_ALL
    safety_margin: float = 0.05  # 安全距离 (m)
    obstacle_weights: Dict[str, float] = field(default_factory=dict)  # 障碍物权重
    
    # 平滑度参数
    path_smoothness: PathSmoothness = PathSmoothness.MEDIUM
    corner_smoothing_radius: float = 0.01  # 转角平滑半径 (m)
    
    # 动态参数
    allow_dynamic_replanning: bool = True
    replanning_frequency: float = 5.0  # 重规划频率 (Hz)
    
    # 关节约束扩展
    joint_velocity_profile: Optional[List[float]] = None  # 关节速度配置文件
    joint_acceleration_profile: Optional[List[float]] = None  # 关节加速度配置文件


@dataclass
class Obstacle:
    """障碍物类"""
    obstacle_id: str  # 障碍物ID
    obstacle_type: str  # 障碍物类型
    position: List[float]  # 位置 [x, y, z]
    dimensions: List[float]  # 尺寸 [dx, dy, dz] 或半径
    is_dynamic: bool = False  # 是否动态
    velocity: Optional[List[float]] = None  # 速度 [vx, vy, vz]
    danger_level: float = 1.0  # 危险等级 (0.0-1.0)
    avoidance_priority: int = 50  # 避让优先级 (0-100)

    def get_bounding_box(self) -> Tuple[List[float], List[float]]:
        """
        获取障碍物的边界框
        
        Returns:
            Tuple[List[float], List[float]]: 最小点和最大点
        """
        if self.obstacle_type == "sphere":
            radius = self.dimensions[0]
            min_point = [self.position[0] - radius, 
                         self.position[1] - radius, 
                         self.position[2] - radius]
            max_point = [self.position[0] + radius, 
                         self.position[1] + radius, 
                         self.position[2] + radius]
        elif self.obstacle_type == "box":
            min_point = [self.position[0] - self.dimensions[0]/2, 
                         self.position[1] - self.dimensions[1]/2, 
                         self.position[2] - self.dimensions[2]/2]
            max_point = [self.position[0] + self.dimensions[0]/2, 
                         self.position[1] + self.dimensions[1]/2, 
                         self.position[2] + self.dimensions[2]/2]
        else:
            # 默认使用球体近似
            radius = max(self.dimensions)
            min_point = [self.position[0] - radius, 
                         self.position[1] - radius, 
                         self.position[2] - radius]
            max_point = [self.position[0] + radius, 
                         self.position[1] + radius, 
                         self.position[2] + radius]
        
        return min_point, max_point


@dataclass
class AdvancedPathPoint(PathPoint):
    """高级路径点类"""
    # 路径点类型
    path_type: PathType = PathType.LINEAR
    
    # 路径约束
    curvature_limit: Optional[float] = None  # 曲率限制
    approach_direction: Optional[List[float]] = None  # 接近方向
    departure_direction: Optional[List[float]] = None  # 离开方向
    
    # 路径参数
    bezier_control_points: Optional[List[List[float]]] = None  # 贝塞尔控制点
    parametric_function: Optional[Callable[[float], List[float]]] = None  # 参数化函数
    
    # 速度控制
    speed_factor: float = 1.0  # 速度因子 (0.0-1.0)
    acceleration_factor: float = 1.0  # 加速度因子 (0.0-1.0)
    
    # 辅助信息
    is_waypoint: bool = True  # 是否为途经点
    is_key_point: bool = False  # 是否为关键点
    metadata: Dict = field(default_factory=dict)  # 元数据


class BezierCurveGenerator:
    """贝塞尔曲线生成器"""
    
    @staticmethod
    def calculate_bezier_point(t: float, points: List[List[float]]) -> List[float]:
        """
        计算贝塞尔曲线上的点
        
        Args:
            t: 参数 (0-1)
            points: 控制点列表
            
        Returns:
            List[float]: 曲线上的点 [x, y, z]
        """
        n = len(points) - 1
        result = [0.0, 0.0, 0.0]
        
        for i in range(n + 1):
            binomial = math.comb(n, i)
            weight = binomial * (t ** i) * ((1 - t) ** (n - i))
            
            result[0] += weight * points[i][0]
            result[1] += weight * points[i][1]
            result[2] += weight * points[i][2]
        
        return result
    
    @staticmethod
    def generate_bezier_curve(control_points: List[List[float]], 
                             num_points: int = 100) -> List[List[float]]:
        """
        生成贝塞尔曲线
        
        Args:
            control_points: 控制点列表
            num_points: 生成的点数量
            
        Returns:
            List[List[float]]: 曲线上的点列表
        """
        curve_points = []
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0.0
            point = BezierCurveGenerator.calculate_bezier_point(t, control_points)
            curve_points.append(point)
        
        return curve_points
    
    @staticmethod
    def generate_cubic_bezier(p0: List[float], p1: List[float], 
                            p2: List[float], p3: List[float], 
                            num_points: int = 100) -> List[List[float]]:
        """
        生成三次贝塞尔曲线
        
        Args:
            p0: 起点
            p1: 控制点1
            p2: 控制点2
            p3: 终点
            num_points: 生成的点数量
            
        Returns:
            List[List[float]]: 曲线上的点列表
        """
        return BezierCurveGenerator.generate_bezier_curve([p0, p1, p2, p3], num_points)
    
    @staticmethod
    def generate_quadratic_bezier(p0: List[float], p1: List[float], 
                                p2: List[float], 
                                num_points: int = 100) -> List[List[float]]:
        """
        生成二次贝塞尔曲线
        
        Args:
            p0: 起点
            p1: 控制点
            p2: 终点
            num_points: 生成的点数量
            
        Returns:
            List[List[float]]: 曲线上的点列表
        """
        return BezierCurveGenerator.generate_bezier_curve([p0, p1, p2], num_points)


class SpiralGenerator:
    """螺旋线生成器"""
    
    @staticmethod
    def generate_circular_spiral(center: List[float], radius_start: float, 
                               radius_end: float, height_start: float,
                               height_end: float, num_points: int = 100,
                               clockwise: bool = True) -> List[List[float]]:
        """
        生成圆形螺旋线
        
        Args:
            center: 中心点 [x, y]
            radius_start: 起始半径
            radius_end: 结束半径
            height_start: 起始高度
            height_end: 结束高度
            num_points: 生成的点数量
            clockwise: 是否顺时针
            
        Returns:
            List[List[float]]: 螺旋线上的点列表
        """
        spiral_points = []
        angle_step = 2 * math.pi / (num_points - 1) * (2 if radius_start != radius_end else 1)
        radius_step = (radius_end - radius_start) / (num_points - 1)
        height_step = (height_end - height_start) / (num_points - 1)
        
        for i in range(num_points):
            angle = i * angle_step * (1 if clockwise else -1)
            radius = radius_start + i * radius_step
            height = height_start + i * height_step
            
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = height
            
            spiral_points.append([x, y, z])
        
        return spiral_points
    
    @staticmethod
    def generate_helical_spiral(center: List[float], radius: float, 
                              height_start: float, height_end: float,
                              turns: float = 1.0, num_points: int = 100,
                              clockwise: bool = True) -> List[List[float]]:
        """
        生成螺旋形螺旋线（等半径）
        
        Args:
            center: 中心点 [x, y]
            radius: 半径
            height_start: 起始高度
            height_end: 结束高度
            turns: 螺旋圈数
            num_points: 生成的点数量
            clockwise: 是否顺时针
            
        Returns:
            List[List[float]]: 螺旋线上的点列表
        """
        spiral_points = []
        total_angle = 2 * math.pi * turns
        angle_step = total_angle / (num_points - 1)
        height_step = (height_end - height_start) / (num_points - 1)
        
        for i in range(num_points):
            angle = i * angle_step * (1 if clockwise else -1)
            height = height_start + i * height_step
            
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = height
            
            spiral_points.append([x, y, z])
        
        return spiral_points


class EnergyOptimizer:
    """能耗优化器"""
    
    @staticmethod
    def calculate_trajectory_energy(joint_trajectory: List[List[float]],
                                   joint_masses: List[float],
                                   dt: float) -> float:
        """
        计算轨迹能耗
        
        Args:
            joint_trajectory: 关节轨迹 [关节角度列表]
            joint_masses: 关节质量列表
            dt: 时间步长
            
        Returns:
            float: 总能耗
        """
        total_energy = 0.0
        
        # 计算速度和加速度
        velocities = []
        accelerations = []
        
        # 计算速度
        for i in range(len(joint_trajectory) - 1):
            joint_velocities = []
            for j in range(len(joint_trajectory[i])):
                vel = (joint_trajectory[i+1][j] - joint_trajectory[i][j]) / dt
                joint_velocities.append(vel)
            velocities.append(joint_velocities)
        
        # 计算加速度
        for i in range(len(velocities) - 1):
            joint_accelerations = []
            for j in range(len(velocities[i])):
                acc = (velocities[i+1][j] - velocities[i][j]) / dt
                joint_accelerations.append(acc)
            accelerations.append(joint_accelerations)
        
        # 计算动能和势能（简化模型）
        for i in range(len(accelerations)):
            kinetic_energy = 0.0
            potential_energy = 0.0
            
            for j in range(len(accelerations[i])):
                # 简化的动能计算
                if i < len(velocities):
                    kinetic_energy += 0.5 * joint_masses[j] * (velocities[i][j] ** 2)
                
                # 简化的势能变化计算（基于关节角度）
                theta = joint_trajectory[i][j]
                potential_energy += joint_masses[j] * 9.81 * math.sin(theta)  # 简化模型
            
            # 能耗约等于能量变化率
            energy_change = (kinetic_energy + potential_energy) * dt
            total_energy += abs(energy_change)
        
        return total_energy
    
    @staticmethod
    def optimize_trajectory_energy(joint_trajectory: List[List[float]],
                                  joint_masses: List[float],
                                  dt: float,
                                  max_iterations: int = 100,
                                  tolerance: float = 0.01) -> List[List[float]]:
        """
        优化轨迹能耗
        
        Args:
            joint_trajectory: 原始关节轨迹
            joint_masses: 关节质量列表
            dt: 时间步长
            max_iterations: 最大迭代次数
            tolerance: 收敛容差
            
        Returns:
            List[List[float]]: 优化后的关节轨迹
        """
        # 简化的能耗优化：使用梯度下降法调整中间点
        optimized_trajectory = [list(point) for point in joint_trajectory]
        current_energy = EnergyOptimizer.calculate_trajectory_energy(
            optimized_trajectory, joint_masses, dt)
        
        learning_rate = 0.01
        
        for iteration in range(max_iterations):
            # 对中间点进行小幅调整
            new_trajectory = [list(point) for point in optimized_trajectory]
            
            # 只调整中间点，保持起点和终点不变
            for i in range(1, len(new_trajectory) - 1):
                for j in range(len(new_trajectory[i])):
                    # 随机小幅调整
                    adjustment = (np.random.random() - 0.5) * learning_rate
                    new_trajectory[i][j] += adjustment
                    
                    # 确保在关节范围内
                    new_trajectory[i][j] = max(-math.pi, min(math.pi, new_trajectory[i][j]))
            
            # 计算新轨迹的能耗
            new_energy = EnergyOptimizer.calculate_trajectory_energy(
                new_trajectory, joint_masses, dt)
            
            # 如果能耗降低，接受新轨迹
            if new_energy < current_energy:
                optimized_trajectory = new_trajectory
                current_energy = new_energy
            
            # 检查收敛
            if iteration > 0 and (current_energy < tolerance or 
                                 learning_rate < tolerance):
                break
            
            # 降低学习率
            learning_rate *= 0.99
        
        logger.info(f"能耗优化完成，迭代次数: {iteration + 1}, 能耗减少: {current_energy}")
        return optimized_trajectory


class CollisionAvoidance:
    """碰撞避免模块"""
    
    @staticmethod
    def calculate_distance_to_obstacle(point: List[float], 
                                      obstacle: Obstacle) -> float:
        """
        计算点到障碍物的距离
        
        Args:
            point: 点 [x, y, z]
            obstacle: 障碍物
            
        Returns:
            float: 距离
        """
        if obstacle.obstacle_type == "sphere":
            # 球体距离计算
            dx = point[0] - obstacle.position[0]
            dy = point[1] - obstacle.position[1]
            dz = point[2] - obstacle.position[2]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz) - obstacle.dimensions[0]
        elif obstacle.obstacle_type == "box":
            # 立方体距离计算
            min_point, max_point = obstacle.get_bounding_box()
            
            # 找到立方体上最近的点
            closest_x = max(min_point[0], min(point[0], max_point[0]))
            closest_y = max(min_point[1], min(point[1], max_point[1]))
            closest_z = max(min_point[2], min(point[2], max_point[2]))
            
            dx = point[0] - closest_x
            dy = point[1] - closest_y
            dz = point[2] - closest_z
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        else:
            # 默认使用球体近似
            dx = point[0] - obstacle.position[0]
            dy = point[1] - obstacle.position[1]
            dz = point[2] - obstacle.position[2]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz) - max(obstacle.dimensions)
        
        return distance
    
    @staticmethod
    def check_point_collision(point: List[float], obstacle: Obstacle, 
                            safety_margin: float = 0.0) -> bool:
        """
        检查点是否与障碍物碰撞
        
        Args:
            point: 点 [x, y, z]
            obstacle: 障碍物
            safety_margin: 安全距离
            
        Returns:
            bool: 是否碰撞
        """
        distance = CollisionAvoidance.calculate_distance_to_obstacle(point, obstacle)
        return distance < safety_margin
    
    @staticmethod
    def check_segment_collision(start: List[float], end: List[float], 
                              obstacle: Obstacle, 
                              safety_margin: float = 0.0) -> bool:
        """
        检查线段是否与障碍物碰撞
        
        Args:
            start: 线段起点
            end: 线段终点
            obstacle: 障碍物
            safety_margin: 安全距离
            
        Returns:
            bool: 是否碰撞
        """
        # 简化实现：采样检查多个点
        num_samples = 10
        for i in range(num_samples + 1):
            t = i / num_samples
            point = [
                start[0] + t * (end[0] - start[0]),
                start[1] + t * (end[1] - start[1]),
                start[2] + t * (end[2] - start[2])
            ]
            
            if CollisionAvoidance.check_point_collision(point, obstacle, safety_margin):
                return True
        
        return False
    
    @staticmethod
    def find_closest_obstacle(point: List[float], obstacles: List[Obstacle]) -> Tuple[Optional[Obstacle], float]:
        """
        找到最近的障碍物
        
        Args:
            point: 点 [x, y, z]
            obstacles: 障碍物列表
            
        Returns:
            Tuple[Optional[Obstacle], float]: 最近的障碍物和距离
        """
        if not obstacles:
            return None, float('inf')
        
        closest_obstacle = None
        min_distance = float('inf')
        
        for obstacle in obstacles:
            distance = CollisionAvoidance.calculate_distance_to_obstacle(point, obstacle)
            if distance < min_distance:
                min_distance = distance
                closest_obstacle = obstacle
        
        return closest_obstacle, min_distance
    
    @staticmethod
    def avoid_obstacles_simple(path: List[List[float]], obstacles: List[Obstacle],
                            safety_margin: float = 0.05) -> List[List[float]]:
        """
        简单的障碍物避让
        
        Args:
            path: 原始路径
            obstacles: 障碍物列表
            safety_margin: 安全距离
            
        Returns:
            List[List[float]]: 避让后的路径
        """
        if not obstacles:
            return path
        
        new_path = []
        
        for i in range(len(path)):
            current_point = path[i]
            
            # 检查当前点是否碰撞
            collision = False
            for obstacle in obstacles:
                if CollisionAvoidance.check_point_collision(
                    current_point, obstacle, safety_margin):
                    collision = True
                    closest_obstacle = obstacle
                    break
            
            if collision and i > 0 and i < len(path) - 1:
                # 发生碰撞，生成避让路径
                # 计算远离障碍物的方向
                direction = np.array(current_point) - np.array(closest_obstacle.position)
                if np.linalg.norm(direction) > 0:
                    direction = direction / np.linalg.norm(direction)
                
                # 计算避让点
                avoidance_distance = safety_margin + max(closest_obstacle.dimensions) * 0.5
                avoidance_point = np.array(current_point) + direction * avoidance_distance
                
                new_path.append(avoidance_point.tolist())
            else:
                new_path.append(current_point)
        
        return new_path


class AdvancedTrajectoryPlanner(TrajectoryPlanner):
    """高级轨迹规划器类"""
    
    def __init__(self, robot_kinematics: Optional[Any] = None):
        """
        初始化高级轨迹规划器
        
        Args:
            robot_kinematics: 机器人运动学对象
        """
        super().__init__(robot_kinematics)
        self.obstacles = []
        self.optimization_objective = OptimizationObjective.BALANCED
        self.collision_avoidance_strategy = CollisionAvoidanceStrategy.AVOID_ALL
        self.joint_masses = [5.0, 5.0, 3.0, 2.0, 2.0, 1.0]  # 默认关节质量
    
    def add_obstacle(self, obstacle: Obstacle) -> None:
        """
        添加障碍物
        
        Args:
            obstacle: 障碍物对象
        """
        self.obstacles.append(obstacle)
        logger.info(f"添加障碍物: {obstacle.obstacle_id}")
    
    def remove_obstacle(self, obstacle_id: str) -> bool:
        """
        移除障碍物
        
        Args:
            obstacle_id: 障碍物ID
            
        Returns:
            bool: 移除是否成功
        """
        for i, obstacle in enumerate(self.obstacles):
            if obstacle.obstacle_id == obstacle_id:
                del self.obstacles[i]
                logger.info(f"移除障碍物: {obstacle_id}")
                return True
        
        logger.warning(f"障碍物 {obstacle_id} 不存在")
        return False
    
    def clear_obstacles(self) -> None:
        """
        清除所有障碍物
        """
        self.obstacles.clear()
        logger.info("清除所有障碍物")
    
    def set_joint_masses(self, masses: List[float]) -> bool:
        """
        设置关节质量
        
        Args:
            masses: 关节质量列表
            
        Returns:
            bool: 设置是否成功
        """
        if len(masses) != 6:
            logger.error("关节质量列表必须包含6个元素")
            return False
        
        self.joint_masses = masses
        logger.info("设置关节质量成功")
        return True
    
    def plan_advanced_cartesian_trajectory(
            self, start_pose: List[float],
            path_points: List[AdvancedPathPoint],
            constraints: Optional[AdvancedTrajectoryConstraint] = None,
            optimize: bool = True) -> Tuple[bool, List[TrajectoryPoint], Dict]:
        """
        规划高级笛卡尔空间轨迹
        
        Args:
            start_pose: 起始位姿 [x, y, z, rx, ry, rz]
            path_points: 路径点列表
            constraints: 轨迹约束
            optimize: 是否优化
            
        Returns:
            Tuple[bool, List[TrajectoryPoint], Dict]: 是否成功、轨迹点列表、附加信息
        """
        if constraints is None:
            constraints = AdvancedTrajectoryConstraint()
        
        # 生成完整路径
        full_path = [start_pose[:3]]  # 只使用位置部分
        orientations = [start_pose[3:]]
        
        current_point = start_pose[:3]
        current_orientation = start_pose[3:]
        
        for i, path_point in enumerate(path_points):
            # 根据路径点类型生成路径
            if path_point.path_type == PathType.LINEAR:
                # 直线运动
                new_points = self._generate_linear_path(current_point, path_point.position, 
                                                      10)  # 10个中间点
                full_path.extend(new_points[1:])  # 避免重复添加起点
                
                # 计算方向插值
                new_orientations = self._interpolate_orientations(
                    current_orientation, path_point.orientation, len(new_points))
                orientations.extend(new_orientations[1:])
                
            elif path_point.path_type == PathType.CIRCULAR:
                # 圆弧运动（需要中间点）
                if i > 0 and hasattr(path_points[i-1], 'position'):
                    center_point = self._calculate_circle_center(
                        current_point, path_points[i-1].position, path_point.position)
                    new_points = self._generate_circular_path(
                        current_point, center_point, path_point.position, 20)
                    full_path.extend(new_points[1:])
                    
                    # 方向插值
                    new_orientations = self._interpolate_orientations(
                        current_orientation, path_point.orientation, len(new_points))
                    orientations.extend(new_orientations[1:])
            
            elif path_point.path_type == PathType.BEZIER and path_point.bezier_control_points:
                # 贝塞尔曲线
                control_points = [current_point] + path_point.bezier_control_points
                if len(control_points) >= 2:
                    new_points = BezierCurveGenerator.generate_bezier_curve(
                        control_points, 30)
                    full_path.extend(new_points[1:])
                    
                    # 方向插值
                    new_orientations = self._interpolate_orientations(
                        current_orientation, path_point.orientation, len(new_points))
                    orientations.extend(new_orientations[1:])
            
            elif path_point.path_type == PathType.SPIRAL:
                # 螺旋线（简化实现）
                if path_point.parametric_function:
                    # 使用参数化函数
                    new_points = []
                    for t in np.linspace(0, 1, 50):
                        point = path_point.parametric_function(t)
                        new_points.append(point)
                    full_path.extend(new_points)
                else:
                    # 默认螺旋线
                    center = [current_point[0], current_point[1]]
                    new_points = SpiralGenerator.generate_helical_spiral(
                        center, 0.1, current_point[2], path_point.position[2], 
                        turns=1.0, num_points=30)
                    full_path.extend(new_points[1:])
                
                # 方向插值
                new_orientations = self._interpolate_orientations(
                    current_orientation, path_point.orientation, len(full_path) - len(orientations) + 1)
                orientations.extend(new_orientations[1:])
            
            elif path_point.path_type == PathType.PARAMETRIC and path_point.parametric_function:
                # 参数化路径
                new_points = []
                for t in np.linspace(0, 1, 50):
                    point = path_point.parametric_function(t)
                    new_points.append(point)
                full_path.extend(new_points)
                
                # 方向插值
                new_orientations = self._interpolate_orientations(
                    current_orientation, path_point.orientation, len(full_path) - len(orientations) + 1)
                orientations.extend(new_orientations[1:])
            
            else:
                # 默认直线
                new_points = self._generate_linear_path(current_point, path_point.position, 10)
                full_path.extend(new_points[1:])
                
                # 方向插值
                new_orientations = self._interpolate_orientations(
                    current_orientation, path_point.orientation, len(new_points))
                orientations.extend(new_orientations[1:])
            
            # 更新当前位置和方向
            current_point = full_path[-1]
            current_orientation = orientations[-1]
        
        # 碰撞避免
        if self.obstacles:
            full_path = CollisionAvoidance.avoid_obstacles_simple(
                full_path, self.obstacles, constraints.safety_margin)
        
        # 轨迹优化
        if optimize:
            full_path = self._optimize_path(full_path, constraints)
        
        # 生成轨迹点
        trajectory_points = []
        for i in range(len(full_path)):
            pose = full_path[i] + orientations[i] if i < len(orientations) else full_path[i] + start_pose[3:]
            
            # 计算速度和加速度（简化）
            velocity = [0.0] * 6
            acceleration = [0.0] * 6
            
            if i > 0 and i < len(full_path) - 1:
                # 简单的速度估计
                prev_pose = full_path[i-1] + orientations[i-1] if i-1 < len(orientations) else full_path[i-1] + start_pose[3:]
                next_pose = full_path[i+1] + orientations[i+1] if i+1 < len(orientations) else full_path[i+1] + start_pose[3:]
                
                for j in range(3):  # 只计算位置速度
                    velocity[j] = (next_pose[j] - prev_pose[j]) / (2 * constraints.time_step)
            
            trajectory_point = TrajectoryPoint(
                time=i * constraints.time_step,
                pose=pose,
                velocity=velocity,
                acceleration=acceleration,
                is_waypoint=any(pp.is_waypoint and np.allclose(pp.position, full_path[i]) for pp in path_points)
            )
            
            trajectory_points.append(trajectory_point)
        
        # 附加信息
        info = {
            "path_length": self._calculate_path_length(full_path),
            "total_time": len(trajectory_points) * constraints.time_step,
            "collision_checked": len(self.obstacles) > 0,
            "optimized": optimize
        }
        
        return True, trajectory_points, info
    
    def plan_energy_optimized_trajectory(
            self, start_joints: List[float],
            target_joints: List[float],
            constraints: Optional[AdvancedTrajectoryConstraint] = None,
            num_waypoints: int = 10) -> Tuple[bool, List[TrajectoryPoint], Dict]:
        """
        规划能耗优化的关节空间轨迹
        
        Args:
            start_joints: 起始关节角度
            target_joints: 目标关节角度
            constraints: 轨迹约束
            num_waypoints: 路径点数量
            
        Returns:
            Tuple[bool, List[TrajectoryPoint], Dict]: 是否成功、轨迹点列表、附加信息
        """
        if constraints is None:
            constraints = AdvancedTrajectoryConstraint()
        
        # 先生成基础轨迹
        success, base_trajectory, _ = self.plan_joint_trajectory(
            start_joints, target_joints, constraints, False)
        
        if not success:
            return False, [], {"error": "基础轨迹生成失败"}
        
        # 提取关节轨迹
        joint_trajectory = []
        for point in base_trajectory:
            joint_trajectory.append(point.joint_positions)
        
        # 能耗优化
        optimized_joint_trajectory = EnergyOptimizer.optimize_trajectory_energy(
            joint_trajectory, self.joint_masses, constraints.time_step)
        
        # 重新生成轨迹点
        trajectory_points = []
        for i, joint_pos in enumerate(optimized_joint_trajectory):
            # 计算速度和加速度
            velocity = [0.0] * 6
            acceleration = [0.0] * 6
            
            if i > 0:
                for j in range(6):
                    velocity[j] = (joint_pos[j] - optimized_joint_trajectory[i-1][j]) / constraints.time_step
            
            if i > 1:
                for j in range(6):
                    prev_vel = (optimized_joint_trajectory[i-1][j] - optimized_joint_trajectory[i-2][j]) / constraints.time_step
                    acceleration[j] = (velocity[j] - prev_vel) / constraints.time_step
            
            trajectory_point = TrajectoryPoint(
                time=i * constraints.time_step,
                joint_positions=joint_pos,
                velocity=velocity,
                acceleration=acceleration,
                is_waypoint=i == 0 or i == len(optimized_joint_trajectory) - 1
            )
            
            trajectory_points.append(trajectory_point)
        
        # 计算能耗
        base_energy = EnergyOptimizer.calculate_trajectory_energy(
            joint_trajectory, self.joint_masses, constraints.time_step)
        optimized_energy = EnergyOptimizer.calculate_trajectory_energy(
            optimized_joint_trajectory, self.joint_masses, constraints.time_step)
        
        energy_saving = ((base_energy - optimized_energy) / base_energy * 100) if base_energy > 0 else 0
        
        info = {
            "base_energy": base_energy,
            "optimized_energy": optimized_energy,
            "energy_saving_percent": energy_saving,
            "total_time": len(trajectory_points) * constraints.time_step
        }
        
        logger.info(f"能耗优化完成，节省: {energy_saving:.2f}%")
        return True, trajectory_points, info
    
    def plan_smooth_transition_trajectory(
            self, current_trajectory: List[TrajectoryPoint],
            new_target_pose: List[float],
            constraints: Optional[AdvancedTrajectoryConstraint] = None,
            transition_time: float = 1.0) -> Tuple[bool, List[TrajectoryPoint], Dict]:
        """
        规划平滑过渡轨迹
        
        Args:
            current_trajectory: 当前轨迹
            new_target_pose: 新目标位姿
            constraints: 轨迹约束
            transition_time: 过渡时间
            
        Returns:
            Tuple[bool, List[TrajectoryPoint], Dict]: 是否成功、轨迹点列表、附加信息
        """
        if constraints is None:
            constraints = AdvancedTrajectoryConstraint()
        
        if not current_trajectory:
            return False, [], {"error": "当前轨迹为空"}
        
        # 获取当前轨迹的最后一个点
        last_point = current_trajectory[-1]
        
        # 生成平滑过渡轨迹
        num_transition_points = int(transition_time / constraints.time_step)
        
        # 使用三次样条生成平滑过渡
        transition_trajectory = []
        
        for i in range(num_transition_points + 1):
            t = i / num_transition_points
            
            # 三次样条插值
            position = []
            orientation = []
            velocity = []
            acceleration = []
            
            # 位置插值
            for j in range(3):
                # 三次多项式: s(t) = a0 + a1*t + a2*t^2 + a3*t^3
                a0 = last_point.pose[j]
                a1 = last_point.velocity[j]
                a2 = -1.5 * (new_target_pose[j] - last_point.pose[j]) + 0.5 * constraints.max_velocity[j] * transition_time
                a3 = 0.5 * (new_target_pose[j] - last_point.pose[j]) - 0.5 * constraints.max_velocity[j] * transition_time
                
                pos = a0 + a1*t + a2*t**2 + a3*t**3
                vel = a1 + 2*a2*t + 3*a3*t**2
                acc = 2*a2 + 6*a3*t
                
                position.append(pos)
                velocity.append(vel)
                acceleration.append(acc)
            
            # 方向插值（简化）
            for j in range(3):
                # 使用线性插值
                orient = last_point.pose[j+3] + t * (new_target_pose[j+3] - last_point.pose[j+3])
                orientation.append(orient)
                velocity.append(0.0)  # 简化角速度计算
                acceleration.append(0.0)  # 简化角加速度计算
            
            pose = position + orientation
            
            trajectory_point = TrajectoryPoint(
                time=last_point.time + i * constraints.time_step,
                pose=pose,
                velocity=velocity,
                acceleration=acceleration,
                is_waypoint=i == num_transition_points
            )
            
            transition_trajectory.append(trajectory_point)
        
        info = {
            "transition_time": transition_time,
            "transition_points": num_transition_points,
            "smoothness_level": constraints.path_smoothness.value
        }
        
        return True, transition_trajectory, info
    
    def detect_trajectory_collisions(
            self, trajectory: List[TrajectoryPoint],
            safety_margin: float = 0.05) -> List[Dict]:
        """
        检测轨迹碰撞
        
        Args:
            trajectory: 轨迹点列表
            safety_margin: 安全距离
            
        Returns:
            List[Dict]: 碰撞信息列表
        """
        collisions = []
        
        if not self.obstacles:
            return collisions
        
        # 检查每个轨迹段
        for i in range(len(trajectory) - 1):
            start_point = trajectory[i].pose[:3]
            end_point = trajectory[i+1].pose[:3]
            
            for obstacle in self.obstacles:
                if CollisionAvoidance.check_segment_collision(
                    start_point, end_point, obstacle, safety_margin):
                    collision_info = {
                        "time": trajectory[i].time,
                        "segment_index": i,
                        "obstacle_id": obstacle.obstacle_id,
                        "obstacle_position": obstacle.position,
                        "collision_point": start_point  # 近似
                    }
                    collisions.append(collision_info)
        
        return collisions
    
    def visualize_trajectory_3d(
            self, trajectory: List[TrajectoryPoint],
            obstacles: Optional[List[Obstacle]] = None,
            title: str = "3D Trajectory Visualization") -> None:
        """
        可视化3D轨迹
        
        Args:
            trajectory: 轨迹点列表
            obstacles: 障碍物列表（如果为None则使用当前障碍物）
            title: 图表标题
        """
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            logger.error("matplotlib 未安装，无法可视化轨迹")
            return
        
        # 提取轨迹点位置
        positions = [point.pose[:3] for point in trajectory]
        positions = np.array(positions)
        
        # 创建3D图表
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 绘制轨迹
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], 'b-', linewidth=2, label='Trajectory')
        
        # 标记起点和终点
        ax.scatter(positions[0, 0], positions[0, 1], positions[0, 2], 'go', s=100, label='Start')
        ax.scatter(positions[-1, 0], positions[-1, 1], positions[-1, 2], 'ro', s=100, label='End')
        
        # 绘制途经点
        waypoints = np.array([point.pose[:3] for point in trajectory if point.is_waypoint])
        if len(waypoints) > 2:
            ax.scatter(waypoints[1:-1, 0], waypoints[1:-1, 1], waypoints[1:-1, 2], 'mo', s=50, label='Waypoints')
        
        # 绘制障碍物
        if obstacles is None:
            obstacles = self.obstacles
        
        for obstacle in obstacles:
            if obstacle.obstacle_type == "sphere":
                # 绘制球体
                u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
                x = obstacle.position[0] + obstacle.dimensions[0] * np.cos(u) * np.sin(v)
                y = obstacle.position[1] + obstacle.dimensions[0] * np.sin(u) * np.sin(v)
                z = obstacle.position[2] + obstacle.dimensions[0] * np.cos(v)
                ax.plot_wireframe(x, y, z, color='r', alpha=0.3)
            elif obstacle.obstacle_type == "box":
                # 绘制立方体
                min_point, max_point = obstacle.get_bounding_box()
                
                # 立方体顶点
                vertices = [
                    [min_point[0], min_point[1], min_point[2]],
                    [max_point[0], min_point[1], min_point[2]],
                    [max_point[0], max_point[1], min_point[2]],
                    [min_point[0], max_point[1], min_point[2]],
                    [min_point[0], min_point[1], max_point[2]],
                    [max_point[0], min_point[1], max_point[2]],
                    [max_point[0], max_point[1], max_point[2]],
                    [min_point[0], max_point[1], max_point[2]]
                ]
                
                # 立方体边
                edges = [
                    [0, 1], [1, 2], [2, 3], [3, 0],  # 底部
                    [4, 5], [5, 6], [6, 7], [7, 4],  # 顶部
                    [0, 4], [1, 5], [2, 6], [3, 7]   # 侧边
                ]
                
                for edge in edges:
                    x = [vertices[edge[0]][0], vertices[edge[1]][0]]
                    y = [vertices[edge[0]][1], vertices[edge[1]][1]]
                    z = [vertices[edge[0]][2], vertices[edge[1]][2]]
                    ax.plot(x, y, z, 'r-', alpha=0.5)
        
        # 设置坐标轴标签
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        
        # 设置标题和图例
        ax.set_title(title)
        ax.legend()
        
        # 设置等比例
        max_range = np.array([positions[:, 0].max() - positions[:, 0].min(),
                             positions[:, 1].max() - positions[:, 1].min(),
                             positions[:, 2].max() - positions[:, 2].min()]).max()
        
        mid_x = (positions[:, 0].max() + positions[:, 0].min()) * 0.5
        mid_y = (positions[:, 1].max() + positions[:, 1].min()) * 0.5
        mid_z = (positions[:, 2].max() + positions[:, 2].min()) * 0.5
        
        ax.set_xlim(mid_x - max_range*0.5, mid_x + max_range*0.5)
        ax.set_ylim(mid_y - max_range*0.5, mid_y + max_range*0.5)
        ax.set_zlim(mid_z - max_range*0.5, mid_z + max_range*0.5)
        
        plt.tight_layout()
        plt.show()
    
    def _optimize_path(self, path: List[List[float]], 
                      constraints: AdvancedTrajectoryConstraint) -> List[List[float]]:
        """
        优化路径
        
        Args:
            path: 原始路径
            constraints: 轨迹约束
            
        Returns:
            List[List[float]]: 优化后的路径
        """
        # 根据平滑度参数调整路径
        if constraints.path_smoothness == PathSmoothness.HIGH or \
           constraints.path_smoothness == PathSmoothness.VERY_HIGH:
            # 使用高斯平滑
            sigma = 2.0 if constraints.path_smoothness == PathSmoothness.HIGH else 3.0
            optimized_path = self._gaussian_smooth(path, sigma)
        else:
            # 使用简单的移动平均平滑
            window_size = 3
            optimized_path = self._moving_average_smooth(path, window_size)
        
        # 保持起点和终点不变
        if optimized_path:
            optimized_path[0] = path[0]
            optimized_path[-1] = path[-1]
        
        return optimized_path
    
    def _gaussian_smooth(self, path: List[List[float]], sigma: float) -> List[List[float]]:
        """
        使用高斯平滑路径
        
        Args:
            path: 原始路径
            sigma: 高斯核标准差
            
        Returns:
            List[List[float]]: 平滑后的路径
        """
        if len(path) < 3:
            return path
        
        # 计算高斯核
        kernel_size = int(2 * sigma + 1)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        kernel = []
        for i in range(kernel_size):
            x = i - kernel_size // 2
            kernel.append(math.exp(-0.5 * (x / sigma) ** 2))
        
        # 归一化核
        kernel_sum = sum(kernel)
        kernel = [k / kernel_sum for k in kernel]
        
        # 应用高斯滤波
        smoothed_path = []
        path_np = np.array(path)
        
        for i in range(len(path)):
            start = max(0, i - kernel_size // 2)
            end = min(len(path), i + kernel_size // 2 + 1)
            
            # 调整核大小
            adjusted_kernel = kernel[kernel_size // 2 - i + start : kernel_size // 2 + (end - i)]
            adjusted_kernel = [k / sum(adjusted_kernel) for k in adjusted_kernel]
            
            # 应用滤波
            smoothed_point = np.sum(path_np[start:end] * np.array(adjusted_kernel)[:, np.newaxis], axis=0)
            smoothed_path.append(smoothed_point.tolist())
        
        return smoothed_path
    
    def _moving_average_smooth(self, path: List[List[float]], 
                             window_size: int) -> List[List[float]]:
        """
        使用移动平均平滑路径
        
        Args:
            path: 原始路径
            window_size: 窗口大小
            
        Returns:
            List[List[float]]: 平滑后的路径
        """
        if len(path) < 3 or window_size <= 1:
            return path
        
        smoothed_path = []
        path_np = np.array(path)
        
        for i in range(len(path)):
            start = max(0, i - window_size // 2)
            end = min(len(path), i + window_size // 2 + 1)
            
            # 计算平均值
            smoothed_point = np.mean(path_np[start:end], axis=0)
            smoothed_path.append(smoothed_point.tolist())
        
        return smoothed_path
    
    def _interpolate_orientations(self, start_orient: List[float],
                                end_orient: List[float],
                                num_points: int) -> List[List[float]]:
        """
        插值方向
        
        Args:
            start_orient: 起始方向 [rx, ry, rz]
            end_orient: 结束方向 [rx, ry, rz]
            num_points: 插值点数量
            
        Returns:
            List[List[float]]: 插值后的方向列表
        """
        orientations = []
        
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0.0
            
            # 线性插值
            orientation = [
                start_orient[0] + t * (end_orient[0] - start_orient[0]),
                start_orient[1] + t * (end_orient[1] - start_orient[1]),
                start_orient[2] + t * (end_orient[2] - start_orient[2])
            ]
            orientations.append(orientation)
        
        return orientations
    
    def _calculate_path_length(self, path: List[List[float]]) -> float:
        """
        计算路径长度
        
        Args:
            path: 路径点列表
            
        Returns:
            float: 路径长度
        """
        if len(path) < 2:
            return 0.0
        
        length = 0.0
        
        for i in range(1, len(path)):
            dx = path[i][0] - path[i-1][0]
            dy = path[i][1] - path[i-1][1]
            dz = path[i][2] - path[i-1][2]
            
            length += math.sqrt(dx*dx + dy*dy + dz*dz)
        
        return length
    
    def _generate_linear_path(self, start: List[float], end: List[float], 
                            num_points: int) -> List[List[float]]:
        """
        生成直线路径
        
        Args:
            start: 起点
            end: 终点
            num_points: 点数量
            
        Returns:
            List[List[float]]: 路径点列表
        """
        path = []
        
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0.0
            point = [
                start[0] + t * (end[0] - start[0]),
                start[1] + t * (end[1] - start[1]),
                start[2] + t * (end[2] - start[2])
            ]
            path.append(point)
        
        return path
    
    def _generate_circular_path(self, start: List[float], center: List[float],
                              end: List[float], num_points: int) -> List[List[float]]:
        """
        生成圆弧路径
        
        Args:
            start: 起点
            center: 中心点
            end: 终点
            num_points: 点数量
            
        Returns:
            List[List[float]]: 路径点列表
        """
        # 简化实现：假设在同一平面
        path = []
        
        # 计算向量
        start_vec = np.array(start) - np.array(center)
        end_vec = np.array(end) - np.array(center)
        
        # 计算角度
        start_angle = math.atan2(start_vec[1], start_vec[0])
        end_angle = math.atan2(end_vec[1], end_vec[0])
        
        # 确保角度差在合适范围内
        if end_angle - start_angle > math.pi:
            end_angle -= 2 * math.pi
        elif start_angle - end_angle > math.pi:
            end_angle += 2 * math.pi
        
        # 计算半径
        radius = np.linalg.norm(start_vec)
        
        # 生成圆弧点
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0.0
            angle = start_angle + t * (end_angle - start_angle)
            
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            # Z坐标线性插值
            z = start[2] + t * (end[2] - start[2])
            
            path.append([x, y, z])
        
        return path
    
    def _calculate_circle_center(self, p1: List[float], p2: List[float], 
                               p3: List[float]) -> List[float]:
        """
        计算三点确定的圆的圆心
        
        Args:
            p1: 点1
            p2: 点2
            p3: 点3
            
        Returns:
            List[float]: 圆心坐标
        """
        # 简化实现：假设在XY平面
        x1, y1, _ = p1
        x2, y2, _ = p2
        x3, y3, _ = p3
        
        # 计算垂直平分线
        A = x2 - x1
        B = y2 - y1
        C = x3 - x1
        D = y3 - y1
        
        E = A * (x1 + x2) + B * (y1 + y2)
        F = C * (x1 + x3) + D * (y1 + y3)
        
        G = 2 * (A * (y3 - y2) - B * (x3 - x2))
        
        if G == 0:
            # 三点共线，返回中点
            return [(x1 + x2 + x3) / 3, (y1 + y2 + y3) / 3, 0]
        
        # 计算圆心
        center_x = (D * E - B * F) / G
        center_y = (A * F - C * E) / G
        center_z = 0  # 简化为XY平面
        
        return [center_x, center_y, center_z]


# 全局高级轨迹规划器实例
_global_advanced_planner = None


def get_advanced_planner() -> AdvancedTrajectoryPlanner:
    """
    获取全局高级轨迹规划器实例
    
    Returns:
        AdvancedTrajectoryPlanner: 高级轨迹规划器实例
    """
    global _global_advanced_planner
    
    if _global_advanced_planner is None:
        _global_advanced_planner = AdvancedTrajectoryPlanner()
    
    return _global_advanced_planner


def reset_advanced_planner() -> None:
    """
    重置全局高级轨迹规划器实例
    """
    global _global_advanced_planner
    _global_advanced_planner = None


if __name__ == '__main__':
    # 示例使用
    planner = AdvancedTrajectoryPlanner()
    
    # 添加障碍物
    obstacle1 = Obstacle(
        obstacle_id="obstacle1",
        obstacle_type="sphere",
        position=[0.3, 0.2, 0.4],
        dimensions=[0.1],  # 半径
        danger_level=0.8
    )
    
    obstacle2 = Obstacle(
        obstacle_id="obstacle2",
        obstacle_type="box",
        position=[0.5, 0.5, 0.3],
        dimensions=[0.2, 0.2, 0.2],  # 长宽高
        danger_level=1.0
    )
    
    planner.add_obstacle(obstacle1)
    planner.add_obstacle(obstacle2)
    
    # 设置约束
    constraints = AdvancedTrajectoryConstraint(
        max_velocity=[0.5, 0.5, 0.5, 1.0, 1.0, 1.0],
        max_acceleration=[0.3, 0.3, 0.3, 0.5, 0.5, 0.5],
        path_smoothness=PathSmoothness.HIGH,
        safety_margin=0.05
    )
    
    # 创建高级路径点
    start_pose = [0.0, 0.2, 0.5, 0.0, 1.57, 0.0]
    
    # 贝塞尔曲线路径点
    bezier_point = AdvancedPathPoint(
        position=[0.6, 0.3, 0.6],
        orientation=[0.0, 1.57, 0.0],
        path_type=PathType.BEZIER,
        bezier_control_points=[[0.2, 0.1, 0.7], [0.4, 0.4, 0.8]]
    )
    
    # 终点
    end_point = AdvancedPathPoint(
        position=[0.7, 0.5, 0.4],
        orientation=[0.0, 1.57, 0.0],
        path_type=PathType.LINEAR
    )
    
    # 规划高级轨迹
    success, trajectory, info = planner.plan_advanced_cartesian_trajectory(
        start_pose, [bezier_point, end_point], constraints, optimize=True
    )
    
    if success:
        print(f"轨迹规划成功！")
        print(f"路径长度: {info['path_length']:.3f} m")
        print(f"总时间: {info['total_time']:.3f} s")
        print(f"检查碰撞: {info['collision_checked']}")
        print(f"优化路径: {info['optimized']}")
        
        # 可视化轨迹
        try:
            planner.visualize_trajectory_3d(trajectory, title="高级轨迹规划示例")
        except Exception as e:
            print(f"可视化失败: {str(e)}")
    else:
        print("轨迹规划失败")
    
    # 测试能耗优化
    print("\n测试能耗优化...")
    start_joints = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]
    target_joints = [1.0, -1.0, 1.0, -1.0, -1.0, 0.5]
    
    success, energy_trajectory, energy_info = planner.plan_energy_optimized_trajectory(
        start_joints, target_joints, constraints
    )
    
    if success:
        print(f"能耗优化轨迹规划成功！")
        print(f"基础能耗: {energy_info['base_energy']:.3f} J")
        print(f"优化能耗: {energy_info['optimized_energy']:.3f} J")
        print(f"节能百分比: {energy_info['energy_saving_percent']:.2f}%")
    else:
        print("能耗优化轨迹规划失败")
