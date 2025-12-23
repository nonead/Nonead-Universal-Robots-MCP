# Universal Robots MCP 扩展功能文档

本文档介绍了 Nonead-Universal-Robots-MCP 项目的扩展功能模块，包括多机器人协同工作、高级轨迹规划、数据记录和分析功能。

## 目录

1. [高级多机器人协调器](#高级多机器人协调器)
2. [高级轨迹规划器](#高级轨迹规划器)
3. [高级数据记录器](#高级数据记录器)
4. [高级数据分析器](#高级数据分析器)
5. [API 参考](#api-参考)
6. [使用示例](#使用示例)

## 高级多机器人协调器

高级多机器人协调器 (`AdvancedMultiRobotCoordinator`) 提供了灵活的多机器人协同工作支持，包括资源管理、任务依赖管理和多种协作模式。

### 主要功能

- **多种协作模式**：支持顺序、并行、同步和分层等多种协作模式
- **资源管理**：避免资源冲突，协调多机器人共享工作空间
- **任务依赖图**：支持复杂的任务依赖关系，确保任务按正确顺序执行
- **动态任务分配**：基于工作负载、技能匹配和空间分区进行任务分配

### 协作模式

| 协作模式 | 描述 | 使用场景 |
|---------|------|--------|
| `SEQUENTIAL` | 顺序执行任务，一个机器人完成后下一个继续 | 任务有严格顺序要求 |
| `PARALLEL` | 并行执行任务，所有机器人同时工作 | 任务相互独立，需要提高效率 |
| `SYNCHRONOUS` | 同步执行任务，机器人动作协调一致 | 高精度协作任务，如搬运大型物体 |
| `HIERARCHICAL` | 分层执行任务，主机器人控制从机器人 | 复杂装配任务，需要中央控制 |
| `SWARM_INTELLIGENCE` | 群体智能协作，基于局部规则 | 未知环境探索或灵活响应 |
| `ADAPTIVE` | 自适应协作，根据环境动态调整 | 复杂多变的工作场景 |

## 高级轨迹规划器

高级轨迹规划器 (`AdvancedTrajectoryPlanner`) 提供了复杂路径生成和优化功能，包括贝塞尔曲线、螺旋线、能耗优化和碰撞避免等。

### 主要功能

- **复杂路径生成**：支持贝塞尔曲线、螺旋线等高级路径生成
- **轨迹优化**：支持时间、能耗和平滑度优化
- **碰撞避免**：动态障碍物检测和规避
- **自适应速度规划**：根据路径复杂度和机器人动力学特性调整速度

### 路径生成类型

| 路径类型 | 描述 | 参数 |
|---------|------|------|
| 贝塞尔曲线 | 平滑的曲线，通过控制点定义 | 控制点列表、点数 |
| 螺旋线 | 螺旋形状路径 | 起点、终点、螺距、圈数 |
| 样条曲线 | 分段多项式曲线 | 控制点、连续性要求 |
| 最优路径 | 考虑机器人动力学的最优路径 | 起点、终点、约束条件 |

## 高级数据记录器

高级数据记录器 (`AdvancedDataRecorder`) 提供了全面的机器人运行数据捕获和存储功能，支持多种数据类型和存储格式。

### 主要功能

- **多种数据类型**：支持机器人状态、关节数据、TCP数据、错误数据等
- **多格式存储**：支持JSON、CSV、SQLite和Pickle等存储格式
- **轮转策略**：支持基于文件大小和时间的轮转策略
- **优先级管理**：重要数据优先记录和存储

### 记录类型

| 记录类型 | 描述 | 包含信息 |
|---------|------|--------|
| `ROBOT_STATE` | 机器人状态 | 运行模式、程序状态、安全模式等 |
| `JOINT_DATA` | 关节数据 | 关节位置、速度、力矩等 |
| `TCP_DATA` | TCP数据 | TCP位置、速度、力等 |
| `ERROR_DATA` | 错误数据 | 错误码、警告信息等 |

## 高级数据分析器

高级数据分析器 (`AdvancedDataAnalyzer`) 提供了强大的数据分析和可视化功能，支持统计分析、趋势检测、异常识别和性能评估等。

### 主要功能

- **统计分析**：提供均值、标准差、最大值、最小值等统计指标
- **趋势检测**：识别数据趋势和周期性模式
- **异常识别**：检测异常行为和潜在故障
- **性能评估**：评估机器人性能和效率
- **可视化**：支持多种图表类型的数据可视化

### 分析类型

| 分析类型 | 描述 | 输出 |
|---------|------|------|
| `STATISTICAL` | 统计分析 | 均值、标准差、最大值、最小值等 |
| `TREND` | 趋势分析 | 趋势线、斜率、截距等 |
| `ANOMALY` | 异常检测 | 异常点、严重程度、可能原因 |
| `PERFORMANCE` | 性能评估 | 循环时间、能耗、精度等 |

## API 参考

### 高级多机器人协调器 API

#### 初始化与配置

```python
from URBasic.advanced_multi_robot_coordinator import AdvancedMultiRobotCoordinator, CollaborationMode

# 创建协调器实例
coordinator = AdvancedMultiRobotCoordinator()

# 注册机器人
coordinator.register_robot(robot_id)

# 设置协作模式
coordinator.set_collaboration_mode(CollaborationMode.PARALLEL)
```

#### 任务管理

```python
# 创建协作任务
task_id = coordinator.create_collaboration_task(
    task_name="装配任务",
    robot_assignments={
        "robot1": {"operation": "move", "params": {"x": 0.1, "y": 0.2, "z": 0.3}},
        "robot2": {"operation": "pick", "params": {"target": "partA"}}
    },
    dependencies=[{"from": "task1", "to": "task2"}]
)

# 执行任务
result = coordinator.execute_task(task_id)

# 获取任务状态
status = coordinator.get_task_status(task_id)
```

### 高级轨迹规划器 API

#### 路径生成

```python
from URBasic.advanced_trajectory_planner import AdvancedTrajectoryPlanner

# 创建轨迹规划器实例
planner = AdvancedTrajectoryPlanner()

# 生成贝塞尔曲线
control_points = [
    [0.0, 0.0, 0.5, 0.0, 0.0, 0.0],
    [0.1, 0.1, 0.5, 0.0, 0.0, 0.0],
    [0.2, 0.0, 0.5, 0.0, 0.0, 0.0]
]
path = planner.generate_bezier_curve(control_points, num_points=50)

# 生成螺旋线
helix_path = planner.generate_helix(
    start_point=[0.1, 0.1, 0.1, 0.0, 0.0, 0.0],
    end_point=[0.1, 0.1, 0.5, 0.0, 0.0, 0.0],
    radius=0.1,
    turns=3,
    num_points=100
)
```

#### 轨迹优化

```python
# 优化轨迹
waypoints = [
    [0.0, 0.0, 0.5, 0.0, 0.0, 0.0],
    [0.1, 0.1, 0.5, 0.0, 0.0, 0.0],
    [0.2, 0.0, 0.5, 0.0, 0.0, 0.0]
]

# 时间优化
optimized_path = planner.optimize_trajectory(
    waypoints=waypoints,
    optimization_type="time"
)

# 能耗优化
energy_optimized = planner.optimize_trajectory(
    waypoints=waypoints,
    optimization_type="energy"
)
```

### 高级数据记录器 API

#### 记录控制

```python
from URBasic.advanced_data_recorder import AdvancedDataRecorder, RecordType

# 创建数据记录器实例
recorder = AdvancedDataRecorder()

# 开始记录
session_id = recorder.start_recording(
    robot_id="robot1",
    record_types=[RecordType.ROBOT_STATE, RecordType.JOINT_DATA],
    duration=60.0  # 记录60秒
)

# 停止记录
recorder.stop_recording(session_id)
```

#### 会话管理

```python
# 获取活跃会话
active_sessions = recorder.get_active_sessions()

# 获取所有已记录的会话
recorded_sessions = recorder.get_recorded_sessions()

# 设置存储路径
recorder.set_storage_path("/path/to/storage")

# 设置存储格式
recorder.set_storage_format("json")
```

### 高级数据分析器 API

#### 数据加载与分析

```python
from URBasic.advanced_data_analyzer import get_data_analyzer, AnalysisType

# 获取数据分析器实例（单例）
analyzer = get_data_analyzer()

# 加载数据
df = analyzer.load_data(
    robot_id="robot1",
    start_time=1620000000.0,
    end_time=1620000600.0
)

# 统计分析
stat_result = analyzer.analyze(df, AnalysisType.STATISTICAL)

# 趋势分析
trend_result = analyzer.analyze(
    df,
    AnalysisType.TREND,
    {'x_column': 'timestamp', 'y_column': 'joint_position_0'}
)
```

#### 报告与可视化

```python
# 生成报告
report = analyzer.generate_report(
    robot_id="robot1",
    start_time=1620000000.0,
    end_time=1620000600.0,
    report_path="/path/to/report.pdf"
)

# 比较多个机器人
comparison = analyzer.compare_robots(
    robot_ids=["robot1", "robot2"],
    metric_columns=["joint_position_0", "tcp_x"],
    start_time=1620000000.0,
    end_time=1620000600.0
)
```

## 使用示例

### 多机器人协同工作示例

```python
# 设置两个机器人协同工作
from URBasic.advanced_multi_robot_coordinator import AdvancedMultiRobotCoordinator, CollaborationMode

# 创建协调器
coordinator = AdvancedMultiRobotCoordinator()

# 注册机器人
coordinator.register_robot("robot1")
coordinator.register_robot("robot2")

# 设置同步协作模式
coordinator.set_collaboration_mode(CollaborationMode.SYNCHRONOUS)

# 创建协同任务
assembly_task = coordinator.create_collaboration_task(
    task_name="装配大型部件",
    robot_assignments={
        "robot1": {
            "operation": "hold",
            "params": {
                "position": {"x": 0.3, "y": 0.1, "z": 0.5},
                "orientation": {"rx": 0.0, "ry": 0.0, "rz": 0.0}
            }
        },
        "robot2": {
            "operation": "attach",
            "params": {
                "target": "partB",
                "position": {"x": 0.35, "y": 0.1, "z": 0.55}
            }
        }
    }
)

# 执行任务
result = coordinator.execute_task(assembly_task)
print(f"任务执行结果: {result}")
```

### 高级轨迹规划示例

```python
# 使用贝塞尔曲线生成复杂路径
from URBasic.advanced_trajectory_planner import AdvancedTrajectoryPlanner

# 创建轨迹规划器
planner = AdvancedTrajectoryPlanner()

# 定义贝塞尔曲线控制点（绕过障碍物）
control_points = [
    [0.1, 0.1, 0.5, 0.0, 0.0, 0.0],   # 起点
    [0.2, 0.3, 0.5, 0.0, 0.0, 0.0],   # 控制点1（绕过障碍物上方）
    [0.3, 0.3, 0.5, 0.0, 0.0, 0.0],   # 控制点2
    [0.4, 0.1, 0.5, 0.0, 0.0, 0.0]    # 终点
]

# 生成路径
path = planner.generate_bezier_curve(
    control_points=control_points,
    num_points=100  # 生成100个路径点
)

# 优化路径（能耗优化）
optimized_path = planner.optimize_trajectory(
    waypoints=path,
    optimization_type="energy"
)

# 输出路径信息
print(f"生成了{len(optimized_path)}个路径点")
print(f"起点: {optimized_path[0]}")
print(f"终点: {optimized_path[-1]}")
```

### 数据记录和分析示例

```python
# 记录机器人数据并进行分析
from URBasic.advanced_data_recorder import AdvancedDataRecorder, RecordType
from URBasic.advanced_data_analyzer import get_data_analyzer, AnalysisType
import time

# 创建记录器
recorder = AdvancedDataRecorder()

# 开始记录（记录30秒）
session_id = recorder.start_recording(
    robot_id="robot1",
    record_types=[
        RecordType.ROBOT_STATE,
        RecordType.JOINT_DATA,
        RecordType.TCP_DATA
    ],
    duration=30.0
)

print(f"数据记录已启动，会话ID: {session_id}")

# 等待记录完成
time.sleep(35)  # 等待35秒确保记录完成

# 获取数据分析器
analyzer = get_data_analyzer()

# 加载数据
print("加载记录的数据...")
df = analyzer.load_data(robot_id="robot1")

print(f"数据加载完成，共{len(df)}条记录")

# 执行统计分析
print("执行统计分析...")
stat_result = analyzer.analyze(df, AnalysisType.STATISTICAL)

# 显示结果
print("\n统计分析结果:")
for column, stats in stat_result.items():
    if column.startswith("joint_position_"):
        print(f"关节{column[-1]}:")
        print(f"  均值: {stats['mean']:.4f}")
        print(f"  标准差: {stats['std']:.4f}")
        print(f"  最小值: {stats['min']:.4f}")
        print(f"  最大值: {stats['max']:.4f}")

# 生成报告
print("\n生成运行报告...")
report = analyzer.generate_report(
    robot_id="robot1",
    report_path="robot_performance_report.pdf"
)

print(f"报告已生成: {report['path']}")
```

## 注意事项

1. **依赖安装**：确保安装了所有必要的依赖包，特别是numpy、pandas、matplotlib和scikit-learn

2. **数据存储**：长时间运行时注意磁盘空间，建议定期清理或归档旧数据

3. **性能优化**：对于大量数据的分析，考虑使用数据采样或分段分析以提高性能

4. **安全考虑**：在实际生产环境中，确保多机器人协作时的安全防护措施到位

## 故障排除

1. **多机器人协调器错误**：检查机器人连接状态和网络通信

2. **轨迹规划失败**：检查路径点是否有效，机器人是否能够到达这些点

3. **数据记录问题**：检查存储权限和磁盘空间

4. **分析结果异常**：验证数据质量，可能需要清洗或过滤异常数据

如有其他问题或需要进一步的帮助，请参考项目文档或联系开发团队。
