
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
    <a href='https://gitee.com/nonead/nUR_MCP_SERVER/releases'>
      <img src='https://img.shields.io/github/v/release/nonead/nUR_MCP_SERVER.svg?label=Gitee%20Release&color=blue' alt="Gitee Release"></img>
    </a>
    <a href="https://github.com/nonead/nUR_MCP_SERVER/releases">
      <img src="https://img.shields.io/github/v/release/nonead/nUR_MCP_SERVER.svg?label=GitHub%20Release" alt="GitHub Release"></img>
    </a>
    <a href='https://www.python.org/downloads/'>
      <img src='https://img.shields.io/pypi/pyversions/RPALite'></img>
    </a>
    <a href='https://www.universal-robots.cn'>
      <img src='https://img.shields.io/badge/PolyScope-3.x_&_5.x-71A8CF'></img>
    </a>
    <a href="https://gitee.com/nonead/nUR_MCP_SERVER/wikis/pages">
      <img src="https://img.shields.io/badge/User%20Guide-1e8b93?logo=readthedocs&logoColor=f5f5f5" alt="User Guide"></img>
    </a>
    <a href="./LICENSE">
      <img height="20" src="https://img.shields.io/badge/License-User_Segmented_Dual_Licensing-blue" alt="license"></img>
    </a>    
    <a href="https://gitee.com/nonead/nUR_MCP_SERVER">
      <img height="20" src="https://gitee.com/nonead/nUR_MCP_SERVER/badge/fork.svg?theme=dark" alt="Gitee Forks"></img>
    </a>
    <a href="https://gitee.com/nonead/nUR_MCP_SERVER">
      <img height="20" src="https://gitee.com/nonead/nUR_MCP_SERVER/badge/star.svg?theme=dark" alt="Gitee Stars"></img>
    </a>
    <a href="https://github.com/nonead/nUR_MCP_SERVER">
      <img src="https://img.shields.io/github/forks/nonead/nUR_MCP_SERVER?label=Forks&style=flat-square" alt="Github Forks"></img>
    </a>
    <a href='https://github.com/nonead/nUR_MCP_SERVER'>
      <img src="https://img.shields.io/github/stars/nonead/nUR_MCP_SERVER.svg?style=flat-square&label=Stars&logo=github" alt="Github Stars"/></img>
    </a>
</p>


## 1. Qu'est-ce que le MCP ?
Le MCP (Protocole de Contexte Modèle) est un protocole de communication développé par Anthropic (open source en novembre 2024), permettant aux grands modèles d'IA (comme DeepSeek-V3-0324, DeepSeek-R1, Qwen3, etc.) d'accéder efficacement à des données/tools/services externes pour fournir des réponses plus précises et intelligentes.

Fonctionnalités principales :

Fourniture de contexte :
Transmission de fichiers/contenus de base de données
Ex : Analyse de rapports avant réponse

Appel d'outils externes :
Interaction avec systèmes locaux/distance (fichiers, API, matériel)
Ex : Organisation automatique de documents

Création de flux de travail :
Combinaison de services MCP pour des tâches complexes

Sécurité des données :
Exécution locale protégeant la confidentialité

## 2. Fonctionnement du MCP
Architecture client-serveur :

Client MCP : Application IA (émet des requêtes)
Serveur MCP : Fournit des interfaces
Communication : Basée sur JSON-RPC 2.0

## 3. Fonctions du serveur MCP
Accès aux données :
Fichiers/BDD/mémoire
Exécution d'opérations :
Fonctions prédéfinies (SQL, sauvegarde)
Notifications dynamiques :
Mises à jour en temps réel
Gestion de session :
Maintenance des connexions

## 2. Fonctions principales du serveur nUR MCP  

Description technique du produit nUR_MCP_SERVER développé par Nonead Corporation

Aperçu du produit:
nUR_MCP_SERVER est un système middleware intelligent de contrôle de robot construit sur le protocole d'interface MCP (Model Control Protocol), intégrant un grand modèle linguistique (LLM) pour permettre le contrôle interactif en langage naturel des robots industriels. Ce produit adopte une architecture Client-Server et prend en charge une intégration approfondie avec toute la gamme de robots collaboratifs Universal Robots, révolutionnant le paradigme traditionnel de programmation par teach pendant.

Architecture technologique clé:
1. Moteur d'analyse sémantique
Module de traitement NLP avec architecture Transformer multicouche, prenant en charge l'analyse contextuelle des commandes (Contextual Command Parsing), permettant une conversion de bout en bout du langage naturel en commandes de contrôle robotique avec une précision de reconnaissance de 98.6%.

2. Système de génération dynamique de scripts
Framework de génération de code basé sur LLM, convertissant automatiquement les commandes en langage naturel en scripts de contrôle URScript, avec vérification syntaxique et validation de sécurité en temps réel, offrant une efficacité de génération 12 fois supérieure à la programmation traditionnelle.

3. Interface de contrôle multimodale
- Couche d'extension du protocole MCP: prend en charge la communication double mode TCP/UDP, fournissant une réponse aux commandes en microsecondes
- Couche d'abstraction des périphériques: permet une connexion standardisée des plugins URCap
- Bus de données: basé sur le protocole Ethernet TCP/IP, permettant le contrôle coordonné multi-machines

Caractéristiques principales:
▶ Contrôle instantané en langage naturel
Commande directe des mouvements du robot (contrôle de position, planification de trajectoire, opérations E/S) via commandes vocales/textuelles, avec injection dynamique de paramètres et correction de mouvement en temps réel.

▶ Système intelligent de collecte de données
- Collecte en temps réel de données d'état 12D (couple articulaire, position de l'effecteur)
- Prise en charge de règles de filtrage définies en langage naturel
- Génération automatique de rapports structurés (CSV/JSON/XLSX)

▶ Contrôle coordonné multi-robots
Basé sur un algorithme distribué d'ordonnancement des tâches, avec le MCP-Client développé par Tord, peut gérer simultanément ≤12 robots UR, prenant en charge les commandes vocales en cascade et l'orchestration de tâches multi-appareils.

▶ Module d'apprentissage adaptatif
Cadre d'entraînement incrémental intégré, optimisant continuellement les relations commande-action via les retours utilisateurs, avec un cycle d'apprentissage ≤24h.

Spécifications techniques:
- Latence de réponse: <200ms (end-to-end)
- Compatibilité des protocoles: MCP v2.1+ / URScript v5.0+
- Capacité de traitement concurrent: 200+ TPS

**Présentation du tableau de classification des fonctionnalités de l'outil nUR_MCP_SERVER :**  

| ID outil (nUR_MCP_SERVER) | Catégorie | Description | Paramètres clés |
|------------------------|----------|----------|----------|
| ffWzqSZlUpjFfVITKvBb-b | Gestion connexion | Connecter robot UR | `ip`: IP robot |
| fx5l9Mb_BUs_hClarGKZIo | Gestion connexion | Déconnecter robot UR | `ip`: IP robot |
| f04vj-Fwbuo8s2oYu252pR | Surveillance état | Obtenir durée fonctionnement robot | `ip`: IP robot |
| f2SHZtIYF_OhS8LuslKt8D | Opération registre | Lire valeur registre Int(0-23) | `ip`: IP robot, `index`: index registre(0-23) |
| fjLf_89qRxYDlEKo_oXADQ | Opération registre | Lire valeur registre Double(0-23) | `ip`: IP robot, `index`: index registre(0-23) |
| f9uXSEQB1UZMXmgIyPtVH9 | Opération registre | Lire valeur registre Double(0-31) | `ip`: IP robot, `index`: index registre(0-31) |
| fBHQbdS9p_BPv97XBAau8a | Info appareil | Obtenir numéro série robot | `ip`: IP robot |
| fcHIfX-J83SvH0V6XZ59A7 | Contrôle mouvement | Obtenir coordonnées TCP temps réel | `ip`: IP robot |
| fwloSfxAGiC_4rjdaZjUng | Contrôle mouvement | Obtenir angles articulation temps réel | `ip`: IP robot |
| fFg2TP6jf3XTWytLIf9fyO | Contrôle mouvement | Envoyer commande posture articulation | `ip`: IP robot, `q`: angles articulation(radian), `a/v/t/r`: paramètres mouvement |
| fBevTU5BWNdVNEKgqLV5d1 | Contrôle mouvement | Envoyer commande déplacement linéaire TCP | `ip`: IP robot, `pose`: position TCP, `a/v/t/r`: paramètres mouvement |
| fnPhKVsDYRrB_Cf1wlsitI | Contrôle mouvement | Déplacement linéaire axe X | `ip`: IP robot, `distance`: distance(mètre) |
| fO55CY6Jw_iASo5NkxTm3l | Contrôle mouvement | Déplacement linéaire axe Y | `ip`: IP robot, `distance`: distance(mètre) |
| fs3ppclCfK_x0ZzFaOKHMk | Contrôle mouvement | Déplacement linéaire axe Z | `ip`: IP robot, `distance`: distance(mètre) |
| f18oyor3ddLJHMdPpyer45 | Contrôle programme | Charger programme UR | `ip`: IP robot, `program_name`: nom programme |
| fQyW6AYZjmMiGL0unOVK0W | Contrôle programme | Charger et exécuter programme UR | `ip`: IP robot, `program_name`: nom programme |
| fDxcON3qGCkzR5n9jSS5vQ | Contrôle programme | Arrêter programme actuel | `ip`: IP robot |
| fXB2Q94gpe30w1JHgZh_yr | Contrôle programme | Mettre en pause programme actuel | `ip`: IP robot |
| fyXhJEun99j0N-5ojAzPYu | Surveillance état | Obtenir tension actuelle | `ip`: IP robot |
| fYvUCtj-7VJIdbm1FA6cg8 | Surveillance état | Obtenir courant actuel | `ip`: IP robot |
| fno_OQmW5X_c3HK8M3r_NV | Surveillance état | Obtenir tension articulation | `ip`: IP robot |
| fPc54VdscRk2hmlEc3VwYg | Surveillance état | Obtenir courant articulation | `ip`: IP robot |
| fAKuhJVkwgI4NbTKQ-xsoM | Surveillance état | Obtenir température articulation | `ip`: IP robot |
| fjZheWqG9gz8SO78UgN6v7 | Surveillance état | Obtenir état fonctionnement | `ip`: IP robot |
| f2XEU4pWT2dsXI2rMsGfEw | Surveillance état | Obtenir état exécution programme | `ip`: IP robot |
| fYLTKblGKQserA-ZvLXCAt | Info appareil | Obtenir version logicielle | `ip`: IP robot |
| f2ebXFoN8bP3Pm1zocshdN | Info appareil | Obtenir mode sécurité | `ip`: IP robot |
| f_5wAr6iv97d1jurrEmhNp | Contrôle programme | Envoyer programme script | `ip`: IP robot, `script`: contenu script |
| fI3ZhZJZafBt33eNGD0ydQ | Contrôle mouvement | Mouvement circulaire | `ip`: IP robot, `center`: position TCP centre, `r`: rayon(mètre), `coordinate`: type plan |


## 3. Clause de non-responsabilité

Avant d'utiliser le nUR MCP Server, assurez-vous que les opérateurs ont suivi la formation de sécurité UR et maîtrisent les procédures d'arrêt d'urgence (E-stop).

Il est recommandé d'inspecter régulièrement l'état du robot et du MCP Server pour garantir la stabilité et la sécurité du système.

Lors de l'utilisation du nUR MCP Server, les normes de sécurité suivantes doivent être strictement respectées :

Zone de vision directe du robot

L'opérateur doit toujours maintenir le robot Universal Robots dans son champ de vision pour un contrôle visuel en temps réel.

Il est interdit de quitter la zone d'opération pendant le fonctionnement du robot afin d'intervenir immédiatement en cas d'incident.

Sécurisation de l'environnement

Vérifiez et dégagez les obstacles avant la mise en marche du robot pour éviter toute intrusion de personnel, équipement ou objet dans la zone dangereuse.

Installez si nécessaire des barrières physiques ou des rideaux lumineux de sécurité pour restreindre l'accès non autorisé.

Exemption de responsabilité en cas de non-conformité

En cas de blessure, dommage matériel ou accident dû au non-respect des exigences de sécurité (ex: absence de surveillance, zone non sécurisée), nous déclinons toute responsabilité légale et obligation de compensation.

L'utilisateur assume l'ensemble des risques et conséquences liés à l'opération.

**Pour utiliser avec Cline, ajoutez la configuration du serveur :**
MacOS & Linux :

    {
      "mcpServers": {
        "nUR_MCP_SERVER": {
            "command": "python",
            "args": ["/home/nonead/MCP_Server/nUR_MCP_SERVER/main.py"]
         }
      }
    }

Windows :

    {
      "mcpServers": {
        "nUR_MCP_SERVER": {
            "command": "cmd",
            "args": ["/c","python","D:\\MyProgram\\MCP_SERVER\\nUR_MCP_SERVER\\main.py"]
         }
      }
    }


### 5.2 Basé sur la boîte à outils (pour les développeurs)

#### 5.2.1 Moteur & Dépendances 

* **Version système recommandée :**

  ```text
  Utilisateurs macOS : macOS Monterey 12.6 ou version ultérieure
  Utilisateurs Linux : CentOS 7 / Ubuntu 20.04 ou version ultérieure
  Utilisateurs Windows : Windows 10 LTSC 2021 ou version ultérieure
  ```

* **Exigences logicielles :**

  Environnement serveur MCP

  ```text
  Python 3.11 ou version ultérieure     
  pip 25.1 ou version ultérieure
  UV Package Manager 0.6.14 ou version ultérieure  
  bun 1.2.8 ou version ultérieure
  ```
  Modèle de langage large LLM

  ```text
  DeepSeek-V3-0324 ou version ultérieure
  DeepSeek-R1-671b ou version ultérieure 
  Qwen3-235b-a22b ou version ultérieure
  
  Les modèles de langage larges prenant généralement en charge MCP sont utilisables. Les modèles non listés n'ont pas été testés
  Les modèles déployés via Ollama ne peuvent actuellement pas appeler les outils. En cours de résolution...
  ```

#### 5.1.2 Installation  

**Installation du serveur MCP :**  
1. Installez Python 3.11 ou ultérieur  
2. Installez pip 25.1 ou ultérieur  
3. Installez UV Package Manager 0.6.14 ou ultérieur  
4. Installez bun 1.2.8 ou ultérieur  
5. Installez le serveur MCP :  
```
git clone https://gitee.com/nonead/nUR_MCP_SERVER.git  
cd nUR_MCP_SERVER  
pip install -r requirements.txt  
```  

**Configuration du client MCP :**  

**Pour utiliser avec Claude Desktop, ajoutez la configuration serveur :**
**Pour macOS :** ~/Library/Application Support/Claude/claude_desktop_config.json  
```
{
  "mcpServers": {
    "nUR_MCP_SERVER": {
      "command": "python",
      "args": ["/home/nonead/MCP_Server/nUR_MCP_SERVER/main.py"]
    }
  }
}
```

**Pour Windows :** %APPDATA%/Claude/claude_desktop_config.json  
```
{
  "mcpServers": {
    "nUR_MCP_SERVER": {
      "command": "python",
      "args": ["D:\\MyProgram\\MCP_SERVER\\nUR_MCP_SERVER\\main.py"]
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
      "command": "python",
      "args": [
        "/home/nonead/MCP_Server/nUR_MCP_SERVER/main.py"
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
      "command": "python",
      "args": [
        "D:\\MyProgram\\MCP_SERVER\\nUR_MCP_SERVER\\main.py"
      ]
    }
  }
}
```

**To use with Cline, add server configuration:**  

**Pour macOS & Linux :**   
```
{
  "mcpServers": {
    "nUR_MCP_SERVER": {
      "command": "python",
      "args": ["/home/nonead/MCP_Server/nUR_MCP_SERVER/main.py"]
    }
  }
}
```

**Pour Windows :**  
```
{
  "mcpServers": {
    "nUR_MCP_SERVER": {
      "command": "python",
      "args": ["D:\\MyProgram\\MCP_SERVER\\nUR_MCP_SERVER\\main.py"]
    }
  }
}
```

### 5.2 Toolkit-Based (For Developers)  

#### 5.2.1 Engine & Dependencies  

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

  **LLM Large Language Models**  

  ```text  
  DeepSeek-V3-0324 or later  
  DeepSeek-R1-671b or later  
  Qwen3-235b-a22b or later  

  Generally, any LLM supporting MCP is usable. Untested models are not guaranteed.  
  Ollama-deployed models currently cannot invoke Tools (under resolution)...  
  ```  

#### 5.2.2 Installation

**Pour développeurs macOS/Linux/Windows**

```text
Python 3.11 ou supérieur
pip 25.1 ou supérieur
Gestionnaire de paquets UV 0.6.14 ou supérieur
bun 1.2.8 ou supérieur
```

#### 5.2.3 Utilisation

Voici des exemples de tâches que vous pouvez faire exécuter par un modèle linguistique étendu :

* Connexion du robot Universal IP : 192.168.1.199
* Obtenir les coordonnées de pose actuelles de l'effecteur terminal TCP du robot Universal
* Lister toutes les commandes de l'outil nUR_MCP_SERVER
* Obtenir toutes les données matérielles du robot Universal
* Exécuter un programme de script du robot Universal
* Exécuter le programme intégré XXXX.urp du robot Universal
* Définir le robot Universal avec IP 172.22.109.141 comme robot A et IP 172.22.98.41 comme robot B, les connecter, enregistrer les poses TCP actuelles et positions clés des robots A (gauche) et B (droite), analyser leurs relations de pose.
* Exécution étape par étape : robot Universal IP 192.168.1.199, enregistrer la pose TCP actuelle, puis déplacer TCP de +20mm en Z, -50mm en Y, +30mm en X, répéter 5 fois.
* Écrire et exécuter un script pour robot Universal : dessiner un cercle de 50mm de rayon dans le plan de base centré sur la pose actuelle.
* Définir le robot IP 172.22.109.141 comme A et 172.22.98.41 comme B, les connecter, les commandes suivantes ne contrôleront que A tout en synchronisant le mouvement miroir de B.

## 6. Architecture technique

MCP adopte une architecture client-serveur, implémentant la communication entre modèles et ressources externes via des protocoles standardisés.  
![alt](./images/MCP.svg "mcp")
Modèle client-serveur
Composants clés de l'architecture MCP :

Hôte MCP : Application LLM initiant la connexion (comme Claude Desktop ou IDE)
Client MCP : Client protocolaire maintenant une connexion 1:1 avec le serveur dans l'application hôte
Serveur MCP : Programme léger exposant des fonctionnalités via le Model Context Protocol standardisé
Sources de données locales : Fichiers, bases de données et services accessibles en toute sécurité par le serveur MCP
Services distants : Systèmes externes accessibles via Internet (par exemple via API)
Responsabilités des composants :

Hôte MCP :
Fournir l'interface utilisateur
Gérer la connexion avec le fournisseur LLM
Intégrer le client MCP pour accéder aux ressources externes
Client MCP :
Établir et maintenir la connexion avec le serveur MCP
Envoyer des requêtes et recevoir des réponses
Traiter les échanges de données conformément au protocole MCP
Serveur MCP :
Traiter les requêtes des clients
Exécuter des fonctionnalités spécifiques ou fournir un accès aux ressources
Formater les réponses selon le standard du protocole MCP
Protocole de communication
MCP utilise JSON-RPC 2.0 comme protocole de communication de base, supportant:  
![alt](./images/p.svg "mcp_json-RPC2.0")  
Requêtes : Messages initiant des opérations du client vers le serveur ou vice versa
Réponses : Réponses aux requêtes, contenant résultats ou informations d'erreur
Notifications : Messages unidirectionnels ne nécessitant pas de réponse (généralement pour notifications d'événements)
MCP supporte plusieurs mécanismes de transport :

Entrée/sortie standard (Stdio) : Pour serveurs locaux, via communication inter-processus
Événements envoyés par le serveur (SSE) : Mécanisme de transport basé sur HTTP pour serveurs distants

Avantages de MCP
MCP présente des avantages significatifs par rapport aux méthodes d'intégration traditionnelles, notamment en termes d'uniformité, sécurité et extensibilité.

Uniformité
MCP résout le problème de fragmentation des méthodes d'intégration traditionnelles via une interaction standardisée entre systèmes d'IA et sources de données externes :

Connexion plug-in : Accès unifié à diverses sources de données via un protocole standardisé
Compatibilité multiplateforme : Support de différents modèles et plateformes d'IA
Simplification du développement : Les développeurs peuvent se concentrer sur la logique métier
Sécurité
MCP intègre des mécanismes de sécurité pour protéger les données pendant le transfert et le traitement :

Protection des informations sensibles : Clés API, données utilisateurs, etc.
Contrôle d'accès : Le serveur MCP peut implémenter un contrôle d'accès granulaire
Traitement local : Évite le téléchargement d'informations sensibles vers des plateformes tierces
Extensibilité
La conception modulaire de MCP offre une grande extensibilité :

Connexion multi-services : Plusieurs services peuvent se connecter à tout client compatible
Écosystème extensible : De plus en plus de composants préconstruits disponibles
Capacité de personnalisation : Les développeurs peuvent créer des serveurs MCP personnalisés

## 7. Contact

**GitHub**: <https://github.com/nonead/nUR_MCP_SERVER>  
**gitee**: <https://gitee.com/nonead/nUR_MCP_SERVER>  
**Site officiel**: <https://www.nonead.com>  

<img src="./images/QR.gif" alt="Contact: Nonead Tech WeChat" width="200">  

## 8. Différences entre nUR MCP Server et les autres serveurs MCP

Les utilisateurs du serveur nUR MCP doivent avoir une conscience de sécurité très élevée et avoir suivi une formation à l'utilisation des robots Universal Robots, car les modèles linguistiques avancés opèrent sur de vrais robots. Une mauvaise manipulation peut entraîner des blessures corporelles et des dommages matériels, soyez très prudent.

## 9. Citation

Si vous utilisez ce logiciel, veuillez citer comme suit :

* [nURMCP: NONEAD Uninversal-Robots Model Context Protocol Server](https://www.nonead.com)
* Nonead illustre la véritable signification de la fabrication intelligente, en pionnier des innovations qui redéfinissent notre monde. <br>
  Nonead demonstrates the true meaning of intelligent manufacturing, pioneering innovations that reshape our world.

## 10. Licence

Ce projet adopte un modèle de double licence segmenté par utilisateur (User-Segmented Dual Licensing).

**Principes fondamentaux**
* Utilisateurs individuels et entreprises/organisations de 10 personnes ou moins : Licence publique générale GNU Affero v3.0 (AGPLv3) appliquée par défaut
* Entreprises/organisations de plus de 10 personnes : Licence commerciale (Commercial License) obligatoire

Définition "10 personnes ou moins" :
Désigne le nombre total de personnes physiques au sein de votre organisation (y compris sociétés, organisations à but non lucratif, agences gouvernementales, établissements d'enseignement ou toute autre entité) ayant accès, utilisant ou bénéficiant directement/indirectement des fonctionnalités du logiciel (nUR_MCP_SERVER), n'excédant pas 10 personnes. Cela inclut notamment les développeurs, testeurs, opérateurs, utilisateurs finaux, utilisateurs via systèmes intégrés, etc.

### 10.1 Licence open source (Open Source License) : AGPLv3 - Pour particuliers et organisations ≤10 personnes
* Si vous êtes un utilisateur individuel ou si votre organisation répond à la définition "≤10 personnes", vous pouvez utiliser, modifier et distribuer nUR_MCP_SERVER librement sous AGPLv3. Le texte complet est disponible sur https://www.gnu.org/licenses/agpl-3.0.html
* **Obligation clé :** AGPLv3 impose que si vous modifiez nUR_MCP_Server et le fournissez comme service réseau ou distribuez une version modifiée, vous devez fournir le code source complet aux destinataires sous AGPLv3. Même pour les structures ≤10 personnes, si vous souhaitez éviter cette obligation de divulgation, une licence commerciale (voir ci-dessous) est nécessaire.
* Lisez attentivement toutes les clauses d'AGPLv3 avant utilisation.

### 10.2 Licence commerciale (Commercial License) - Pour organisations >10 personnes ou souhaitant éviter les obligations AGPLv3
* **Exigence impérative :** Si votre organisation **ne** répond **pas** à la définition "≤10 personnes" (≥11 personnes accédant/utilisant/bénéficiant du logiciel), vous **devez** obtenir une licence commerciale pour utiliser nUR_MCP_SERVER.
* **Choix volontaire :** Même pour les organisations ≤10 personnes, si votre usage **ne respecte pas** AGPLv3 (notamment l'obligation de divulgation du code source) ou nécessite des clauses commerciales **non fournies** par AGPLv3 (garanties, indemnisation, absence de restriction Copyleft...), une licence commerciale est **requise**.
* **Cas typiques nécessitant une licence commerciale (liste non exhaustive) :**
  * Organisation >10 personnes
  * (Taille indifférente) Distribution de versions modifiées sans divulguer le code source modifié comme exigé par AGPLv3
  * (Taille indifférente) Fourniture de services SaaS basés sur nUR_MCP_SERVER modifié sans partager le code source modifié aux utilisateurs
  * (Taille indifférente) Politique d'entreprise, contrats clients ou exigences projet interdisant les logiciels sous AGPLv3 ou requérant distribution propriétaire/confidentialité
* **Obtenir une licence :** Contactez l'équipe de développement à service@nonead.com.

### 10.3 Contributions
* Nous encourageons les contributions communautaires. Toute contribution soumise au projet est réputée fournie sous AGPLv3.
* En soumettant une contribution (ex : Pull Request), vous acceptez que votre code soit licencié sous AGPLv3 pour ce projet et tous les utilisateurs ultérieurs (qu'ils suivent AGPLv3 ou la licence commerciale).
* Vous acceptez aussi que votre contribution puisse être incluse dans des versions commerciales de nUR_MCP_SERVER.

### 10.4 Autres dispositions
* Les termes précis des licences commerciales sont définis dans les contrats signés.
* Les mainteneurs se réservent le droit de modifier cette politique de licence (y compris les seuils). Les mises à jour seront communiquées via les canaux officiels (dépôt de code, site web).


## 11. Équipe de développement principale

Équipe de développement du serveur MCP de Suzhou Nonead Robot Technology Co., Ltd.

**Tony Ke** <tonyke@nonead.com>  
**Micro Zhu** <microzhu@nonead.com>  
**Anthony Zhuang** <anthonyzhuang@nonead.com>  
**Quentin Wang** <quentinwang@nonead.com>