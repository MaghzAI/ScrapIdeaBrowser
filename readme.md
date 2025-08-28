# Web Scraper Pro

🚀 **Web Scraper Pro** هو تطبيق متقدم لكشط صفحات الويب المحمية والمفتوحة، مع دعم تصدير المحتوى إلى Markdown و PDF، وواجهة عربية احترافية سهلة الاستخدام.

## الميزات الرئيسية
- كشط ذكي للمواقع مع دعم الكوكيز (Cookies) من المتصفح
- تنظيف تلقائي للمحتوى من العناصر غير المرغوبة (رؤوس، أقدام، إعلانات، إلخ)
- تصدير المحتوى إلى ملفات Markdown أو PDF أو كليهما
- إحصائيات مباشرة عن عدد الصفحات المكشوطة والفاشلة والروابط المكتشفة
- سجل عمليات مفصل مع تصنيف للعمليات الناجحة والفاشلة
- دعم اختيار عمق الكشط وعدة إعدادات متقدمة
- واجهة رسومية مبنية على Flet تدعم اللغة العربية بالكامل

## المتطلبات
- Python 3.8+
- المتصفحات المدعومة: Chrome, Firefox, Edge, Safari, Opera (لاستخراج الكوكيز)
- الحزم البرمجية:
  - flet
  - requests
  - beautifulsoup4
  - pdfkit
  - browser_cookie3
  - html2text

> **ملاحظة:** لحفظ PDF يجب تثبيت أداة `wkhtmltopdf` على جهازك.

## التثبيت

1. ثبت الحزم المطلوبة:
   ```bash
   pip install -r requirements.txt
   ```
2. (اختياري لحفظ PDF) ثبت wkhtmltopdf:
   - على Ubuntu/Debian:
     ```bash
     sudo apt install wkhtmltopdf
     ```
   - على Windows: [حمل الأداة من هنا](https://wkhtmltopdf.org/downloads.html)

## التشغيل

شغل التطبيق بالأمر:
```bash
python ScrapWeb.py
```

## طريقة الاستخدام
1. أدخل النطاق (Domain) وحدد المتصفح لاستخراج الكوكيز.
2. اضغط على "استخراج Cookies واختبار الاتصال".
3. أدخل رابط الصفحة الرئيسية ومعرف العنصر الذي يحتوي على الروابط.
4. اختر مجلد الحفظ وإعدادات الكشط والتصدير.
5. اضغط "بدء الكشط الذكي".
6. تابع التقدم والسجل والإحصائيات من الواجهة.

## النشر على Render - دليل استكشاف الأخطاء

### 🚀 الحل المقترح: استخدام Streamlit (موصى به)

بسبب مشاكل توافق Flutter في Flet، تم إنشاء نسخة بديلة باستخدام **Streamlit** والتي تعمل بسلاسة على Render.

#### خطوات النشر باستخدام Streamlit:

1. **استبدال ملف Procfile:**
   ```bash
   cp Procfile.streamlit Procfile
   ```

2. **رفع الكود:**
   ```bash
   git add .
   git commit -m "إضافة نسخة Streamlit محسّنة للنشر"
   git push origin main
   ```

3. **إعداد متغيرات البيئة في Render:**
   ```
   PORT = 10000
   PYTHON_VERSION = 3.13
   ```

4. **التطبيق سيعمل على:**
   `https://your-app-name.onrender.com`

#### مميزات نسخة Streamlit:
- ✅ **لا توجد مشاكل Flutter** - تعمل بسلاسة على جميع المنصات
- ✅ **أداء أفضل** - تحميل أسرع واستجابة أكبر
- ✅ **دعم كامل لـ Render** - مُحسّن خصيصاً للنشر السحابي
- ✅ **واجهة حديثة** - تصميم جميل وسهل الاستخدام
- ✅ **نفس الوظائف** - كشط الويب، PDF، Markdown

### البديل: إصلاح مشاكل Flet

إذا أردت الاستمرار مع Flet، إليك الحلول للمشاكل الشائعة:

#### 🐛 خطأ Flutter Build Compatibility:
```bash
Uncaught (in promise) FlutterLoader could not find a build compatible...
```

**الحلول:**
1. **تغيير web_renderer:**
   ```python
   web_renderer="html"  # بدلاً من "auto"
   ```

2. **تحديث إعدادات المتصفح:**
   - تأكد من دعم المتصفح لـ WebAssembly
   - جرب متصفحات مختلفة (Chrome, Firefox, Edge)

3. **تنظيف cache:**
   ```bash
   # أعد تشغيل التطبيق مع إعدادات جديدة
   python ScrapWeb.py
   ```

#### 🔌 مشاكل WebSocket:
```bash
WebSocket connection to 'wss://.../ws' failed
WebSocketChannelException: WebSocket connection failed
```

**الحلول:**
1. **التأكد من إعدادات البورت:**
   - تأكد من أن `PORT=10000` في متغيرات البيئة
   - تأكد من أن التطبيق يستخدم `host="0.0.0.0"`

2. **إعدادات الـ CORS:**
   - Render يحتاج إعدادات CORS خاصة
   - تأكد من إعداد `route_url_strategy="path"`

3. **بدائل أخرى:**
   - استخدم HTTP-only mode إذا أمكن
   - جرب منصات أخرى مثل Railway أو Heroku

#### 🎨 مشاكل الخطوط (Fonts):
```bash
Could not find a set of Noto fonts to display all missing characters
```

**الحل:**
- هذا خطأ بصري فقط، لا يؤثر على وظائف التطبيق
- يمكن تجاهله أو إضافة خطوط مخصصة

### بدائل النشر:

إذا استمرت مشاكل Flet، جرب هذه البدائل:

1. **Railway.app** - أفضل دعم لـ WebSocket
2. **Heroku** - سهل الاستخدام
3. **Vercel** - سريع للتطبيقات الثابتة
4. **Fly.io** - ممتاز للتطبيقات الديناميكية

---

## 🎯 التوصية النهائية

**استخدم نسخة Streamlit** لأنها:
- أكثر استقراراً على Render
- لا تحتوي على مشاكل Flutter
- سهلة الصيانة والتطوير
- تدعم جميع ميزات التطبيق الأصلية

للتبديل إلى Streamlit:
```bash
cp Procfile.streamlit Procfile
git add .
git commit -m "التبديل إلى نسخة Streamlit"
git push origin main
```

---

**Web Scraper Pro** © 2025