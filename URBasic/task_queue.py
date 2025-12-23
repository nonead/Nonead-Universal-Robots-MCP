#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
任务队列和优先级管理模块

此模块提供任务队列管理功能，支持：
- 任务优先级排序
- 任务状态管理
- 任务执行控制
- 任务依赖关系处理
- 并行任务执行
"""

import queue
import threading
import time
import uuid
import logging
from enum import Enum, IntEnum
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('task_queue')

class TaskPriority(IntEnum):
    """
    任务优先级枚举
    """
    LOW = 10
    MEDIUM = 5
    HIGH = 3
    URGENT = 1

class TaskStatus(Enum):
    """
    任务状态枚举
    """
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskType(Enum):
    """
    任务类型枚举
    """
    MOTION = "MOTION"
    FORCE_CONTROL = "FORCE_CONTROL"
    SCRIPT_EXECUTION = "SCRIPT_EXECUTION"
    DATA_COLLECTION = "DATA_COLLECTION"
    SYSTEM = "SYSTEM"
    CUSTOM = "CUSTOM"

class Task:
    """
    任务基类
    """
    
    def __init__(self, task_type=TaskType.CUSTOM, priority=TaskPriority.MEDIUM,
                 name=None, description=None, robot_id=None, dependencies=None):
        """
        初始化任务
        
        Args:
            task_type: 任务类型
            priority: 任务优先级
            name: 任务名称
            description: 任务描述
            robot_id: 机器人ID
            dependencies: 依赖的任务ID列表
        """
        self.task_id = str(uuid.uuid4())
        self.task_type = task_type
        self.priority = priority
        self.name = name or f"{task_type.value}_Task_{self.task_id[:8]}"
        self.description = description or ""
        self.robot_id = robot_id
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.progress = 0.0
        self.metadata = {}
    
    def __lt__(self, other):
        """
        用于优先级队列排序
        
        Args:
            other: 另一个任务
            
        Returns:
            bool: 当前任务优先级是否更高
        """
        return self.priority < other.priority
    
    def start(self):
        """
        开始执行任务
        """
        self.status = TaskStatus.RUNNING
        self.started_at = time.time()
        logger.info(f"任务开始执行: {self.name} ({self.task_id})")
    
    def pause(self):
        """
        暂停任务
        """
        self.status = TaskStatus.PAUSED
        logger.info(f"任务已暂停: {self.name} ({self.task_id})")
    
    def resume(self):
        """
        恢复任务
        """
        self.status = TaskStatus.RUNNING
        logger.info(f"任务已恢复: {self.name} ({self.task_id})")
    
    def complete(self, result=None):
        """
        完成任务
        
        Args:
            result: 任务结果
        """
        self.status = TaskStatus.COMPLETED
        self.completed_at = time.time()
        self.result = result
        self.progress = 100.0
        logger.info(f"任务已完成: {self.name} ({self.task_id})")
    
    def fail(self, error):
        """
        任务失败
        
        Args:
            error: 错误信息
        """
        self.status = TaskStatus.FAILED
        self.completed_at = time.time()
        self.error = str(error)
        logger.error(f"任务执行失败: {self.name} ({self.task_id}) - {error}")
    
    def cancel(self):
        """
        取消任务
        """
        self.status = TaskStatus.CANCELLED
        logger.info(f"任务已取消: {self.name} ({self.task_id})")
    
    def update_progress(self, progress):
        """
        更新任务进度
        
        Args:
            progress: 进度值 (0-100)
        """
        self.progress = max(0.0, min(100.0, progress))
        logger.debug(f"任务进度更新: {self.name} ({self.task_id}) - {progress}%")
    
    def to_dict(self):
        """
        将任务信息转换为字典
        
        Returns:
            dict: 任务信息字典
        """
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "name": self.name,
            "description": self.description,
            "robot_id": self.robot_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "progress": self.progress,
            "dependencies": self.dependencies,
            "metadata": self.metadata
        }

class MotionTask(Task):
    """
    运动任务类
    """
    
    def __init__(self, motion_type, target_pose, speed=0.1, acceleration=0.1,
                 priority=TaskPriority.MEDIUM, name=None, robot_id=None):
        """
        初始化运动任务
        
        Args:
            motion_type: 运动类型 ('movej', 'movel', 'circular'等)
            target_pose: 目标位姿
            speed: 运动速度
            acceleration: 加速度
            priority: 任务优先级
            name: 任务名称
            robot_id: 机器人ID
        """
        super().__init__(TaskType.MOTION, priority, name, f"{motion_type} motion to target", robot_id)
        self.motion_type = motion_type
        self.target_pose = target_pose
        self.speed = speed
        self.acceleration = acceleration
        self.metadata.update({
            "motion_type": motion_type,
            "target_pose": target_pose,
            "speed": speed,
            "acceleration": acceleration
        })

class ForceControlTask(Task):
    """
    力控制任务类
    """
    
    def __init__(self, control_type, force_values, duration=None,
                 priority=TaskPriority.HIGH, name=None, robot_id=None):
        """
        初始化力控制任务
        
        Args:
            control_type: 控制类型 ('constant', 'impedance', 'guided'等)
            force_values: 力值设置
            duration: 持续时间
            priority: 任务优先级
            name: 任务名称
            robot_id: 机器人ID
        """
        super().__init__(TaskType.FORCE_CONTROL, priority, name, f"{control_type} force control", robot_id)
        self.control_type = control_type
        self.force_values = force_values
        self.duration = duration
        self.metadata.update({
            "control_type": control_type,
            "force_values": force_values,
            "duration": duration
        })

class ScriptExecutionTask(Task):
    """
    脚本执行任务类
    """
    
    def __init__(self, script_path, script_args=None,
                 priority=TaskPriority.MEDIUM, name=None, robot_id=None):
        """
        初始化脚本执行任务
        
        Args:
            script_path: 脚本路径
            script_args: 脚本参数
            priority: 任务优先级
            name: 任务名称
            robot_id: 机器人ID
        """
        super().__init__(TaskType.SCRIPT_EXECUTION, priority, name, f"Execute script {script_path}", robot_id)
        self.script_path = script_path
        self.script_args = script_args or {}
        self.metadata.update({
            "script_path": script_path,
            "script_args": script_args
        })

class TaskQueueManager:
    """
    任务队列管理器类
    """
    
    def __init__(self, max_workers=3):
        """
        初始化任务队列管理器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.task_queue = queue.PriorityQueue()
        self.tasks = {}
        self.task_history = []
        self.max_history_size = 1000
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.worker_threads = []
        
        # 启动工作线程
        for i in range(max_workers):
            thread = threading.Thread(target=self._worker_loop, name=f"TaskWorker-{i}")
            thread.daemon = True
            thread.start()
            self.worker_threads.append(thread)
        
        logger.info(f"任务队列管理器已启动，工作线程数: {max_workers}")
    
    def add_task(self, task):
        """
        添加任务到队列
        
        Args:
            task: Task对象
            
        Returns:
            str: 任务ID
        """
        with self.lock:
            # 检查任务ID是否已存在
            if task.task_id in self.tasks:
                logger.warning(f"任务ID已存在: {task.task_id}")
                return task.task_id
            
            # 检查依赖任务
            can_queue = True
            for dep_id in task.dependencies:
                if dep_id not in self.tasks:
                    logger.error(f"依赖任务不存在: {dep_id}")
                    can_queue = False
                    break
                dep_task = self.tasks[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    logger.warning(f"依赖任务未完成: {dep_id} (状态: {dep_task.status.value})")
                    can_queue = False
                    break
            
            # 添加任务到任务字典
            self.tasks[task.task_id] = task
            
            # 如果可以立即排队，则添加到优先级队列
            if can_queue:
                self.task_queue.put(task)
                task.status = TaskStatus.QUEUED
                logger.info(f"任务已添加到队列: {task.name} ({task.task_id})")
            else:
                logger.info(f"任务已添加但等待依赖: {task.name} ({task.task_id})")
            
            return task.task_id
    
    def cancel_task(self, task_id):
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功取消
        """
        with self.lock:
            if task_id not in self.tasks:
                logger.warning(f"任务不存在: {task_id}")
                return False
            
            task = self.tasks[task_id]
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                logger.warning(f"任务状态不允许取消: {task.status.value}")
                return False
            
            # 取消任务
            task.cancel()
            
            # 如果任务在历史中，也更新历史记录
            for hist_task in self.task_history:
                if hist_task.task_id == task_id:
                    hist_task.cancel()
                    break
            
            return True
    
    def pause_task(self, task_id):
        """
        暂停任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功暂停
        """
        with self.lock:
            if task_id not in self.tasks:
                logger.warning(f"任务不存在: {task_id}")
                return False
            
            task = self.tasks[task_id]
            if task.status != TaskStatus.RUNNING:
                logger.warning(f"任务状态不允许暂停: {task.status.value}")
                return False
            
            task.pause()
            return True
    
    def resume_task(self, task_id):
        """
        恢复任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功恢复
        """
        with self.lock:
            if task_id not in self.tasks:
                logger.warning(f"任务不存在: {task_id}")
                return False
            
            task = self.tasks[task_id]
            if task.status != TaskStatus.PAUSED:
                logger.warning(f"任务状态不允许恢复: {task.status.value}")
                return False
            
            task.resume()
            return True
    
    def get_task(self, task_id):
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Task: 任务对象，不存在则返回None
        """
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self):
        """
        获取所有任务
        
        Returns:
            list: 任务列表
        """
        with self.lock:
            return list(self.tasks.values())
    
    def get_active_tasks(self):
        """
        获取活跃任务（非完成、非失败、非取消的任务）
        
        Returns:
            list: 活跃任务列表
        """
        active_tasks = []
        with self.lock:
            for task in self.tasks.values():
                if task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    active_tasks.append(task)
        return active_tasks
    
    def get_task_history(self, limit=100):
        """
        获取任务历史
        
        Args:
            limit: 返回的最大任务数量
            
        Returns:
            list: 历史任务列表
        """
        with self.lock:
            return self.task_history[-limit:]
    
    def _worker_loop(self):
        """
        工作线程循环
        """
        while not self.stop_event.is_set():
            try:
                # 从队列获取任务
                task = self.task_queue.get(timeout=0.5)
                
                # 检查任务状态
                if task.status != TaskStatus.QUEUED:
                    self.task_queue.task_done()
                    continue
                
                # 开始执行任务
                task.start()
                
                # 执行任务
                try:
                    # 这里应该调用实际的任务执行逻辑
                    # 暂时使用模拟执行
                    result = self._execute_task(task)
                    task.complete(result)
                except Exception as e:
                    task.fail(e)
                
                # 任务完成，处理历史记录
                with self.lock:
                    self._add_to_history(task)
                    
                    # 检查是否有等待此任务的其他任务
                    self._check_pending_tasks()
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"工作线程错误: {str(e)}")
    
    def _execute_task(self, task):
        """
        执行任务
        
        Args:
            task: Task对象
            
        Returns:
            any: 任务结果
        """
        # 模拟任务执行
        # 实际应用中，这里应该根据任务类型调用相应的执行逻辑
        
        logger.info(f"执行任务: {task.name} ({task.task_id})")
        
        # 模拟进度更新
        for i in range(10):
            if task.status == TaskStatus.PAUSED:
                # 等待任务恢复
                while task.status == TaskStatus.PAUSED and not self.stop_event.is_set():
                    time.sleep(0.1)
                if self.stop_event.is_set():
                    raise Exception("任务执行被中断")
            
            if task.status == TaskStatus.CANCELLED:
                raise Exception("任务已取消")
            
            progress = (i + 1) * 10
            task.update_progress(progress)
            time.sleep(0.2)  # 模拟执行时间
        
        return {"success": True, "message": f"Task {task.name} completed successfully"}
    
    def _add_to_history(self, task):
        """
        添加任务到历史记录
        
        Args:
            task: Task对象
        """
        # 从活动任务中移除
        if task.task_id in self.tasks:
            del self.tasks[task.task_id]
        
        # 添加到历史记录
        self.task_history.append(task)
        
        # 保持历史记录大小
        if len(self.task_history) > self.max_history_size:
            self.task_history.pop(0)
    
    def _check_pending_tasks(self):
        """
        检查并激活等待依赖的任务
        """
        tasks_to_queue = []
        
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            
            # 检查所有依赖是否已完成
            all_deps_completed = True
            for dep_id in task.dependencies:
                # 检查依赖是否在历史记录中
                dep_completed = False
                for hist_task in self.task_history:
                    if hist_task.task_id == dep_id and hist_task.status == TaskStatus.COMPLETED:
                        dep_completed = True
                        break
                
                if not dep_completed:
                    all_deps_completed = False
                    break
            
            if all_deps_completed:
                tasks_to_queue.append(task)
        
        # 将满足依赖的任务加入队列
        for task in tasks_to_queue:
            self.task_queue.put(task)
            task.status = TaskStatus.QUEUED
            logger.info(f"任务依赖已满足，已加入队列: {task.name} ({task.task_id})")
    
    def shutdown(self, wait=True):
        """
        关闭任务队列管理器
        
        Args:
            wait: 是否等待任务完成
        """
        logger.info("关闭任务队列管理器...")
        
        # 设置停止事件
        self.stop_event.set()
        
        # 关闭线程池
        self.executor.shutdown(wait=wait)
        
        # 等待工作线程结束
        if wait:
            for thread in self.worker_threads:
                thread.join(timeout=5.0)
        
        logger.info("任务队列管理器已关闭")

# 创建全局任务队列管理器实例
global_task_manager = TaskQueueManager()

def create_motion_task(motion_type, target_pose, speed=0.1, acceleration=0.1,
                      priority=TaskPriority.MEDIUM, name=None, robot_id=None):
    """
    创建并添加运动任务的便捷函数
    
    Args:
        motion_type: 运动类型
        target_pose: 目标位姿
        speed: 速度
        acceleration: 加速度
        priority: 优先级
        name: 任务名称
        robot_id: 机器人ID
        
    Returns:
        str: 任务ID
    """
    task = MotionTask(motion_type, target_pose, speed, acceleration, priority, name, robot_id)
    return global_task_manager.add_task(task)

def create_force_control_task(control_type, force_values, duration=None,
                             priority=TaskPriority.HIGH, name=None, robot_id=None):
    """
    创建并添加力控制任务的便捷函数
    
    Args:
        control_type: 控制类型
        force_values: 力值
        duration: 持续时间
        priority: 优先级
        name: 任务名称
        robot_id: 机器人ID
        
    Returns:
        str: 任务ID
    """
    task = ForceControlTask(control_type, force_values, duration, priority, name, robot_id)
    return global_task_manager.add_task(task)

def create_script_task(script_path, script_args=None,
                      priority=TaskPriority.MEDIUM, name=None, robot_id=None):
    """
    创建并添加脚本执行任务的便捷函数
    
    Args:
        script_path: 脚本路径
        script_args: 脚本参数
        priority: 优先级
        name: 任务名称
        robot_id: 机器人ID
        
    Returns:
        str: 任务ID
    """
    task = ScriptExecutionTask(script_path, script_args, priority, name, robot_id)
    return global_task_manager.add_task(task)