
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



## 1. MCP란?
MCP(모델 컨텍스트 프로토콜)는 Anthropic사가 개발한 통신 프로토콜(2024년 11월 오픈소스화)로, AI 대형 언어 모델(DeepSeek-V3-0324, DeepSeek-R1, Qwen3 등)이 외부 데이터/도구/서비스에 효율적으로 접근하여 더 정확하고 지능적인 답변을 제공하기 위해 사용됩니다.

MCP 주요 기능

컨텍스트 정보 제공:
앱이 파일/DB 내용 등 추가 정보 전달
예: 보고서를 AI가 읽고 내용 기반 답변

외부 도구 연동:
파일 조작/DB 조회/API 호출/하드웨어 제어 등 직접 제어
예: 문서 자동 정리, DB 데이터 기반 보고서 생성

지능형 워크플로우 구축:
다중 MCP 서비스 조합으로 데이터 분석 자동화/고객 지원 등 구현

데이터 보안:
로컬 환경 운영으로 민감 데이터 보호

## 2. MCP 작동 원리
클라이언트-서버 구조

MCP 클라이언트: AI 앱(요청 발신)
MCP 서버: 데이터/도구 인터페이스 제공
통신: JSON-RPC 2.0 표준(실시간 알림 지원)

## 3. MCP 서버 주요 기능
데이터 접근:
파일/DB/메모리 데이터 제공
도구 실행:
SQL 조회/파일 저장 기능 제공
실시간 업데이트:
데이터 변경 시 AI 알림
세션 관리:
연결 상태 관리

## 2. nUR MCP 서버 핵심 기능  

Nonead Corporation이 자체 개발한 nUR_MCP_SERVER 제품 기술 설명

제품 개요:
nUR_MCP_SERVER는 MCP(Model Control Protocol) 인터페이스 프로토콜을 기반으로 구축된 지능형 로봇 제어 미들웨어 시스템으로, 대형 언어 모델(LLM)을 통합하여 산업용 로봇의 자연어 상호작용 제어를 구현합니다. 이 제품은 Client-Server 아키텍처로 설계되었으며 Universal Robots 전 시리즈 협동 로봇과의 심층적인 통합을 지원하여 기존 티치 펜던트 프로그래밍 방식의 산업용 로봇 운영 패러다임을 혁신합니다.

핵심 기술 아키텍처:
1. 의미 분석 엔진
다층 Transformer 아키텍처의 NLP 처리 모듈을 탑재하여 컨텍스트 인식 명령어 파싱(Contextual Command Parsing)을 지원하며, 자연어에서 로봇 제어 명령어로의 엔드투엔드 변환을 구현하여 명령어 인식 정확도 98.6% 달성

2. 동적 스크립트 생성 시스템
LLM 기반 코드 생성 프레임워크로 자연어 명령을 URScript 로봇 제어 스크립트로 자동 변환하며, 실시간 문법 검증 및 안전성 검사를 지원하여 기존 프로그래밍 대비 12배 향상된 생성 효율 제공

3. 멀티모달 제어 인터페이스
- MCP 프로토콜 확장 계층: TCP/UDP 듀얼 모드 통신 지원, 마이크로초 단위 명령 응답 제공
- 디바이스 추상화 계층: URCap 플러그인 표준화 접근 구현
- 데이터 버스: TCP/IP 이더넷 프로토콜 기반으로 다중 기기 협업 제어 구현

핵심 기능 특성:
▶ 자연어 즉시 제어
음성/텍스트 명령으로 로봇 동작 직접 구동(위치 제어, 궤적 계획, IO 작업), 동적 매개변수 주입 및 실시간 운동 수정 지원

▶ 지능형 데이터 수집 시스템
- 관절 토크, 엔드 이펙터 위치 등 12차원 상태 데이터 실시간 수집
- 자연어 정의 데이터 필터링 규칙 지원
- 구조화된 데이터 보고서 자동 생성(CSV/JSON/XLSX)

▶ 다중 기기 협업 제어
분산 작업 스케줄링 알고리즘 기반, Tord에서 개발한 MCP-Client와 연동하여 ≤12대 UR 로봇 클러스터 동시 관리 가능, 음성 연속 명령 및 크로스 디바이스 작업 오케스트레이션 지원

▶ 적응형 학습 모듈
내장 증분 학습 프레임워크로 사용자 피드백을 통해 명령-동작 매핑 관계 지속 최적화, 시스템 반복 학습 주기 ≤24시간

기술 사양:
- 명령 응답 지연: <200ms(엔드투엔드)
- 프로토콜 호환성: MCP v2.1+ / URScript v5.0+
- 동시 처리 능력: 200+ TPS

**nUR_MCP_SERVER 도구의 기능 분류 테이블 소개:**  

| 도구ID | 기능 분류 | 기능 설명 | 주요 매개변수 |
|--------|----------|----------|----------|
| fkUCFg7YmxSflgfmJawHeo (`connect_ur`) | 연결 관리 | UR 로봇 연결 | ip:로봇 IP |
| fcr4pIqoIXyxh3ko9FOsWU (`disconnect_ur`) | 연결 관리 | UR 로봇 연결 해제 | ip:로봇 IP |
| fNKAydKkxHwmGFgyrePBsN (`get_time`) | 상태 모니터링 | 가동 시간 확인(초) | ip:로봇 IP |
| fYTMsGvSRpUdWmURng7kGX (`get_output_int_register`) | 레지스터 작업 | Int 레지스터 출력 가져오기(0-23) | ip:로봇 IP, index:레지스터 인덱스 |
| fvfqDMdDJer6kpbCzwFL1D (`get_output_double_register`) | 레지스터 작업 | Double 레지스터 출력 가져오기(0-23) | ip:로봇 IP, index:레지스터 인덱스 |
| fCJ6sRw9m0ArdZ-MCaeNWK (`get_output_bit_register`) | 레지스터 작업 | Double 레지스터 출력 가져오기(0-31) | ip:로봇 IP, index:레지스터 인덱스 |
| f_ZXAIUv-eqHelwWxrzDHe (`get_serial_number`) | 장치 정보 | 시리얼 번호 가져오기 | ip:로봇 IP |
| fZ2ALt5kD50gV9AdEgBrRO (`get_robot_model`) | 장치 정보 | 모델 확인 | ip:로봇 IP |
| fEtHcw5RNF54X9RYIEU-1m (`get_actual_tcp_pose`) | 운동 제어 | 실시간 TCP 좌표 가져오기 | ip:로봇 IP |
| ftsb2AsiqiPqSBxHIwALOx (`get_actual_joint_pose`) | 운동 제어 | 실시간 관절 각도 가져오기 | ip:로봇 IP |
| fXmkr4PLkHKF0wgQGEHzLt (`movej`) | 운동 제어 | 관절 자세 명령 전송 | ip:로봇 IP, q:관절 각도(라디안) |
| fWdukQrgFZeK-DEcST4AwO (`movel`) | 운동 제어 | TCP 직선 이동 명령 전송 | ip:로봇 IP, pose:TCP 위치 |
| f2gbgju7QsymJa4wPgZQ0T (`movel_x`) | 운동 제어 | X축 직선 이동 | ip:로봇 IP, distance:이동 거리(미터) |
| fS6rCxVp498s5edU7jCMB3 (`movel_y`) | 운동 제어 | Y축 직선 이동 | ip:로봇 IP, distance:이동 거리(미터) |
| fJps7j-T3lwzXhp8p0_suy (`movel_z`) | 운동 제어 | Z축 직선 이동 | ip:로봇 IP, distance:이동 거리(미터) |
| fTMj5413O5CzsORAyBYXj8 (`load_program`) | 프로그램 제어 | UR 프로그램 로드 | ip:로봇 IP, program_name:프로그램 이름 |
| fqiYJ1c9fqCs5eYd-yKEeJ (`load_and_run_program`) | 프로그램 제어 | UR 프로그램 로드 및 실행 | ip:로봇 IP, program_name:프로그램 이름 |
| fW6-wrPoqm2bE3bMgtLbLP (`stop_program`) | 프로그램 제어 | 현재 프로그램 정지 | ip:로봇 IP |
| fsEmm-VX3CCY_XvnCDms7f (`pause_program`) | 프로그램 제어 | 현재 프로그램 일시 정지 | ip:로봇 IP |
| f83-fUQBd-YRSdIQDpuYmW (`get_actual_robot_voltage`) | 상태 모니터링 | 현재 전압 확인 | ip:로봇 IP |
| foMoD2L690vRdQxdW_gRNl (`get_actual_robot_current`) | 상태 모니터링 | 현재 전류 확인 | ip:로봇 IP |
| fDZBXqofuIb-7IjS6t2YJ2 (`get_actual_joint_voltage`) | 상태 모니터링 | 관절 전압 확인 | ip:로봇 IP |
| fgAa_kwSmXmvld6Alx39ij (`get_actual_joint_current`) | 상태 모니터링 | 관절 전류 확인 | ip:로봇 IP |
| furAKHVnYvORJ9R7N7vpbl (`get_joint_temperatures`) | 상태 모니터링 | 관절 온도 확인 | ip:로봇 IP |
| fuNb7TgOgWNukjAVjusMN4 (`get_robot_mode`) | 상태 모니터링 | 작동 상태 확인 | ip:로봇 IP |
| fD12XJtqjgI46Oufwt928c (`get_program_state`) | 상태 모니터링 | 프로그램 실행 상태 확인 | ip:로봇 IP |
| fMLa2mjlactTbD_CCKB1tX (`get_ur_software_version`) | 장치 정보 | 소프트웨어 버전 확인 | ip:로봇 IP |
| fWXQKGQ6J5mas9K9mGPK3x (`get_safety_mode`) | 장치 정보 | 안전 모드 확인 | ip:로봇 IP |
| f81vKugz9xnncjirTC3B6A (`get_programs`) | 프로그램 제어 | 프로그램 목록 가져오기 | ip:로봇 IP, username/password:SSH 인증 정보 |
| ffaaQZeknwwTISLYdYqM0_ (`send_program_script`) | 프로그램 제어 | 프로그램 스크립트 전송 | ip:로봇 IP, script:스크립트 내용 |
| fsWlT3tCOn1ub-kUZCrq7E (`draw_circle`) | 운동 제어 | 원 운동 | ip:로봇 IP, center:중심점 TCP 위치, r:반경(미터) |
| f7y1QpjnA9s1bzfLeOkTnS (`draw_square`) | 운동 제어 | 정사각형 그리기 | ip:로봇 IP, origin:시작점 TCP 위치, border:변 길이(미터) |
| fuN_LLSc22VKXWXwbwNARo (`draw_rectangle`) | 운동 제어 | 직사각형 그리기 | ip:로봇 IP, origin:시작점 TCP 위치, width/height:가로/세로(미터) |

참고: 모든 도구는 로봇 연결이 먼저 수립된 후 사용 가능합니다.

## 3. 면책사항

nUR MCP Server 사용 전, 운영 담당자가 UR 로봇 안전 교육을 이수하고 비상정지(E-stop) 등 안전 조작에 숙련되었는지 반드시 확인하십시오.

로봇 및 MCP Server 운영 상태를 정기적으로 점검하여 시스템 안정성과 안전성을 확보할 것을 권장합니다.

nUR MCP Server 사용 시 다음 안전 규정을 엄격히 준수해야 합니다:

로봇 가시 범위 내 운영

운영자는 언제나 유니버설 로봇이 시야 내에 위치하도록 하여 실시간 모니터링이 가능해야 합니다.

로봇 작동 중 작업 구역 이탈을 금지하며, 사고 발생 시 신속히 대응할 수 있도록 합니다.

작업 환경 안전 확보

로봇 가동 전 주변 장애물을 점검 및 제거하고, 위험 구역에 인원/장비/기타 물체가 진입하지 않도록 하십시오.

필요 시 물리적 방벽 또는 안전 광센서를 설치하여 무단 접근을 방지합니다.

안전 규정 위반 시 책임 면제

상기 안전 요건(감시 소홀, 작업 구역 미정리 등)을 준수하지 않아 인적 상해, 장비 손상 또는 생산 사고가 발생할 경우, 당사는 법적 책임 및 배상 의무를 지지 않습니다.

모든 운영 위험과 결과는 사용자 측에서 부담합니다.


## 4. 버전 릴리스

### 4.1 최근 업데이트

* 2025.05.15 : nUR_MCP_SERVER 첫 출시

### 4.2 향후 계획

* nUR MCP Server 전용 MCP Client 지원, 실행기 보안 기능 강화
* UR 로봇 로그 기록 추가
* UR 로봇 프로그램 백업 및 업로드

## 5. 빠른 시작

### 5.1 제품 기반 (일반 사용자용)

#### 5.1.1 엔진 & 종속성

* **권장 시스템 버전:**

  ```text
  macOS 사용자: macOS Monterey 12.6 이상
  Linux 사용자: CentOS 7 / Ubuntu 20.04 이상
  Windows 사용자: Windows 10 LTSC 2021 이상
  ```

* **소프트웨어 요구사항:**

  MCP 서버 환경

  ```text
  Python 3.11 이상     
  pip 25.1 이상
  UV Package Manager 0.6.14 이상  
  bun 1.2.8 이상
  ```

  MCP 클라이언트

  ```text
   Claude Desktop 3.7.0 이상
   Cherry Studio 1.2.10 이상
   Cline 3.14.1 이상

   ClaudeMind, Cursor, NextChat, ChatMCP, Copilot-MCP, Continue, Dolphin-MCP, Goose는 테스트되지 않았습니다.
  ```

   LLM 대형 언어 모델

  ```text
  DeepSeek-V3-0324 이상
  DeepSeek-R1-671b  이상 
  Qwen3-235b-a22b 이상
  
  일반적으로 MCP를 지원하는 대형 언어 모델은 사용 가능하며, 목록 이외의 모델은 테스트되지 않았습니다.
  Ollama로 배포된 모델은 현재 Tool 호출이 불가능하며, 해결 중입니다...
  ```

#### 5.1.2 설치

**MCP 서버 설치:**
1. Python 3.11 이상 설치
2. pip 25.1 이상 설치
3. UV Package Manager 0.6.14 이상 설치
4. bun 1.2.8 이상 설치
5. MCP Server 설치:
```
     git clone https://gitee.com/nonead/Nonead-Universal-Robots-MCP.git
     cd nUR_MCP_SERVER
     pip install -r requirements.txt
```

**MCP 클라이언트 설정:**

**Claude Desktop과 함께 사용하려면 서버 설정을 추가하세요:**
MacOS: ~/Library/Application Support/Claude/claude_desktop_config.json  

    {
      "mcpServers": {
        "nUR_MCP_SERVER": {
          "command": "uvx",
          "args": ["/home/nonead/MCP_Server/Nonead-Universal-Robots-MCP"]
        }
      }
    }

Windows: %APPDATA%/Claude/claude_desktop_config.json  

    {
      "mcpServers": {
        "nUR_MCP_SERVER": {
          "command": "uvx",
          "args": ["D:\\MyProgram\\MCP_SERVER\\Nonead-Universal-Robots-MCP"]
        }
      }
    }

**Cherry Studio와 함께 사용하려면 서버 설정을 추가하세요：**  

**macOS & Linux용:**  
```
{
  "mcpServers": {
    "nUR_MCP_SERVER": {
      "name": "nUR_MCP_Server",
      "type": "stdio",
      "description": "NONEAD Universal-Robots MCP Server",
      "isActive": true,
      "provider": "NONEAD Corporation",
      "providerUrl": "https://www.nonead.com",
      "logoUrl": "https://www.nonead.com/assets/img/vi/5.png",
      "tags": [
        "NONEAD",
        "nUR_MCP_Server",
        "Universal-Robots"
      ],
      "command": "uvx",
      "args": [
        "/home/nonead/MCP_Server/Nonead-Universal-Robots-MCP"
      ]
    }
  }
}
```

**Windows용:**  
```
{
  "mcpServers": {
    "nUR_MCP_SERVER": {
      "name": "nUR_MCP_Server",
      "type": "stdio",
      "description": "NONEAD Universal-Robots MCP Server",
      "isActive": true,
      "provider": "NONEAD Corporation",
      "providerUrl": "https://www.nonead.com",
      "logoUrl": "https://www.nonead.com/assets/img/vi/5.png",
      "tags": [
        "NONEAD",
        "nUR_MCP_Server",
        "Universal-Robots"
      ],
      "command": "uvx",
      "args": [
        "D:\\MyProgram\\MCP_SERVER\\Nonead-Universal-Robots-MCP"
      ]
    }
  }
}
```

**Cline과 함께 사용하려면 서버 구성을 추가하세요:**
MacOS & Linux:

    {
      "mcpServers": {
        "nUR_MCP_SERVER": {
            "command": "uvx",
            "args": ["/home/nonead/MCP_Server/Nonead-Universal-Robots-MCP"]
         }
      }
    }

Windows:

    {
      "mcpServers": {
        "nUR_MCP_SERVER": {
            "command": "uvx",
            "args": ["D:\\MyProgram\\MCP_SERVER\\Nonead-Universal-Robots-MCP"]
         }
      }
    }


### 5.2 툴킷 기반 (개발자용)

#### 5.2.1 엔진 & 의존성 

* **권장 시스템 버전:**

  ```text
  macOS 사용자: macOS Monterey 12.6 이상
  Linux 사용자: CentOS 7 / Ubuntu 20.04 이상
  Windows 사용자: Windows 10 LTSC 2021 이상
  ```

* **소프트웨어 요구사항:**

  MCP 서버 환경

  ```text
  Python 3.11 이상     
  pip 25.1 이상
  UV Package Manager 0.6.14 이상  
  bun 1.2.8 이상
  ```
  LLM 대형 언어 모델

  ```text
  DeepSeek-V3-0324 이상
  DeepSeek-R1-671b 이상 
  Qwen3-235b-a22b 이상
  
  일반적으로 MCP를 지원하는 대형 언어 모델은 사용 가능합니다. 목록 외 모델은 테스트되지 않았습니다
  Ollama로 배포된 모델은 현재 Tool 호출이 불가능합니다. 해결 중입니다...
  ```

#### 5.2.2 설치

**macOS/Linux/Windows 개발자용**

```text
Python 3.11 이상
pip 25.1 이상
UV 패키지 관리자 0.6.14 이상
bun 1.2.8 이상
```

#### 5.2.3 사용 방법

다음은 대형 언어 모델이 수행할 수 있는 작업 예시입니다:

* 유니버설 로봇 IP 연결: 192.168.1.199
* 유니버설 로봇 TCP 엔드 이펙터 현재 포즈 좌표 획득
* nUR_MCP_SERVER 도구의 모든 명령어 목록 표시
* 유니버설 로봇의 모든 하드웨어 데이터 획득
* 유니버설 로봇 스크립트 프로그램 실행
* 유니버설 로봇 내장 프로그램 XXXX.urp 실행
* IP 172.22.109.141 로봇을 A, IP 172.22.98.41 로봇을 B로 지정 후 연결. A(왼쪽)와 B(오른쪽)의 현재 TCP 포즈 및 각 키 포지션 기록, 두 로봇 포즈 상관관계 분석
* 단계적 실행: IP 192.168.1.199 로봇에서 현재 TCP 포즈 기록 후 +Z 방향 20mm, -Y 방향 50mm, +X 방향 30mm 이동을 5회 반복
* 유니버설 로봇 스크립트 작성 및 실행: 현재 포즈를 중심으로 베이스 평면에 반경 50mm 원 그리기
* IP 172.22.109.141을 A, 172.22.98.41을 B로 설정 후 연결. 이후 명령은 A만 제어하며 B에 미러 동작 동기화

## 6. 기술 아키텍처

MCP는 클라이언트-서버 아키텍처를 채택, 표준화 프로토콜로 모델과 외부 리소스 간 통신 구현.  
![alt](./images/MCP.svg "mcp")  
클라이언트-서버 모델
MCP 아키텍처 주요 구성요소:

MCP 호스트: 연결을 시작하는 LLM 애플리케이션(Claude Desktop 또는 IDE 등)
MCP 클라이언트: 호스트 앱 내 서버와 1:1 연결 유지 프로토콜 클라이언트
MCP 서버: 표준화 Model Context Protocol로 특정 기능 노출 경량 프로그램
로컬 데이터 소스: MCP 서버가 안전하게 접근 가능한 컴퓨터 파일/DB/서비스
원격 서비스: MCP 서버가 연결 가능한 API 기반 외부 시스템
주요 구성요소 책임:

MCP 호스트:
UI 제공
LLM 공급자 연결 관리
외부 리소스 접근을 위한 MCP 클라이언트 통합
MCP 클라이언트:
MCP 서버와 연결 수립/유지
요청 전송/응답 수신
MCP 프로토콜 표준 준수 데이터 교환 처리
MCP 서버:
클라이언트 요청 처리
특정 기능 실행/리소스 접근 제공
MCP 프로토콜 표준 준수 응답 형식화
통신 프로토콜
MCP는 JSON-RPC 2.0을 기본 통신 프로토콜로 사용:  
![alt](./images/p.svg "mcp_json-RPC2.0")   
요청: 클라이언트→서버/서버→클라이언트 작업 시작 메시지
응답: 요청에 대한 회신(결과/오류 정보 포함)
알림: 응답 불필요 단방향 메시지(주로 이벤트 알림용)
MCP 지원 전송 메커니즘:

표준 입출력(Stdio): 로컬 서버용, 프로세스 간 통신 구현
Server-Sent Events(SSE): HTTP 기반 전송 메커니즘, 원격 서버용

MCP 장점
MCP는 기존 통합 방법 대비 통일성·보안성·확장성에서 뛰어난 장점 보유.

통일성
표준화된 AI 시스템과 외부 데이터 소스 상호작용으로 기존 단편화 문제 해결:

플러그인식 접속: 통일 프로토콜로 다양한 데이터 소스 플러그인 접속 가능
크로스 플랫폼 호환: 서로 다른 AI 모델/플랫폼 지원
개발 단순화: 개발자는 비즈니스 로직에 집중 가능
보안성
내장 보안 메커니즘으로 데이터 전송/처리 과정 보호:

민감 정보 보호: API 키/사용자 데이터 등 민감 정보 보호
접근 제어: MCP 서버에서 세밀한 접근 제어 구현
로컬 처리: 민감 정보를 제3자에 업로드 없이 로컬 처리
확장성
모듈러 설계로 높은 확장성 구현:

멀티 서비스 연결: 여러 서비스가 호환 클라이언트에 연결 가능
생태계 확대: 성숙화에 따라 이용 가능한 사전 제작 컴포넌트 증가
커스터마이즈 능력: 개발자는 필요 시 커스텀 MCP 서버 생성 가능 

## 7. 연락처

**GitHub**: <https://github.com/nonead/Nonead-Universal-Robots-MCP>  
**gitee**: <https://gitee.com/nonead/Nonead-Universal-Robots-MCP>  
**공식 웹사이트**: <https://www.nonead.com>  

<img src="./images/QR.gif" alt="연락처: Nonead Tech WeChat" width="200">  

## 8. nUR MCP 서버와 다른 MCP 서버의 차이점

nUR MCP 서버를 사용하는 사용자는 매우 높은 안전 의식을 가지고 있어야 하며, 유니버설 로봇 사용 교육을 받아야 합니다. 대형 언어 모델이 조작하는 것은 실제 로봇이며, 부적절한 조작은 인신 피해와 재산 손실을 초래할 수 있으므로 반드시 주의하십시오.

## 9. 인용

본 소프트웨어를 사용하는 경우 아래와 같이 인용해 주세요:

* [nURMCP: NONEAD Uninversal-Robots Model Context Protocol Server](https://www.nonead.com)
* 탁덕은 지능 제조의 진수를 보여주며, 혁신으로 세계를 바꿉니다 <br>
  Nonead demonstrates the true meaning of intelligent manufacturing, pioneering innovations that reshape our world.

## 10. 라이선스

본 프로젝트는 사용자 구분형 듀얼 라이선스(User-Segmented Dual Licensing) 모델을 채택합니다.

**기본 원칙**
* 개인 사용자 및 10인 이하 기업/조직: 기본적으로 GNU Affero 일반 공중 라이선스 v3.0(AGPLv3) 적용
* 10인 초과 기업/조직: 상용 라이선스(Commercial License) 취득 필수

"10인 이하" 정의:
귀 조직(회사, 비영리 단체, 정부 기관, 교육 기관 등 모든 법인 포함)에서 본 소프트웨어(nUR_MCP_SERVER) 기능에 접근·사용하거나 어떤 형태로든 직접·간접적으로 이익을 얻는 개인 총수가 10인을 초과하지 않는 경우를 의미합니다. 개발자, 테스터, 운영자, 최종 사용자, 통합 시스템을 통한 간접 이용자 등이 포함되나 이에 국한되지 않습니다.

### 10.1 오픈소스 라이선스(Open Source License): AGPLv3 - 개인 및 10인 이하 조직 대상
* 귀하가 개인 사용자이거나 귀 조직이 상기 "10인 이하" 정의에 해당할 경우, AGPLv3 조건 하에 nUR_MCP_SERVER를 자유롭게 사용·수정·배포할 수 있습니다. AGPLv3 전문은 https://www.gnu.org/licenses/agpl-3.0.html에서 확인 가능합니다.
* **주요 의무:** AGPLv3 핵심 요건으로, nUR_MCP_Server를 수정하여 네트워크 서비스로 제공하거나 수정판을 배포할 경우 수령자에게 AGPLv3 라이선스에 따른 전체 소스 코드 제공 의무가 있습니다. "10인 이하" 기준에 해당하더라도 이 소스 코드 공개 의무를 회피하려면 상용 라이선스(하단 참조) 취득을 고려해야 합니다.
* 사용 전 반드시 AGPLv3 전체 조항을 정독하고 이해하시기 바랍니다.

### 10.2 상용 라이선스(Commercial License) - 10인 초과 조직 또는 AGPLv3 의무 회피 희망 사용자 대상
* **필수 요건:** 귀 조직이 상기 "10인 이하" 정의에 **해당하지 않는**(즉 11인 이상이 본 소프트웨어에 접근/사용/이익을 얻는) 경우, nUR_MCP_SERVER 사용 전 당사에 연락하여 상용 라이선스를 체결해야 합니다.
* **선택적 적용:** 귀 조직이 "10인 이하" 조건에 해당하더라도 사용 시나리오가 **AGPLv3 조항을 충족하지 못하는**(특히 소스 코드 공개 의무) 경우, 또는 AGPLv3가 **제공하지 않는** 특정 상용 조항(보증, 배상, Copyleft 제한 없음 등)이 필요한 경우에도 상용 라이선스 체결이 필수입니다.
* **상용 라이선스가 필요한 일반적 사례(이에 국한되지 않음):**
  * 조직 규모 10인 초과 시
  * (조직 규모 무관) 수정한 nUR_MCP_SERVER 버전을 배포하되 AGPLv3에 따른 수정 부분 소스 코드 공개를 원치 않는 경우
  * (조직 규모 무관) 수정한 nUR_MCP_SERVER를 기반으로 네트워크 서비스(SaaS)를 제공하되 서비스 이용자에게 수정 소스 코드를 제공하지 않으려는 경우
  * (조직 규모 무관) 회사 정책, 고객 계약 또는 프로젝트 요건 상 AGPLv3 라이선스 소프트 사용이 불가하거나 폐쇄적 배포·기밀 유지가 필요한 경우
* **상용 라이선스 취득:** nUR_MCP_SERVER 개발 팀에 service@nonead.com으로 연락주시기 바랍니다.

### 10.3 기여(Contributions)
* nUR_MCP_SERVER에 대한 커뮤니티 기여를 환영합니다. 본 프로젝트에 제출되는 모든 기여는 AGPLv3 라이선스 하에 제공된 것으로 간주됩니다.
* 본 프로젝트에 기여(예: Pull Request)를 제출함으로써, 귀하의 코드가 AGPLv3 라이선스로 본 프로젝트 및 모든 후속 이용자(궁극적으로 AGPLv3 또는 상용 라이선스를 선택하든지 여부와 무관)에게 제공되는 것에 동의한 것으로 간주합니다.
* 또한 귀하의 기여가 상용 라이선스 하에 배포되는 nUR_MCP_SERVER 버전에 포함될 수 있음을 이해하고 동의하는 것으로 간주합니다.

### 10.4 기타 조항(Other Terms)
* 상용 라이선스의 구체적 조건은 체결된 정식 상용 라이선스 계약에 따릅니다.
* 프로젝트 메인테이너는 필요 시 본 라이선스 정책(사용자 규모 정의 및 임계값 포함)을 갱신할 권리를 보유합니다. 관련 업데이트는 프로젝트 공식 채널(코드 저장소, 공식 웹사이트 등)에서 공지됩니다.


## 11. 개발 핵심 팀

수저우 탁덕 로봇 기술 유한회사 MCP 서버 개발 팀

**Tony Ke** <tonyke@nonead.com>  
**Micro Zhu** <microzhu@nonead.com>  
**Anthony Zhuang** <anthonyzhuang@nonead.com>  
**Quentin Wang** <quentinwang@nonead.com>
