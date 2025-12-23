
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



## 1. ما هو MCP؟
بروتوكول سياق النموذج (MCP) هو بروتوكول اتصالات طورته Anthropic (مفتوح المصدر نوفمبر 2024)، يمكّن نماذج الذكاء الاصطناعي الكبيرة (مثل DeepSeek-V3-0324، DeepSeek-R1، Qwen3) من الوصول الفعال إلى البيانات/الأدوات/الخدمات الخارجية.

الميزات الرئيسية:

توفير السياق:
نقل الملفات/محتوى قواعد البيانات
مثال: تحليل التقارير قبل الإجابة

دمج الأدوات:
التحكم في الأنظمة المحلية/البعيدة
مثال: تنظيم المستندات آليًا

أتمتة العمليات:
دمج خدمات MCP المتعددة

حماية البيانات:
التنفيذ المحلي يحمي المعلومات

## 2. آلية العمل
هندسة خادم-عميل:

عميل MCP: تطبيق الذكاء الاصطناعي (يرسل الطلبات)
خادم MCP: يوفر واجهات البيانات
التواصل: وفق معيار JSON-RPC 2.0

## 3. وظائف الخادم
الوصول للبيانات:
الملفات/قواعد البيانات/الذاكرة
تنفيذ العمليات:
وظائف محددة مسبقًا (استعلامات SQL إلخ)
الإشعارات الديناميكية:
تحديثات فورية
إدارة الجلسات:
الحفاظ على الاتصالات

## 2. نواة خادم nUR MCP الأساسية  

الوصف الفني لمنتج nUR_MCP_SERVER المطور بواسطة Nonead Corporation

نظرة عامة على المنتج:
nUR_MCP_SERVER هو نظام وسيط للتحكم الذكي في الروبوتات مبني على بروتوكول واجهة MCP (Model Control Protocol)، متكامل مع نماذج اللغة الكبيرة (LLM) لتمكين التحكم التفاعلي باللغة الطبيعية في الروبوتات الصناعية. يعتمد المنتج على تصميم بنية العميل-الخادم ويدعم التكامل العميق مع سلسلة روبوتات Universal Robots التعاونية، مما يحدث ثورة في نموذج التحكم التقليدي عبر teach pendant.

الهندسة التقنية الأساسية:
1. محرك التحليل الدلالي
وحدة معالجة اللغة الطبيعية (NLP) متعددة الطبقات ببنية Transformer، تدعم تحليل الأوامر السياقي (Contextual Command Parsing) بدقة تصل إلى 98.6% للتعرف على الأوامر.

2. نظام توليد النصوص الديناميكي
إطار عمل لتوليد الأكواد يعتمد على LLM يحول أوامر اللغة الطبيعية تلقائياً إلى نصوص تحكم URScript، مع دعم التحقق النحوي والسلامة في الوقت الفعلي، وكفاءة توليد تزيد 12 ضعفاً عن البرمجة التقليدية.

3. واجهة تحكم متعددة الوسائط
- طبقة توسيع بروتوكول MCP: تدعم اتصال TCP/UDP المزدوج، مع استجابة للأوامر في مستوى الميكروثانية
- طبقة تجريد الأجهزة: تمكين الاتصال الموحد لملحقات URCap
- ناقل البيانات: يعتمد على بروتوكول TCP/IP للتحكم المتعدد في الروبوتات

الميزات الرئيسية:
▶ التحكم الفوري باللغة الطبيعية
توجيه حركات الروبوت مباشرة (التحكم في الوضعية، تخطيط المسار، عمليات الإدخال/الإخراج) عبر أوامر صوتية/نصية، مع دعم حقن المعلمات الديناميكية وتصحيح الحركة في الوقت الحقيقي.

▶ نظام جمع البيانات الذكي
- جمع بيانات الحالة 12 بعدياً (عزم المفاصل، وضعية نهاية الذراع) في الوقت الحقيقي
- دعم قواعد تصفية البيانات المعرفة باللغة الطبيعية
- توليد تقارير بيانات منظمة تلقائياً (CSV/JSON/XLSX)

▶ التحكم المتعدد في الروبوتات
يعتمد على خوارزمية توزيع المهام، مع عميل MCP من Tord لإدارة ≤12 روبوت UR معاً، ويدعم الأوامر الصوتية المتتالية وتنسيق المهام عبر الأجهزة.

▶ وحدة التعلم التكيفي
إطار عمل تدريبي تزايدي مدمج يحسن باستمرار علاقة التخطيط بين الأوامر-الإجراءات عبر ملاحظات المستخدمين، مع دورة تعلم ≤24 ساعة.

المواصفات الفنية:
- زمن استجابة الأوامر: <200 مللي ثانية (من البداية للنهاية)
- توافق البروتوكولات: MCP v2.1+ / URScript v5.0+
- قدرة المعالجة المتزامنة: 200+ TPS

**جدول تصنيف وظائف أداة nUR_MCP_SERVER:**  

| معرف الأداة | فئة الوظيفة | وصف الوظيفة | المعلمات الرئيسية |
|--------|----------|----------|----------|
| fkUCFg7YmxSflgfmJawHeo (`connect_ur`) | إدارة الاتصال | الاتصال بروبوت UR | ip:عنوان الروبوت |
| fcr4pIqoIXyxh3ko9FOsWU (`disconnect_ur`) | إدارة الاتصال | قطع اتصال روبوت UR | ip:عنوان الروبوت |
| fNKAydKkxHwmGFgyrePBsN (`get_time`) | مراقبة الحالة | الحصول على مدة التشغيل (ثانية) | ip:عنوان الروبوت |
| fYTMsGvSRpUdWmURng7kGX (`get_log_int`) | عمليات السجل | الحصول على إخراج سجل Int (0-23) | ip:عنوان الروبوت, index:فهرس السجل |
| fvfqDMdDJer6kpbCzwFL1D (`get_log_double_0_23`) | عمليات السجل | الحصول على إخراج سجل Double (0-23) | ip:عنوان الروبوت, index:فهرس السجل |
| fCJ6sRw9m0ArdZ-MCaeNWK (`get_log_double_0_31`) | عمليات السجل | الحصول على إخراج سجل Double (0-31) | ip:عنوان الروبوت, index:فهرس السجل |
| f_ZXAIUv-eqHelwWxrzDHe (`get_serial_number`) | معلومات الجهاز | الحصول على الرقم التسلسلي | ip:عنوان الروبوت |
| fZ2ALt5kD50gV9AdEgBrRO (`get_robot_model`) | معلومات الجهاز | الحصول على الموديل | ip:عنوان الروبوت |
| fEtHcw5RNF54X9RYIEU-1m (`get_actual_tcp_pose`) | تحريك الحركة | الحصول على إحداثيات TCP في الوقت الحقيقي | ip:عنوان الروبوت |
| ftsb2AsiqiPqSBxHIwALOx (`get_actual_joint_pose`) | تحريك الحركة | الحصول على زوايا المفاصل في الوقت الحقيقي | ip:عنوان الروبوت |
| fXmkr4PLkHKF0wgQGEHzLt (`movej`) | تحريك الحركة | إرسال أمر وضعية المفاصل | ip:عنوان الروبوت, q:زوايا المفاصل(راديان) |
| fWdukQrgFZeK-DEcST4AwO (`movel`) | تحريك الحركة | إرسال أمر حركة خطية TCP | ip:عنوان الروبوت, pose:موضع TCP |
| f2gbgju7QsymJa4wPgZQ0T (`movel_x`) | تحريك الحركة | حركة خطية محور X | ip:عنوان الروبوت, distance:مسافة الحركة(متر) |
| fS6rCxVp498s5edU7jCMB3 (`movel_y`) | تحريك الحركة | حركة خطية محور Y | ip:عنوان الروبوت, distance:مسافة الحركة(متر) |
| fJps7j-T3lwzXhp8p0_suy (`movel_z`) | تحريك الحركة | حركة خطية محور Z | ip:عنوان الروبوت, distance:مسافة الحركة(متر) |
| fTMj5413O5CzsORAyBYXj8 (`load_program`) | تحكم البرنامج | تحميل برنامج UR | ip:عنوان الروبوت, program_name:اسم البرنامج |
| fqiYJ1c9fqCs5eYd-yKEeJ (`load_and_run_program`) | تحكم البرنامج | تحميل وتنفيذ برنامج UR | ip:عنوان الروبوت, program_name:اسم البرنامج |
| fW6-wrPoqm2bE3bMgtLbLP (`stop_program`) | تحكم البرنامج | إيقاف البرنامج الحالي | ip:عنوان الروبوت |
| fsEmm-VX3CCY_XvnCDms7f (`pause_program`) | تحكم البرنامج | إيقاف البرنامج الحالي مؤقتًا | ip:عنوان الروبوت |
| f83-fUQBd-YRSdIQDpuYmW (`get_actual_robot_voltage`) | مراقبة الحالة | الحصول على الجهد الحالي | ip:عنوان الروبوت |
| foMoD2L690vRdQxdW_gRNl (`get_actual_robot_current`) | مراقبة الحالة | الحصول على التيار الحالي | ip:عنوان الروبوت |
| fDZBXqofuIb-7IjS6t2YJ2 (`get_actual_joint_voltage`) | مراقبة الحالة | الحصول على جهد المفاصل | ip:عنوان الروبوت |
| fgAa_kwSmXmvld6Alx39ij (`get_actual_joint_current`) | مراقبة الحالة | الحصول على تيار المفاصل | ip:عنوان الروبوت |
| furAKHVnYvORJ9R7N7vpbl (`get_joint_temperatures`) | مراقبة الحالة | الحصول على درجة حرارة المفاصل | ip:عنوان الروبوت |
| fuNb7TgOgWNukjAVjusMN4 (`get_robot_mode`) | مراقبة الحالة | الحصول على حالة التشغيل | ip:عنوان الروبوت |
| fD12XJtqjgI46Oufwt928c (`get_program_state`) | مراقبة الحالة | الحصول على حالة تنفيذ البرنامج | ip:عنوان الروبوت |
| fMLa2mjlactTbD_CCKB1tX (`get_ur_software_version`) | معلومات الجهاز | الحصول على إصدار البرنامج | ip:عنوان الروبوت |
| fWXQKGQ6J5mas9K9mGPK3x (`get_safety_mode`) | معلومات الجهاز | الحصول على وضع الأمان | ip:عنوان الروبوت |
| f81vKugz9xnncjirTC3B6A (`get_programs`) | تحكم البرنامج | الحصول على قائمة البرامج | ip:عنوان الروبوت, username/password:بيانات اعتماد SSH |
| ffaaQZeknwwTISLYdYqM0_ (`send_program_script`) | تحكم البرنامج | إرسال نص برنامج | ip:عنوان الروبوت, script:محتوى النص |
| fsWlT3tCOn1ub-kUZCrq7E (`draw_circle`) | تحريك الحركة | حركة دائرية | ip:عنوان الروبوت, center:موضع TCP المركز, r:نصف القطر(متر) |
| f7y1QpjnA9s1bzfLeOkTnS (`draw_square`) | تحريك الحركة | رسم مربع | ip:عنوان الروبوت, origin:موضع TCP البداية, border:طول الضلع(متر) |
| fuN_LLSc22VKXWXwbwNARo (`draw_rectangle`) | تحريك الحركة | رسم مستطيل | ip:عنوان الروبوت, origin:موضع TCP البداية, width/height:العرض/الارتفاع(متر) |

ملاحظة: جميع الأدوات تتطلب اتصالاً مسبقاً بالروبوت.

## 3. إخلاء المسؤولية

قبل استخدام nUR MCP Server، تأكد من تدريب المشغلين على سلامة روبوتات UR ومعرفتهم بإيقاف الطوارئ (E-stop).

افحص الروبوت والخوادم بانتظام لضمان الاستقرار.

التزم بالبروتوكولات التالية عند الاستخدام:

الرؤية المباشرة للروبوت

يجب أن يبقى روبوت Universal Robots ضمن مجال رؤية المشغل للمراقبة الفورية.

يُمنع مغادرة المنطقة أثناء التشغيل.

تأمين البيئة

أزل العوائق وتأكد من خلو المنطقة الخطرة من الأشخاص/الأشياء.

ضع حواجز مادية أو ستائر ضوئية عند الحاجة.

تنصل قانوني

نحن غير مسؤولين عن الإصابات أو الأضرار الناجمة عن عدم الامتثال للاشتراطات (مثل الإهمال أو عدم التأمين).

المستخدم يتحمل جميع المخاطر.

## 4. إصدارات النسخ

### 4.1 التحديثات الحديثة

* **2025.05.15**: الإصدار الأولي لـ nUR_MCP_SERVER

### 4.2 الخطط المستقبلية

* تطوير عميل MCP مخصص لخادم nUR MCP لتحسين ميزات أمان المشغلات
* إضافة وظيفة تسجيل سجلات روبوتات UR
* تمكين نسخ احتياطي وتحويل برامج روبوتات UR

## 5. البدء السريع

### 5.1 حسب المنتج (للمستخدمين العاديين)

#### 5.1.1 المحرك والتبعيات

* **إصدارات النظام الموصى بها:**

  ```text
  مستخدمو macOS: macOS Monterey 12.6 أو أحدث
  مستخدمو Linux: CentOS 7 / Ubuntu 20.04 أو أحدث
  مستخدمو Windows: Windows 10 LTSC 2021 أو أحدث
  ```

* **متطلبات البرمجيات:**

  **بيئة خادم MCP**

  ```text
  Python 3.11 أو أحدث
  pip 25.1 أو أحدث
  مدير الحزم UV 0.6.14 أو أحدث
  bun 1.2.8 أو أحدث
  ```

  **عميل MCP**

  ```text
  Claude Desktop 3.7.0 أو أحدث
  Cherry Studio 1.2.10 أو أحدث
  Cline 3.14.1 أو أحدث

  ClaudeMind، Cursor، NextChat، ChatMCP، Copilot-MCP، Continue، Dolphin-MCP، Goose - لم يتم اختبارها.
  ```

  **نماذج اللغة الكبيرة LLM**

  ```text
  DeepSeek-V3-0324 أو أحدث
  DeepSeek-R1-671b أو أحدث
  Qwen3-235b-a22b أو أحدث

  بشكل عام، يمكن استخدام أي نموذج LLM مدعوم من MCP. النماذج غير المدرجة هنا لم يتم اختبارها.
  النماذج المثبتة عبر Ollama لا يمكنها حاليًا استدعاء الأدوات (قيد الحل)...
  ```

#### 5.1.2 التثبيت  

**تثبيت خادم MCP:**  
1. ثبّت بايثون 3.11 أو أحدث  
2. ثبّت pip 25.1 أو أحدث  
3. ثبّت مدير الحزم UV 0.6.14 أو أحدث  
4. ثبّت bun 1.2.8 أو أحدث  
5. ثبّت خادم MCP:  
```
git clone https://gitee.com/nonead/Nonead-Universal-Robots-MCP.git  
cd nUR_MCP_SERVER  
pip install -r requirements.txt  
```  

**تهيئة عميل MCP:**  

**لاستخدام مع Claude Desktop، أضف تكوين الخادم:**
**لـ macOS:** ~/Library/Application Support/Claude/claude_desktop_config.json  
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

**لـ Windows:** %APPDATA%/Claude/claude_desktop_config.json  
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

**لاستخدام مع Cherry Studio، أضف تكوين الخادم:**

**لـ macOS وLinux:**
```
{
  "mcpServers": {
    "nUR_MCP_SERVER": {
      "name": "nUR_MCP_Server",
      "type": "stdio",
      "description": "خادم NONEAD Universal-Robots MCP",
      "isActive": true,
      "provider": "شركة NONEAD",
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

**لـ Windows:**
```
{
  "mcpServers": {
    "nUR_MCP_SERVER": {
      "name": "nUR_MCP_Server",
      "type": "stdio",
      "description": "خادم NONEAD Universal-Robots MCP",
      "isActive": true,
      "provider": "شركة NONEAD",
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

**لاستخدامه مع Cline، أضف تكوين الخادم:**
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


### 5.2 بناءً على مجموعة الأدوات (للمطورين)

#### 5.2.1 المحرك والتبعيات 

* **إصدارات النظام الموصى بها:**

  ```text
  مستخدمو macOS: macOS Monterey 12.6 أو أحدث
  مستخدمو Linux: CentOS 7 / Ubuntu 20.04 أو أحدث
  مستخدمو Windows: Windows 10 LTSC 2021 أو أحدث
  ```

* **متطلبات البرمجيات:**

  بيئة خادم MCP

  ```text
  Python 3.11 أو أحدث     
  pip 25.1 أو أحدث
  UV Package Manager 0.6.14 أو أحدث  
  bun 1.2.8 أو أحدث
  ```
  نماذج اللغة الكبيرة LLM

  ```text
  DeepSeek-V3-0324 أو أحدث
  DeepSeek-R1-671b أو أحدث 
  Qwen3-235b-a22b أو أحدث
  
  عادةً ما تكون نماذج اللغة الكبيرة التي تدعم MCP قابلة للاستخدام. النماذج غير المدرجة لم يتم اختبارها
  النماذج الموزعة عبر Ollama لا يمكنها حاليًا استدعاء الأدوات. قيد الحل...
  ```

#### 5.2.2 التثبيت

**لمطوري macOS/Linux/Windows**

```text
  Python 3.11  أو أحدث     
  pip 25.1  أو أحدث
  UV Package Manager 0.6.14  أو أحدث  
  bun 1.2.8  أو أحدث
```

#### 5.2.3 الاستخدام

أمثلة على مهام يمكن لنماذج اللغة الكبيرة تنفيذها:

* توصيل روبوت يونيفرسال عبر IP: 192.168.1.199
* الحصول على إحداثيات وضعية أداة TCP النهائية الحالية
* سرد جميع أوامر أداة nUR_MCP_SERVER
* استرجاع جميع بيانات أجهزة روبوت يونيفرسال
* تنفيذ برنامج نصي للروبوت
* تشغيل البرنامج المدمج XXXX.urp
* تعريف روبوت IP 172.22.109.141 كـ A وIP 172.22.98.41 كـ B، توصيلهما، تسجيل أوضاع TCP الحالية والمواقع الرئيسية لـ A (يسار) وB (يمين)، تحليل العلاقة بين الأوضاع
* تنفيذ خطوة بخطوة: روبوت يونيفرسال IP 192.168.1.199، تسجيل وضع TCP الحالي، ثم تحريك +20مم في Z، -50مم في Y، +30مم في X، تكرار 5 مرات
* كتابة وتنفيذ سكريبت روبوت: رسم دائرة نصف قطرها 50مم في المستوى الأساسي متمركزة على الوضع الحالي
* تعريف روبوتات IP 172.22.109.141 كـ A و172.22.98.41 كـ B، توصيلهما، الأوامر اللاحقة تتحكم فقط في A مع مزامنة حركة مرآة لـ B

## 6. البنية التقنية

تستخدم MCP بنية عميل-خادم مع بروتوكولات معيارية للتواصل بين النموذج والموارد الخارجية.  
![alt](./images/MCP.svg "mcp")  
نموذج العميل-الخادم
المكونات الأساسية:

مضيف MCP: تطبيق LLM (مثل Claude Desktop) يبدأ الاتصالات
عميل MCP: عميل بروتوكول يحافظ على اتصال 1:1 مع الخادم
خادم MCP: برنامج خفيف يعرض وظائف عبر Model Context Protocol المعياري
مصادر البيانات المحلية: ملفات/قواعد بيانات/خدمات يصل إليها الخادم بأمان
الخدمات البعيدة: أنظمة خارجية متاحة عبر الإنترنت (مثل APIs)
المسؤوليات:

مضيف MCP:
يوفر واجهة مستخدم
يدير اتصال موفر LLM
يدمج عميل MCP للوصول إلى الموارد الخارجية
عميل MCP:
يؤسس/يحافظ على اتصال خادم MCP
يرسل الطلبات ويتلقى الردود
يتعامل مع تبادل البيانات حسب معايير MCP
خادم MCP:
يعالج طلبات العملاء
ينفذ وظائف محددة أو يوفر وصولاً للموارد
يُنسق الردود حسب معايير بروتوكول MCP
بروتوكول الاتصال
تستخدم MCP JSON-RPC 2.0 كبروتوكول أساسي، تدعم:  
![alt](./images/p.svg "mcp_json-RPC2.0")    
الطلبات: رسائل تبدأ عمليات من العميل→الخادم أو العكس
الردود: إجابات على الطلبات تحتوي نتائج أو معلومات خطأ
الإشعارات: رسائل أحادية الاتجاه لا تتطلب رداً (عادة للإخطارات)
آليات النقل المدعومة:

الإدخال/الإخراج القياسي (Stdio): للخوادم المحلية عبر اتصال بين العمليات
أحداث مرسلة من الخادم (SSE): آلية نقل تعتمد على HTTP للخوادم البعيدة

مزايا MCP
تتفوق MCP على الطرق التقليدية في التوحيد والأمان والقابلية للتوسع.

التوحيد
التفاعل المعياري يحل مشاكل التجزئة:

وصول يشبه الملحق: بروتوكول موحد لمصادر بيانات متنوعة
التوافق عبر المنصات: يدعم نماذج/منصات ذكاء اصطناعي مختلفة
تبسيط التطوير: التركيز على المنطق التجاري
الأمان
آليات أمان مدمجة تحمي البيانات:

حماية المعلومات الحساسة: مفاتيح API/بيانات المستخدم إلخ
تحكم في الوصول: خادم MCP يمكّن قيود وصول مفصلة
المعالجة المحلية: تتجنب تحميل بيانات حساسة لأطراف ثالثة
القابلية للتوسع
التصميم المعياري يمكّن قابلية توسع عالية:

اتصال متعدد الخدمات: خدمات متعددة تتصل بعملاء متوافقين
توسع النظام البيئي: مكتبة متنامية من المكونات الجاهزة
قابلية التخصيص: تطوير خوادم MCP مخصصة

## 7. اتصل بنا

**GitHub**: <https://github.com/nonead/Nonead-Universal-Robots-MCP>  
**gitee**: <https://gitee.com/nonead/Nonead-Universal-Robots-MCP>  
**الموقع الرسمي**: <https://www.nonead.com>  

<img src="./images/QR.gif" alt="للتواصل: Nonead Tech WeChat" width="200">  

## 8. الفرق بين nUR MCP Server وخوادم MCP الأخرى

يجب أن يتمتع مستخدمو nUR MCP Server بوعي أمان عالٍ جدًا وأن يكونوا قد أكملوا تدريب تشغيل روبوتات Universal، حيث يتحكم النموذج اللغوي الكبير في روبوتات فعلية. قد يتسبب التشغيل غير الصحيح في إصابات بشرية وأضرار مادية - يُرجى توخي أقصى درجات الحذر.

## 9. الاقتباس

إذا كنت تستخدم هذا البرنامج، يُرجى الاقتباس على النحو التالي:

* [nURMCP: NONEAD Universal-Robots Model Context Protocol Server](https://www.nonead.com)
* توضح Nonead المعنى الحقيقي للتصنيع الذكي، وتقود الابتكارات التي تعيد تشكيل عالمنا.

## 10. الترخيص

يعتمد هذا المشروع نموذج ترخيص مزدوج حسب فئة المستخدم (User-Segmented Dual Licensing).

**المبادئ الأساسية**
* المستخدمون الأفراد والشركات/المؤسسات التي تضم 10 أشخاص أو أقل: ينطبق عليها ترخيص جنو أفيرو العام العام v3.0 (AGPLv3) افتراضياً
* الشركات/المؤسسات التي تضم أكثر من 10 أشخاص: يجب الحصول على ترخيص تجاري (Commercial License)

تعريف "10 أشخاص أو أقل":
يقصد به العدد الإجمالي للأفراد في مؤسستك (بما في ذلك الشركات، المنظمات غير الربحية، الوكالات الحكومية، المؤسسات التعليمية أو أي كيان قانوني) الذين يمكنهم الوصول إلى البرنامج (nUR_MCP_SERVER) أو استخدامه أو الاستفادة منه بشكل مباشر أو غير مباشر، دون تجاوز 10 أشخاص. يشمل ذلك المطورين، المختبرين، المشغلين، المستخدمين النهائيين، المستخدمين عبر الأنظمة المدمجة وغيرهم.

### 10.1 ترخيص المصدر المفتوح (Open Source License): AGPLv3 - للأفراد والمؤسسات التي تضم 10 أشخاص أو أقل
* إذا كنت مستخدمًا فرديًا أو كانت مؤسستك تستوفي تعريف "10 أشخاص أو أقل" أعلاه، يمكنك استخدام nUR_MCP_SERVER وتعديله وتوزيعه بحرية تحت شروط AGPLv3. النص الكامل للترخيص متاح على https://www.gnu.org/licenses/agpl-3.0.html
* **الالتزام الرئيسي:** من متطلبات AGPLv3 الأساسية أنه إذا قمت بتعديل nUR_MCP_Server وقدمته كخدمة شبكية أو وزعت نسخة معدلة، يجب عليك توفير الكود المصدري الكامل للمستلمين تحت ترخيص AGPLv3. حتى إذا كنت تستوفي معيار "10 أشخاص أو أقل"، إذا كنت ترغب في تجنب هذا الالتزام بالإفصاح عن الكود المصدري، يجب أن تفكر في الحصول على ترخيص تجاري (انظر أدناه).
* يرجى قراءة وفهم جميع بنود AGPLv3 بعناية قبل الاستخدام.

### 10.2 الترخيص التجاري (Commercial License) - للمؤسسات التي تضم أكثر من 10 أشخاص أو الراغبين في تجنب التزامات AGPLv3
* **المتطلب الإلزامي:** إذا كانت مؤسستك **لا** تستوفي تعريف "10 أشخاص أو أقل" أعلاه (أي 11 شخصًا أو أكثر يمكنهم الوصول إلى البرنامج/استخدامه/الاستفادة منه)، **يجب** عليك الاتصال بنا للحصول على ترخيص تجاري قبل استخدام nUR_MCP_SERVER.
* **الخيار الطوعي:** حتى إذا كانت مؤسستك تستوفي شرط "10 أشخاص أو أقل"، ولكن سيناريو استخدامك **لا يتوافق مع بنود AGPLv3** (خاصةً التزام الإفصاح عن الكود المصدري)، أو كنت بحاجة إلى **شروط تجارية محددة** لا يوفرها AGPLv3 (مثل الضمانات، التعويضات، عدم وجود قيود كوبيليفت وغيرها)، **يجب** عليك أيضًا الحصول على ترخيص تجاري.
* **الحالات الشائعة التي تتطلب ترخيصًا تجاريًا (على سبيل المثال لا الحصر):**
  * حجم المؤسسة أكثر من 10 أشخاص
  * (بغض النظر عن حجم المؤسسة) الرغبة في توزيع نسخ معدلة من nUR_MCP_SERVER دون الكشف عن الكود المصدري للتعديلات وفقًا لـ AGPLv3
  * (بغض النظر عن حجم المؤسسة) تقديم خدمات شبكية (SaaS) تعتمد على nUR_MCP_SERVER المعدل دون توفير الكود المصدري المعدل لمستخدمي الخدمة وفقًا لـ AGPLv3
  * (بغض النظر عن حجم المؤسسة) سياسات الشركة، عقود العملاء أو متطلبات المشروع التي تمنع استخدام برامج مرخصة تحت AGPLv3 أو تتطلب التوزيع مغلق المصدر/السرية
* **الحصول على ترخيص تجاري:** يرجى الاتصال بفريق تطوير nUR_MCP_SERVER عبر البريد الإلكتروني service@nonead.com.

### 10.3 المساهمات (Contributions)
* نرحب بمساهمات المجتمع في nUR_MCP_SERVER. جميع المساهمات المقدمة لهذا المشروع تعتبر مرخصة تحت AGPLv3.
* من خلال تقديم مساهمة لهذا المشروع (مثلًا عبر Pull Request)، فإنك توافق على ترخيص كودك تحت AGPLv3 لهذا المشروع وجميع المستخدمين اللاحقين (بغض النظر عما إذا كان هؤلاء المستخدمون يتبعون AGPLv3 أو الترخيص التجاري).
* كما تفهم وتوافق على أن مساهمتك قد يتم تضمينها في إصدارات nUR_MCP_SERVER المرخصة تجاريًا.

### 10.4 بنود أخرى (Other Terms)
* تخضع الشروط والأحكام المحددة للترخيص التجاري للاتفاقية التجارية الموقعة.
* يحتفظ القائمون على المشروع بالحق في تحديث سياسة الترخيص هذه (بما في ذلك تعريفات حجم المستخدم والعتبات) حسب الحاجة. سيتم إعلام التحديثات عبر القنوات الرسمية للمشروع (مثل مستودع الكود، الموقع الرسمي).


## 11. فريق التطوير الأساسي

فريق تطوير خادم MCP في شركة Suzhou Nonead Robot Technology Co., Ltd.

**Tony Ke** <tonyke@nonead.com>  
**Micro Zhu** <microzhu@nonead.com>  
**Anthony Zhuang** <anthonyzhuang@nonead.com>  
**Quentin Wang** <quentinwang@nonead.com>