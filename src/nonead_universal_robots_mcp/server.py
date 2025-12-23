import time

from mcp.server.fastmcp import FastMCP
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import paramiko
import URBasic
from URBasic.advanced_multi_robot_coordinator import AdvancedMultiRobotCoordinator, CollaborationMode
from URBasic.advanced_trajectory_planner import AdvancedTrajectoryPlanner
from URBasic.advanced_data_recorder import AdvancedDataRecorder, DataRecordType
from URBasic.advanced_data_analyzer import get_data_analyzer, AnalysisType

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)
handler = RotatingFileHandler(
    log_dir / "server.log",
    maxBytes=1024 * 1024,  # 1MB
    backupCount=3,  # 保留 3 个旧日志
    encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

mcp = FastMCP(
    "nUR_MCP_SERVER",
    description="Control UR robots through the Model Context Protocol"
)

robot_list = None
robotModle_list = None

# 初始化新功能模块
multi_robot_coordinator = None
advanced_trajectory_planner = None
advanced_data_recorder = None
advanced_data_analyzer = None

# 初始化扩展模块


def initialize_extended_modules():
    """初始化所有扩展模块"""
    global multi_robot_coordinator, advanced_trajectory_planner
    global advanced_data_recorder, advanced_data_analyzer

    try:
        # 初始化多机器人协调器
        multi_robot_coordinator = AdvancedMultiRobotCoordinator()
        logger.info("高级多机器人协调器初始化成功")

        # 初始化高级轨迹规划器
        advanced_trajectory_planner = AdvancedTrajectoryPlanner()
        logger.info("高级轨迹规划器初始化成功")

        # 初始化高级数据记录器
        advanced_data_recorder = AdvancedDataRecorder()
        logger.info("高级数据记录器初始化成功")

        # 获取数据分析器实例（单例）
        advanced_data_analyzer = get_data_analyzer()
        logger.info("高级数据分析器初始化成功")

        return True
    except Exception as e:
        logger.error(f"初始化扩展模块失败: {str(e)}")
        return False


def set_robot_list():
    global robot_list, robotModle_list
    robot_list = dict()
    robotModle_list = dict()


def link_check(ip):
    """检查连接状态，若连接断开或不存在，则建立连接"""
    if robot_list.get(ip, "unknown") == "unknown" or not robot_list[
        ip].robotConnector.RTDE.isRunning():
        return connect_ur(ip)
    return '连接成功'


def return_msg(txt: str):
    return json.dumps(txt, indent=2, ensure_ascii=False)


def right_pose_joint(current_pose, q):
    """关节的弧度验证，允许0.1的误差,按角度计算大约5度"""
    if q[0] + 0.1 >= current_pose[0] >= q[0] - 0.1:
        if q[1] + 0.1 >= current_pose[1] >= q[1] - 0.1:
            if q[2] + 0.1 >= current_pose[2] >= q[2] - 0.1:
                if q[3] + 0.1 >= current_pose[3] >= q[3] - 0.1:
                    if q[4] + 0.1 >= current_pose[4] >= q[4] - 0.1:
                        if q[5] + 0.1 >= current_pose[5] >= q[5] - 0.1:
                            return True
    return False


def round_pose(pose):
    """给坐标取近似值，精确到三位小数"""
    pose[0] = round(pose[0], 3)
    pose[1] = round(pose[1], 3)
    pose[2] = round(pose[2], 3)
    pose[3] = round(pose[3], 3)
    pose[4] = round(pose[4], 3)
    pose[5] = round(pose[5], 3)
    return pose


def movejConfirm(ip, q):
    """
    movej移动的结果确认
    1：移动到位
    2：移动结束，但是位置不准确
    """
    loop_flg = True
    count = 0
    while loop_flg:
        time.sleep(1)
        current_pose = round_pose(robot_list[ip].get_actual_joint_positions())
        if right_pose_joint(current_pose, q):
            robot_list[ip].robotConnector.DashboardClient.ur_running()
            running = robot_list[ip].robotConnector.DashboardClient.last_respond
            if running == 'Program running: false':
                return 1
        else:
            robot_list[ip].robotConnector.DashboardClient.ur_running()
            running = robot_list[ip].robotConnector.DashboardClient.last_respond

            if running == 'Program running: true':
                # 尚未移动完成
                continue
            else:
                # 移动完成
                count = count + 1
                if count > 5:
                    return 2


def right_pose_tcp(current_pose_1, pose):
    """tcp位置是否一致的校验，这里允许10mm的误差"""
    if pose[0] + 0.010 >= current_pose_1[0] >= pose[0] - 0.010:
        if pose[1] + 0.010 >= current_pose_1[1] >= pose[1] - 0.010:
            if pose[2] + 0.010 >= current_pose_1[2] >= pose[2] - 0.010:
                return True

    return False


def movelConfirm(ip, pose):
    """
    movel移动的结果确认
    1：移动到位
    2：移动结束，但是位置不准确
    """
    loop_flg = True
    count = 0
    while loop_flg:
        time.sleep(1)
        current_pose = round_pose(robot_list[ip].get_actual_tcp_pose())
        if right_pose_tcp(current_pose, pose):
            robot_list[ip].robotConnector.DashboardClient.ur_running()
            running = robot_list[ip].robotConnector.DashboardClient.last_respond
            if running == 'Program running: false':
                return 1
        else:
            robot_list[ip].robotConnector.DashboardClient.ur_running()
            running = robot_list[ip].robotConnector.DashboardClient.last_respond

            if running == 'Program running: true':
                '''尚未移动完成'''
                continue
            else:
                '''移动完成'''
                count = count + 1
                if count > 5:
                    return 2


@mcp.tool()
def connect_ur(ip: str):
    """根据用户提供的IP连接UR
    IP：机器人地址"""
    try:
        host = ip
        global robot_list, robotModle_list

        if robot_list.get(ip, "unknown") != "unknown":
            robot_list[ip].robotConnector.close()
            return return_msg(f"优傲机器人连接失败: {ip}")

        robotModle = URBasic.robotModel.RobotModel()
        robot = URBasic.urScriptExt.UrScriptExt(host=host, robotModel=robotModle)
        robot_list[ip] = robot
        robotModle_list[ip] = robotModle

        if robot_list.get(ip, "unknown") == "unknown" or not robot_list[
            ip].robotConnector.RTDE.isRunning():
            return return_msg(f"优傲机器人连接失败: {ip}")

        logger.info(f"连接成功。IP:{host}")
        return return_msg(f"连接成功。IP:{host}")
    except Exception as e:
        logger.error(f"优傲机器人连接失败: {str(e)}")
        return return_msg(f"优傲机器人连接失败: {str(e)}")


@mcp.tool()
def disconnect_ur(ip: str):
    """根据用户提供的IP，断开与UR机器人的连接
    IP：机器人地址"""
    try:
        if robot_list.get(ip, "unknown") == "unknown":
            return return_msg("连接不存在")
        robot_list[ip].close()
        logger.info(f"连接已断开。IP:{ip}")
        return return_msg("连接已断开。")
    except Exception as e:
        logger.error(f"连接断开失败: {str(e)}")
        return return_msg(f"连接断开失败: {str(e)}")


@mcp.tool()
def get_serial_number(ip: str):
    """获取指定IP机器人的序列号
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        robot_list[ip].robotConnector.DashboardClient.ur_serial_number()
        logger.info(f"IP为{ip}的优傲机器人的序列号为： {robot_list[ip].robotConnector.DashboardClient.last_respond}")
        return return_msg(
            f"IP为{ip}的优傲机器人的序列号为： {robot_list[ip].robotConnector.DashboardClient.last_respond}")
    except Exception as e:
        logger.error(f"获取序列号失败: {str(e)}")
        return return_msg(f"获取序列号失败: {str(e)}")


@mcp.tool()
def get_time(ip: str) -> str:
    """根据用户提供的IP，获取指定机器人的开机时长(秒)
    IP：机器人地址"""
    try:
        if '连接成功' not in link_check(ip):
            return return_msg(f"与机器人的连接已断开。IP:{ip}")
        logger.info(f"{robotModle_list[ip].RobotTimestamp():.2f}")
        return return_msg(f"{robotModle_list[ip].RobotTimestamp():.2f}")
    except Exception as e:
        logger.error(f"获取开机时长失败: {str(e)}")
        return return_msg(f"获取开机时长失败: {str(e)}")


@mcp.tool()
def get_ur_software_version(ip: str):
    """根据用户提供的IP，获取指定机器人的软件版本
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        robot_list[ip].robotConnector.DashboardClient.ur_polyscopeVersion()
        result = robot_list[ip].robotConnector.DashboardClient.last_respond
        logger.info(f"IP为{ip}的优傲机器人的软件版本是{result}")
        return return_msg(f"IP为{ip}的优傲机器人的软件版本是{result}")
    except Exception as e:
        logger.error(f"软件版本获取失败: {str(e)}")
        return return_msg(f"软件版本获取失败: {str(e)}")


@mcp.tool()
def get_robot_model(ip: str):
    """获取指定IP的机器人型号
    IP：机器人地址"""
    try:
        robot_list[ip].robotConnector.DashboardClient.ur_get_robot_model()
        model = robot_list[ip].robotConnector.DashboardClient.last_respond
        robot_list[ip].robotConnector.DashboardClient.ur_is_remote_control()
        e = robot_list[ip].robotConnector.DashboardClient.last_respond.lower()
        if e == 'true' or e == 'false':
            model = f"{model}e"
        logger.info(f"{model}e")
        return return_msg(model)
    except Exception as e:
        logger.error(f"获取机器人型号失败: {str(e)}")
        return return_msg(f"获取机器人型号失败: {str(e)}")


@mcp.tool()
def get_safety_mode(ip: str):
    """获取指定IP机器人的安全模式
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        robot_list[ip].robotConnector.DashboardClient.ur_safetymode()
        result = robot_list[ip].robotConnector.DashboardClient.last_respond
        logger.info(f"IP为{ip}的优傲机器人的安全模式是{result}")
        return return_msg(f"IP为{ip}的优傲机器人的安全模式是{result}")
    except Exception as e:
        logger.error(f"安全模式获取失败: {str(e)}")
        return return_msg(f"安全模式获取失败: {str(e)}")


@mcp.tool()
def get_robot_mode(ip: str):
    """获取指定IP机器人的运行状态
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        robot_list[ip].robotConnector.DashboardClient.ur_robotmode()
        logger.info(f"IP为{ip}的优傲机器人的运行状态为： {robot_list[ip].robotConnector.DashboardClient.last_respond}")
        return return_msg(
            f"IP为{ip}的优傲机器人的运行状态为： {robot_list[ip].robotConnector.DashboardClient.last_respond}")
    except Exception as e:
        logger.error(f"运行状态获取失败: {str(e)}")
        return return_msg(f"运行状态获取失败: {str(e)}")


@mcp.tool()
def get_program_state(ip: str):
    """获取指定IP机器人的程序执行状态
        IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")

        robot_list[ip].robotConnector.DashboardClient.ur_get_loaded_program()
        prog_name = robot_list[ip].robotConnector.DashboardClient.last_respond
        robot_list[ip].robotConnector.DashboardClient.ur_programState()
        prog_state = robot_list[ip].robotConnector.DashboardClient.last_respond
        robot_list[ip].robotConnector.DashboardClient.ur_isProgramSaved()
        flg = robot_list[ip].robotConnector.DashboardClient.last_respond
        robot_list[ip].robotConnector.DashboardClient.ur_running()
        running = robot_list[ip].robotConnector.DashboardClient.last_respond

        prog_saved = ''
        prog_running = ''
        if flg.startswith("false"):
            prog_saved = '程序未保存，请及时保存或备份正在编辑的程序。'
        if running == 'Program running: true':
            prog_running = '机械臂正在动作。'
        logger.info(
            f"IP为{ip}的优傲机器人当前加载的程序是：{prog_name}，程序的执行状态是：{prog_state}。{prog_saved}。{prog_running}")
        return return_msg(
            f"IP为{ip}的优傲机器人当前加载的程序是：{prog_name}，程序的执行状态是：{prog_state}。{prog_saved}。{prog_running}")
    except Exception as e:
        logger.error(f"程序的执行状态获取失败: {str(e)}")
        return return_msg(f"程序的执行状态获取失败: {str(e)}")


@mcp.tool()
def get_actual_tcp_pose(ip: str):
    """获取指定IP机器人的当前TCP位置
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        logger.info(f"当前TCP位置： {robot_list[ip].get_actual_tcp_pose()}")
        return return_msg(f"当前TCP位置： {robot_list[ip].get_actual_tcp_pose()}")
    except Exception as e:
        logger.error(f"TCP位置获取失败: {str(e)}")
        return return_msg(f"TCP位置获取失败: {str(e)}")


@mcp.tool()
def get_actual_joint_pose(ip: str):
    """获取指定IP机器人的当前关节角度
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        logger.info(f"当前关节姿态 {robot_list[ip].get_actual_joint_positions()}")
        return return_msg(f"当前关节姿态 {robot_list[ip].get_actual_joint_positions()}")
    except Exception as e:
        logger.error(f"TCP位置获取失败: {str(e)}")
        return return_msg(f"TCP位置获取失败: {str(e)}")


@mcp.tool()
def get_output_int_register(ip: str, index: int):
    """获取指定IP机器人Int寄存器的值,
    IP：机器人地址
    index：寄存器下标，范围是[0，23]"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        logger.info(f"{robotModle_list[ip].OutputIntRegister(index)}")
        return return_msg(f"Int寄存器{index}={robotModle_list[ip].OutputIntRegister(index)}")
    except Exception as e:
        logger.error(f"Int寄存器的值获取失败: {str(e)}")
        return return_msg(f"Int寄存器的值获取失败: {str(e)}")


@mcp.tool()
def get_output_double_register(ip: str, index: int):
    """获取指定IP机器人Double寄存器的值,
    IP：机器人地址
    index：寄存器下标，范围是[0，23]"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        logger.info(f"Double寄存器{index}={robotModle_list[ip].OutputDoubleRegister(index)}")
        return return_msg(f"{robotModle_list[ip].OutputDoubleRegister(index)}")
    except Exception as e:
        logger.error(f"Double寄存器的值获取失败: {str(e)}")
        return return_msg(f"Double寄存器的值获取失败: {str(e)}")


@mcp.tool()
def get_output_bit_register(ip: str, index: int):
    """获取指定IP机器人Bool寄存器的值,
    IP：机器人地址
    index：寄存器下标，范围是[0，23]"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        bits = robotModle_list[ip].OutputBitRegister()
        logger.info(f"Bool寄存器{index}={bits[index]}")
        return return_msg(f"{bits[index]}")
    except Exception as e:
        logger.error(f"Bool寄存器的值获取失败: {str(e)}")
        return return_msg(f"Bool寄存器的值获取失败: {str(e)}")


@mcp.tool()
def get_actual_robot_voltage(ip: str):
    """获取指定IP机器人的电压（伏特）
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        logger.info(f"{robotModle_list[ip].ActualRobotVoltage()}（伏特）")
        return return_msg(f"{robotModle_list[ip].ActualRobotVoltage()}（伏特）")
    except Exception as e:
        logger.error(f"机器人的电压获取失败: {str(e)}")
        return return_msg(f"机器人的电压获取失败: {str(e)}")


@mcp.tool()
def get_actual_robot_current(ip: str):
    """获取指定IP机器人的电流（安培）
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        logger.info(f"{robotModle_list[ip].ActualRobotCurrent()}（安培）")
        return return_msg(f"{robotModle_list[ip].ActualRobotCurrent()}（安培）")
    except Exception as e:
        logger.error(f"机器人的电流获取失败: {str(e)}")
        return return_msg(f"机器人的电流获取失败: {str(e)}")


@mcp.tool()
def get_actual_joint_voltage(ip: str):
    """获取指定IP机器人的各关节电压（伏特）
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        logger.info(f"{robotModle_list[ip].ActualJointVoltage()}（伏特）")
        return return_msg(f"{robotModle_list[ip].ActualJointVoltage()}（伏特）")
    except Exception as e:
        logger.error(f"机器人的关节电压获取失败: {str(e)}")
        return return_msg(f"机器人的关节电压获取失败: {str(e)}")


@mcp.tool()
def get_actual_joint_current(ip: str):
    """获取指定IP机器人各关节的电流（安培）
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        logger.info(f"{robotModle_list[ip].ActualJointVoltage()}（安培）")
        return return_msg(f"{robotModle_list[ip].ActualJointVoltage()}（安培）")
    except Exception as e:
        logger.error(f"机器人各关节的电流获取失败: {str(e)}")
        return return_msg(f"机器人各关节的电流获取失败: {str(e)}")


@mcp.tool()
def get_joint_temperatures(ip: str):
    """获取指定IP机器人各关节的温度（摄氏度）。
    IP：机器人地址"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        logger.info(f"{robotModle_list[ip].JointTemperatures()}（摄氏度）")
        return return_msg(f"{robotModle_list[ip].JointTemperatures()}（摄氏度）")
    except Exception as e:
        logger.error(f"机器人各关节的温度获取失败: {str(e)}")
        return return_msg(f"机器人各关节的温度获取失败: {str(e)}")


@mcp.tool()
def get_programs(ip: str, username='root', password='easybot'):
    """获取指定IP机器人的所有程序。
    IP：机器人地址
    username：ssh账号
    password：ssh密码
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=22, username=username, password=password)
        # 创建交互式 shell
        shell = ssh.invoke_shell()
        # 执行多个命令
        shell.send('cd /programs\n')
        shell.send('ls -1\n')
        # 获取输出
        import time
        time.sleep(1)  # 等待命令执行
        output = shell.recv(65535).decode()
        ssh.close()
        files = []
        for file in output.split('\n'):
            name = file.replace(' ', '').replace('\r', '')
            if name.endswith('.urp'):
                files.append(name)
        logger.info(f"{str(files)}")
        return return_msg(f"命令已发送：{str(files)}")
    except Exception as e:
        return return_msg(f"程序列表获取失败。{str(e)}")


@mcp.tool()
def send_program_script(ip: str, script: str):
    """发送脚本到指定IP的机器人。
    IP：机器人地址
    script：脚本内容"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        robot_list[ip].robotConnector.RealTimeClient.SendProgram(script)
        time.sleep(1)
        logger.info(f"发送脚本:{script}")
        return return_msg(f"脚本程序已发送，请确认执行结果。")
    except Exception as e:
        logger.error(f"发送脚本失败: {str(e)}")
        return return_msg(f"发送脚本失败: {str(e)}")


@mcp.tool()
def movej(ip: str, q: list, a=1, v=1, t=0, r=0):
    """发送新的关节姿态到指定IP的机器人，使每个关节都旋转至指定弧度。
    IP：机器人地址，
    q：各关节角度，
    a：加速度（米每平方秒），
    v：速度（米每秒），
    t：移动时长（秒），
    r：交融半径（米）。"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")

        cmd = f"movej({q},{a},{v},{t},{r})"
        logger.info(f"发送脚本:{cmd}")
        robot_list[ip].movej(q, a, v, t, r)
        time.sleep(1)
        result = movejConfirm(ip, q)

        if result == 1:
            return return_msg(f"命令 {cmd} 已发送，移动完成。")
        else:
            return return_msg(f"命令 {cmd} 已发送，移动失败。")
    except Exception as e:
        logger.error(f"发送新的关节姿态到UR机器人失败: {str(e)}")
        return return_msg(f"发送新的关节姿态到UR机器人: {str(e)}")


@mcp.tool()
def movel(ip: str, pose: list, a=1, v=1, t=0, r=0):
    """发送新的TCP位置到指定IP的机器人，使TCP移动到指定位置，移动期间TCP作直线移动。
    IP：机器人地址
    pose：TCP位置
    a：加速度（米每平方秒）
    v：速度（米每秒）
    t：移动时长（秒）
    r：交融半径（米）"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        cmd = f"movel(p{pose},{a},{v},{t},{r})"
        logger.info(f"发送脚本:{cmd}")
        robot_list[ip].movel(pose, a, v, t, r)
        time.sleep(1)
        result = movelConfirm(ip, pose)

        if result == 1:
            return return_msg(f"命令 {cmd} 已发送，移动完成。")
        else:
            return return_msg(f"命令 {cmd} 已发送，移动失败。")
    except Exception as e:
        logger.error(f"发送新的TCP位置到指定IP的机器人失败: {str(e)}")
        return return_msg(f"发送新的TCP位置到指定IP的机器人: {str(e)}")


@mcp.tool()
def movel_x(ip: str, distance: float):
    """命令指定IP机器人的TCP沿X轴方向移动
    IP：机器人地址
    distance：移动距离（米）"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        pose = robot_list[ip].get_actual_tcp_pose()
        pose[0] = pose[0] + distance
        robot_list[ip].movel(pose)
        time.sleep(1)
        result = movelConfirm(ip, pose)
        cmd = (f"def my_program():\n"
               f"  movel(p[{'{:.4f}'.format(pose[0])},{'{:.4f}'.format(pose[1])},{'{:.4f}'.format(pose[2])},{'{:.4f}'.format(pose[3])},{'{:.4f}'.format(pose[4])},{'{:.4f}'.format(pose[5])},],0.5,0.25,0,0)\n"
               f"end\nmy_program()")
        logger.info(f"发送脚本:{cmd}")
        if result == 1:
            return return_msg(f"命令 {cmd} 已发送，移动完成。")
        else:
            return return_msg(f"命令 {cmd} 已发送，移动失败。")
    except Exception as e:
        logger.error(f"移动失败: {str(e)}")
        return return_msg(f"移动失败: {str(e)}")


@mcp.tool()
def movel_y(ip: str, distance: float):
    """命令指定IP机器人的TCP沿Y轴方向移动
    IP：机器人地址
    distance：移动距离（米）"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        pose = robot_list[ip].get_actual_tcp_pose()
        pose[1] = pose[1] + distance

        robot_list[ip].movel(pose)
        time.sleep(1)
        result = movelConfirm(ip, pose)
        cmd = (f"def my_program():\n"
               f"  movel(p[{'{:.4f}'.format(pose[0])},{'{:.4f}'.format(pose[1])},{'{:.4f}'.format(pose[2])},{'{:.4f}'.format(pose[3])},{'{:.4f}'.format(pose[4])},{'{:.4f}'.format(pose[5])},],0.5,0.25,0,0)\n"
               f"end\nmy_program()")
        logger.info(f"发送脚本:{cmd}")
        if result == 1:
            return return_msg(f"命令 {cmd} 已发送，移动完成。")
        else:
            return return_msg(f"命令 {cmd} 已发送，移动失败。")
    except Exception as e:
        logger.error(f"移动失败: {str(e)}")
        return return_msg(f"移动失败: {str(e)}")


@mcp.tool()
def movel_z(ip: str, distance: float):
    """命令指定IP机器人的TCP沿Y轴方向移动
    IP：机器人地址
    distance：移动距离（米）"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        pose = robot_list[ip].get_actual_tcp_pose()
        pose[2] = pose[2] + distance
        robot_list[ip].movel(pose)
        time.sleep(1)
        result = movelConfirm(ip, pose)
        cmd = (f"def my_program():\n"
               f"  movel(p[{'{:.4f}'.format(pose[0])},{'{:.4f}'.format(pose[1])},{'{:.4f}'.format(pose[2])},{'{:.4f}'.format(pose[3])},{'{:.4f}'.format(pose[4])},{'{:.4f}'.format(pose[5])},],0.5,0.25,0,0)\n"
               f"end\nmy_program()")
        logger.info(f"发送脚本:{cmd}")
        if result == 1:
            return return_msg(f"命令 {cmd} 已发送，移动完成。")
        else:
            return return_msg(f"命令 {cmd} 已发送，移动失败。")
    except Exception as e:
        logger.error(f"移动失败: {str(e)}")
        return return_msg(f"移动失败: {str(e)}")


@mcp.tool()
def draw_circle(ip: str, center: list, r: float, coordinate="z"):
    """命令指定IP的机器人，给定圆心位置和半径，在水平或竖直方向画一个圆
        center：圆心的TCP位置
        r：半径（米）
        coordinate：圆所在的平面。z：圆形所在的平面与基座所在平面垂直,其它：圆形所在的平面与基座所在平面平行。默认值：z。"""
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        wp_1 = [center[0], center[1], center[2], center[3], center[4], center[5]]
        wp_2 = [center[0], center[1], center[2], center[3], center[4], center[5]]
        wp_3 = [center[0], center[1], center[2], center[3], center[4], center[5]]
        wp_4 = [center[0], center[1], center[2], center[3], center[4], center[5]]
        cmd = ''
        if coordinate.lower() == "z":
            wp_1[2] = wp_1[2] + r

            wp_2[1] = wp_2[1] + r

            wp_3[2] = wp_3[2] - r

            wp_4[1] = wp_4[1] - r
        else:
            wp_1[0] = wp_1[0] - r

            wp_2[1] = wp_2[1] + r

            wp_3[0] = wp_3[0] + r

            wp_4[1] = wp_4[1] - r

        cmd = (
            f"def my_program():\n"
            f"  movep(p{str(wp_1)}, a=1, v=0.25, r=0.025)\n"
            f"  movec(p{str(wp_2)}, p{str(wp_3)}, a=1, v=0.25, r=0.025, mode=0)\n"
            f"  movec(p{str(wp_4)}, p{str(wp_1)}, a=1, v=0.25, r=0.025, mode=0)\nend\nmy_program()")
        logger.info(f"draw_circle 发送脚本:{cmd}")
        robot_list[ip].robotConnector.RealTimeClient.SendProgram(cmd)
        time.sleep(1)
        return return_msg(f"命令已发送：{cmd}")
    except Exception as e:
        logger.error(f"命令发送失败: {str(e)}")
        return return_msg(f"命令发送失败: {str(e)}")


@mcp.tool()
def draw_square(ip: str, origin: list, border: float, coordinate="z"):
    """给定起点位置和边长，在水平或竖直方向画一个正方形
        origin：画正方形时TCP的起点位置
        border：边长（米）
        coordinate：圆所在的平面。z：圆形所在的平面与基座所在平面垂直,其它：圆形所在的平面与基座所在平面平行。默认值：z。
        """
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        wp_1 = [origin[0], origin[1], origin[2], origin[3], origin[4], origin[5]]
        wp_2 = [origin[0], origin[1], origin[2], origin[3], origin[4], origin[5]]
        wp_3 = [origin[0], origin[1], origin[2], origin[3], origin[4], origin[5]]
        if coordinate.lower() == "z":
            wp_1[1] = wp_1[1] + border

            wp_2[1] = wp_2[1] + border
            wp_2[2] = wp_2[2] - border

            wp_3[2] = wp_3[2] - border

        else:
            wp_1[1] = wp_1[1] + border

            wp_2[1] = wp_2[1] + border
            wp_2[0] = wp_2[0] + border

            wp_3[0] = wp_3[0] + border

        cmd = (f"def my_program():\n"
               f"  movel(p{str(origin)}, a=1, v=0.25)\n"
               f"  movel(p{str(wp_1)}, a=1, v=0.25)\n"
               f"  movel(p{str(wp_2)}, a=1, v=0.25)\n"
               f"  movel(p{str(wp_3)}, a=1, v=0.25)\n"
               f"  movel(p{str(origin)}, a=1, v=0.25)\nend\nmy_program()")
        logger.info(f"draw_square 发送脚本:\n{cmd}")
        robot_list[ip].robotConnector.RealTimeClient.SendProgram(cmd)
        time.sleep(1)
        return return_msg(f"命令已发送：{cmd}")
    except Exception as e:
        logger.error(f"命令发送失败: {str(e)}")
        return return_msg(f"命令发送失败: {str(e)}")


@mcp.tool()
def draw_rectangle(ip: str, origin: list, width: float, height: float, coordinate="z"):
    """给定起点位置和边长，在水平或竖直方向画一个正方形
            origin：画长方形时TCP的起点位置
            width：长（米）
            height：宽（米）
            coordinate：圆所在的平面。z：圆形所在的平面与基座所在平面垂直,其它：圆形所在的平面与基座所在平面平行。默认值：z。"""

    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        wp_1 = [origin[0], origin[1], origin[2], origin[3], origin[4], origin[5]]
        wp_2 = [origin[0], origin[1], origin[2], origin[3], origin[4], origin[5]]
        wp_3 = [origin[0], origin[1], origin[2], origin[3], origin[4], origin[5]]
        if coordinate.lower() == "z":
            wp_1[1] = wp_1[1] + width

            wp_2[1] = wp_2[1] + width
            wp_2[2] = wp_2[2] - height

            wp_3[2] = wp_3[2] - height

        else:
            wp_1[1] = wp_1[1] + width

            wp_2[1] = wp_2[1] + width
            wp_2[0] = wp_2[0] + height

            wp_3[0] = wp_3[0] + height

        cmd = (f"def my_program():\n"
               f"  movel(p{str(origin)}, a=1, v=0.25)\n"
               f"  movel(p{str(wp_1)}, a=1, v=0.25)\n"
               f"  movel(p{str(wp_2)}, a=1, v=0.25)\n"
               f"  movel(p{str(wp_3)}, a=1, v=0.25)\n"
               f"  movel(p{str(origin)}, a=1, v=0.25)\nend\nmy_program()")
        logger.info(f"draw_rectangle 发送脚本:\n{cmd}")
        robot_list[ip].robotConnector.RealTimeClient.SendProgram(cmd)
        return return_msg(f"命令已发送：{cmd}")
    except Exception as e:
        logger.error(f"命令发送失败: {str(e)}")
        return return_msg(f"命令发送失败: {str(e)}")


# 以下是新增的工具函数

@mcp.tool()
def setup_multi_robot_coordination(robot_ids: list, collaboration_mode: str = "parallel"):
    """
    设置多机器人协同工作环境
    
    参数:
    - robot_ids: 参与协同的机器人ID列表
    - collaboration_mode: 协作模式，可选值包括"sequential", "parallel", "synchronous", "hierarchical"
    
    返回:
    - 成功或失败的消息
    """
    try:
        if multi_robot_coordinator is None:
            return return_msg("多机器人协调器未初始化")
        
        # 映射协作模式字符串到枚举值
        mode_map = {
            "sequential": CollaborationMode.SEQUENTIAL,
            "parallel": CollaborationMode.PARALLEL,
            "synchronous": CollaborationMode.SYNCHRONOUS,
            "hierarchical": CollaborationMode.HIERARCHICAL
        }
        
        if collaboration_mode not in mode_map:
            return return_msg(f"不支持的协作模式: {collaboration_mode}")
        
        # 注册机器人到协调器
        for robot_id in robot_ids:
            # 检查机器人是否已连接
            if robot_id in robot_list and robot_list[robot_id].robotConnector.RTDE.isRunning():
                multi_robot_coordinator.register_robot(robot_id)
                logger.info(f"机器人 {robot_id} 已注册到协调器")
            else:
                return return_msg(f"机器人 {robot_id} 未连接或不可用")
        
        # 设置协作模式
        multi_robot_coordinator.set_collaboration_mode(mode_map[collaboration_mode])
        
        return return_msg(f"多机器人协同环境设置成功，协作模式: {collaboration_mode}")
    except Exception as e:
        logger.error(f"设置多机器人协同环境失败: {str(e)}")
        return return_msg(f"设置多机器人协同环境失败: {str(e)}")


@mcp.tool()
def create_collaborative_task(task_name: str, robot_assignments: dict, dependencies: list = None):
    """
    创建多机器人协同任务
    
    参数:
    - task_name: 任务名称
    - robot_assignments: 机器人任务分配，格式为{"robot_id": {"operation": "...", "params": {...}}}
    - dependencies: 任务依赖关系列表，格式为[{"from": "task1", "to": "task2"}]
    
    返回:
    - 任务创建结果
    """
    try:
        if multi_robot_coordinator is None:
            return return_msg("多机器人协调器未初始化")
        
        # 创建任务
        task_id = multi_robot_coordinator.create_collaboration_task(
            task_name=task_name,
            robot_assignments=robot_assignments,
            dependencies=dependencies
        )
        
        return return_msg(f"协同任务创建成功，任务ID: {task_id}")
    except Exception as e:
        logger.error(f"创建协同任务失败: {str(e)}")
        return return_msg(f"创建协同任务失败: {str(e)}")


@mcp.tool()
def execute_collaborative_task(task_id: str):
    """
    执行多机器人协同任务
    
    参数:
    - task_id: 任务ID
    
    返回:
    - 执行结果
    """
    try:
        if multi_robot_coordinator is None:
            return return_msg("多机器人协调器未初始化")
        
        # 执行任务
        result = multi_robot_coordinator.execute_task(task_id)
        
        return return_msg(f"协同任务执行结果: {result}")
    except Exception as e:
        logger.error(f"执行协同任务失败: {str(e)}")
        return return_msg(f"执行协同任务失败: {str(e)}")


@mcp.tool()
def generate_bezier_path(control_points: list, num_points: int = 50):
    """
    生成贝塞尔曲线路径
    
    参数:
    - control_points: 控制点列表，格式为[{"x": 0, "y": 0, "z": 0, "rx": 0, "ry": 0, "rz": 0}, ...]
    - num_points: 生成的路径点数量
    
    返回:
    - 路径点列表
    """
    try:
        if advanced_trajectory_planner is None:
            return return_msg("高级轨迹规划器未初始化")
        
        # 转换控制点格式
        points = [
            [p["x"], p["y"], p["z"], p["rx"], p["ry"], p["rz"]]
            for p in control_points
        ]
        
        # 生成贝塞尔曲线
        path = advanced_trajectory_planner.generate_bezier_curve(
            control_points=points,
            num_points=num_points
        )
        
        # 转换回字典格式
        result_path = []
        for point in path:
            result_path.append({
                "x": point[0],
                "y": point[1],
                "z": point[2],
                "rx": point[3],
                "ry": point[4],
                "rz": point[5]
            })
        
        return return_msg({"path": result_path})
    except Exception as e:
        logger.error(f"生成贝塞尔路径失败: {str(e)}")
        return return_msg(f"生成贝塞尔路径失败: {str(e)}")


@mcp.tool()
def optimize_trajectory(ip: str, waypoints: list, optimization_type: str = "time"):
    """
    优化轨迹（时间、能耗或平滑度）
    
    参数:
    - ip: 机器人IP地址
    - waypoints: 路径点列表
    - optimization_type: 优化类型，可选值包括"time", "energy", "smoothness"
    
    返回:
    - 优化后的路径
    """
    try:
        if '连接失败' in link_check(ip):
            return return_msg(f"与机器人的连接已断开。")
        
        if advanced_trajectory_planner is None:
            return return_msg("高级轨迹规划器未初始化")
        
        # 转换waypoints格式
        points = [
            [p["x"], p["y"], p["z"], p["rx"], p["ry"], p["rz"]]
            for p in waypoints
        ]
        
        # 获取机器人模型参数
        robot_model = robotModle_list[ip]
        
        # 优化轨迹
        optimized_path = advanced_trajectory_planner.optimize_trajectory(
            waypoints=points,
            optimization_type=optimization_type,
            robot_model=robot_model
        )
        
        # 转换回字典格式
        result_path = []
        for point in optimized_path:
            result_path.append({
                "x": point[0],
                "y": point[1],
                "z": point[2],
                "rx": point[3],
                "ry": point[4],
                "rz": point[5]
            })
        
        return return_msg({"optimized_path": result_path})
    except Exception as e:
        logger.error(f"优化轨迹失败: {str(e)}")
        return return_msg(f"优化轨迹失败: {str(e)}")


@mcp.tool()
def start_data_recording(robot_id: str, record_types: list, duration: float = 0):
    """
    开始记录机器人数据
    
    参数:
    - robot_id: 机器人ID
    - record_types: 记录类型列表，可选值包括"robot_state", "joint_data", "tcp_data", "error_data"
    - duration: 记录持续时间（秒），0表示持续记录直到停止
    
    返回:
    - 记录会话ID
    """
    try:
        if advanced_data_recorder is None:
            return return_msg("高级数据记录器未初始化")
        
        # 映射记录类型字符串到枚举值
        type_map = {
            "robot_state": DataRecordType.ROBOT_STATE,
            "joint_data": DataRecordType.JOINT_DATA,
            "tcp_data": DataRecordType.TCP_DATA,
            "error_data": DataRecordType.ERROR
        }
        
        record_enum_types = []
        for record_type in record_types:
            if record_type in type_map:
                record_enum_types.append(type_map[record_type])
            else:
                return return_msg(f"不支持的记录类型: {record_type}")
        
        # 启动记录
        session_id = advanced_data_recorder.start_recording(
            robot_id=robot_id,
            record_types=record_enum_types,
            duration=duration
        )
        
        return return_msg({"session_id": session_id, "message": "数据记录已启动"})
    except Exception as e:
        logger.error(f"开始数据记录失败: {str(e)}")
        return return_msg(f"开始数据记录失败: {str(e)}")


@mcp.tool()
def stop_data_recording(session_id: str):
    """
    停止数据记录
    
    参数:
    - session_id: 记录会话ID
    
    返回:
    - 停止状态
    """
    try:
        if advanced_data_recorder is None:
            return return_msg("高级数据记录器未初始化")
        
        # 停止记录
        success = advanced_data_recorder.stop_recording(session_id)
        
        if success:
            return return_msg({"success": True, "message": "数据记录已停止"})
        else:
            return return_msg({"success": False, "message": "停止数据记录失败，会话不存在"})
    except Exception as e:
        logger.error(f"停止数据记录失败: {str(e)}")
        return return_msg(f"停止数据记录失败: {str(e)}")


@mcp.tool()
def analyze_robot_data(robot_id: str, analysis_type: str, start_time: float = None, end_time: float = None):
    """
    分析机器人数据
    
    参数:
    - robot_id: 机器人ID
    - analysis_type: 分析类型，可选值包括"statistical", "trend", "anomaly", "performance"
    - start_time: 开始时间戳
    - end_time: 结束时间戳
    
    返回:
    - 分析结果
    """
    try:
        if advanced_data_analyzer is None:
            return return_msg("高级数据分析器未初始化")
        
        # 映射分析类型字符串到枚举值
        type_map = {
            "statistical": AnalysisType.STATISTICAL,
            "trend": AnalysisType.TREND,
            "anomaly": AnalysisType.ANOMALY,
            "performance": AnalysisType.PERFORMANCE
        }
        
        if analysis_type not in type_map:
            return return_msg(f"不支持的分析类型: {analysis_type}")
        
        # 加载数据
        df = advanced_data_analyzer.load_data(
            robot_id=robot_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if df.empty:
            return return_msg({"error": "未找到数据"})
        
        # 执行分析
        analysis_params = {}
        if analysis_type == "trend" and 'timestamp' in df.columns:
            # 对于趋势分析，使用时间戳作为x轴
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            if numeric_columns and numeric_columns[0] != 'timestamp':
                analysis_params = {'x_column': 'timestamp', 'y_column': numeric_columns[0]}
        
        result = advanced_data_analyzer.analyze(
            df,
            type_map[analysis_type],
            analysis_params
        )
        
        return return_msg({"analysis_type": analysis_type, "result": result})
    except Exception as e:
        logger.error(f"分析机器人数据失败: {str(e)}")
        return return_msg(f"分析机器人数据失败: {str(e)}")


@mcp.tool()
def generate_robot_report(robot_id: str, start_time: float = None, end_time: float = None, report_path: str = None):
    """
    生成机器人运行报告
    
    参数:
    - robot_id: 机器人ID
    - start_time: 开始时间戳
    - end_time: 结束时间戳
    - report_path: 报告保存路径
    
    返回:
    - 报告生成结果
    """
    try:
        if advanced_data_analyzer is None:
            return return_msg("高级数据分析器未初始化")
        
        # 生成报告
        report = advanced_data_analyzer.generate_report(
            robot_id=robot_id,
            start_time=start_time,
            end_time=end_time,
            report_path=report_path
        )
        
        if 'error' in report:
            return return_msg({"error": report['error']})
        
        return return_msg({"success": True, "report": report})
    except Exception as e:
        logger.error(f"生成机器人报告失败: {str(e)}")
        return return_msg(f"生成机器人报告失败: {str(e)}")


@mcp.tool()
def compare_robots_performance(robot_ids: list, metric_columns: list, start_time: float = None, end_time: float = None):
    """
    比较多个机器人的性能
    
    参数:
    - robot_ids: 机器人ID列表
    - metric_columns: 比较指标列
    - start_time: 开始时间戳
    - end_time: 结束时间戳
    
    返回:
    - 比较结果
    """
    try:
        if advanced_data_analyzer is None:
            return return_msg("高级数据分析器未初始化")
        
        # 执行比较
        comparison = advanced_data_analyzer.compare_robots(
            robot_ids=robot_ids,
            metric_columns=metric_columns,
            start_time=start_time,
            end_time=end_time
        )
        
        return return_msg({"comparison": comparison})
    except Exception as e:
        logger.error(f"比较机器人性能失败: {str(e)}")
        return return_msg(f"比较机器人性能失败: {str(e)}")



# Main execution

def main():
    """Run the MCP server"""
    logger.info("Nonead-Universal-Robots-MCP  启动")
    set_robot_list()

    # 初始化扩展模块
    logger.info("初始化扩展功能模块...")
    initialize_extended_modules()

    logger.info("MCP服务器启动中...")
    mcp.run()


if __name__ == "__main__":
    main()
