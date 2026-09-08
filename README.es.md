
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



## 1. ¿Qué es MCP?
El MCP (Protocolo de Contexto de Modelo) es un protocolo de comunicación desarrollado por Anthropic (de código abierto desde noviembre 2024) que permite a los grandes modelos de IA (ej. DeepSeek-V3-0324, DeepSeek-R1, Qwen3) acceder eficientemente a datos/herramientas/servicios externos.

Funcionalidades clave:

Provisión de contexto:
Transmisión de archivos/contenidos de BD
Ej: Análisis de informes previo a respuestas

Integración de herramientas:
Operación remota/local de sistemas
Ej: Organización automática de documentos

Automatización de flujos:
Combinación de servicios MCP

Seguridad de datos:
Ejecución local protege información

## 2. Funcionamiento
Arquitectura cliente-servidor:

Cliente MCP: Aplica IA (envía solicitudes)
Servidor MCP: Provee interfaces
Comunicación: Basada en JSON-RPC 2.0

## 3. Funciones del servidor
Acceso a datos:
Archivos/BD/memoria
Ejecución de herramientas:
Funciones predefinidas (consultas SQL etc.)
Notificaciones dinámicas:
Actualizaciones en tiempo real
Gestión de sesiones:
Mantenimiento de conexiones

## 2. Funciones principales del servidor nUR MCP  

Descripción técnica del producto nUR_MCP_SERVER desarrollado por Nonead Corporation

Resumen del producto:
nUR_MCP_SERVER es un sistema middleware de control de robots inteligentes construido sobre el protocolo de interfaz MCP (Model Control Protocol), que integra modelos de lenguaje grande (LLM) para permitir el control interactivo en lenguaje natural de robots industriales. Este producto utiliza un diseño de arquitectura Cliente-Servidor y soporta integración profunda con toda la serie de robots colaborativos Universal Robots, revolucionando el paradigma tradicional de programacióncon teach pendant de robots industriales.

Arquitectura tecnológica clave:

Motor de análisis semántico
Módulo de procesamiento NLP con arquitectura Transformer multicapa, soporta análisis contextual de comandos (Contextual Command Parsing), logrando conversión de extremo a extremo de lenguaje natural a comandos de control con precisión de reconocimiento del 98.6%.

Sistema dinámico de generación de scripts
Framework de generación de código basado en LLM, convierte automáticamente comandos en lenguaje natural a scripts URScript, con verificación sintáctica y validación de seguridad en tiempo real, eficiencia 12 veces superior a programación tradicional.

Interfaz de control multimodal

Capa de extensión MCP: Soporta comunicación dual TCP/UDP, respuesta en microsegundos
Capa de abstracción: Conexión estandarizada de plugins URCap
Bus de datos: Protocolo TCP/IP para control coordinado multirobot
Características principales:
▶ Control inmediato por lenguaje natural
Comando directo de movimientos (control de posición, planificación de trayectoria, E/S) mediante voz/texto, con inyección dinámica de parámetros y corrección en tiempo real.

▶ Sistema inteligente de adquisición de datos

Captura en tiempo real de datos 12D (par articular, posición efector final)
Reglas de filtrado definibles en lenguaje natural
Generación automática de informes (CSV/JSON/XLSX)
▶ Control coordinado multirobot
Algoritmo distribuido de planificación de tareas + MCP-Client de Tord para gestionar ≤12 robots UR simultáneos, soporta comandos en cascada y orquestación multitarea.

▶ Módulo de aprendizaje adaptativo
Framework de entrenamiento incremental integrado, optimiza mapeo comando-acción mediante feedback con ciclo ≤24h.

Especificaciones:

Latencia: <200ms (end-to-end)
Compatibilidad: MCP v2.1+/URScript v5.0+
Capacidad concurrente: 200+ TPS

**Tabla de Clasificación de Funciones de la Herramienta nUR_MCP_SERVER:**  

| ID Herramienta | Categoría | Descripción | Parámetros clave |
|--------|----------|----------|----------|
| fkUCFg7YmxSflgfmJawHeo (`connect_ur`) | Gestión conexión | Conectar robot UR | ip:IP robot |
| fcr4pIqoIXyxh3ko9FOsWU (`disconnect_ur`) | Gestión conexión | Desconectar robot UR | ip:IP robot |
| fNKAydKkxHwmGFgyrePBsN (`get_time`) | Monitoreo estado | Obtener tiempo encendido (segundos) | ip:IP robot |
| fYTMsGvSRpUdWmURng7kGX (`get_output_int_register`) | Operación registro | Obtener salida registro Int (0-23) | ip:IP robot, index:índice registro |
| fvfqDMdDJer6kpbCzwFL1D (`get_output_double_register`) | Operación registro | Obtener salida registro Double (0-23) | ip:IP robot, index:índice registro |
| fCJ6sRw9m0ArdZ-MCaeNWK (`get_output_bit_register`) | Operación registro | Obtener salida registro Double (0-31) | ip:IP robot, index:índice registro |
| f_ZXAIUv-eqHelwWxrzDHe (`get_serial_number`) | Información dispositivo | Obtener número serie | ip:IP robot |
| fZ2ALt5kD50gV9AdEgBrRO (`get_robot_model`) | Información dispositivo | Obtener modelo | ip:IP robot |
| fEtHcw5RNF54X9RYIEU-1m (`get_actual_tcp_pose`) | Control movimiento | Obtener coordenadas TCP tiempo real | ip:IP robot |
| ftsb2AsiqiPqSBxHIwALOx (`get_actual_joint_pose`) | Control movimiento | Obtener ángulos articulación tiempo real | ip:IP robot |
| fXmkr4PLkHKF0wgQGEHzLt (`movej`) | Control movimiento | Enviar comando postura articulación | ip:IP robot, q:ángulos articulación(radianes) |
| fWdukQrgFZeK-DEcST4AwO (`movel`) | Control movimiento | Enviar comando movimiento lineal TCP | ip:IP robot, pose:posición TCP |
| f2gbgju7QsymJa4wPgZQ0T (`movel_x`) | Control movimiento | Movimiento lineal eje X | ip:IP robot, distance:distancia movimiento(metros) |
| fS6rCxVp498s5edU7jCMB3 (`movel_y`) | Control movimiento | Movimiento lineal eje Y | ip:IP robot, distance:distancia movimiento(metros) |
| fJps7j-T3lwzXhp8p0_suy (`movel_z`) | Control movimiento | Movimiento lineal eje Z | ip:IP robot, distance:distancia movimiento(metros) |
| fTMj5413O5CzsORAyBYXj8 (`load_program`) | Control programa | Cargar programa UR | ip:IP robot, program_name:nombre programa |
| fqiYJ1c9fqCs5eYd-yKEeJ (`load_and_run_program`) | Control programa | Cargar y ejecutar programa UR | ip:IP robot, program_name:nombre programa |
| fW6-wrPoqm2bE3bMgtLbLP (`stop_program`) | Control programa | Detener programa actual | ip:IP robot |
| fsEmm-VX3CCY_XvnCDms7f (`pause_program`) | Control programa | Pausar programa actual | ip:IP robot |
| f83-fUQBd-YRSdIQDpuYmW (`get_actual_robot_voltage`) | Monitoreo estado | Obtener voltaje actual | ip:IP robot |
| foMoD2L690vRdQxdW_gRNl (`get_actual_robot_current`) | Monitoreo estado | Obtener corriente actual | ip:IP robot |
| fDZBXqofuIb-7IjS6t2YJ2 (`get_actual_joint_voltage`) | Monitoreo estado | Obtener voltaje articulación | ip:IP robot |
| fgAa_kwSmXmvld6Alx39ij (`get_actual_joint_current`) | Monitoreo estado | Obtener corriente articulación | ip:IP robot |
| furAKHVnYvORJ9R7N7vpbl (`get_joint_temperatures`) | Monitoreo estado | Obtener temperatura articulación | ip:IP robot |
| fuNb7TgOgWNukjAVjusMN4 (`get_robot_mode`) | Monitoreo estado | Obtener estado operación | ip:IP robot |
| fD12XJtqjgI46Oufwt928c (`get_program_state`) | Monitoreo estado | Obtener estado ejecución programa | ip:IP robot |
| fMLa2mjlactTbD_CCKB1tX (`get_ur_software_version`) | Información dispositivo | Obtener versión software | ip:IP robot |
| fWXQKGQ6J5mas9K9mGPK3x (`get_safety_mode`) | Información dispositivo | Obtener modo seguridad | ip:IP robot |
| f81vKugz9xnncjirTC3B6A (`get_programs`) | Control programa | Obtener lista programas | ip:IP robot, username/password:credenciales SSH |
| ffaaQZeknwwTISLYdYqM0_ (`send_program_script`) | Control programa | Enviar script programa | ip:IP robot, script:contenido script |
| fsWlT3tCOn1ub-kUZCrq7E (`draw_circle`) | Control movimiento | Movimiento circular | ip:IP robot, center:posición TCP centro, r:radio(metros) |
| f7y1QpjnA9s1bzfLeOkTnS (`draw_square`) | Control movimiento | Dibujar cuadrado | ip:IP robot, origin:posición TCP inicio, border:longitud lado(metros) |
| fuN_LLSc22VKXWXwbwNARo (`draw_rectangle`) | Control movimiento | Dibujar rectángulo | ip:IP robot, origin:posición TCP inicio, width/height:ancho/alto(metros) |

Nota: Todas las herramientas requieren conexión previa con el robot.

## 3. Declaración de responsabilidad

Antes de usar el nUR MCP Server, verifique que el operador ha recibido capacitación en seguridad de robots UR y conoce el paro de emergencia (E-stop).

Inspeccione regularmente el robot y el estado del MCP Server para garantizar estabilidad y seguridad.

Al usar el nUR MCP Server, cumpla estrictamente con:

Visibilidad del robot

El operador debe mantener al robot Universal Robots dentro de su campo visual para monitoreo en tiempo real.

Prohibido abandonar el área durante su operación para intervenir ante emergencias.

Ambiente de trabajo seguro

Elimine obstáculos y asegure que ninguna persona/objeto ingrese a la zona de riesgo antes de activar el robot.

Instale barreras físicas o cortinas luminosas de seguridad si es necesario.

Exención de responsabilidad

No nos hacemos responsables por lesiones, daños o accidentes causados por incumplimiento de normas de seguridad (ej: desatención, área no asegurada).

El usuario asume todos los riesgos operativos.

## 4. Version Releases  

### 4.1 Recent Updates  

* **2025.05.15**: Initial release of nUR_MCP_SERVER  

### 4.2 Future Plans  

* Develop a dedicated MCP Client for nUR MCP Server to enhance actuator safety features.  
* Add UR robot log recording functionality.  
* Enable backup and upload of UR robot programs.  

## 5. Quick Start  

### 5.1 Product-Based (For General Users)  

#### 5.1.1 Engine & Dependencies  

* **Recommended System Versions:**  

  ```text  
  macOS Users: macOS Monterey 12.6 or later  
  Linux Users: CentOS 7 / Ubuntu 20.04 or later  
  Windows Users: Windows 10 LTSC 2021 or later  
  ```  

* **Software Requirements:**  

  **MCP Server Environment**  

  ```text  
  Python 3.11 or later  
  pip 25.1 or later  
  UV Package Manager 0.6.14 or later  
  bun 1.2.8 or later  
  ```  

  **MCP Client**  

  ```text  
  Claude Desktop 3.7.0 or later  
  Cherry Studio 1.2.10 or later  
  Cline 3.14.1 or later  

  ClaudeMind, Cursor, NextChat, ChatMCP, Copilot-MCP, Continue, Dolphin-MCP, Goose - Not tested.  
  ```  

  **LLM Large Language Models**  

  ```text  
  DeepSeek-V3-0324 or later  
  DeepSeek-R1-671b or later  
  Qwen3-235b-a22b or later  

  Generally, any MCP-supported LLM can be used. Models not listed here have not been tested.  
  Ollama-deployed models currently cannot invoke Tools (under resolution)...  
  ```

#### 5.1.2 Instalación  

**Instalación del servidor MCP:**  
1. Instalar Python 3.11 o superior  
2. Instalar pip 25.1 o superior  
3. Instalar UV Package Manager 0.6.14 o superior  
4. Instalar bun 1.2.8 o superior  
5. Instalar el servidor MCP:  
```
git clone https://gitee.com/nonead/Nonead-Universal-Robots-MCP.git  
cd nUR_MCP_SERVER  
pip install -r requirements.txt  
```  

**Configuración del cliente MCP:**  

**Para usar con Claude Desktop, agregue configuración de servidor:**
**Para macOS:** ~/Library/Application Support/Claude/claude_desktop_config.json  
```
{
  "mcpServers": {
    "nUR_MCP_SERVER": {
      "command": "uvx",
      "args": ["/home/nonead/MCP_Server/Nonead-Universal-Robots-MCP"]
    }
  }
}
```

**Para Windows:** %APPDATA%/Claude/claude_desktop_config.json  
```
{
  "mcpServers": {
    "nUR_MCP_SERVER": {
      "command": "uvx",
      "args": ["D:\\MyProgram\\MCP_SERVER\\Nonead-Universal-Robots-MCP"]
    }
  }
}
```

**To use with Cherry Studio, add server configuration:**  

**For macOS & Linux:**  
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

**For Windows:**  
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

**Para usar con Cline, agregue la configuración del servidor:**
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


### 5.2 Basado en toolkit (para desarrolladores)

#### 5.2.1 Motor y dependencias 

* **Versiones recomendadas del sistema:**

  ```text
  Usuarios de macOS: macOS Monterey 12.6 o superior
  Usuarios de Linux: CentOS 7 / Ubuntu 20.04 o superior
  Usuarios de Windows: Windows 10 LTSC 2021 o superior
  ```

* **Requisitos de software:**

  Entorno del servidor MCP

  ```text
  Python 3.11 o superior     
  pip 25.1 o superior
  UV Package Manager 0.6.14 o superior  
  bun 1.2.8 o superior
  ```
  Modelos de lenguaje grande LLM

  ```text
  DeepSeek-V3-0324 o superior
  DeepSeek-R1-671b o superior 
  Qwen3-235b-a22b o superior
  
  Generalmente, los modelos de lenguaje grande que admiten MCP son utilizables. Modelos no listados no han sido probados
  Los modelos implementados mediante Ollama actualmente no pueden llamar a Herramientas. En proceso de resolución...
  ```

#### 5.2.2 Instalación

**Para desarrolladores macOS/Linux/Windows**

```text
Python 3.11 o superior
pip 25.1 o superior
Gestor de paquetes UV 0.6.14 o superior
bun 1.2.8 o superior
```

#### 5.2.3 Uso

Ejemplos de tareas ejecutables por modelos lingüísticos avanzados:

* Conectar robot Universal IP: 192.168.1.199
* Obtener coordenadas de pose actual del efector final TCP
* Listar todos los comandos de la herramienta nUR_MCP_SERVER  
* Obtener todos los datos hardware del robot Universal  
* Ejecutar programa de script del robot Universal  
* Ejecutar programa incorporado XXXX.urp del robot  
* Definir robot IP 172.22.109.141 como Robot A e IP 172.22.98.41 como Robot B, conectar ambos, registrar poses TCP y posiciones clave actuales de A (izquierda) y B (derecha), analizar relación entre poses  
* Ejecución paso a paso: Robot Universal IP 192.168.1.199, registrar pose TCP actual, luego mover TCP +20mm en Z, -50mm en Y, +30mm en X, repetir 5 veces  
* Crear y ejecutar script para robot Universal: Dibujar círculo de 50mm de radio en plano base centrado en pose actual  
* Definir robots IP 172.22.109.141 como A y 172.22.98.41 como B, conectar, comandos posteriores controlarán solo A sincronizando movimiento espejo de B  

## 6. Arquitectura Técnica  

MCP utiliza arquitectura cliente-servidor con protocolos estandarizados para comunicación modelo-recursos externos.  
![alt](./images/MCP.svg "mcp")  
Modelo Cliente-Servidor  
Componentes principales:  

Host MCP: Aplicación LLM (ej. Claude Desktop o IDE) que inicia conexiones  
Cliente MCP: Cliente protocolario manteniendo conexión 1:1 con servidor  
Servidor MCP: Programa ligero exponiendo funcionalidad vía Model Context Protocol  
Fuentes de datos locales: Archivos, bases de datos y servicios accesibles seguramente por Servidor MCP  
Servicios remotos: Sistemas externos accesibles vía internet (ej. APIs)  
Responsabilidades:  

Host MCP:  
Provee interfaz de usuario  
Gestiona conexión con proveedor LLM  
Integra Cliente MCP para acceso a recursos externos  
Cliente MCP:  
Establece/mantiene conexión con Servidor MCP  
Envía solicitudes y recibe respuestas  
Maneja intercambio de datos según estándares MCP  
Servidor MCP:  
Procesa solicitudes de clientes  
Ejecuta funciones específicas o provee acceso a recursos  
Formatea respuestas según estándares MCP  
Protocolo de Comunicación  
MCP usa JSON-RPC 2.0 como protocolo base, soportando:  
![alt](./images/p.svg "mcp_json-RPC2.0")  
Solicitudes: Mensajes que inician operaciones cliente→servidor o viceversa  
Respuestas: Réplicas conteniendo resultados o información de error  
Notificaciones: Mensajes unidireccionales sin respuesta requerida (notificaciones)  
Mecanismos de transporte soportados:  

E/S estándar (Stdio): Para servidores locales vía comunicación entre procesos  
Eventos enviados por servidor (SSE): Transporte basado en HTTP para servidores remotos  

Ventajas de MCP  
MCP supera métodos tradicionales en unificación, seguridad y extensibilidad.  

Unificación  
Interacción estandarizada resuelve problemas de fragmentación:  

Acceso tipo plugin: Protocolo unificado para diversas fuentes de datos  
Compatibilidad multiplataforma: Soporta diferentes modelos/plataformas de IA  
Simplificación de desarrollo: Enfoque en lógica de negocio  
Seguridad  
Mecanismos integrados protegen datos:  

Protección de información sensible: Claves API/datos de usuario etc.  
Control de acceso: Servidor MCP permite restricciones granulares  
Procesamiento local: Evita subir datos sensibles a terceros  
Extensibilidad  
Diseño modular permite alta escalabilidad:  

Conexión multiservicio: Múltiples servicios conectables a clientes compatibles  
Expansión de ecosistema: Creciente biblioteca de componentes preconstruidos  
Capacidad de personalización: Desarrollo de Servidores MCP personalizados  

## 7. Contáctenos

**GitHub**: <https://github.com/nonead/Nonead-Universal-Robots-MCP>  
**gitee**: <https://gitee.com/nonead/Nonead-Universal-Robots-MCP>  
**Sitio web oficial**: <https://www.nonead.com>  

<img src="./images/QR.gif" alt="Contacto: Nonead Tech WeChat" width="200">  

## 8. Diferencias entre nUR MCP Server y otros servidores MCP

Los usuarios de nUR MCP Server deben tener una conciencia de seguridad extremadamente alta y haber completado la capacitación en el uso de robots Universal, ya que el modelo de lenguaje grande controla robots reales. El funcionamiento inadecuado puede causar lesiones personales y daños a la propiedad - por favor extreme las precauciones.

## 9. Cita

Si utiliza este software, cite de la siguiente manera:

* [nURMCP: NONEAD Universal-Robots Model Context Protocol Server](https://www.nonead.com)
* Nonead demuestra el verdadero significado de la fabricación inteligente, innovando para remodelar nuestro mundo.

## 10. Licencia

Este proyecto adopta un modelo de doble licencia segmentado por usuario (User-Segmented Dual Licensing).

**Principios básicos**
* Usuarios individuales y empresas/organizaciones ≤10 personas: Licencia Pública General GNU Affero v3.0 (AGPLv3) por defecto
* Empresas/organizaciones >10 personas: Requiere licencia comercial (Commercial License)

Definición "≤10 personas":
Número total de individuos en su organización (incluyendo empresas, ONGs, agencias gubernamentales, instituciones educativas o cualquier entidad) que acceden, usan o se benefician directa/indirectamente del software (nUR_MCP_SERVER), sin exceder 10 personas. Incluye desarrolladores, testers, operadores, usuarios finales, etc.

### 10.1 Licencia open source (Open Source License): AGPLv3 - Para particulares y organizaciones ≤10 personas
* Si es usuario individual o su organización cumple la definición "≤10 personas", puede usar, modificar y distribuir nUR_MCP_SERVER bajo AGPLv3. Texto completo en https://www.gnu.org/licenses/agpl-3.0.html
* **Obligación clave:** AGPLv3 exige que si modifica nUR_MCP_Server y lo provee como servicio web o distribuye versiones modificadas, debe proporcionar el código fuente completo bajo AGPLv3. Incluso para organizaciones ≤10 personas, si desea evitar esta obligación, necesita licencia comercial (ver abajo).
* Lea atentamente todos los términos de AGPLv3 antes de usar.

### 10.2 Licencia comercial (Commercial License) - Para organizaciones >10 personas o que deseen evitar obligaciones AGPLv3
* **Requisito obligatorio:** Si su organización **no** cumple "≤10 personas" (≥11 personas accediendo/usando/beneficiándose del software), **debe** obtener licencia comercial.
* **Opción voluntaria:** Incluso para organizaciones ≤10 personas, si su uso **no cumple** AGPLv3 (especialmente divulgación de código) o necesita términos comerciales **no provistos** por AGPLv3 (garantías, indemnización, sin restricciones Copyleft...), requiere licencia comercial.
* **Casos comunes que necesitan licencia comercial (no limitado a):**
  * Organización >10 personas
  * (Tamaño irrelevante) Distribuir versiones modificadas sin revelar código fuente modificado según AGPLv3
  * (Tamaño irrelevante) Ofrecer SaaS basado en nUR_MCP_SERVER modificado sin compartir código modificado
  * (Tamaño irrelevante) Políticas corporativas, contratos o requisitos que prohíban software AGPLv3 o requieran distribución cerrada/confidencialidad
* **Obtener licencia:** Contacte al equipo de desarrollo en service@nonead.com.

### 10.3 Contribuciones
* Aceptamos contribuciones comunitarias. Todas las contribuciones se consideran licenciadas bajo AGPLv3.
* Al contribuir (ej: Pull Request), acepta licenciar su código bajo AGPLv3 para este proyecto y todos los usuarios posteriores (ya sea bajo AGPLv3 o licencia comercial).
* También acepta que su contribución pueda incluirse en versiones comerciales de nUR_MCP_SERVER.

### 10.4 Otros términos
* Los términos específicos de licencias comerciales se rigen por contratos firmados.
* Los mantenedores se reservan el derecho de actualizar esta política (incluyendo umbrales). Actualizaciones se anunciarán en canales oficiales (repositorio, sitio web).


## 11. Equipo central de desarrollo

Equipo de desarrollo del servidor MCP de Suzhou Nonead Robot Technology Co., Ltd.

**Tony Ke** <tonyke@nonead.com>  
**Micro Zhu** <microzhu@nonead.com>  
**Anthony Zhuang** <anthonyzhuang@nonead.com>  
**Quentin Wang** <quentinwang@nonead.com>