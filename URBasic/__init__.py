from __future__ import division

__author__ = "Anthony Zhuang"
__copyright__ = "Copyright 2009-2025"
__license__ = "MIT License"

from URBasic.connectionState import ConnectionState
from URBasic.dashboard import DashBoard
from URBasic.manipulation import *
from URBasic.realTimeClient import RealTimeClient
from URBasic.robotConnector import RobotConnector
from URBasic.robotModel import RobotModel
from URBasic.rtde import RTDE
from URBasic.urScript import UrScript
from URBasic.urScriptExt import UrScriptExt

# 核心功能模块导入
from URBasic.multi_robot_coordinator import (
    MultiRobotCoordinator,
    RobotRole,
    TaskAllocationStrategy,
    CollaborationMode,
    CoordinationState,
    RobotAgent,
    CollaborationTask,
    MotionTask
)
from URBasic.advanced_multi_robot_coordinator import AdvancedMultiRobotCoordinator

# 其他高级功能模块（按需导入，避免不必要的依赖检查）
try:
    from URBasic.error_handling import ErrorHandler, RobotError, ErrorCategory
except ImportError as e:
    print(f"Warning: Failed to import URBasic.error_handling: {e}")

try:
    from URBasic.force_control import ForceController, ForceMonitoring
except ImportError as e:
    print(f"Warning: Failed to import URBasic.force_control: {e}")

try:
    from URBasic.trajectory_planner import TrajectoryPlanner
except ImportError as e:
    print(f"Warning: Failed to import URBasic.trajectory_planner: {e}")

try:
    from URBasic.advanced_trajectory_planner import (
        AdvancedTrajectoryPlanner,
        PathType
    )
except ImportError as e:
    print(f"Warning: Failed to import URBasic.advanced_trajectory_planner: {e}")

try:
    from URBasic.auto_recovery import AutoRecoveryManager
except ImportError as e:
    print(f"Warning: Failed to import URBasic.auto_recovery: {e}")

try:
    from URBasic.operation_history import OperationHistory
except ImportError as e:
    print(f"Warning: Failed to import URBasic.operation_history: {e}")

try:
    from URBasic.status_monitor import RobotStatusMonitor, StatusDashboard
except ImportError as e:
    print(f"Warning: Failed to import URBasic.status_monitor: {e}")

try:
    from URBasic.task_queue import TaskQueueManager, Task, TaskPriority, TaskStatus, TaskType
except ImportError as e:
    print(f"Warning: Failed to import URBasic.task_queue: {e}")

try:
    from URBasic.user_friendly_errors import ErrorLocalization, ErrorExplainer
except ImportError as e:
    print(f"Warning: Failed to import URBasic.user_friendly_errors: {e}")

# 数据分析相关模块（需要额外依赖）
try:
    from URBasic.advanced_data_analyzer import (
        AdvancedDataAnalyzer,
        VisualizationType,
        AnomalyDetectionMethod
    )
except ImportError as e:
    print(f"Warning: Failed to import URBasic.advanced_data_analyzer: {e}")

try:
    from URBasic.advanced_data_recorder import (
        AdvancedDataRecorder,
        DataRecordType,
        StorageFormat,
        RotationStrategy,
        RecordPriority,
        DataRecord,
        RobotStateRecord
    )
except ImportError as e:
    print(f"Warning: Failed to import URBasic.advanced_data_recorder: {e}")

