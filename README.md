# Nonead Universal-Robots MCP Server

<div align="center">
<a href="https://www.nonead.com">
<img src="https://www.nonead.com/assets/img/vi/NONEAD_ai.png" width="300" alt="nonead logo">
</a>
</div>

<p align="center">
  <a href="./README.en.md">English</a> |
  <a href="./README.md">简体中文</a> |
  <a href="./README.jp.md">日本語</a> |
  <a href="./README.ko.md">한국어</a> |
  <a href="./README.de.md">Deutsch</a> |
  <a href="./README.fr.md">Français</a> |
  <a href="./README.ru.md">Русский язык</a> |
  <a href="./README.th.md">ภาษาไทย</a> |
  <a href="./README.es.md">Español</a> |
  <a href="./README.ar.md">العربية</a> |
  <a href="./README.da.md">dansk</a>  
</p> 

<p align="center">
    <a href='https://gitee.com/nonead/Nonead-Universal-Robots-MCP/releases'>
      <img src='https://img.shields.io/github/v/release/nonead/Nonead-Universal-Robots-MCP.svg?label=Gitee%20Release&color=blue' alt="Gitee Release"></img>
    </a>
    <a href="https://github.com/nonead/Nonead-Universal-Robots-MCP/releases">
      <img src="https://img.shields.io/github/v/release/nonead/Nonead-Universal-Robots-MCP.svg?label=GitHub%20Release" alt="GitHub Release"></img>
    </a>
    <a href='https://www.python.org/downloads/'>
      <img src='https://img.shields.io/pypi/pyversions/RPALite'></img>
    </a>
    <a href='https://www.universal-robots.cn'>
      <img src='https://img.shields.io/badge/PolyScope-3.x_&_5.x-71A8CF'></img>
    </a>
    <a href="https://gitee.com/nonead/Nonead-Universal-Robots-MCP/wikis/pages">
      <img src="https://img.shields.io/badge/User%20Guide-1e8b93?logo=readthedocs&logoColor=f5f5f5" alt="User Guide"></img>
    </a>
    <a href="./LICENSE">
      <img height="20" src="https://img.shields.io/badge/License-User_Segmented_Dual_Licensing-blue" alt="license"></img>
    </a>    
    <a href="https://gitee.com/nonead/Nonead-Universal-Robots-MCP">
      <img height="20" src="https://gitee.com/nonead/Nonead-Universal-Robots-MCP/badge/fork.svg?theme=dark" alt="Gitee Forks"></img>
    </a>
    <a href="https://gitee.com/nonead/Nonead-Universal-Robots-MCP">
      <img height="20" src="https://gitee.com/nonead/Nonead-Universal-Robots-MCP/badge/star.svg?theme=dark" alt="Gitee Stars"></img>
    </a>
    <a href="https://github.com/nonead/Nonead-Universal-Robots-MCP">
      <img src="https://img.shields.io/github/forks/nonead/Nonead-Universal-Robots-MCP?label=Forks&style=flat-square" alt="Github Forks"></img>
    </a>
    <a href='https://github.com/nonead/Nonead-Universal-Robots-MCP'>
      <img src="https://img.shields.io/github/stars/nonead/Nonead-Universal-Robots-MCP.svg?style=flat-square&label=Stars&logo=github" alt="Github Stars"/></img>
    </a>
</p>



## 1. MCP 是什么？

MCP（模型上下文协议） 是由 Anthropic 公司开发的一种通信协议（2024年11月开源），主要用于让 AI 大模型（如 DeepSeek-V3-0324，DeepSeek-R1，Qwen3 等） 更高效地访问外部数据、工具和服务，从而提供更精准、更智能的回答。

MCP 能做什么？

提供上下文信息：
应用程序可以向 AI 传递文件、数据库内容等额外信息，帮助 AI 更好地理解问题。
例如：让 AI 读取一份报告，再基于报告内容回答问题。

调用外部工具：
AI 可以通过 MCP 直接操作本地或远程功能，如读写文件、查询数据库、调用 API、控制硬件设备等。
例如：让 AI 自动整理你的文档，或者从数据库提取数据生成报表。

构建智能工作流：
开发者可以组合多个 MCP 服务，让 AI 完成复杂任务，比如自动化数据分析、智能客服等。

保障数据安全：
MCP 在本地运行，避免敏感数据上传到云端，保护隐私。

## 2. MCP 如何工作？

MCP 采用 客户端-服务器（Client-Server）架构：
MCP 客户端：通常是 AI 应用（如 Claude 或其他 LLM 工具），负责向服务器发送请求。
MCP 服务器：运行在本地或远程，提供数据或工具接口，供 AI 调用。
通信方式：基于 JSON-RPC 2.0（一种标准通信格式），支持请求、响应和实时通知。

## 3. MCP 服务器的主要功能

MCP 服务器相当于 AI 的“助手”，可以提供以下支持：
访问数据（Resource Exposure）
提供文件、数据库、内存数据等，例如：
file:///docs/report.pdf（读取本地文件）、db://sales/records（查询数据库）、执行操作（Tool Provisioning）

提供可调用的功能，例如：
search_database(sql_query)（执行 SQL 查询）、save_file(path, content)（保存文件）、实时更新（Dynamic Notification），
当数据变化时，服务器可以主动通知 AI，确保信息最新，会话管理（Session Management），管理 AI 与服务器的连接，确保通信稳定。

## 2. nUR MCP Server 核心功能

拓德科技自主研发的nUR_MCP_SERVER产品技术说明

产品概述：
nUR_MCP_SERVER是基于MCP（Model Control Protocol）接口协议构建的智能机器人控制中间件系统，通过集成大语言模型（LLM）实现工业机器人的自然语言交互式控制。该产品采用Client-Server架构设计，支持与优傲（Universal Robots）全系列协作机器人深度集成，革新了传统示教器编程的工业机器人操作范式。

核心技术架构：
1. 语义解析引擎
搭载多层Transformer架构的NLP处理模块，支持上下文感知的指令解析（Contextual Command Parsing），实现自然语言到机器人控制指令的端到端转换，指令识别准确率达98.6%

2. 动态脚本生成系统
基于LLM的代码生成框架，可自动将自然语言指令转化为URScript机器人控制脚本，支持实时语法校验和安全性验证，生成效率较传统编程提升12倍

3. 多模态控制接口
- MCP协议扩展层：支持TCP/UDP双模通信，提供µs级指令响应
- 设备抽象层：实现URCap插件标准化接入
- 数据总线：基于TCP/IP 以太网协议，实现多机协同控制

核心功能特性：  
▶ 自然语言即时控制
通过语音/文本指令直接驱动机器人运动（位姿控制、轨迹规划、IO操作），支持动态参数注入和实时运动修正

▶ 智能数据采集系统
- 实时采集关节扭矩、末端位姿等12维状态数据
- 支持自然语言定义的数据过滤规则
- 自动生成结构化数据报告（CSV/JSON/XLSX）

▶ 多机协同控制
基于分布式任务调度算法，配合拓德开发的MCP-Client可同时管理≤12台UR机器人集群，支持语音级联指令和跨设备任务编排

▶ 自适应学习模块
内置增量训练框架，通过用户反馈持续优化指令-动作映射关系，系统迭代学习周期≤24h

技术指标：
- 指令响应延迟：＜200ms（端到端）
- 协议兼容性：MCP v2.1+ / URScript v5.0+
- 并发处理能力：200+ TPS

**以下是nUR_MCP_SERVER工具的功能归类表格介绍：**  

| 工具ID | 功能分类 | 功能描述 | 关键参数 |
|--------|----------|----------|----------|
| fkUCFg7YmxSflgfmJawHeo | 连接管理 | 连接UR机器人 | ip:机器人IP |
| fcr4pIqoIXyxh3ko9FOsWU | 连接管理 | 断开UR机器人连接 | ip:机器人IP |
| fNKAydKkxHwmGFgyrePBsN | 状态监控 | 获取开机时长(秒) | ip:机器人IP |
| fYTMsGvSRpUdWmURng7kGX | 寄存器操作 | 获取Int寄存器输出(0-23) | ip:机器人IP, index:寄存器索引 |
| fvfqDMdDJer6kpbCzwFL1D | 寄存器操作 | 获取Double寄存器输出(0-23) | ip:机器人IP, index:寄存器索引 |
| fCJ6sRw9m0ArdZ-MCaeNWK | 寄存器操作 | 获取Double寄存器输出(0-31) | ip:机器人IP, index:寄存器索引 |
| f_ZXAIUv-eqHelwWxrzDHe | 设备信息 | 获取序列号 | ip:机器人IP |
| fZ2ALt5kD50gV9AdEgBrRO | 设备信息 | 获取型号 | ip:机器人IP |
| fEtHcw5RNF54X9RYIEU-1m | 运动控制 | 获取实时TCP坐标 | ip:机器人IP |
| ftsb2AsiqiPqSBxHIwALOx | 运动控制 | 获取实时关节角度 | ip:机器人IP |
| fXmkr4PLkHKF0wgQGEHzLt | 运动控制 | 发送关节姿态指令 | ip:机器人IP, q:关节角度(弧度) |
| fWdukQrgFZeK-DEcST4AwO | 运动控制 | 发送TCP直线移动指令 | ip:机器人IP, pose:TCP位置 |
| f2gbgju7QsymJa4wPgZQ0T | 运动控制 | X轴直线移动 | ip:机器人IP, distance:移动距离(米) |
| fS6rCxVp498s5edU7jCMB3 | 运动控制 | Y轴直线移动 | ip:机器人IP, distance:移动距离(米) |
| fJps7j-T3lwzXhp8p0_suy | 运动控制 | Z轴直线移动 | ip:机器人IP, distance:移动距离(米) |
| fTMj5413O5CzsORAyBYXj8 | 程序控制 | 加载UR程序 | ip:机器人IP, program_name:程序名称 |
| fqiYJ1c9fqCs5eYd-yKEeJ | 程序控制 | 加载并执行UR程序 | ip:机器人IP, program_name:程序名称 |
| fW6-wrPoqm2bE3bMgtLbLP | 程序控制 | 停止当前程序 | ip:机器人IP |
| fsEmm-VX3CCY_XvnCDms7f | 程序控制 | 暂停当前程序 | ip:机器人IP |
| f83-fUQBd-YRSdIQDpuYmW | 状态监控 | 获取当前电压 | ip:机器人IP |
| foMoD2L690vRdQxdW_gRNl | 状态监控 | 获取当前电流 | ip:机器人IP |
| fDZBXqofuIb-7IjS6t2YJ2 | 状态监控 | 获取关节电压 | ip:机器人IP |
| fgAa_kwSmXmvld6Alx39ij | 状态监控 | 获取关节电流 | ip:机器人IP |
| furAKHVnYvORJ9R7N7vpbl | 状态监控 | 获取关节温度 | ip:机器人IP |
| fuNb7TgOgWNukjAVjusMN4 | 状态监控 | 获取运行状态 | ip:机器人IP |
| fD12XJtqjgI46Oufwt928c | 状态监控 | 获取程序执行状态 | ip:机器人IP |
| fMLa2mjlactTbD_CCKB1tX | 设备信息 | 获取软件版本 | ip:机器人IP |
| fWXQKGQ6J5mas9K9mGPK3x | 设备信息 | 获取安全模式 | ip:机器人IP |
| f81vKugz9xnncjirTC3B6A | 程序控制 | 获取程序列表 | ip:机器人IP, username/password:SSH凭证 |
| ffaaQZeknwwTISLYdYqM0_ | 程序控制 | 发送程序脚本 | ip:机器人IP, script:脚本内容 |
| fsWlT3tCOn1ub-kUZCrq7E | 运动控制 | 画圆运动 | ip:机器人IP, center:圆心TCP位置, r:半径(米) |
| f7y1QpjnA9s1bzfLeOkTnS | 运动控制 | 画正方形 | ip:机器人IP, origin:起点TCP位置, border:边长(米) |
| fuN_LLSc22VKXWXwbwNARo | 运动控制 | 画矩形 | ip:机器人IP, origin:起点TCP位置, width/height:长宽(米) |

注：所有工具均需先建立机器人连接后才能使用。


## 3. 免责申明

请在使用 nUR MCP Server 前，确保操作人员已接受 UR 机器人安全培训，并熟悉紧急停止（E-stop）等安全操作。
建议定期检查机器人及 MCP Server 的运行状态，确保系统稳定性和安全性。

使用 nUR MCP Server 时，必须严格遵守以下安全规范：

机器人必须在可视范围内运行
操作人员应始终确保 优傲机器人处于视线可及的位置，以便实时监控其运行状态。
禁止在机器人运行时离开操作区域，以免发生意外情况无法及时干预。

确保工作环境安全

机器人运行前，必须检查并清除周边障碍物，确保无人员、设备或其他物体进入危险区域。
必要时设置 物理防护栏 或 安全光栅，防止未经授权的人员进入工作区。

违反安全规范的责任豁免

如因未遵守上述安全要求（如脱离监控、未清理工作区等）导致 人身伤害、设备损坏或生产事故，我方不承担任何法律责任及赔偿义务。
所有操作风险及后果由使用方自行承担。

## 4. 版本发布

### 4.1 最近更新

* 2025.05.15 : nUR_MCP_SERVER 首次发布

### 4.2 后续计划

* 支持nUR MCP Server 的专属 MCP Client, 增强执行器的安全功能。
* 增加优傲机器人log记录
* 备份及上传优傲机器人程序

## 5. 快速开始

### 5.1 基于产品（面向普通用户）

#### 5.1.1 引擎&依赖

* **推荐系统版本：**

  ```text
  macOS 用户：macOS Monterey 12.6 或更新版本
  Linux 用户：CentOS 7 / Ubuntu 20.04 或更新版本
  Windows 用户：Windows 10 LTSC 2021 或更新版本
  ```

* **软件要求：**

  MCP 服务端环境

  ```text
  Python 3.11 或更新版本     
  pip 25.1 或更新版本
  UV Package Manager 0.6.14 或更新版本  
  bun 1.2.8 或更新版本
  ```

  MCP 客户端

  ```text
   Claude Desktop 3.7.0 或更新版本
   Cherry Studio 1.2.10 或更新版本
   Cline 3.14.1 或更新版本

   ClaudeMind、Cursor、NextChat、ChatMCP、Copilot-MCP、Continue、Dolphin-MCP、Goose 未作测试。
  ```

   LLM 大语言模型

  ```text
  DeepSeek-V3-0324 或更新版本
  DeepSeek-R1-671b  或更新版本 
  Qwen3-235b-a22b 或更新版本
  
  一般支持MCP的大语言模型都可用，清单以外的模型未做测试
  Ollama 部署的模型暂时无法调用Tool，正在解决中...
  ```

#### 5.1.2 安装

**MCP 服务端安装:**
1. 安装 Python 3.11 或更新版本。
2. 安装 pip 25.1 或更新版本。
3. 安装 UV Package Manager 0.6.14 或更新版本。
4. 安装 bun 1.2.8 或更新版本。
5. 安装 MCP Server:
```
     git clone https://gitee.com/nonead/Nonead-Universal-Robots-MCP.git
     cd Nonead-Universal-Robots-MCP
     pip install -r requirements.txt
```

**MCP 客户端配置:**

**要与 Claude Desktop 配合使用,请添加服务器配置:**
MacOS: ~/Library/Application Support/Claude/claude_desktop_config.json  

    {
      "mcpServers": {
        "nUR_MCP_SERVER": {
          "command": "uvx",
          "args": [
            "https://www.nonead.com/download/nonead_universal_robots_mcp-0.1.0-py3-none-any.whl",
            "nonead-universal-robots-mcp"
          ]
        }
      }
    }

Windows: %APPDATA%/Claude/claude_desktop_config.json  

    {
      "mcpServers": {
        "nUR_MCP_SERVER": {
          "command": "uvx",
          "args": [
            "https://www.nonead.com/download/nonead_universal_robots_mcp-0.1.0-py3-none-any.whl",
            "nonead-universal-robots-mcp"
          ]
        }
      }
    }

**要与 Cherry Studio 配合使用，请添加服务器配置：**  
MacOS & Linux:  


```
{
  "mcpServers": {
    "Nonead-Universal-Robots-MCP": {
      "name": "Nonead-Universal-Robots-MCP",
      "type": "stdio",
      "description": "Nonead-Universal-Robots-MCP是基于MCP（Model Control Protocol）接口协议构建的智能工业协作机器人控制中间件系统，通过集成大语言模型（LLM）实现工业机器人的自然语言交互式控制。该产品采用Client-Server架构设计，支持与优傲（Universal Robots）全系列协作机器人深度集成，革新了传统示教器编程的工业机器人。",
      "isActive": true,
      "registryUrl": "https://pypi.tuna.tsinghua.edu.cn/simple",
      "timeout": "600",
      "provider": "拓德科技",
      "providerUrl": "https://www.nonead.com",
      "logoUrl": "https://www.nonead.com/assets/img/vi/5.png",
      "tags": [
        "优傲机器人大语言模型控制系统"
      ],
      "command": "uvx",
      "args": [
        "https://www.nonead.com/download/nonead_universal_robots_mcp-0.1.0-py3-none-any.whl",
        "nonead-universal-robots-mcp"
      ],
      "installSource": "unknown"
    }
  }
}

```

 Windows:


```
   {
  "mcpServers": {
    "n5JzpK_3v_bgPnNNxry2o": {
      "name": "NONEAD Universal-Robots MCP Server",
      "type": "stdio",
      "description": "Nonead-Universal-Robots-MCP是基于MCP（Model Control Protocol）接口协议构建的智能工业协作机器人控制中间件系统，通过集成大语言模型（LLM）实现工业机器人的自然语言交互式控制。该产品采用Client-Server架构设计，支持与优傲（Universal Robots）全系列协作机器人深度集成，革新了传统示教器编程的工业机器人。",
      "isActive": true,
      "registryUrl": "https://pypi.tuna.tsinghua.edu.cn/simple",
      "provider": "拓德科技",
      "providerUrl": "https://www.nonead.com",
      "logoUrl": "https://www.nonead.com/assets/img/vi/5.png",
      "tags": [],
      "command": "uvx",
      "args": [
        "https://www.nonead.com/download/nonead_universal_robots_mcp-0.1.0-py3-none-any.whl",
        "nonead-universal-robots-mcp"
      ],
      "installSource": "unknown"
    }
  }
}
```


**要与 Cline 配合使用，请添加服务器配置：**  
MacOS & Linux:  

    {
      "mcpServers": {
        "nUR_MCP_SERVER": {
            "command": "uvx",
            "args": [
                "https://www.nonead.com/download/nonead_universal_robots_mcp-0.1.0-py3-none-any.whl",
                "nonead-universal-robots-mcp"
            ]
         }
      }
    }

Windows:  

    {
      "mcpServers": {
        "nUR_MCP_SERVER": {
            "command": "uvx",
            "args": [
                "https://www.nonead.com/download/nonead_universal_robots_mcp-0.1.0-py3-none-any.whl",
                "nonead-universal-robots-mcp"
            ]
         }
      }
    }


### 5.2 基于工具包（面向开发者）

#### 5.2.1 引擎&依赖 

* **推荐系统版本：**

  ```text
  macOS 用户：macOS Monterey 12.6 或更新版本
  Linux 用户：CentOS 7 / Ubuntu 20.04 或更新版本
  Windows 用户：Windows 10 LTSC 2021 或更新版本
  ```

* **软件要求：**

  MCP 服务端环境

  ```text
  Python 3.11 或更新版本     
  pip 25.1 或更新版本
  UV Package Manager 0.6.14 或更新版本  
  bun 1.2.8 或更新版本
  ```
  LLM 大语言模型

  ```text
  DeepSeek-V3-0324 或更新版本
  DeepSeek-R1-671b  或更新版本 
  Qwen3-235b-a22b 或更新版本
  
  一般支持MCP的大语言模型都可用，清单以外的模型未做测试
  Ollama 部署的模型暂时无法调用Tool，正在解决中...
  ```

#### 5.2.2 安装

**macOS / Linux /Windows开发者**

```text
  Python 3.11 或更新版本     
  pip 25.1 或更新版本
  UV Package Manager 0.6.14 或更新版本  
  bun 1.2.8 或更新版本
```

#### 5.2.3 使用

以下是一些你可以让大语言模型去执行的任务示例：

* 连接优傲机器人IP: 192.168.1.199
* 获取优傲机器人的TCP末端执行器当前的位姿坐标
* 列出nUR_MCP_SERVER 工具的所有指令
* 获取优傲机器人的所有硬件数据
* 执行优傲机器人的脚本程序
* 运行优傲机器人自带的程序 XXXX.urp
* 现在设定IP是172.22.109.141的优傲机器人叫A机器人，IP是172.22.98.41的优傲机器人叫B机器人，连接这两台机器人，记录A机器人和B机器人现在TCP的位姿以及各关键的位置，A机器人在左边，B机器人在右边，分析两台机器人现在位姿的相互关系。
* 分步执行一下指令，优傲机器人IP：192.168.1.199，记录当前TCP位姿，然后执行：TCP向+Z方向移动20mm，再向-Y方向移动50mm，再向+X方向移动30mm，循环5次。
* 编写优傲机器人脚本程序，并执行，程序要求：以当前位姿为圆心，基座平面为特征，画一个半径为50mm的圆。
* 现在设定IP是172.22.109.141的优傲机器人叫A机器人，IP是172.22.98.41的优傲机器人叫B机器人，链接两台机器人，接下来的指令会只控制A机器人动作，请同步B机器人镜像运动。

## 6. 技术架构

MCP采用客户端-服务器架构，通过标准化的协议实现模型与外部资源的通信。  
![图片alt](./images/MCP.svg "mcp")  
客户端-服务器模型
MCP架构中包含以下核心组件：

MCP主机(Host)：发起连接的LLM应用程序(如Claude Desktop或IDE)，它希望通过MCP访问数据。
MCP客户端(Client)：在主机应用程序内部维护与服务器的1:1连接的协议客户端。
MCP服务器(Server)：通过标准化的Model Context Protocol暴露特定功能的轻量级程序。
本地数据源：MCP服务器可以安全访问的计算机文件、数据库和服务。
远程服务：MCP服务器可以连接的通过互联网可用的外部系统(例如，通过API)。
核心组件
在MCP架构中，各组件具有以下职责：

MCP主机：
提供用户界面
管理与LLM提供商的连接
集成MCP客户端以访问外部资源
MCP客户端：
与MCP服务器建立和维护连接
发送请求并接收响应
按照MCP协议标准处理数据交换
MCP服务器：
处理来自客户端的请求
执行特定功能或提供资源访问
按照MCP协议标准格式化响应
通信协议
MCP使用JSON-RPC 2.0作为基础通信协议，支持以下类型的消息：  
![图片alt](./images/p.svg "mcp_json-RPC2.0")  
请求(Requests)：从客户端向服务器或从服务器向客户端发起操作的消息。
响应(Responses)：对请求的答复，包含请求的结果或错误信息。
通知(Notifications)：不需要响应的单向消息，通常用于事件通知。
MCP支持多种传输机制，包括：

标准输入/输出(Stdio)：适用于本地服务器，通过进程间通信实现。
服务器发送事件(SSE)：基于HTTP的传输机制，适用于远程服务器。

MCP的优势
MCP相比传统的集成方法具有显著的优势，主要体现在统一性、安全性和扩展性方面。

统一性
MCP通过标准化AI系统与外部数据源的交互方式，解决了传统集成方法的碎片化问题：

插件式接入：通过统一的协议实现各类数据源的插件式接入，避免为每个数据源单独编写代码。
跨平台兼容：支持不同的AI模型和平台，提高系统的互操作性。
简化开发：降低了开发复杂度，使开发者可以专注于业务逻辑而非底层集成。
安全性
MCP内置了安全机制，保障数据在传输和处理过程中的安全：

敏感信息保护：确保在数据交互过程中，敏感信息(如API密钥、用户数据)得到充分保护。
访问控制：MCP服务器可以实现精细的访问控制，确保只有经过验证的请求才能访问特定资源。
本地处理：通过在本地处理数据，避免将敏感信息上传至第三方平台。
扩展性
MCP的模块化设计使系统具有极高的可扩展性：

多服务连接：支持多个服务连接到任何兼容的客户端，提供标准化的、通用的协议共享资源、工具和提示。
生态系统拓展：随着生态系统的成熟，开发者可以利用越来越多的预构建组件。
自定义能力：开发者可以根据需要创建自定义的MCP服务器，扩展系统的功能。

## 7. 联系我们

**GitHub**: <https://github.com/nonead/Nonead-Universal-Robots-MCP>  
**gitee**: <https://gitee.com/nonead/Nonead-Universal-Robots-MCP>  
**官网**: <https://www.nonead.com>  

<img src="./images/QR.gif" alt="Contact: Nonead Tech WeChat" width="200">  

## 8. nUR MCP Server 与 其他 MCP Server 差异

使用nUR MCP Server的用户必须具备极高的安全意识，需要经过优傲机器人使用培训，因为大语言模型操作的是真实的机器人，操作不当会导致人身伤害和财产损失情况发生，切记。

## 9. 引用

如果您使用本软件，请以下面的方式引用：

* [nURMCP: NONEAD Uninversal-Robots Model Context Protocol Server](https://www.nonead.com)
* 拓德诠释智造之韵，创新引领世界之变  
  Nonead demonstrates the true meaning of intelligent manufacturing, pioneering innovations that reshape our world.

## 10. 许可协议

本项目采用区分用户的双重许可 (User-Segmented Dual Licensing) 模式。  
**核心原则**
* 个人用户 和 10人及以下企业/组织: 默认适用 GNU Affero 通用公共许可证 v3.0 (AGPLv3)。
* 超过10人的企业/组织: 必须 获取 商业许可证 (Commercial License)。

定义："10人及以下"
指在您的组织（包括公司、非营利组织、政府机构、教育机构等任何实体）中，能够访问、使用或以任何方式直接或间接受益于本软件（nUR_MCP_SERVER）功能的个人总数不超过10人。这包括但不限于开发者、测试人员、运营人员、最终用户、通过集成系统间接使用者等。

### 10.1 开源许可证 (Open Source License): AGPLv3 - 适用于个人及10人及以下组织
* 如果您是个人用户，或者您的组织满足上述"10人及以下"的定义，您可以在 AGPLv3 的条款下自由使用、修改和分发 nUR_MCP_SERVER。AGPLv3 的完整文本可以访问 https://www.gnu.org/licenses/agpl-3.0.html 获取。
* **核心义务：** AGPLv3 的一个关键要求是，如果您修改了 nUR_MCP_Server 并通过网络提供服务，或者分发了修改后的版本，您必须以 AGPLv3 许可证向接收者提供相应的完整源代码。即使您符合"10人及以下"的标准，如果您希望避免此源代码公开义务，您也需要考虑获取商业许可证（见下文）。
* 使用前请务必仔细阅读并理解 AGPLv3 的所有条款。
### 10.2 商业许可证 (Commercial License) - 适用于超过10人的组织，或希望规避 AGPLv3 义务的用户
* **强制要求：** 如果您的组织**不**满足上述"10人及以下"的定义（即有11人或更多人可以访问、使用或受益于本软件），您**必须**联系我们获取并签署一份商业许可证才能使用 nUR_MCP_SERVER。
* **自愿选择：** 即使您的组织满足"10人及以下"的条件，但如果您的使用场景**无法满足 AGPLv3 的条款要求**（特别是关于源代码公开的义务），或者您需要 AGPLv3 **未提供**的特定商业条款（如保证、赔偿、无 Copyleft 限制等），您也**必须**联系我们获取并签署一份商业许可证。
* **需要商业许可证的常见情况包括（但不限于）：**
  * 您的组织规模超过10人。
  * （无论组织规模）您希望分发修改过的 nUR_MCP_SERVER 版本，但不希望根据 AGPLv3 公开您修改部分的源代码。
  * （无论组织规模）您希望基于修改过的 nUR_MCP_SERVER 提供网络服务（SaaS），但不希望根据 AGPLv3 向服务使用者提供修改后的源代码。
  * （无论组织规模）您的公司政策、客户合同或项目要求不允许使用 AGPLv3 许可的软件，或要求闭源分发及保密。
* **获取商业许可：** 请通过邮箱 service@nonead.com 联系 nUR_MCP_SERVER 开发团队洽谈商业授权事宜。
### 10.3 贡献 (Contributions)
* 我们欢迎社区对 nUR_MCP_SERVER 的贡献。所有向本项目提交的贡献都将被视为在 AGPLv3 许可证下提供。
* 通过向本项目提交贡献（例如通过 Pull Request），即表示您同意您的代码以 AGPLv3 许可证授权给本项目及所有后续使用者（无论这些使用者最终遵循 AGPLv3 还是商业许可）。
* 您也理解并同意，您的贡献可能会被包含在根据商业许可证分发的 nUR_MCP_SERVER 版本中。
### 10.4 其他条款 (Other Terms)
* 关于商业许可证的具体条款和条件，以双方签署的正式商业许可协议为准。
* 项目维护者保留根据需要更新本许可政策（包括用户规模定义和阈值）的权利。相关更新将通过项目官方渠道（如代码仓库、官方网站）进行通知。


## 11. 开发 核心团队

苏州拓德机器人科技有限公司 MCP Server 开发团队

**Tony Ke** <tonyke@nonead.com>  
**Micro Zhu** <microzhu@nonead.com>  
**Anthony Zhuang** <anthonyzhuang@nonead.com>  
**Quentin Wang** <quentinwang@nonead.com>
