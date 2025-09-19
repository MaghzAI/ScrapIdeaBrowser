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
import zipfile
import smtplib
import ssl
from email.message import EmailMessage

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
        self.archives = []  # لحفظ بيانات الأرشيفات

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
            self.show_archives_table()

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
        """بدء عملية الكشط مع دعم الكشط متعدد الصفحات"""
        if not self.main_url or not self.element_id:
            st.error("❌ يرجى إكمال جميع الحقول المطلوبة")
            return

        with st.spinner("🚀 بدء عملية الكشط..."):
            self.log("🚀 بدء الكشط المتقدم", "success")
            try:
                # قائمة انتظار مع مستوى العمق
                urls_queue = [(self.main_url, 0)]  # (url, depth)
                processed_count = 0
                max_depth = self.depth
                visited = set()
                while urls_queue:
                    current_url, depth = urls_queue.pop(0)
                    if max_depth != "unlimited" and int(depth) >= int(max_depth):
                        continue
                    if current_url in visited:
                        continue
                    processed_count += 1
                    visited.add(current_url)
                    content = self.get_page_content(current_url)
                    if not content:
                        self.failed_urls.add(current_url)
                        continue
                    success = self.save_content(current_url, content, self.save_folder)
                    if success:
                        self.scraped_urls.add(current_url)
                        self.log(f"💾 تم حفظ المحتوى [{processed_count}]: {current_url}", "success")
                    else:
                        self.failed_urls.add(current_url)
                        self.log(f"❌ فشل في حفظ المحتوى: {current_url}", "error")
                    # استخراج الروابط من الصفحة الرئيسية فقط أو كل صفحة حسب العمق
                    if depth == 0:
                        new_links = self.extract_links(content, current_url, self.element_id)
                        for link in new_links:
                            if link not in visited:
                                urls_queue.append((link, depth + 1))
                # ضغط المجلد بعد الكشط
                zip_path = self.zip_folder(self.save_folder)
                st.success(f"🗜️ تم ضغط الملفات: {zip_path}")
                # إرسال الملف المضغوط إلى البريد الإلكتروني
                self.send_email_with_attachment(zip_path)
                # إضافة بيانات الأرشيف للجدول
                archive_info = {
                    "project": os.path.basename(self.save_folder),
                    "zip": zip_path,
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
                }
                self.archives.append(archive_info)
                st.success("🎉 تم إكمال الكشط لجميع الصفحات بنجاح!")
            except Exception as e:
                self.log(f"💥 خطأ في الكشط: {str(e)}", "error")
                st.error(f"💥 خطأ في الكشط: {str(e)}")

    def extract_links(self, html, base_url, element_id):
        """استخراج الروابط من الصفحة الرئيسية فقط"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        # البحث عن العنصر المحدد
        element = soup.find(id=element_id) or soup.find(class_=element_id)
        if not element:
            try:
                element = soup.select_one(element_id)
            except Exception:
                pass
        if not element:
            return links
        for link_tag in element.find_all('a', href=True):
            href = link_tag.get('href', '').strip()
            if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            full_url = requests.compat.urljoin(base_url, href)
            if requests.utils.urlparse(full_url).netloc == requests.utils.urlparse(base_url).netloc:
                clean_url = full_url.split('#')[0].rstrip('/')
                if clean_url not in links and clean_url != base_url:
                    links.append(clean_url)
        return list(set(links))

    def zip_folder(self, folder_path):
        """ضغط المجلد المحدد إلى ملف ZIP"""
        zip_path = folder_path.rstrip(os.sep) + ".zip"
        base, ext = os.path.splitext(zip_path)
        i = 1
        while os.path.exists(zip_path):
            zip_path = f"{base}_{i}{ext}"
            i += 1
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, os.path.dirname(folder_path))
                    zf.write(full_path, arcname=rel_path)
        return zip_path

    def send_email_with_attachment(self, file_path):
        """إرسال البريد الإلكتروني مع المرفق إلى dsyemen2020@gmail.com"""
        try:
            SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
            SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
            USER = os.environ.get("SMTP_USER", "")
            PASSWORD = os.environ.get("SMTP_PASS", "")
            TO = "dsyemen2020@gmail.com"
            if not USER or not PASSWORD:
                st.warning("⚠️ لم يتم تعيين بيانات SMTP (SMTP_USER/SMTP_PASS)")
                return
            msg = EmailMessage()
            msg["Subject"] = f"نتائج كشط الويب - {os.path.basename(file_path)}"
            msg["From"] = USER
            msg["To"] = TO
            msg.set_content(f"""
السلام عليكم ورحمة الله وبركاته،

تم الانتهاء من عملية كشط الويب بنجاح.

تفاصيل المشروع:
• اسم المشروع: {os.path.basename(file_path).replace('.zip', '')}
• اسم الملف: {os.path.basename(file_path)}
• التاريخ والوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• حجم الملف: {os.path.getsize(file_path) / (1024*1024):.2f} ميجابايت

مع تحيات،
Web Scraper Pro
""")
            with open(file_path, "rb") as f:
                file_data = f.read()
            msg.add_attachment(file_data, maintype="application", subtype="zip", filename=os.path.basename(file_path))
            context = ssl.create_default_context()
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.starttls(context=context)
                smtp.login(USER, PASSWORD)
                smtp.send_message(msg)
            st.success(f"📧 تم إرسال الأرشيف إلى {TO}")
        except Exception as e:
            st.error(f"❌ خطأ في إرسال البريد: {str(e)}")

    def show_archives_table(self):
        """عرض جدول الأرشيفات مع روابط التحميل"""
        if self.archives:
            st.subheader("📂 ملخص الأرشيفات المحفوظة")
            df = pd.DataFrame(self.archives)
            def make_download_link(zip_path):
                if os.path.exists(zip_path):
                    return f'<a href="file://{zip_path}" download>تحميل</a>'
                return "غير متوفر"
            df['تحميل'] = df['zip'].apply(make_download_link)
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

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
