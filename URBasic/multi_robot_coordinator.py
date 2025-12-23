#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多机器人协同控制模块

此模块提供了多台UR机器人协同工作的功能，支持任务分配、动作同步、
冲突避免和协作任务执行。

作者: Nonead
日期: 2024
版本: 1.0
"""

import threading
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Union, Callable, Tuple

import numpy as np

# 导入必要的URBasic模块
from URBasic.robotConnector import RobotConnector
from URBasic.error_handling import RobotError, ErrorCategory, ErrorHandler

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RobotRole(Enum):
    """机器人角色枚举"""
    LEADER = "leader"
    FOLLOWER = "follower"
    COORDINATOR = "coordinator"
    WORKER = "worker"
    INSPECTOR = "inspector"


class TaskAllocationStrategy(Enum):
    """任务分配策略枚举"""
    ROUND_ROBIN = "round_robin"
    WORKLOAD_BASED = "workload_based"
    DISTANCE_BASED = "distance_based"
    SKILL_BASED = "skill_based"
    CUSTOM = "custom"


class CollaborationMode(Enum):
    """协作模式枚举"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"      # 并行执行
    SYNCHRONIZED = "synchronized"  # 同步执行
    HIERARCHICAL = "hierarchical"  # 分层执行


class CoordinationState(Enum):
    """协调状态枚举"""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


class RobotAgent:
    """机器人代理类，代表单个机器人实例的接口"""
    
    def __init__(self, robot_name: str, robot_ip: str, role: RobotRole = RobotRole.WORKER):
        """
        初始化机器人代理
        
        Args:
            robot_name: 机器人名称
            robot_ip: 机器人IP地址
            role: 机器人角色
        """
        self.robot_name = robot_name
        self.robot_ip = robot_ip
        self.role = role
        self.robot = None  # 机器人实例
        self.connector = None  # 连接实例
        self.connected = False
        self.pose = None  # 当前TCP位姿
        self.joint_positions = None  # 当前关节位置
        self.velocity = None  # 当前速度
        self.payload = None  # 当前负载
        self.workload = 0  # 工作负载指标
        self.last_update_time = 0  # 最后更新时间
        self._lock = threading.RLock()  # 线程锁
    
    def connect(self, port: int = 30003, timeout: float = 10.0) -> bool:
        """
        连接到机器人
        
        Args:
            port: 端口号
            timeout: 超时时间(秒)
            
        Returns:
            bool: 连接是否成功
        """
        try:
            with self._lock:
                if self.connected:
                    logger.warning(f"机器人 {self.robot_name} 已经连接")
                    return True
                
                self.connector = RobotConnector(
                    robot_ip=self.robot_ip,
                    robot_name=self.robot_name,
                    tcp_port=port
                )
                self.robot = robot_ext.RobotExt(self.connector)
                self.connected = True
                logger.info(f"成功连接到机器人 {self.robot_name} ({self.robot_ip})")
                
                # 更新机器人状态
                self.update_state()
                return True
        except Exception as e:
            logger.error(f"连接机器人 {self.robot_name} 失败: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        断开与机器人的连接
        
        Returns:
            bool: 断开是否成功
        """
        try:
            with self._lock:
                if not self.connected:
                    return True
                
                if self.connector:
                    self.connector.close()
                
                self.connected = False
                self.robot = None
                self.connector = None
                logger.info(f"已断开与机器人 {self.robot_name} 的连接")
                return True
        except Exception as e:
            logger.error(f"断开与机器人 {self.robot_name} 的连接失败: {str(e)}")
            return False
    
    def update_state(self) -> bool:
        """
        更新机器人状态
        
        Returns:
            bool: 更新是否成功
        """
        try:
            with self._lock:
                if not self.connected or not self.robot:
                    return False
                
                self.pose = self.robot.get_actual_tcp_pose()
                self.joint_positions = self.robot.get_actual_joint_positions()
                self.velocity = self.robot.get_actual_tcp_speed()
                self.last_update_time = time.time()
                return True
        except Exception as e:
            logger.error(f"更新机器人 {self.robot_name} 状态失败: {str(e)}")
            return False
    
    def get_distance_to(self, target_pose: List[float]) -> float:
        """
        计算到目标位置的距离
        
        Args:
            target_pose: 目标位姿 [x, y, z, rx, ry, rz]
            
        Returns:
            float: 距离值
        """
        if not self.pose:
            return float('inf')
        
        # 计算笛卡尔空间距离
        position_distance = np.linalg.norm(np.array(self.pose[:3]) - np.array(target_pose[:3]))
        return position_distance
    
    def is_available(self) -> bool:
        """
        检查机器人是否可用
        
        Returns:
            bool: 是否可用
        """
        return self.connected and self.robot is not None
    
    def set_workload(self, workload: float) -> None:
        """
        设置机器人工作负载
        
        Args:
            workload: 工作负载值 (0-100)
        """
        self.workload = max(0, min(100, workload))


class CollaborationTask:
    """协作任务基类"""
    
    def __init__(self, task_id: str, task_name: str, priority: int = 50):
        """
        初始化协作任务
        
        Args:
            task_id: 任务ID
            task_name: 任务名称
            priority: 任务优先级 (0-100, 100最高)
        """
        self.task_id = task_id
        self.task_name = task_name
        self.priority = priority
        self.assigned_robots = []  # 分配的机器人列表
        self.required_resources = {}
        self.start_time = None
        self.end_time = None
        self.status = CoordinationState.IDLE
        self.progress = 0.0  # 任务进度 (0-100)
        self.result = None
        self.error = None
    
    def can_execute(self, robot_agent: RobotAgent) -> bool:
        """
        检查机器人是否可以执行此任务
        
        Args:
            robot_agent: 机器人代理
            
        Returns:
            bool: 是否可以执行
        """
        return robot_agent.is_available()
    
    def execute(self, robot_agent: RobotAgent) -> bool:
        """
        在指定机器人上执行任务
        
        Args:
            robot_agent: 机器人代理
            
        Returns:
            bool: 执行是否成功
        """
        raise NotImplementedError("子类必须实现execute方法")
    
    def abort(self) -> bool:
        """
        中止任务
        
        Returns:
            bool: 中止是否成功
        """
        self.status = CoordinationState.COMPLETED
        return True
    
    def get_completion_time_estimate(self, robot_agent: RobotAgent) -> float:
        """
        估计完成时间
        
        Args:
            robot_agent: 机器人代理
            
        Returns:
            float: 估计时间(秒)
        """
        return 0.0


class MotionTask(CollaborationTask):
    """运动任务类"""
    
    def __init__(self, task_id: str, task_name: str, target_pose: List[float], 
                 speed: float = 0.1, acceleration: float = 0.1, 
                 priority: int = 50, motion_type: str = 'movel'):
        """
        初始化运动任务
        
        Args:
            task_id: 任务ID
            task_name: 任务名称
            target_pose: 目标位姿 [x, y, z, rx, ry, rz]
            speed: 运动速度
            acceleration: 运动加速度
            priority: 任务优先级
            motion_type: 运动类型 ('movel', 'movej', 'movep')
        """
        super().__init__(task_id, task_name, priority)
        self.target_pose = target_pose
        self.speed = speed
        self.acceleration = acceleration
        self.motion_type = motion_type
    
    def execute(self, robot_agent: RobotAgent) -> bool:
        """
        执行运动任务
        
        Args:
            robot_agent: 机器人代理
            
        Returns:
            bool: 执行是否成功
        """
        try:
            if not robot_agent.is_available():
                return False
            
            self.start_time = time.time()
            self.status = CoordinationState.EXECUTING
            
            # 执行运动命令
            if self.motion_type == 'movel':
                robot_agent.robot.movej(self.target_pose, self.speed, self.acceleration)
            elif self.motion_type == 'movej':
                robot_agent.robot.movej(self.target_pose, self.speed, self.acceleration)
            elif self.motion_type == 'movep':
                # 需要实现movep方法
                pass
            
            self.end_time = time.time()
            self.status = CoordinationState.COMPLETED
            self.progress = 100.0
            robot_agent.update_state()
            return True
        except Exception as e:
            self.error = str(e)
            self.status = CoordinationState.ERROR
            logger.error(f"执行运动任务 {self.task_name} 失败: {str(e)}")
            return False
    
    def get_completion_time_estimate(self, robot_agent: RobotAgent) -> float:
        """
        估计运动任务完成时间
        
        Args:
            robot_agent: 机器人代理
            
        Returns:
            float: 估计时间(秒)
        """
        if not robot_agent.pose:
            return 10.0  # 默认估计时间
        
        # 计算距离
        distance = robot_agent.get_distance_to(self.target_pose)
        
        # 简单的时间估计
        if self.speed > 0:
            time_estimate = distance / self.speed * 2  # 考虑加减速
            return max(1.0, time_estimate)  # 最小1秒
        
        return 10.0


class MultiRobotCoordinator:
    """多机器人协调器类"""
    
    def __init__(self, allocation_strategy: TaskAllocationStrategy = TaskAllocationStrategy.WORKLOAD_BASED):
        """
        初始化多机器人协调器
        
        Args:
            allocation_strategy: 任务分配策略
        """
        self.robots = {}  # 机器人字典 {robot_name: RobotAgent}
        self.tasks = {}  # 任务字典 {task_id: CollaborationTask}
        self.allocation_strategy = allocation_strategy
        self.collaboration_mode = CollaborationMode.PARALLEL
        self.coordination_state = CoordinationState.IDLE
        self._lock = threading.RLock()  # 线程锁
        self._task_queue = []  # 任务队列
        self._error_handler = ErrorHandler()
    
    def add_robot(self, robot_name: str, robot_ip: str, role: RobotRole = RobotRole.WORKER) -> bool:
        """
        添加机器人
        
        Args:
            robot_name: 机器人名称
            robot_ip: 机器人IP地址
            role: 机器人角色
            
        Returns:
            bool: 添加是否成功
        """
        try:
            with self._lock:
                if robot_name in self.robots:
                    logger.warning(f"机器人 {robot_name} 已存在")
                    return False
                
                robot_agent = RobotAgent(robot_name, robot_ip, role)
                self.robots[robot_name] = robot_agent
                logger.info(f"已添加机器人: {robot_name} ({robot_ip}), 角色: {role.value}")
                return True
        except Exception as e:
            logger.error(f"添加机器人失败: {str(e)}")
            return False
    
    def remove_robot(self, robot_name: str) -> bool:
        """
        移除机器人
        
        Args:
            robot_name: 机器人名称
            
        Returns:
            bool: 移除是否成功
        """
        try:
            with self._lock:
                if robot_name not in self.robots:
                    logger.warning(f"机器人 {robot_name} 不存在")
                    return False
                
                robot_agent = self.robots[robot_name]
                robot_agent.disconnect()
                del self.robots[robot_name]
                logger.info(f"已移除机器人: {robot_name}")
                return True
        except Exception as e:
            logger.error(f"移除机器人失败: {str(e)}")
            return False
    
    def connect_all_robots(self, port: int = 30003, timeout: float = 10.0) -> Dict[str, bool]:
        """
        连接所有机器人
        
        Args:
            port: 端口号
            timeout: 超时时间(秒)
            
        Returns:
            Dict[str, bool]: 每个机器人的连接结果
        """
        results = {}
        
        with self._lock:
            for robot_name, robot_agent in self.robots.items():
                results[robot_name] = robot_agent.connect(port, timeout)
        
        return results
    
    def disconnect_all_robots(self) -> Dict[str, bool]:
        """
        断开所有机器人连接
        
        Returns:
            Dict[str, bool]: 每个机器人的断开结果
        """
        results = {}
        
        with self._lock:
            for robot_name, robot_agent in self.robots.items():
                results[robot_name] = robot_agent.disconnect()
        
        return results
    
    def update_all_robot_states(self) -> Dict[str, bool]:
        """
        更新所有机器人状态
        
        Returns:
            Dict[str, bool]: 每个机器人的更新结果
        """
        results = {}
        
        with self._lock:
            for robot_name, robot_agent in self.robots.items():
                results[robot_name] = robot_agent.update_state()
        
        return results
    
    def add_task(self, task: CollaborationTask) -> bool:
        """
        添加协作任务
        
        Args:
            task: 协作任务实例
            
        Returns:
            bool: 添加是否成功
        """
        try:
            with self._lock:
                if task.task_id in self.tasks:
                    logger.warning(f"任务 {task.task_id} 已存在")
                    return False
                
                self.tasks[task.task_id] = task
                self._task_queue.append(task)
                logger.info(f"已添加任务: {task.task_name} (ID: {task.task_id})")
                return True
        except Exception as e:
            logger.error(f"添加任务失败: {str(e)}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """
        移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 移除是否成功
        """
        try:
            with self._lock:
                if task_id not in self.tasks:
                    logger.warning(f"任务 {task_id} 不存在")
                    return False
                
                task = self.tasks[task_id]
                
                # 从队列中移除
                if task in self._task_queue:
                    self._task_queue.remove(task)
                
                del self.tasks[task_id]
                logger.info(f"已移除任务: {task.task_name} (ID: {task_id})")
                return True
        except Exception as e:
            logger.error(f"移除任务失败: {str(e)}")
            return False
    
    def allocate_tasks(self) -> Dict[str, List[CollaborationTask]]:
        """
        分配任务到机器人
        
        Returns:
            Dict[str, List[CollaborationTask]]: 每个机器人分配的任务列表
        """
        allocation_result = {robot_name: [] for robot_name in self.robots}
        available_robots = [agent for agent in self.robots.values() if agent.is_available()]
        
        if not available_robots:
            logger.warning("没有可用的机器人")
            return allocation_result
        
        # 根据策略分配任务
        if self.allocation_strategy == TaskAllocationStrategy.ROUND_ROBIN:
            # 轮询分配
            for i, task in enumerate(self._task_queue):
                robot_idx = i % len(available_robots)
                robot_agent = available_robots[robot_idx]
                
                if task.can_execute(robot_agent):
                    allocation_result[robot_agent.robot_name].append(task)
                    task.assigned_robots.append(robot_agent.robot_name)
        
        elif self.allocation_strategy == TaskAllocationStrategy.WORKLOAD_BASED:
            # 基于工作负载分配
            for task in self._task_queue:
                # 找出工作负载最小的机器人
                suitable_robots = [r for r in available_robots if task.can_execute(r)]
                if suitable_robots:
                    min_workload_robot = min(suitable_robots, key=lambda r: r.workload)
                    allocation_result[min_workload_robot.robot_name].append(task)
                    task.assigned_robots.append(min_workload_robot.robot_name)
                    # 更新工作负载估计
                    min_workload_robot.set_workload(min_workload_robot.workload + task.priority / 10)
        
        elif self.allocation_strategy == TaskAllocationStrategy.DISTANCE_BASED:
            # 基于距离分配（适用于运动任务）
            for task in self._task_queue:
                if isinstance(task, MotionTask):
                    suitable_robots = [r for r in available_robots if task.can_execute(r)]
                    if suitable_robots:
                        # 找出距离目标位置最近的机器人
                        closest_robot = min(suitable_robots, 
                                           key=lambda r: r.get_distance_to(task.target_pose))
                        allocation_result[closest_robot.robot_name].append(task)
                        task.assigned_robots.append(closest_robot.robot_name)
        
        return allocation_result
    
    def execute_allocated_tasks(self, allocation: Dict[str, List[CollaborationTask]]) -> Dict[str, Dict[str, bool]]:
        """
        执行已分配的任务
        
        Args:
            allocation: 任务分配结果
            
        Returns:
            Dict[str, Dict[str, bool]]: 每个机器人的任务执行结果
        """
        execution_results = {robot_name: {} for robot_name in allocation}
        self.coordination_state = CoordinationState.EXECUTING
        
        if self.collaboration_mode == CollaborationMode.SEQUENTIAL:
            # 顺序执行
            for robot_name, tasks in allocation.items():
                if robot_name in self.robots and tasks:
                    robot_agent = self.robots[robot_name]
                    for task in tasks:
                        result = task.execute(robot_agent)
                        execution_results[robot_name][task.task_id] = result
        
        elif self.collaboration_mode == CollaborationMode.PARALLEL:
            # 并行执行 - 使用线程
            threads = []
            thread_results = {}
            
            def execute_robot_tasks(robot_name, tasks):
                robot_results = {}
                if robot_name in self.robots and tasks:
                    robot_agent = self.robots[robot_name]
                    for task in tasks:
                        result = task.execute(robot_agent)
                        robot_results[task.task_id] = result
                thread_results[robot_name] = robot_results
            
            # 创建线程
            for robot_name, tasks in allocation.items():
                if tasks:  # 只有分配了任务的机器人才创建线程
                    thread = threading.Thread(
                        target=execute_robot_tasks,
                        args=(robot_name, tasks)
                    )
                    threads.append(thread)
                    thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            execution_results = thread_results
        
        elif self.collaboration_mode == CollaborationMode.SYNCHRONIZED:
            # 同步执行 - 确保所有机器人同时开始和结束
            # 简化实现，先计算所有任务的完成时间估计
            task_time_estimates = {}
            
            for robot_name, tasks in allocation.items():
                if robot_name in self.robots and tasks:
                    robot_agent = self.robots[robot_name]
                    total_time = 0
                    for task in tasks:
                        total_time += task.get_completion_time_estimate(robot_agent)
                    task_time_estimates[robot_name] = total_time
            
            # 确定最长执行时间
            max_execution_time = max(task_time_estimates.values()) if task_time_estimates else 0
            
            # 开始同步执行
            start_time = time.time()
            
            for robot_name, tasks in allocation.items():
                if robot_name in self.robots and tasks:
                    robot_agent = self.robots[robot_name]
                    for task in tasks:
                        result = task.execute(robot_agent)
                        execution_results[robot_name][task.task_id] = result
                    
                    # 等待，确保同步
                    elapsed = time.time() - start_time
                    if elapsed < max_execution_time:
                        time.sleep(max_execution_time - elapsed)
        
        self.coordination_state = CoordinationState.COMPLETED
        return execution_results
    
    def detect_collision_risks(self, safety_distance: float = 0.1) -> List[Tuple[str, str, float]]:
        """
        检测机器人之间的碰撞风险
        
        Args:
            safety_distance: 安全距离阈值
            
        Returns:
            List[Tuple[str, str, float]]: 碰撞风险列表 [(robot1, robot2, distance)]
        """
        collision_risks = []
        
        # 获取所有可用机器人
        available_robots = [(name, agent) for name, agent in self.robots.items() 
                          if agent.is_available() and agent.pose]
        
        # 检测每对机器人之间的距离
        for i, (name1, robot1) in enumerate(available_robots):
            for j, (name2, robot2) in enumerate(available_robots[i+1:], i+1):
                distance = np.linalg.norm(np.array(robot1.pose[:3]) - np.array(robot2.pose[:3]))
                if distance < safety_distance:
                    collision_risks.append((name1, name2, distance))
        
        return collision_risks
    
    def get_system_status(self) -> Dict:
        """
        获取整个系统的状态
        
        Returns:
            Dict: 系统状态信息
        """
        robot_statuses = {}
        
        for robot_name, robot_agent in self.robots.items():
            robot_statuses[robot_name] = {
                'connected': robot_agent.connected,
                'role': robot_agent.role.value,
                'pose': robot_agent.pose,
                'joint_positions': robot_agent.joint_positions,
                'workload': robot_agent.workload,
                'last_update': robot_agent.last_update_time
            }
        
        task_statuses = {}
        for task_id, task in self.tasks.items():
            task_statuses[task_id] = {
                'name': task.task_name,
                'status': task.status.value,
                'progress': task.progress,
                'priority': task.priority,
                'assigned_robots': task.assigned_robots
            }
        
        return {
            'coordination_state': self.coordination_state.value,
            'collaboration_mode': self.collaboration_mode.value,
            'allocation_strategy': self.allocation_strategy.value,
            'robot_count': len(self.robots),
            'available_robot_count': sum(1 for r in self.robots.values() if r.is_available()),
            'task_count': len(self.tasks),
            'robots': robot_statuses,
            'tasks': task_statuses
        }
    
    def clear_completed_tasks(self) -> int:
        """
        清理已完成的任务
        
        Returns:
            int: 清理的任务数量
        """
        with self._lock:
            completed_task_ids = [task_id for task_id, task in self.tasks.items() 
                                if task.status == CoordinationState.COMPLETED]
            
            for task_id in completed_task_ids:
                if task_id in self.tasks:
                    del self.tasks[task_id]
                    # 从队列中移除
                    for task in self._task_queue:
                        if task.task_id == task_id:
                            self._task_queue.remove(task)
                            break
            
            return len(completed_task_ids)


# 创建全局协调器实例
_global_coordinator = None


def get_coordinator() -> MultiRobotCoordinator:
    """
    获取全局协调器实例
    
    Returns:
        MultiRobotCoordinator: 协调器实例
    """
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = MultiRobotCoordinator()
    return _global_coordinator


def reset_coordinator() -> None:
    """
    重置全局协调器实例
    """
    global _global_coordinator
    _global_coordinator = None


# 示例用法
if __name__ == '__main__':
    # 创建协调器
    coordinator = MultiRobotCoordinator()
    
    # 添加机器人
    coordinator.add_robot('robot1', '192.168.1.101', RobotRole.LEADER)
    coordinator.add_robot('robot2', '192.168.1.102', RobotRole.FOLLOWER)
    
    # 连接机器人
    results = coordinator.connect_all_robots()
    print(f"连接结果: {results}")
    
    # 更新机器人状态
    coordinator.update_all_robot_states()
    
    # 创建任务
    task1 = MotionTask(
        'task1',
        'Move to position A',
        [0.3, 0.2, 0.5, 0, 3.14, 0],
        0.2,
        0.2,
        80
    )
    
    task2 = MotionTask(
        'task2', 
        'Move to position B',
        [0.5, 0.4, 0.3, 0, 3.14, 0],
        0.2,
        0.2,
        60
    )
    
    # 添加任务
    coordinator.add_task(task1)
    coordinator.add_task(task2)
    
    # 设置协作模式
    coordinator.collaboration_mode = CollaborationMode.PARALLEL
    
    # 分配并执行任务
    allocation = coordinator.allocate_tasks()
    print(f"任务分配: {allocation}")
    
    results = coordinator.execute_allocated_tasks(allocation)
    print(f"执行结果: {results}")
    
    # 检测碰撞风险
    risks = coordinator.detect_collision_risks()
    print(f"碰撞风险: {risks}")
    
    # 获取系统状态
    status = coordinator.get_system_status()
    print(f"系统状态: {status}")
    
    # 清理
    coordinator.disconnect_all_robots()
