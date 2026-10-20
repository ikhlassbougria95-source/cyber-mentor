# CyberMentor (FREE) - with 30-day course
<img width="1240" height="588" alt="Capture d’écran_20-10-2026_111116_localhost" src="https://github.com/user-attachments/assets/ac70e1f0-482e-4e80-b7a6-f9e356024584" />

# 🛡️ CyberMentor - AI Security Mentor & Learning Assistant

**CyberMentor** هو تطبيق ومساعد ذكي تفاعلي مخصص لمجال الأمن السيبراني، يتيح للمستخدمين التعلم وتلقي التوجيه الأمني وتدقيق الأكواد من خلال دمج نماذج الذكاء الاصطناعي المحلية والسحابية (Hybrid LLM Architecture).

---

## ✨ المميزات الرئيسية (Key Features)

- **مرونة النماذج (Hybrid AI Models):** يدعم التشغيل المحلي عبر **Ollama (Llama 3.2)** للحفاظ على الخصوصية، أو الربط السحابي مع **Google Gemini API** للسرعة والتقييم المتقدم.
- **منهج سيبراني متكامل:** يدمج مساراً تعليمياً وتفاعلياً يمتد لـ 30 يوماً متضمنة الدروس والموارد (`curriculum.json`).
- **تحليل وتوجيه أمني:** يساعد في فهم الثغرات الأمنية واكتشاف الأخطاء البرمجية واقتراح الحلول.
- **واجهة خفيفة وسريعة:** خادم خلفي مبني بلغة Python يسهل تشغيله محلياً أو نشره.

---

## 🛠️ التقنيات المستخدمة (Tech Stack)

- **Language:** Python
- **AI Runtimes & Frameworks:** Ollama (Llama 3.2), Google Gemini API
- **Backend:** Python (Flask / Server API)
- **Data & Curriculum:** JSON Structured Storage

---

## 🚀 طريقة التشغيل (Quick Start Guide)

### 1️⃣ الاستخدام المحلي مع Ollama (Local & Free)

لتشغيل التطبيق باستخدام نموذج محلي مجاني عبر Ollama:

```cmd
set PROVIDER=ollama
set FAST_MODEL=llama3.2:3b
python server.py
