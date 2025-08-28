#!/usr/bin/env python3
"""
سكريبت تشخيص للتطبيق على Render
يستخدم للتحقق من صحة النشر والإعدادات
"""

import os
import sys
import subprocess
import requests
from datetime import datetime

def check_environment():
    """التحقق من متغيرات البيئة"""
    print("🔍 فحص متغيرات البيئة...")

    port = os.environ.get("PORT", "غير محدد")
    python_version = os.environ.get("PYTHON_VERSION", "غير محدد")
    render_env = os.environ.get("RENDER", "غير محدد")

    print(f"📍 PORT: {port}")
    print(f"🐍 PYTHON_VERSION: {python_version}")
    print(f"🌐 RENDER: {render_env}")

    return port, python_version

def check_dependencies():
    """التحقق من التبعيات"""
    print("\n📦 فحص التبعيات...")

    try:
        import flet
        print("✅ Flet متوفر")
    except ImportError:
        print("❌ Flet غير متوفر")

    try:
        import weasyprint
        print("✅ WeasyPrint متوفر")
    except ImportError:
        print("❌ WeasyPrint غير متوفر")

    try:
        import requests
        print("✅ Requests متوفر")
    except ImportError:
        print("❌ Requests غير متوفر")

def check_network_connectivity():
    """التحقق من الاتصال بالشبكة"""
    print("\n🌐 فحص الاتصال بالشبكة...")

    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            print("✅ الاتصال بالإنترنت يعمل")
        else:
            print(f"⚠️ استجابة غير طبيعية: {response.status_code}")
    except Exception as e:
        print(f"❌ مشكلة في الاتصال: {str(e)}")

def check_flet_configuration():
    """التحقق من إعدادات Flet"""
    print("\n🎨 فحص إعدادات Flet...")

    # فحص إصدار Flet
    try:
        import flet
        print(f"✅ إصدار Flet: {flet.__version__}")
    except:
        print("❌ لا يمكن قراءة إصدار Flet")

    # فحص المنفذ المطلوب
    port = os.environ.get("PORT", "8000")
    print(f"📍 المنفذ المطلوب: {port}")

def generate_diagnostic_report():
    """إنشاء تقرير تشخيصي"""
    print("\n📊 إنشاء تقرير تشخيصي...")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""
=== تقرير تشخيصي لـ Web Scraper Pro ===
تاريخ التشخيص: {timestamp}
===========================================

متغيرات البيئة:
- PORT: {os.environ.get('PORT', 'غير محدد')}
- PYTHON_VERSION: {os.environ.get('PYTHON_VERSION', 'غير محدد')}
- RENDER: {os.environ.get('RENDER', 'غير محدد')}

إصدار Python: {sys.version}

نظام التشغيل: {sys.platform}

===========================================
"""

    print(report)

    # حفظ التقرير
    try:
        with open("diagnostic_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print("✅ تم حفظ التقرير في diagnostic_report.txt")
    except Exception as e:
        print(f"❌ خطأ في حفظ التقرير: {str(e)}")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشخيص تطبيق Web Scraper Pro...")
    print("=" * 50)

    check_environment()
    check_dependencies()
    check_network_connectivity()
    check_flet_configuration()
    generate_diagnostic_report()

    print("\n" + "=" * 50)
    print("✅ انتهى التشخيص!")
    print("📄 راجع التقرير في diagnostic_report.txt")

if __name__ == "__main__":
    main()
