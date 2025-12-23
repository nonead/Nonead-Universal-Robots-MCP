#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级多机器人协同控制模块

此模块扩展了基础的多机器人协同功能，提供更高级的任务分配、动态协作、
冲突解决、负载均衡和容错能力。

作者: Nonead
日期: 2024
版本: 1.0
"""

import threading
import time
import logging
import heapq
import numpy as np
from typing import Dict, List, Optional, Union, Callable, Tuple, Set
from enum import Enum, auto
from collections import defaultdict, deque

# 导入基础模块
from URBasic.multi_robot_coordinator import (
    MultiRobotCoordinator, RobotAgent, CollaborationTask, 
    MotionTask, RobotRole, TaskAllocationStrategy, CollaborationMode,
    CoordinationState
)
from URBasic.error_handling import RobotError, ErrorCategory, ErrorHandler
from URBasic.trajectory_planner import TrajectoryPlanner
from URBasic.operation_history import get_history_manager

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedTaskAllocationStrategy(Enum):
    """高级任务分配策略枚举"""
    DYNAMIC_WORKLOAD = "dynamic_workload"        # 动态工作负载分配
    SKILL_MATCHING = "skill_matching"           # 技能匹配分配
    PRIORITY_BASED = "priority_based"           # 基于优先级的分配
    SPATIAL_PARTITIONING = "spatial_partitioning"  # 空间分区分配
    HYBRID_OPTIMIZATION = "hybrid_optimization"    # 混合优化分配


class CollaborationPattern(Enum):
    """协作模式枚举"""
    SEQUENTIAL = "sequential"            # 顺序执行
    PARALLEL = "parallel"               # 并行执行
    SYNCHRONIZED = "synchronized"       # 同步执行
    HIERARCHICAL = "hierarchical"       # 分层执行
    SWARM = "swarm"                     # 群体智能
    ADAPTIVE = "adaptive"               # 自适应协作


class ResourceType(Enum):
    """资源类型枚举"""
    WORKSPACE = "workspace"              # 工作空间
    TOOL = "tool"                        # 工具
    GRIPPER = "gripper"                  # 夹具
    SENSOR = "sensor"                    # 传感器
    MATERIAL = "material"                # 材料
    STATION = "station"                  # 工作站


class ResourceAllocationStatus(Enum):
    """资源分配状态枚举"""
    AVAILABLE = "available"              # 可用
    ALLOCATED = "allocated"              # 已分配
    RESERVED = "reserved"                # 已预留
    UNAVAILABLE = "unavailable"          # 不可用


class Resource:
    """资源类，用于表示机器人可以使用的资源"""
    
    def __init__(self, resource_id: str, resource_type: ResourceType, 
                 location: Optional[List[float]] = None, 
                 description: str = ""):
        """
        初始化资源
        
        Args:
            resource_id: 资源ID
            resource_type: 资源类型
            location: 资源位置 [x, y, z]
            description: 资源描述
        """
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.location = location
        self.description = description
        self.status = ResourceAllocationStatus.AVAILABLE
        self.allocated_to = None  # 分配给哪个机器人
        self.allocation_time = None  # 分配时间
        self.release_time = None  # 预计释放时间
        self._lock = threading.RLock()
    
    def allocate(self, robot_name: str, duration: Optional[float] = None) -> bool:
        """
        分配资源给机器人
        
        Args:
            robot_name: 机器人名称
            duration: 分配持续时间（秒）
            
        Returns:
            bool: 分配是否成功
        """
        with self._lock:
            if self.status == ResourceAllocationStatus.AVAILABLE:
                self.status = ResourceAllocationStatus.ALLOCATED
                self.allocated_to = robot_name
                self.allocation_time = time.time()
                if duration:
                    self.release_time = time.time() + duration
                logger.info(f"资源 {self.resource_id} 已分配给机器人 {robot_name}")
                return True
            return False
    
    def release(self) -> bool:
        """
        释放资源
        
        Returns:
            bool: 释放是否成功
        """
        with self._lock:
            if self.status in [ResourceAllocationStatus.ALLOCATED, 
                              ResourceAllocationStatus.RESERVED]:
                self.status = ResourceAllocationStatus.AVAILABLE
                self.allocated_to = None
                self.allocation_time = None
                self.release_time = None
                logger.info(f"资源 {self.resource_id} 已释放")
                return True
            return False
    
    def reserve(self, robot_name: str, duration: float) -> bool:
        """
        预留资源
        
        Args:
            robot_name: 机器人名称
            duration: 预留持续时间（秒）
            
        Returns:
            bool: 预留是否成功
        """
        with self._lock:
            if self.status == ResourceAllocationStatus.AVAILABLE:
                self.status = ResourceAllocationStatus.RESERVED
                self.allocated_to = robot_name
                self.allocation_time = time.time()
                self.release_time = time.time() + duration
                logger.info(f"资源 {self.resource_id} 已预留给机器人 {robot_name}")
                return True
            return False
    
    def to_dict(self) -> Dict:
        """
        转换为字典
        
        Returns:
            Dict: 资源信息字典
        """
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type.value,
            "location": self.location,
            "description": self.description,
            "status": self.status.value,
            "allocated_to": self.allocated_to,
            "allocation_time": self.allocation_time,
            "release_time": self.release_time
        }


class AdvancedCollaborationTask(CollaborationTask):
    """高级协作任务类"""
    
    def __init__(self, task_id: str, task_name: str, priority: int = 50,
                 required_resources: Optional[List[str]] = None,
                 dependencies: Optional[List[str]] = None,
                 estimated_duration: float = 0.0,
                 skill_requirements: Optional[Dict[str, float]] = None):
        """
        初始化高级协作任务
        
        Args:
            task_id: 任务ID
            task_name: 任务名称
            priority: 任务优先级（0-100，越高优先级越高）
            required_resources: 所需资源ID列表
            dependencies: 依赖任务ID列表
            estimated_duration: 估计执行时间（秒）
            skill_requirements: 技能要求字典 {技能名称: 所需熟练度}
        """
        super().__init__(task_id, task_name, priority)
        self.required_resources = required_resources or []
        self.dependencies = dependencies or []
        self.estimated_duration = estimated_duration
        self.skill_requirements = skill_requirements or {}
        self.assigned_robot = None
        self.start_time = None
        self.end_time = None
        self.progress = 0.0  # 进度百分比
        self.resource_allocations = {}
    
    def can_execute(self, robot_agent: RobotAgent, resource_manager: 'ResourceManager') -> bool:
        """
        检查任务是否可以执行
        
        Args:
            robot_agent: 机器人代理
            resource_manager: 资源管理器
            
        Returns:
            bool: 是否可以执行
        """
        # 检查机器人是否可用
        if not robot_agent.is_available():
            return False
        
        # 检查资源是否可用
        for resource_id in self.required_resources:
            resource = resource_manager.get_resource(resource_id)
            if not resource or resource.status != ResourceAllocationStatus.AVAILABLE:
                return False
        
        # 检查技能要求
        if not self._check_skill_requirements(robot_agent):
            return False
        
        return True
    
    def _check_skill_requirements(self, robot_agent: RobotAgent) -> bool:
        """
        检查机器人是否满足技能要求
        
        Args:
            robot_agent: 机器人代理
            
        Returns:
            bool: 是否满足技能要求
        """
        # 实际应用中，这里应该检查机器人的技能熟练度
        # 这里简化为假设所有机器人都满足技能要求
        return True
    
    def allocate_resources(self, resource_manager: 'ResourceManager') -> bool:
        """
        分配任务所需资源
        
        Args:
            resource_manager: 资源管理器
            
        Returns:
            bool: 分配是否成功
        """
        if not self.assigned_robot:
            logger.error(f"任务 {self.task_id} 未分配机器人，无法分配资源")
            return False
        
        for resource_id in self.required_resources:
            if resource_manager.allocate_resource(resource_id, self.assigned_robot):
                self.resource_allocations[resource_id] = True
            else:
                # 回滚已分配的资源
                for allocated_resource_id in list(self.resource_allocations.keys()):
                    resource_manager.release_resource(allocated_resource_id)
                    del self.resource_allocations[allocated_resource_id]
                return False
        
        return True
    
    def release_resources(self, resource_manager: 'ResourceManager') -> bool:
        """
        释放任务占用的资源
        
        Args:
            resource_manager: 资源管理器
            
        Returns:
            bool: 释放是否成功
        """
        success = True
        for resource_id in list(self.resource_allocations.keys()):
            if not resource_manager.release_resource(resource_id):
                success = False
            else:
                del self.resource_allocations[resource_id]
        return success
    
    def update_progress(self, progress: float) -> None:
        """
        更新任务进度
        
        Args:
            progress: 进度百分比（0-100）
        """
        self.progress = min(max(progress, 0.0), 100.0)
    
    def to_dict(self) -> Dict:
        """
        转换为字典
        
        Returns:
            Dict: 任务信息字典
        """
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "priority": self.priority,
            "required_resources": self.required_resources,
            "dependencies": self.dependencies,
            "estimated_duration": self.estimated_duration,
            "skill_requirements": self.skill_requirements,
            "assigned_robot": self.assigned_robot,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "progress": self.progress,
            "resource_allocations": list(self.resource_allocations.keys())
        }


class ResourceManager:
    """资源管理器类，负责管理和分配资源"""
    
    def __init__(self):
        """初始化资源管理器"""
        self.resources = {}
        self._lock = threading.RLock()
    
    def add_resource(self, resource: Resource) -> bool:
        """
        添加资源
        
        Args:
            resource: 资源对象
            
        Returns:
            bool: 添加是否成功
        """
        with self._lock:
            if resource.resource_id in self.resources:
                logger.warning(f"资源 {resource.resource_id} 已存在")
                return False
            self.resources[resource.resource_id] = resource
            logger.info(f"添加资源: {resource.resource_id}")
            return True
    
    def remove_resource(self, resource_id: str) -> bool:
        """
        移除资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            bool: 移除是否成功
        """
        with self._lock:
            if resource_id not in self.resources:
                logger.warning(f"资源 {resource_id} 不存在")
                return False
            # 检查资源是否已分配
            resource = self.resources[resource_id]
            if resource.status in [ResourceAllocationStatus.ALLOCATED, 
                                  ResourceAllocationStatus.RESERVED]:
                logger.error(f"资源 {resource_id} 正在使用中，无法移除")
                return False
            del self.resources[resource_id]
            logger.info(f"移除资源: {resource_id}")
            return True
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """
        获取资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            Optional[Resource]: 资源对象，如果不存在则返回None
        """
        with self._lock:
            return self.resources.get(resource_id)
    
    def get_available_resources(self, resource_type: Optional[ResourceType] = None) -> List[Resource]:
        """
        获取可用资源
        
        Args:
            resource_type: 资源类型，如果为None则返回所有类型的可用资源
            
        Returns:
            List[Resource]: 可用资源列表
        """
        with self._lock:
            resources = []
            for resource in self.resources.values():
                if resource.status == ResourceAllocationStatus.AVAILABLE:
                    if resource_type is None or resource.resource_type == resource_type:
                        resources.append(resource)
            return resources
    
    def allocate_resource(self, resource_id: str, robot_name: str, 
                         duration: Optional[float] = None) -> bool:
        """
        分配资源给机器人
        
        Args:
            resource_id: 资源ID
            robot_name: 机器人名称
            duration: 分配持续时间（秒）
            
        Returns:
            bool: 分配是否成功
        """
        resource = self.get_resource(resource_id)
        if not resource:
            logger.error(f"资源 {resource_id} 不存在")
            return False
        
        return resource.allocate(robot_name, duration)
    
    def release_resource(self, resource_id: str) -> bool:
        """
        释放资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            bool: 释放是否成功
        """
        resource = self.get_resource(resource_id)
        if not resource:
            logger.error(f"资源 {resource_id} 不存在")
            return False
        
        return resource.release()
    
    def get_resources_by_type(self, resource_type: ResourceType) -> List[Resource]:
        """
        根据类型获取资源
        
        Args:
            resource_type: 资源类型
            
        Returns:
            List[Resource]: 资源列表
        """
        with self._lock:
            return [r for r in self.resources.values() 
                    if r.resource_type == resource_type]
    
    def update_resource_status(self) -> None:
        """
        更新资源状态，处理超时的预留和分配
        """
        current_time = time.time()
        with self._lock:
            for resource in self.resources.values():
                if resource.release_time and current_time > resource.release_time:
                    resource.release()
    
    def get_resource_usage_statistics(self) -> Dict:
        """
        获取资源使用统计信息
        
        Returns:
            Dict: 统计信息字典
        """
        stats = defaultdict(lambda: {"total": 0, "available": 0, "allocated": 0, "reserved": 0})
        
        with self._lock:
            for resource in self.resources.values():
                resource_type = resource.resource_type.value
                stats[resource_type]["total"] += 1
                stats[resource_type][resource.status.value] += 1
        
        return dict(stats)


class TaskDependencyGraph:
    """任务依赖图类，用于管理任务之间的依赖关系"""
    
    def __init__(self):
        """初始化任务依赖图"""
        self.graph = defaultdict(list)  # 任务ID -> 依赖任务ID列表
        self.reverse_graph = defaultdict(list)  # 任务ID -> 依赖于该任务的任务ID列表
        self.tasks = {}
        self._lock = threading.RLock()
    
    def add_task(self, task: AdvancedCollaborationTask) -> bool:
        """
        添加任务
        
        Args:
            task: 任务对象
            
        Returns:
            bool: 添加是否成功
        """
        with self._lock:
            if task.task_id in self.tasks:
                logger.warning(f"任务 {task.task_id} 已存在")
                return False
            
            self.tasks[task.task_id] = task
            
            # 添加依赖关系
            for dependency_id in task.dependencies:
                if dependency_id not in self.tasks:
                    logger.warning(f"任务 {task.task_id} 的依赖任务 {dependency_id} 不存在")
                    continue
                self.graph[task.task_id].append(dependency_id)
                self.reverse_graph[dependency_id].append(task.task_id)
            
            return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 移除是否成功
        """
        with self._lock:
            if task_id not in self.tasks:
                logger.warning(f"任务 {task_id} 不存在")
                return False
            
            # 移除依赖关系
            if task_id in self.graph:
                for dependency_id in self.graph[task_id]:
                    if task_id in self.reverse_graph[dependency_id]:
                        self.reverse_graph[dependency_id].remove(task_id)
                del self.graph[task_id]
            
            if task_id in self.reverse_graph:
                for dependent_task_id in self.reverse_graph[task_id]:
                    if task_id in self.graph[dependent_task_id]:
                        self.graph[dependent_task_id].remove(task_id)
                del self.reverse_graph[task_id]
            
            # 移除任务
            del self.tasks[task_id]
            return True
    
    def get_ready_tasks(self) -> List[AdvancedCollaborationTask]:
        """
        获取可以执行的任务（所有依赖任务都已完成）
        
        Returns:
            List[AdvancedCollaborationTask]: 就绪任务列表
        """
        ready_tasks = []
        
        with self._lock:
            for task_id, task in self.tasks.items():
                # 检查任务是否已分配
                if task.assigned_robot:
                    continue
                
                # 检查所有依赖任务是否已完成
                all_dependencies_completed = True
                for dependency_id in task.dependencies:
                    if dependency_id in self.tasks:
                        dependency_task = self.tasks[dependency_id]
                        if dependency_task.end_time is None:
                            all_dependencies_completed = False
                            break
                    else:
                        # 依赖任务不存在，视为完成
                        pass
                
                if all_dependencies_completed:
                    ready_tasks.append(task)
        
        # 按优先级排序
        return sorted(ready_tasks, key=lambda t: t.priority, reverse=True)
    
    def get_dependent_tasks(self, task_id: str) -> List[AdvancedCollaborationTask]:
        """
        获取依赖于指定任务的任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            List[AdvancedCollaborationTask]: 依赖任务列表
        """
        with self._lock:
            return [self.tasks[t_id] for t_id in self.reverse_graph.get(task_id, []) 
                    if t_id in self.tasks]
    
    def check_cycles(self) -> bool:
        """
        检查依赖图中是否存在循环
        
        Returns:
            bool: 如果存在循环则返回True，否则返回False
        """
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id):
            visited.add(task_id)
            rec_stack.add(task_id)
            
            # 检查所有依赖
            for dependency_id in self.graph.get(task_id, []):
                if dependency_id not in visited:
                    if has_cycle(dependency_id):
                        return True
                elif dependency_id in rec_stack:
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        with self._lock:
            for task_id in self.tasks.keys():
                if task_id not in visited:
                    if has_cycle(task_id):
                        return True
            return False
    
    def get_task_path(self, start_task_id: str, end_task_id: str) -> Optional[List[str]]:
        """
        获取从开始任务到结束任务的路径
        
        Args:
            start_task_id: 开始任务ID
            end_task_id: 结束任务ID
            
        Returns:
            Optional[List[str]]: 任务ID路径列表，如果不存在路径则返回None
        """
        visited = set()
        path = []
        
        def dfs(task_id):
            visited.add(task_id)
            path.append(task_id)
            
            if task_id == end_task_id:
                return True
            
            for dependent_task_id in self.reverse_graph.get(task_id, []):
                if dependent_task_id not in visited:
                    if dfs(dependent_task_id):
                        return True
            
            path.pop()
            return False
        
        with self._lock:
            if dfs(start_task_id):
                return path
            return None


class AdvancedMultiRobotCoordinator(MultiRobotCoordinator):
    """高级多机器人协调器类"""
    
    def __init__(self, allocation_strategy: TaskAllocationStrategy = 
                 TaskAllocationStrategy.WORKLOAD_BASED,
                 advanced_strategy: AdvancedTaskAllocationStrategy = 
                 AdvancedTaskAllocationStrategy.DYNAMIC_WORKLOAD):
        """
        初始化高级多机器人协调器
        
        Args:
            allocation_strategy: 基础任务分配策略
            advanced_strategy: 高级任务分配策略
        """
        super().__init__(allocation_strategy)
        self.advanced_strategy = advanced_strategy
        self.resource_manager = ResourceManager()
        self.task_dependency_graph = TaskDependencyGraph()
        self.collaboration_pattern = CollaborationPattern.PARALLEL
        self.skill_registry = defaultdict(dict)  # {机器人名称: {技能名称: 熟练度}}
        self.task_blackboard = {}  # 任务共享数据黑板
        self.continuous_monitoring = False
        self.monitoring_thread = None
        self._stop_monitoring = threading.Event()
    
    def register_robot_skills(self, robot_name: str, skills: Dict[str, float]) -> bool:
        """
        注册机器人技能
        
        Args:
            robot_name: 机器人名称
            skills: 技能字典 {技能名称: 熟练度}
            
        Returns:
            bool: 注册是否成功
        """
        if robot_name not in self.robots:
            logger.error(f"机器人 {robot_name} 不存在")
            return False
        
        self.skill_registry[robot_name] = skills
        logger.info(f"为机器人 {robot_name} 注册了 {len(skills)} 项技能")
        return True
    
    def get_robot_skill_score(self, robot_name: str, skill_requirements: Dict[str, float]) -> float:
        """
        计算机器人对技能要求的匹配分数
        
        Args:
            robot_name: 机器人名称
            skill_requirements: 技能要求字典
            
        Returns:
            float: 匹配分数（0-100）
        """
        if robot_name not in self.skill_registry or not skill_requirements:
            return 0.0
        
        robot_skills = self.skill_registry[robot_name]
        total_score = 0.0
        required_count = 0
        
        for skill, required_level in skill_requirements.items():
            if skill in robot_skills:
                # 计算该技能的匹配度（0-100%）
                match_percentage = min(robot_skills[skill] / required_level, 1.0) * 100
                total_score += match_percentage
                required_count += 1
        
        if required_count == 0:
            return 0.0
        
        # 返回平均匹配分数
        return total_score / required_count
    
    def add_advanced_task(self, task: AdvancedCollaborationTask) -> bool:
        """
        添加高级任务
        
        Args:
            task: 高级任务对象
            
        Returns:
            bool: 添加是否成功
        """
        # 添加到任务依赖图
        if not self.task_dependency_graph.add_task(task):
            return False
        
        # 检查是否存在循环依赖
        if self.task_dependency_graph.check_cycles():
            logger.error(f"添加任务 {task.task_id} 后出现循环依赖")
            self.task_dependency_graph.remove_task(task.task_id)
            return False
        
        # 添加到基础任务列表
        return super().add_task(task)
    
    def remove_task(self, task_id: str) -> bool:
        """
        移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 移除是否成功
        """
        # 从任务依赖图中移除
        self.task_dependency_graph.remove_task(task_id)
        
        # 从基础任务列表中移除
        return super().remove_task(task_id)
    
    def allocate_advanced_tasks(self) -> Dict[str, List[AdvancedCollaborationTask]]:
        """
        分配高级任务
        
        Returns:
            Dict[str, List[AdvancedCollaborationTask]]: 分配结果 {机器人名称: [任务列表]}
        """
        allocation = defaultdict(list)
        
        # 获取可以执行的任务
        ready_tasks = self.task_dependency_graph.get_ready_tasks()
        
        for task in ready_tasks:
            # 根据高级策略进行任务分配
            if self.advanced_strategy == AdvancedTaskAllocationStrategy.DYNAMIC_WORKLOAD:
                robot_name = self._allocate_by_dynamic_workload(task)
            elif self.advanced_strategy == AdvancedTaskAllocationStrategy.SKILL_MATCHING:
                robot_name = self._allocate_by_skill_matching(task)
            elif self.advanced_strategy == AdvancedTaskAllocationStrategy.PRIORITY_BASED:
                robot_name = self._allocate_by_priority(task)
            elif self.advanced_strategy == AdvancedTaskAllocationStrategy.SPATIAL_PARTITIONING:
                robot_name = self._allocate_by_spatial_partitioning(task)
            elif self.advanced_strategy == AdvancedTaskAllocationStrategy.HYBRID_OPTIMIZATION:
                robot_name = self._allocate_by_hybrid_optimization(task)
            else:
                # 默认使用动态工作负载
                robot_name = self._allocate_by_dynamic_workload(task)
            
            if robot_name:
                task.assigned_robot = robot_name
                allocation[robot_name].append(task)
        
        return dict(allocation)
    
    def _allocate_by_dynamic_workload(self, task: AdvancedCollaborationTask) -> Optional[str]:
        """
        根据动态工作负载分配任务
        
        Args:
            task: 任务对象
            
        Returns:
            Optional[str]: 分配的机器人名称
        """
        # 计算每个机器人的工作负载
        robot_workloads = {}
        
        for robot_name, robot in self.robots.items():
            if not robot.is_available():
                continue
            
            # 检查任务是否可以在该机器人上执行
            if not task.can_execute(robot, self.resource_manager):
                continue
            
            # 计算当前工作负载（已分配任务的估计执行时间总和）
            current_workload = 0
            for allocated_task in self.tasks:
                if allocated_task.assigned_robot == robot_name and \
                   allocated_task.end_time is None:
                    current_workload += allocated_task.estimated_duration
            
            robot_workloads[robot_name] = current_workload
        
        # 选择工作负载最小的机器人
        if robot_workloads:
            return min(robot_workloads, key=robot_workloads.get)
        
        return None
    
    def _allocate_by_skill_matching(self, task: AdvancedCollaborationTask) -> Optional[str]:
        """
        根据技能匹配分配任务
        
        Args:
            task: 任务对象
            
        Returns:
            Optional[str]: 分配的机器人名称
        """
        skill_scores = {}
        
        for robot_name, robot in self.robots.items():
            if not robot.is_available():
                continue
            
            # 检查任务是否可以在该机器人上执行
            if not task.can_execute(robot, self.resource_manager):
                continue
            
            # 计算技能匹配分数
            score = self.get_robot_skill_score(robot_name, task.skill_requirements)
            if score > 0:
                skill_scores[robot_name] = score
        
        # 选择技能匹配分数最高的机器人
        if skill_scores:
            return max(skill_scores, key=skill_scores.get)
        
        return None
    
    def _allocate_by_priority(self, task: AdvancedCollaborationTask) -> Optional[str]:
        """
        根据优先级分配任务
        
        Args:
            task: 任务对象
            
        Returns:
            Optional[str]: 分配的机器人名称
        """
        # 为高优先级任务选择最空闲的机器人
        if task.priority >= 80:
            return self._allocate_by_dynamic_workload(task)
        # 为中优先级任务平衡工作负载
        elif task.priority >= 50:
            return self._allocate_by_dynamic_workload(task)
        # 为低优先级任务选择技能匹配的机器人
        else:
            return self._allocate_by_skill_matching(task)
    
    def _allocate_by_spatial_partitioning(self, task: AdvancedCollaborationTask) -> Optional[str]:
        """
        根据空间分区分配任务
        
        Args:
            task: 任务对象
            
        Returns:
            Optional[str]: 分配的机器人名称
        """
        # 简化实现：假设任务的位置是其第一个所需资源的位置
        task_location = None
        for resource_id in task.required_resources:
            resource = self.resource_manager.get_resource(resource_id)
            if resource and resource.location:
                task_location = resource.location
                break
        
        if not task_location:
            # 如果没有位置信息，使用动态工作负载分配
            return self._allocate_by_dynamic_workload(task)
        
        # 计算每个机器人到任务位置的距离
        distances = {}
        
        for robot_name, robot in self.robots.items():
            if not robot.is_available() or not robot.pose:
                continue
            
            # 检查任务是否可以在该机器人上执行
            if not task.can_execute(robot, self.resource_manager):
                continue
            
            # 计算距离
            distance = np.linalg.norm(np.array(robot.pose[:3]) - np.array(task_location))
            distances[robot_name] = distance
        
        # 选择距离最近的机器人
        if distances:
            return min(distances, key=distances.get)
        
        return None
    
    def _allocate_by_hybrid_optimization(self, task: AdvancedCollaborationTask) -> Optional[str]:
        """
        使用混合优化策略分配任务
        
        Args:
            task: 任务对象
            
        Returns:
            Optional[str]: 分配的机器人名称
        """
        # 计算每个机器人的综合评分
        scores = {}
        
        for robot_name, robot in self.robots.items():
            if not robot.is_available():
                continue
            
            # 检查任务是否可以在该机器人上执行
            if not task.can_execute(robot, self.resource_manager):
                continue
            
            # 计算各项评分
            # 1. 技能匹配评分（40%权重）
            skill_score = self.get_robot_skill_score(robot_name, task.skill_requirements)
            
            # 2. 工作负载评分（30%权重）- 工作负载越低，评分越高
            current_workload = 0
            for allocated_task in self.tasks:
                if allocated_task.assigned_robot == robot_name and \
                   allocated_task.end_time is None:
                    current_workload += allocated_task.estimated_duration
            # 假设最大工作负载为100秒，将工作负载转换为0-100的评分
            workload_score = max(0, 100 - min(current_workload, 100))
            
            # 3. 空间评分（30%权重）- 如果有位置信息
            spatial_score = 100  # 默认满分
            task_location = None
            for resource_id in task.required_resources:
                resource = self.resource_manager.get_resource(resource_id)
                if resource and resource.location:
                    task_location = resource.location
                    break
            
            if task_location and robot.pose:
                distance = np.linalg.norm(np.array(robot.pose[:3]) - np.array(task_location))
                # 假设最大距离为2米，将距离转换为0-100的评分
                spatial_score = max(0, 100 - min(distance * 50, 100))
            
            # 计算综合评分
            total_score = (skill_score * 0.4 + workload_score * 0.3 + spatial_score * 0.3)
            scores[robot_name] = total_score
        
        # 选择综合评分最高的机器人
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def execute_allocated_tasks(self, allocation: Dict[str, List[AdvancedCollaborationTask]]) -> Dict[str, Dict[str, bool]]:
        """
        执行分配的任务
        
        Args:
            allocation: 分配结果 {机器人名称: [任务列表]}
            
        Returns:
            Dict[str, Dict[str, bool]]: 执行结果 {机器人名称: {任务ID: 是否成功}}
        """
        results = defaultdict(dict)
        
        for robot_name, tasks in allocation.items():
            robot = self.robots.get(robot_name)
            if not robot or not robot.is_available():
                continue
            
            for task in tasks:
                # 分配资源
                if not task.allocate_resources(self.resource_manager):
                    logger.error(f"任务 {task.task_id} 资源分配失败")
                    results[robot_name][task.task_id] = False
                    continue
                
                # 根据协作模式执行任务
                if self.collaboration_pattern == CollaborationPattern.SEQUENTIAL:
                    success = self._execute_task_sequential(robot, task)
                elif self.collaboration_pattern == CollaborationPattern.SYNCHRONIZED:
                    # 同步执行需要更多的协调机制
                    success = self._execute_task_sequential(robot, task)
                elif self.collaboration_pattern == CollaborationPattern.HIERARCHICAL:
                    # 分层执行需要机器人角色的支持
                    success = self._execute_task_sequential(robot, task)
                elif self.collaboration_pattern == CollaborationPattern.SWARM:
                    # 群体智能需要更复杂的协调算法
                    success = self._execute_task_sequential(robot, task)
                elif self.collaboration_pattern == CollaborationPattern.ADAPTIVE:
                    # 自适应协作根据任务类型动态选择执行方式
                    success = self._execute_task_adaptive(robot, task)
                else:
                    # 默认并行执行
                    success = self._execute_task_sequential(robot, task)
                
                # 记录结果
                results[robot_name][task.task_id] = success
                
                # 释放资源
                task.release_resources(self.resource_manager)
        
        return dict(results)
    
    def _execute_task_sequential(self, robot: RobotAgent, task: AdvancedCollaborationTask) -> bool:
        """
        顺序执行任务
        
        Args:
            robot: 机器人代理
            task: 任务对象
            
        Returns:
            bool: 执行是否成功
        """
        try:
            task.start_time = time.time()
            
            # 如果是运动任务，执行运动
            if isinstance(task, MotionTask):
                success = task.execute(robot)
            else:
                # 对于其他类型的任务，调用基础执行方法
                success = task.execute(robot)
            
            if success:
                task.end_time = time.time()
                task.update_progress(100.0)
                logger.info(f"任务 {task.task_id} 执行成功")
            else:
                logger.error(f"任务 {task.task_id} 执行失败")
            
            return success
        except Exception as e:
            logger.error(f"任务 {task.task_id} 执行异常: {str(e)}")
            return False
    
    def _execute_task_adaptive(self, robot: RobotAgent, task: AdvancedCollaborationTask) -> bool:
        """
        自适应执行任务
        
        Args:
            robot: 机器人代理
            task: 任务对象
            
        Returns:
            bool: 执行是否成功
        """
        # 根据任务类型和机器人状态自适应选择执行策略
        # 这里简化实现，实际应用中可能需要更复杂的逻辑
        return self._execute_task_sequential(robot, task)
    
    def start_continuous_monitoring(self, interval: float = 1.0) -> bool:
        """
        开始持续监控
        
        Args:
            interval: 监控间隔（秒）
            
        Returns:
            bool: 启动是否成功
        """
        if self.continuous_monitoring:
            logger.warning("持续监控已经在运行")
            return False
        
        self._stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        self.continuous_monitoring = True
        logger.info("持续监控已启动")
        return True
    
    def stop_continuous_monitoring(self) -> bool:
        """
        停止持续监控
        
        Returns:
            bool: 停止是否成功
        """
        if not self.continuous_monitoring:
            logger.warning("持续监控未运行")
            return False
        
        self._stop_monitoring.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        self.continuous_monitoring = False
        logger.info("持续监控已停止")
        return True
    
    def _monitoring_loop(self, interval: float) -> None:
        """
        监控循环
        
        Args:
            interval: 监控间隔（秒）
        """
        while not self._stop_monitoring.is_set():
            try:
                # 更新机器人状态
                self.update_all_robot_states()
                
                # 更新资源状态
                self.resource_manager.update_resource_status()
                
                # 检查任务进度
                self._check_task_progress()
                
                # 检测碰撞风险
                risks = self.detect_collision_risks()
                if risks:
                    logger.warning(f"检测到 {len(risks)} 个碰撞风险")
                    # 这里可以添加风险处理逻辑
                
                # 检查是否有新的就绪任务
                new_ready_tasks = self.task_dependency_graph.get_ready_tasks()
                if new_ready_tasks:
                    # 分配并执行新的就绪任务
                    new_allocation = {}
                    for task in new_ready_tasks:
                        if task.assigned_robot:
                            continue
                        # 简化：使用动态工作负载分配
                        robot_name = self._allocate_by_dynamic_workload(task)
                        if robot_name:
                            task.assigned_robot = robot_name
                            if robot_name not in new_allocation:
                                new_allocation[robot_name] = []
                            new_allocation[robot_name].append(task)
                    
                    if new_allocation:
                        self.execute_allocated_tasks(new_allocation)
                
            except Exception as e:
                logger.error(f"监控循环异常: {str(e)}")
            
            # 等待下一次监控
            self._stop_monitoring.wait(interval)
    
    def _check_task_progress(self) -> None:
        """
        检查任务进度
        """
        current_time = time.time()
        
        for task in self.tasks:
            if isinstance(task, AdvancedCollaborationTask) and \
               task.start_time and task.end_time is None:
                # 估算进度
                elapsed = current_time - task.start_time
                if task.estimated_duration > 0:
                    estimated_progress = min(elapsed / task.estimated_duration * 100, 100)
                    task.update_progress(estimated_progress)
    
    def get_advanced_system_status(self) -> Dict:
        """
        获取高级系统状态
        
        Returns:
            Dict: 系统状态信息
        """
        # 获取基础状态
        basic_status = super().get_system_status()
        
        # 添加高级信息
        advanced_status = {
            "resource_status": self.resource_manager.get_resource_usage_statistics(),
            "task_dependency_status": {
                "total_tasks": len(self.task_dependency_graph.tasks),
                "ready_tasks": len(self.task_dependency_graph.get_ready_tasks()),
                "has_cycles": self.task_dependency_graph.check_cycles()
            },
            "collaboration_pattern": self.collaboration_pattern.value,
            "advanced_allocation_strategy": self.advanced_strategy.value,
            "continuous_monitoring_active": self.continuous_monitoring
        }
        
        return {**basic_status, **advanced_status}


# 全局高级协调器实例
_global_advanced_coordinator = None


def get_advanced_coordinator() -> AdvancedMultiRobotCoordinator:
    """
    获取全局高级协调器实例
    
    Returns:
        AdvancedMultiRobotCoordinator: 高级协调器实例
    """
    global _global_advanced_coordinator
    
    if _global_advanced_coordinator is None:
        _global_advanced_coordinator = AdvancedMultiRobotCoordinator()
    
    return _global_advanced_coordinator


def reset_advanced_coordinator() -> None:
    """
    重置全局高级协调器实例
    """
    global _global_advanced_coordinator
    _global_advanced_coordinator = None


if __name__ == '__main__':
    # 示例使用
    coordinator = AdvancedMultiRobotCoordinator(
        advanced_strategy=AdvancedTaskAllocationStrategy.HYBRID_OPTIMIZATION
    )
    
    # 添加机器人
    coordinator.add_robot('robot1', '192.168.1.101', RobotRole.LEADER)
    coordinator.add_robot('robot2', '192.168.1.102', RobotRole.FOLLOWER)
    coordinator.add_robot('robot3', '192.168.1.103', RobotRole.WORKER)
    
    # 注册机器人技能
    coordinator.register_robot_skills('robot1', {
        'precision_assembly': 90,
        'welding': 70,
        'material_handling': 85
    })
    
    coordinator.register_robot_skills('robot2', {
        'precision_assembly': 75,
        'welding': 95,
        'material_handling': 60
    })
    
    coordinator.register_robot_skills('robot3', {
        'precision_assembly': 60,
        'welding': 65,
        'material_handling': 90
    })
    
    # 添加资源
    workspace1 = Resource('workspace1', ResourceType.WORKSPACE, 
                         location=[0.3, 0.2, 0.5], 
                         description='装配工作台1')
    workspace2 = Resource('workspace2', ResourceType.WORKSPACE, 
                         location=[0.5, 0.4, 0.3], 
                         description='装配工作台2')
    gripper = Resource('gripper1', ResourceType.GRIPPER, 
                      description='通用夹具')
    
    coordinator.resource_manager.add_resource(workspace1)
    coordinator.resource_manager.add_resource(workspace2)
    coordinator.resource_manager.add_resource(gripper)
    
    # 创建高级任务
    task1 = AdvancedCollaborationTask(
        'task1',
        '精密装配任务',
        priority=90,
        required_resources=['workspace1', 'gripper1'],
        estimated_duration=120,
        skill_requirements={'precision_assembly': 80}
    )
    
    task2 = AdvancedCollaborationTask(
        'task2',
        '焊接任务',
        priority=80,
        required_resources=['workspace2'],
        estimated_duration=180,
        skill_requirements={'welding': 85}
    )
    
    task3 = AdvancedCollaborationTask(
        'task3',
        '材料搬运任务',
        priority=70,
        estimated_duration=60,
        skill_requirements={'material_handling': 75}
    )
    
    # 添加任务依赖
    task3.dependencies = ['task1', 'task2']
    
    # 添加任务
    coordinator.add_advanced_task(task1)
    coordinator.add_advanced_task(task2)
    coordinator.add_advanced_task(task3)
    
    # 设置协作模式
    coordinator.collaboration_pattern = CollaborationPattern.ADAPTIVE
    
    # 开始持续监控
    coordinator.start_continuous_monitoring(interval=2.0)
    
    try:
        print("高级多机器人协调器示例运行中...")
        print("按Ctrl+C停止...")
        
        # 主循环
        while True:
            # 定期打印系统状态
            status = coordinator.get_advanced_system_status()
            print(f"系统状态: {status['coordination_state']}")
            print(f"就绪任务数: {status['task_dependency_status']['ready_tasks']}")
            print(f"资源使用: {status['resource_status']}")
            print("-" * 50)
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("示例已停止")
    finally:
        # 停止监控
        coordinator.stop_continuous_monitoring()
        
        # 断开所有机器人连接
        coordinator.disconnect_all_robots()
