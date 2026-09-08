
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



## 1. Was ist MCP?
Das MCP (Model Context Protocol) ist ein von Anthropic entwickeltes Kommunikationsprotokoll (Open Source ab November 2024), das Großsprachmodellen (wie DeepSeek-V3-0324, DeepSeek-R1, Qwen3 etc.) den effizienten Zugriff auf externe Daten/Tools/Dienste ermöglicht.

Hauptfunktionen:

Kontextbereitstellung:
Übermittlung von Dateien/Datenbankinhalten
Beispiel: Berichtsanalyse vor Antwort

Externe Tool-Nutzung:
Direkte Steuerung lokaler/entfernter Funktionen
Beispiel: Automatische Dokumentenorganisation

Workflow-Automatisierung:
Kombination mehrerer MCP-Dienste

Datensicherheit:
Lokale Ausführung schützt sensible Daten

## 2. Funktionsweise
Client-Server-Architektur:

MCP-Client: KI-Anwendung (sendet Anfragen)
MCP-Server: Stellt Schnittstellen bereit
Kommunikation: JSON-RPC 2.0 Standard

## 3. Serverfunktionen
Datenzugriff:
Dateien/Datenbanken/Arbeitsspeicher
Tool-Bereitstellung:
Vordefinierte Funktionen (SQL-Abfragen etc.)
Echtzeit-Updates:
Automatische Benachrichtigungen
Sitzungsverwaltung:
Verbindungsmanagement

## 2. nUR MCP Server Kernfunktionen  

Technische Beschreibung des nUR_MCP_SERVER-Produkts von Nonead Corporation

Produktübersicht:
nUR_MCP_SERVER ist eine intelligente Robotiksteuerungs-Middleware, basierend auf dem MCP-Interfaceprotokoll (Model Control Protocol) mit LLM-Integration zur natürlichen Sprachsteuerung von Industrierobotern. Die Client-Server-Architektur ermöglicht tiefgreifende Integration mit Universal Robots-Serien und revolutioniert die traditionelle Teach-Pendant-Programmierung.

Kernarchitektur:
1. Semantik-Analyse-Engine
NLP-Modul mit Multi-Layer-Transformer-Architektur ermöglicht kontextbewusste Befehlsanalyse (98,6% Genauigkeit) und End-to-End-Konvertierung natürlicher Sprache in Steuerbefehle.

2. Dynamisches Skriptgenerierungssystem
LLM-basierter Code-Generator wandelt Sprachbefehle in URScript um (12x schneller als herkömmliche Programmierung) mit Echtzeit-Syntaxprüfung und Sicherheitsvalidierung.

3. Multimodale Steuerschnittstelle
- MCP-Protokollschicht: TCP/UDP-Dualmodus (µs-Antwortzeit)
- Geräteabstraktionsschicht: Standardisierte URCap-Anbindung
- Datenbus: TCP/IP-basierte Multi-Roboter-Steuerung

Hauptfunktionen:
▶ Natürliche Sprachsteuerung
Direkte Bewegungssteuerung (Positionsregelung, Bahnplanung, I/O) per Sprach-/Textbefehl mit dynamischer Parametereingabe und Echtzeitkorrektur.

▶ Intelligente Datenerfassung
- Echtzeit-Erfassung von 12D-Zustandsdaten (Gelenkmomente, Endeffektorposition)
- Sprachdefinierte Datenfilterregeln
- Automatische Berichtsgenerierung (CSV/JSON/XLSX)

▶ Multi-Roboter-Koordination
Verteilter Task-Scheduler + Tords MCP-Client zur Steuerung von ≤12 UR-Robotern mit Sprachkaskaden und geräteübergreifender Aufgabenorchestrierung.

▶ Adaptives Lernmodul
Integriertes Incremental-Learning-Framework optimiert Befehl-Aktion-Zuordnung durch Nutzerfeedback (Lernzyklus ≤24h).

Technische Daten:
- Befehlslatenz: <200ms (End-to-End)
- Protokollkompatibilität: MCP v2.1+/URScript 5.0+
- Parallelverarbeitung: 200+ TPS

**Funktionsklassifizierungstabelle des nUR_MCP_SERVER-Tools:**  

| Tool-ID | Funktionskategorie | Funktionsbeschreibung | Schlüsselparameter |
|--------|----------|----------|----------|
| fkUCFg7YmxSflgfmJawHeo (`connect_ur`) | Verbindungsverwaltung | UR-Roboter verbinden | ip:Roboter-IP |
| fcr4pIqoIXyxh3ko9FOsWU (`disconnect_ur`) | Verbindungsverwaltung | UR-Roboter trennen | ip:Roboter-IP |
| fNKAydKkxHwmGFgyrePBsN (`get_time`) | Statusüberwachung | Betriebszeit abrufen (Sekunden) | ip:Roboter-IP |
| fYTMsGvSRpUdWmURng7kGX (`get_output_int_register`) | Registeroperation | Int-Registerausgang abrufen (0-23) | ip:Roboter-IP, index:Registerindex |
| fvfqDMdDJer6kpbCzwFL1D (`get_output_double_register`) | Registeroperation | Double-Registerausgang abrufen (0-23) | ip:Roboter-IP, index:Registerindex |
| fCJ6sRw9m0ArdZ-MCaeNWK (`get_output_bit_register`) | Registeroperation | Double-Registerausgang abrufen (0-31) | ip:Roboter-IP, index:Registerindex |
| f_ZXAIUv-eqHelwWxrzDHe (`get_serial_number`) | Geräteinformation | Seriennummer abrufen | ip:Roboter-IP |
| fZ2ALt5kD50gV9AdEgBrRO (`get_robot_model`) | Geräteinformation | Modell abrufen | ip:Roboter-IP |
| fEtHcw5RNF54X9RYIEU-1m (`get_actual_tcp_pose`) | Bewegungssteuerung | Echtzeit-TCP-Koordinaten abrufen | ip:Roboter-IP |
| ftsb2AsiqiPqSBxHIwALOx (`get_actual_joint_pose`) | Bewegungssteuerung | Echtzeit-Gelenkwinkel abrufen | ip:Roboter-IP |
| fXmkr4PLkHKF0wgQGEHzLt (`movej`) | Bewegungssteuerung | Gelenkpositionsbefehl senden | ip:Roboter-IP, q:Gelenkwinkel(Radiant) |
| fWdukQrgFZeK-DEcST4AwO (`movel`) | Bewegungssteuerung | TCP-Linearbewegungsbefehl senden | ip:Roboter-IP, pose:TCP-Position |
| f2gbgju7QsymJa4wPgZQ0T (`movel_x`) | Bewegungssteuerung | Linearbewegung X-Achse | ip:Roboter-IP, distance:Bewegungsstrecke(Meter) |
| fS6rCxVp498s5edU7jCMB3 (`movel_y`) | Bewegungssteuerung | Linearbewegung Y-Achse | ip:Roboter-IP, distance:Bewegungsstrecke(Meter) |
| fJps7j-T3lwzXhp8p0_suy (`movel_z`) | Bewegungssteuerung | Linearbewegung Z-Achse | ip:Roboter-IP, distance:Bewegungsstrecke(Meter) |
| fTMj5413O5CzsORAyBYXj8 (`load_program`) | Programmsteuerung | UR-Programm laden | ip:Roboter-IP, program_name:Programmname |
| fqiYJ1c9fqCs5eYd-yKEeJ (`load_and_run_program`) | Programmsteuerung | UR-Programm laden und ausführen | ip:Roboter-IP, program_name:Programmname |
| fW6-wrPoqm2bE3bMgtLbLP (`stop_program`) | Programmsteuerung | Aktuelles Programm stoppen | ip:Roboter-IP |
| fsEmm-VX3CCY_XvnCDms7f (`pause_program`) | Programmsteuerung | Aktuelles Programm pausieren | ip:Roboter-IP |
| f83-fUQBd-YRSdIQDpuYmW (`get_actual_robot_voltage`) | Statusüberwachung | Aktuelle Spannung abrufen | ip:Roboter-IP |
| foMoD2L690vRdQxdW_gRNl (`get_actual_robot_current`) | Statusüberwachung | Aktuellen Strom abrufen | ip:Roboter-IP |
| fDZBXqofuIb-7IjS6t2YJ2 (`get_actual_joint_voltage`) | Statusüberwachung | Gelenkspannung abrufen | ip:Roboter-IP |
| fgAa_kwSmXmvld6Alx39ij (`get_actual_joint_current`) | Statusüberwachung | Gelenkstrom abrufen | ip:Roboter-IP |
| furAKHVnYvORJ9R7N7vpbl (`get_joint_temperatures`) | Statusüberwachung | Gelenktemperatur abrufen | ip:Roboter-IP |
| fuNb7TgOgWNukjAVjusMN4 (`get_robot_mode`) | Statusüberwachung | Betriebsstatus abrufen | ip:Roboter-IP |
| fD12XJtqjgI46Oufwt928c (`get_program_state`) | Statusüberwachung | Programmausführungsstatus abrufen | ip:Roboter-IP |
| fMLa2mjlactTbD_CCKB1tX (`get_ur_software_version`) | Geräteinformation | Softwareversion abrufen | ip:Roboter-IP |
| fWXQKGQ6J5mas9K9mGPK3x (`get_safety_mode`) | Geräteinformation | Sicherheitsmodus abrufen | ip:Roboter-IP |
| f81vKugz9xnncjirTC3B6A (`get_programs`) | Programmsteuerung | Programmliste abrufen | ip:Roboter-IP, username/password:SSH-Anmeldedaten |
| ffaaQZeknwwTISLYdYqM0_ (`send_program_script`) | Programmsteuerung | Programmskript senden | ip:Roboter-IP, script:Skriptinhalt |
| fsWlT3tCOn1ub-kUZCrq7E (`draw_circle`) | Bewegungssteuerung | Kreisbewegung | ip:Roboter-IP, center:TCP-Mittelpunktposition, r:Radius(Meter) |
| f7y1QpjnA9s1bzfLeOkTnS (`draw_square`) | Bewegungssteuerung | Quadrat zeichnen | ip:Roboter-IP, origin:TCP-Startposition, border:Seitenlänge(Meter) |
| fuN_LLSc22VKXWXwbwNARo (`draw_rectangle`) | Bewegungssteuerung | Rechteck zeichnen | ip:Roboter-IP, origin:TCP-Startposition, width/height:Breite/Höhe(Meter) |

Hinweis: Alle Tools erfordern eine vorherige Roboterverbindung.

## 3. Haftungsausschluss

Stellen Sie vor der Nutzung des nUR MCP Server sicher, dass das Bedienpersonal eine UR-Robotersicherheitsschulung absolviert hat und mit Not-Aus (E-Stop) vertraut ist.

Führen Sie regelmäßige Inspektionen des Roboters und des MCP Server durch, um Systemstabilität und Sicherheit zu gewährleisten.

Bei der Nutzung des nUR MCP Server sind folgende Sicherheitsvorschriften zwingend einzuhalten:

Sichtbereich des Roboters

Der Bediener muss den Universal Robots-Roboter stets im Sichtfeld behalten, um den Betriebszustand in Echtzeit überwachen zu können.

Verlassen des Arbeitsbereichs während des Betriebs ist verboten, um bei Notfällen eingreifen zu können.

Sichere Arbeitsumgebung

Vor dem Start sind Hindernisse zu beseitigen und sicherzustellen, dass sich keine Personen/Objekte im Gefahrenbereich befinden.

Bei Bedarf sind physische Schutzzäune oder Sicherheitslichtvorhänge zu installieren.

Haftungsfreistellung bei Verstößen

Bei Verletzungen, Geräteschäden oder Produktionsstörungen aufgrund von Sicherheitsverstößen (z.B. fehlende Überwachung, ungesicherter Arbeitsbereich) übernehmen wir keine rechtliche Haftung oder Entschädigungspflicht.

Alle Betriebsrisiken und Folgen trägt der Anwender.

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

#### 5.1.2 Installation  

**MCP-Server-Installation:**  
1. Python 3.11 oder höher installieren  
2. pip 25.1 oder höher installieren  
3. UV Package Manager 0.6.14 oder höher installieren  
4. bun 1.2.8 oder höher installieren  
5. MCP-Server installieren:  
```
git clone https://gitee.com/nonead/Nonead-Universal-Robots-MCP.git  
cd nUR_MCP_SERVER  
pip install -r requirements.txt  
```  

**MCP-Client-Konfiguration:**  

**Für die Verwendung mit Claude Desktop Serverkonfiguration hinzufügen:**
**Für macOS:** ~/Library/Application Support/Claude/claude_desktop_config.json  
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

**Für Windows:** %APPDATA%/Claude/claude_desktop_config.json  
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

**Zur Verwendung mit Cline fügen Sie die Serverkonfiguration hinzu:**
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


### 5.2 Toolkit-basiert (für Entwickler)

#### 5.2.1 Engine & Abhängigkeiten 

* **Empfohlene Systemversionen:**

  ```text
  macOS-Benutzer: macOS Monterey 12.6 oder neuer
  Linux-Benutzer: CentOS 7 / Ubuntu 20.04 oder neuer
  Windows-Benutzer: Windows 10 LTSC 2021 oder neuer
  ```

* **Softwareanforderungen:**

  MCP-Serverumgebung

  ```text
  Python 3.11 oder neuer     
  pip 25.1 oder neuer
  UV Package Manager 0.6.14 oder neuer  
  bun 1.2.8 oder neuer
  ```
  LLM-Großsprachmodelle

  ```text
  DeepSeek-V3-0324 oder neuer
  DeepSeek-R1-671b oder neuer 
  Qwen3-235b-a22b oder neuer
  
  Allgemein sind Großsprachmodelle, die MCP unterstützen, verwendbar. Nicht aufgeführte Modelle wurden nicht getestet
  Mit Ollama bereitgestellte Modelle können derzeit keine Tools aufrufen. Wird bearbeitet...
  ```

#### 5.2.2 Installation

**Für macOS/Linux/Windows-Entwickler**

```text
Python 3.11 oder neuer
pip 25.1 oder neuer
UV Paketmanager 0.6.14 oder neuer
bun 1.2.8 oder neuer
```

#### 5.2.3 Verwendung

Beispiele für Aufgaben, die von großen Sprachmodellen ausgeführt werden können:

* Universal-Roboter-IP verbinden: 192.168.1.199  
* Aktuelle TCP-Endeffektor-Position des Universal-Roboters abrufen  
* Alle Befehle des nUR_MCP_SERVER-Tools auflisten  
* Alle Hardware-Daten des Universal-Roboters abrufen  
* Skriptprogramm des Universal-Roboters ausführen  
* Integriertes Programm XXXX.urp des Roboters ausführen  
* Roboter mit IP 172.22.109.141 als A und IP 172.22.98.41 als B definieren, verbinden, aktuelle TCP-Positionen und Schlüsselpositionen von A (links) und B (rechts) aufzeichnen, Positionsbeziehung analysieren  
* Schrittweise Ausführung: Universal-Roboter IP 192.168.1.199, aktuelle TCP-Position aufzeichnen, dann TCP um +20mm in Z, -50mm in Y, +30mm in X bewegen, 5 Mal wiederholen  
* Universal-Roboter-Skript erstellen/ausführen: Kreis mit 50mm Radius in Basisebene um aktuelle Position zeichnen  
* Roboter mit IP 172.22.109.141 als A und 172.22.98.41 als B definieren/verbinden, nachfolgende Befehle steuern nur A mit synchroner Spiegelbewegung von B  

## 6. Technische Architektur  

MCP nutzt Client-Server-Architektur mit standardisierten Protokollen für Modell-zu-externen-Ressourcen-Kommunikation.  
![alt](./images/MCP.svg "mcp")  
Client-Server-Modell  
Kernkomponenten:  

MCP-Host: LLM-Anwendung (z.B. Claude Desktop) die Verbindungen initiiert  
MCP-Client: Protokollclient der 1:1 Serververbindung in Host-App verwaltet  
MCP-Server: Leichtgewichtiges Programm das Funktionen via standardisiertes Model Context Protocol bereitstellt  
Lokale Datenquellen: Dateien/Datenbanken/Dienste sicher zugänglich für MCP-Server  
Remote-Dienste: Externe Systeme via Internet erreichbar (z.B. APIs)  
Zuständigkeiten:  

MCP-Host:  
Stellt Benutzeroberfläche bereit  
Verwaltet LLM-Anbieterverbindung  
Integriert MCP-Client für externen Ressourcenzugriff  
MCP-Client:  
Stellt/erhält MCP-Serververbindung aufrecht  
Sendet Anfragen/empfängt Antworten  
Verarbeitet Datenaustausch gemäß MCP-Standards  
MCP-Server:  
Verarbeitet Clientanfragen  
Führt spezifische Funktionen aus oder ermöglicht Ressourcenzugriff  
Formatiert Antworten gemäß MCP-Protokollstandards  
Kommunikationsprotokoll  
MCP verwendet JSON-RPC 2.0 als Basisprotokoll, unterstützt:  
![alt](./images/p.svg "mcp_json-RPC2.0")  
Anfragen: Nachrichten die Operationen von Client→Server oder umgekehrt initiieren  
Antworten: Rückmeldungen zu Anfragen mit Ergebnissen/Fehlerinformationen  
Benachrichtigungen: Einweg-Nachrichten ohne Antwort (typisch für Ereignismeldungen)  
Unterstützte Transportmechanismen:  

Standard-E/A (Stdio): Für lokale Server via Prozesskommunikation  
Server-Sent Events (SSE): HTTP-basierter Transport für Remote-Server  

MCP-Vorteile  
MCP übertrifft traditionelle Methoden in Einheitlichkeit, Sicherheit und Erweiterbarkeit.  

Einheitlichkeit  
Standardisierte Interaktion löst Fragmentierungsprobleme:  

Plugin-artiger Zugang: Einheitliches Protokoll für diverse Datenquellen  
Plattformübergreifende Kompatibilität: Unterstützt verschiedene KI-Modelle/Plattformen  
Entwicklungsvereinfachung: Fokus auf Geschäftslogik  
Sicherheit  
Integrierte Sicherheitsmechanismen schützen Daten:  

Sensible Informationssicherung: API-Schlüssel/Benutzerdaten etc.  
Zugriffskontrolle: MCP-Server ermöglicht granulare Zugriffsbeschränkungen  
Lokale Verarbeitung: Vermeidet Upload sensibler Daten zu Dritten  
Erweiterbarkeit  
Modulares Design ermöglicht hohe Skalierbarkeit:  

Multi-Service-Verbindung: Mehrere Dienste mit kompatiblen Clients verbindbar  
Ökosystemerweiterung: Wachsende Bibliothek vorgefertigter Komponenten  
Anpassungsfähigkeit: Entwicklung benutzerdefinierter MCP-Server möglich  

## 7. Kontakt

**GitHub**: <https://github.com/nonead/Nonead-Universal-Robots-MCP>  
**gitee**: <https://gitee.com/nonead/Nonead-Universal-Robots-MCP>  
**Offizielle Website**: <https://www.nonead.com>  

<img src="./images/QR.gif" alt="Kontakt: Nonead Tech WeChat" width="200">  

## 8. Unterschiede zwischen nUR MCP Server und anderen MCP Servern

Benutzer des nUR MCP Servers müssen ein sehr hohes Sicherheitsbewusstsein haben und eine Schulung zur Verwendung von Universal Robots absolviert haben, da das große Sprachmodell echte Roboter steuert. Fehlbedienungen können zu Personenschäden und Sachschäden führen. Bitte seien Sie äußerst vorsichtig.

## 9. Zitierung

Wenn Sie diese Software verwenden, zitieren Sie bitte wie folgt:

* [nURMCP: NONEAD Uninversal-Robots Model Context Protocol Server](https://www.nonead.com)
* Nonead zeigt die wahre Bedeutung der intelligenten Fertigung und führt Innovationen an, die unsere Welt verändern. <br>
  Nonead demonstrates the true meaning of intelligent manufacturing, pioneering innovations that reshape our world.

## 10. Lizenz

Dieses Projekt verwendet ein benutzersegmentiertes Dual-Lizenzmodell (User-Segmented Dual Licensing).

**Grundprinzipien**
* Privatnutzer und Unternehmen/Organisationen mit ≤10 Personen: Standardmäßig GNU Affero General Public License v3.0 (AGPLv3)
* Unternehmen/Organisationen mit >10 Personen: Erfordert eine kommerzielle Lizenz (Commercial License)

Definition "≤10 Personen":
Die Gesamtzahl der Personen in Ihrer Organisation (einschließlich Unternehmen, NGOs, Regierungsbehörden, Bildungseinrichtungen oder anderen Entitäten), die direkt/indirekt auf die Software (nUR_MCP_SERVER) zugreifen, sie nutzen oder davon profitieren, darf 10 Personen nicht überschreiten. Dies umfasst Entwickler, Tester, Betreiber, Endnutzer etc.

### 10.1 Open-Source-Lizenz (AGPLv3) - Für Privatpersonen und Organisationen mit ≤10 Personen
* Wenn Sie Privatnutzer sind oder Ihre Organisation die "≤10 Personen"-Definition erfüllt, können Sie nUR_MCP_SERVER unter AGPLv3 nutzen, modifizieren und verteilen. Vollständiger Text unter https://www.gnu.org/licenses/agpl-3.0.html
* **Schlüsselverpflichtung:** AGPLv3 verlangt, dass bei Modifikationen von nUR_MCP_Server und Bereitstellung als Webdienst oder Verteilung modifizierter Versionen der vollständige Quellcode unter AGPLv3 bereitgestellt werden muss. Selbst für Organisationen mit ≤10 Personen gilt: Falls Sie diese Verpflichtung umgehen möchten, benötigen Sie eine kommerzielle Lizenz (siehe unten).
* Lesen Sie alle AGPLv3-Bedingungen sorgfältig vor der Nutzung.

### 10.2 Kommerzielle Lizenz - Für Organisationen mit >10 Personen oder zur Umgehung von AGPLv3-Verpflichtungen
* **Zwingende Voraussetzung:** Wenn Ihre Organisation **nicht** "≤10 Personen" erfüllt (≥11 Personen mit Zugriff/Nutzung/Profit von der Software), **müssen** Sie eine kommerzielle Lizenz erwerben.
* **Freiwillige Option:** Selbst für Organisationen mit ≤10 Personen: Falls Ihre Nutzung **nicht** AGPLv3 entspricht (insbesondere Quellcode-Offenlegung) oder Sie kommerzielle Bedingungen benötigen, die **nicht** durch AGPLv3 abgedeckt sind (Garantien, Entschädigung, keine Copyleft-Beschränkungen...), ist eine kommerzielle Lizenz erforderlich.
* **Häufige Fälle, die eine kommerzielle Lizenz erfordern (nicht abschließend):**
  * Organisation mit >10 Personen
  * (Größe irrelevant) Verteilung modifizierter Versionen ohne Offenlegung des modifizierten Quellcodes gemäß AGPLv3
  * (Größe irrelevant) Bereitstellung von SaaS basierend auf modifiziertem nUR_MCP_SERVER ohne Weitergabe des modifizierten Codes
  * (Größe irrelevant) Unternehmensrichtlinien, Verträge oder Anforderungen, die AGPLv3-Software verbieten oder geschlossene Vertraulichkeit verlangen
* **Lizenzierung:** Kontaktieren Sie das Entwicklungsteam unter service@nonead.com.

### 10.3 Beiträge
* Community-Beiträge sind willkommen. Alle Beiträge gelten als unter AGPLv3 lizenziert.
* Durch Beitragseinreichung (z.B. Pull Request) erklären Sie sich damit einverstanden, Ihren Code unter AGPLv3 für dieses Projekt und alle zukünftigen Nutzer (ob unter AGPLv3 oder kommerzieller Lizenz) zu lizenzieren.
* Sie akzeptieren auch, dass Ihr Beitrag in kommerziellen Versionen von nUR_MCP_SERVER enthalten sein kann.

### 10.4 Weitere Bedingungen
* Spezifische Bedingungen kommerzieller Lizenzen unterliegen den unterzeichneten Verträgen.
* Die Projektbetreuer behalten sich das Recht vor, diese Richtlinie (einschließlich Schwellenwerten) zu aktualisieren. Änderungen werden über offizielle Kanäle (Repository, Website) bekannt gegeben.

## 11. Entwicklung Kernteam

MCP Server Entwicklungsteam der Suzhou Nonead Robot Technology Co., Ltd.

**Tony Ke** <tonyke@nonead.com>  
**Micro Zhu** <microzhu@nonead.com>  
**Anthony Zhuang** <anthonyzhuang@nonead.com>  
**Quentin Wang** <quentinwang@nonead.com>