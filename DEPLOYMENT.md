# Web Scraper Pro - Deployment on Render

## إعداد النشر على Render

تم تجهيز التطبيق للنشر على Render مع الملفات التالية:

### الملفات المضافة:
- `Procfile`: يحدد كيفية تشغيل التطبيق
- `render.yaml`: تكوين النشر التلقائي
- `runtime.txt`: إصدار Python المطلوب

### خطوات النشر:

1. **رفع الكود إلى GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **النشر على Render:**
   - اذهب إلى [render.com](https://render.com)
   - اضغط "New" → "Web Service"
   - اربط repository الخاص بك
   - اختر الإعدادات التالية:
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python ScrapWeb.py`
   - أضف متغير البيئة: `PORT` = `10000`

3. **متطلبات إضافية:**
   - التطبيق يستخدم wkhtmltopdf لإنشاء ملفات PDF
   - قد يحتاج إلى تكوين إضافي على Render لدعم wkhtmltopdf

## ملاحظات مهمة:

- تأكد من أن جميع المتطلبات في `requirements.txt` محدثة
- اختبر التطبيق محلياً قبل النشر
- Render قد يحتاج وقت للبناء والنشر (حوالي 5-10 دقائق)

---

**Web Scraper Pro** © 2025 - جاهز للنشر على Render
