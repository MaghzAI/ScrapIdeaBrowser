#!/usr/bin/env python3
"""
بديل لتشغيل التطبيق بدون مشاكل Flutter
يستخدم Streamlit بدلاً من Flet للنشر على Render
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import time
import browser_cookie3
import json

# إعدادات الصفحة
st.set_page_config(
    page_title="Web Scraper Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS لتحسين المظهر
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .success { border-left-color: #4CAF50; background-color: #f8fff8; }
    .error { border-left-color: #f44336; background-color: #fff8f8; }
    .warning { border-left-color: #ff9800; background-color: #fffef8; }
    .info { border-left-color: #2196F3; background-color: #f8fbff; }
</style>
""", unsafe_allow_html=True)

class StreamlitScraperApp:
    def __init__(self):
        self.session = requests.Session()
        self.scraped_urls = set()
        self.failed_urls = set()

    def main(self):
        """الواجهة الرئيسية"""
        st.markdown("""
        <div class="main-header">
            <h1>🚀 Web Scraper Pro</h1>
            <p>أداة متقدمة لكشط صفحات الويب</p>
        </div>
        """, unsafe_allow_html=True)

        # الشريط الجانبي
        with st.sidebar:
            st.header("⚙️ إعدادات")
            self.show_settings()

        # المحتوى الرئيسي
        tab1, tab2, tab3 = st.tabs(["🏠 الرئيسية", "📊 الإحصائيات", "📋 السجل"])

        with tab1:
            self.show_main_interface()

        with tab2:
            self.show_statistics()

        with tab3:
            self.show_logs()

    def show_settings(self):
        """إعدادات التطبيق"""
        st.subheader("🌐 إعدادات الاتصال")

        # النطاق
        self.domain = st.text_input(
            "النطاق (Domain)",
            value="ideabrowser.com",
            help="مثال: github.com, stackoverflow.com"
        )

        # اختيار المتصفح
        self.browser = st.selectbox(
            "المتصفح لاستخراج الكوكيز",
            ["auto", "chrome", "firefox", "edge", "safari", "opera"],
            index=1,
            help="البحث التلقائي موصى به"
        )

        # زر استخراج الكوكيز
        if st.button("🔐 استخراج Cookies واختبار الاتصال", type="primary"):
            self.extract_cookies_and_test()

    def show_main_interface(self):
        """الواجهة الرئيسية"""
        st.subheader("🔍 إعدادات الكشط")

        col1, col2 = st.columns(2)

        with col1:
            self.main_url = st.text_input(
                "رابط الصفحة الرئيسية",
                value="https://www.ideabrowser.com/idea-of-the-day",
                help="الصفحة التي تحتوي على الروابط"
            )

            self.element_id = st.text_input(
                "معرف العنصر (ID/Class)",
                value="main-wrapper",
                help="العنصر الذي يحتوي على الروابط"
            )

        with col2:
            self.depth = st.selectbox(
                "عمق الكشط",
                ["1", "2", "3", "unlimited"],
                index=1,
                help="عدد المستويات للكشط"
            )

            self.export_format = st.selectbox(
                "تنسيق التصدير",
                ["markdown", "pdf", "both"],
                index=2,
                help="تنسيق حفظ المحتوى"
            )

        # مجلد الحفظ
        self.save_folder = st.text_input(
            "مجلد الحفظ",
            value=str(Path.home() / "ScrapedContent"),
            help="المجلد لحفظ الملفات"
        )

        # أزرار التحكم
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🚀 بدء الكشط", type="primary", use_container_width=True):
                self.start_scraping()

        with col2:
            if st.button("⏸️ إيقاف", use_container_width=True):
                st.warning("⚠️ هذه الميزة ستكون متاحة قريباً")

        with col3:
            if st.button("🔄 إعادة تعيين", use_container_width=True):
                st.success("✅ تم إعادة تعيين التطبيق")

    def show_statistics(self):
        """عرض الإحصائيات"""
        st.subheader("📊 إحصائيات الكشط")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("الصفحات المكشوطة", len(self.scraped_urls), "✅")

        with col2:
            st.metric("الصفحات الفاشلة", len(self.failed_urls), "❌")

        with col3:
            st.metric("الروابط المكتشفة", len(self.scraped_urls) + len(self.failed_urls), "🔗")

        with col4:
            success_rate = 0
            if len(self.scraped_urls) + len(self.failed_urls) > 0:
                success_rate = (len(self.scraped_urls) / (len(self.scraped_urls) + len(self.failed_urls))) * 100
            st.metric("نسبة النجاح", ".1f")

        # قائمة الروابط
        if self.scraped_urls:
            st.subheader("✅ الصفحات المكشوطة بنجاح")
            for url in list(self.scraped_urls)[:10]:  # أظهر أول 10 روابط فقط
                st.write(f"• {url}")

        if self.failed_urls:
            st.subheader("❌ الصفحات الفاشلة")
            for url in list(self.failed_urls)[:5]:  # أظهر أول 5 روابط فقط
                st.write(f"• {url}")

    def show_logs(self):
        """عرض السجل"""
        st.subheader("📋 سجل العمليات")

        if not hasattr(st.session_state, 'logs'):
            st.session_state.logs = []

        # عرض السجل
        for log_entry in reversed(st.session_state.logs[-20:]):  # أظهر آخر 20 إدخال
            timestamp, message, log_type = log_entry
            if log_type == "success":
                st.success(f"[{timestamp}] {message}")
            elif log_type == "error":
                st.error(f"[{timestamp}] {message}")
            elif log_type == "warning":
                st.warning(f"[{timestamp}] {message}")
            else:
                st.info(f"[{timestamp}] {message}")

    def log(self, message, log_type="info"):
        """إضافة رسالة للسجل"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if not hasattr(st.session_state, 'logs'):
            st.session_state.logs = []
        st.session_state.logs.append((timestamp, message, log_type))

    def extract_cookies_and_test(self):
        """استخراج الكوكيز واختبار الاتصال"""
        with st.spinner("🔄 استخراج الكوكيز..."):
            try:
                # استخراج الكوكيز
                if self.browser == "auto":
                    browsers = ["chrome", "firefox", "edge", "safari", "opera"]
                    cookies_found = False
                    for browser_name in browsers:
                        try:
                            if browser_name == "chrome":
                                cookies = browser_cookie3.chrome(domain_name=self.domain)
                            elif browser_name == "firefox":
                                cookies = browser_cookie3.firefox(domain_name=self.domain)
                            elif browser_name == "edge":
                                cookies = browser_cookie3.edge(domain_name=self.domain)
                            elif browser_name == "safari":
                                cookies = browser_cookie3.safari(domain_name=self.domain)
                            elif browser_name == "opera":
                                cookies = browser_cookie3.opera(domain_name=self.domain)

                            cookies_list = list(cookies)
                            if cookies_list:
                                # إضافة الكوكيز للجلسة
                                for cookie in cookies_list:
                                    self.session.cookies.set(
                                        cookie.name,
                                        cookie.value,
                                        domain=cookie.domain,
                                        path=cookie.path
                                    )
                                self.log(f"✅ تم العثور على {len(cookies_list)} كوكي في {browser_name}", "success")
                                cookies_found = True
                                break
                        except:
                            continue

                    if not cookies_found:
                        self.log("❌ لم يتم العثور على كوكيز", "error")
                        return
                else:
                    # استخراج من متصفح محدد
                    try:
                        if self.browser == "chrome":
                            cookies = browser_cookie3.chrome(domain_name=self.domain)
                        elif self.browser == "firefox":
                            cookies = browser_cookie3.firefox(domain_name=self.domain)
                        elif self.browser == "edge":
                            cookies = browser_cookie3.edge(domain_name=self.domain)
                        elif self.browser == "safari":
                            cookies = browser_cookie3.safari(domain_name=self.domain)
                        elif self.browser == "opera":
                            cookies = browser_cookie3.opera(domain_name=self.domain)

                        cookies_list = list(cookies)
                        for cookie in cookies_list:
                            self.session.cookies.set(
                                cookie.name,
                                cookie.value,
                                domain=cookie.domain,
                                path=cookie.path
                            )
                        self.log(f"✅ تم استخراج {len(cookies_list)} كوكي", "success")
                    except Exception as e:
                        self.log(f"❌ خطأ في استخراج الكوكيز: {str(e)}", "error")
                        return

                # اختبار الاتصال
                test_url = f"https://{self.domain}"
                try:
                    response = self.session.get(test_url, timeout=10)
                    if response.status_code == 200:
                        self.log("✅ نجح اختبار الاتصال! جاهز للكشط", "success")
                        st.success("🎉 نجح اختبار الاتصال! جاهز للكشط")
                    else:
                        self.log(f"⚠️ رمز الاستجابة: {response.status_code}", "warning")
                        st.warning(f"⚠️ رمز الاستجابة: {response.status_code}")
                except Exception as e:
                    self.log(f"❌ خطأ في الاختبار: {str(e)}", "error")
                    st.error(f"❌ خطأ في الاختبار: {str(e)}")

            except Exception as e:
                self.log(f"❌ خطأ عام: {str(e)}", "error")
                st.error(f"❌ خطأ عام: {str(e)}")

    def start_scraping(self):
        """بدء عملية الكشط"""
        if not self.main_url or not self.element_id:
            st.error("❌ يرجى إكمال جميع الحقول المطلوبة")
            return

        with st.spinner("🚀 بدء عملية الكشط..."):
            self.log("🚀 بدء الكشط المتقدم", "success")

            try:
                # جلب محتوى الصفحة الرئيسية
                content = self.get_page_content(self.main_url)
                if not content:
                    st.error("❌ فشل في جلب محتوى الصفحة الرئيسية")
                    return

                # حفظ المحتوى
                success = self.save_content(self.main_url, content, self.save_folder)
                if success:
                    self.scraped_urls.add(self.main_url)
                    self.log("💾 تم حفظ المحتوى بنجاح", "success")
                    st.success("🎉 تم إكمال الكشط بنجاح!")
                else:
                    self.failed_urls.add(self.main_url)
                    self.log("❌ فشل في حفظ المحتوى", "error")
                    st.error("❌ فشل في حفظ المحتوى")

            except Exception as e:
                self.log(f"💥 خطأ في الكشط: {str(e)}", "error")
                st.error(f"💥 خطأ في الكشط: {str(e)}")

    def get_page_content(self, url):
        """جلب محتوى الصفحة"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ar,en-US,en;q=0.5',
            }

            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text

        except Exception as e:
            self.log(f"❌ خطأ في جلب {url}: {str(e)}", "error")
            return None

    def save_content(self, url, content, folder):
        """حفظ المحتوى"""
        try:
            # إنشاء المجلد إذا لم يكن موجوداً
            os.makedirs(folder, exist_ok=True)

            # حفظ كـ Markdown
            if self.export_format in ["markdown", "both"]:
                success_md = self.save_as_markdown(url, content, folder)
            else:
                success_md = True

            # حفظ كـ PDF (إذا كان متاحاً)
            if self.export_format in ["pdf", "both"]:
                success_pdf = self.save_as_pdf(url, content, folder)
            else:
                success_pdf = True

            return success_md and success_pdf

        except Exception as e:
            self.log(f"❌ خطأ في حفظ المحتوى: {str(e)}", "error")
            return False

    def save_as_markdown(self, url, content, folder):
        """حفظ كـ Markdown"""
        try:
            from urllib.parse import urlparse
            import html2text

            # تحليل HTML
            soup = BeautifulSoup(content, 'html.parser')

            # إنشاء اسم الملف
            parsed_url = urlparse(url)
            if url == self.main_url:
                filename = "main_page.md"
            else:
                filename = "page.md"

            filepath = os.path.join(folder, filename)

            # تحويل إلى Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            markdown_content = h.handle(str(soup))

            # حفظ الملف
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            file_size = os.path.getsize(filepath) / 1024
            self.log(f"📝 تم حفظ Markdown: {filename} ({file_size:.1f} KB)", "success")
            return True

        except Exception as e:
            self.log(f"❌ خطأ في حفظ Markdown: {str(e)}", "error")
            return False

    def save_as_pdf(self, url, content, folder):
        """حفظ كـ PDF"""
        try:
            from weasyprint import HTML
            from urllib.parse import urlparse

            # تحليل HTML
            soup = BeautifulSoup(content, 'html.parser')

            # إنشاء اسم الملف
            parsed_url = urlparse(url)
            if url == self.main_url:
                filename = "main_page.pdf"
            else:
                filename = "page.pdf"

            filepath = os.path.join(folder, filename)

            # تحويل إلى PDF
            html_doc = HTML(string=str(soup))
            html_doc.write_pdf(filepath)

            file_size = os.path.getsize(filepath) / 1024
            self.log(f"📄 تم حفظ PDF: {filename} ({file_size:.1f} KB)", "success")
            return True

        except Exception as e:
            self.log(f"❌ خطأ في حفظ PDF: {str(e)}", "error")
            return False

# تشغيل التطبيق
if __name__ == "__main__":
    app = StreamlitScraperApp()
    app.main()
