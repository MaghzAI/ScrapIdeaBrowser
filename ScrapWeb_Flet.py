#  Old By Flet
import flet as ft
import requests
from bs4 import BeautifulSoup
import os
from weasyprint import HTML, CSS
from urllib.parse import urljoin, urlparse
import threading
from datetime import datetime
import time
import browser_cookie3
import json
from pathlib import Path
import html2text
import re
import zipfile
import smtplib
import ssl
from email.message import EmailMessage
import traceback

class WebScraperApp:
    def __init__(self):
        self.scraped_urls = set()
        self.failed_urls = set()
        self.is_scraping = False
        self.is_paused = False
        self.session = requests.Session()
        self.main_url = None
        self.total_found_links = 0
        
        # محول HTML إلى Markdown
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.ignore_emphasis = False
        self.html_converter.body_width = 0  # لا تقطع الأسطر
        
    def main(self, page: ft.Page):
        """الوظيفة الرئيسية لإنشاء الواجهة المحسنة"""
        page.title = "🚀 Web Scraper Pro - الإصدار المتقدم"
        page.window.width = 1200
        page.window.height = 900
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        
        # الألوان المحسنة
        primary_color = ft.Colors.INDIGO_600
        secondary_color = ft.Colors.BLUE_GREY_600
        success_color = ft.Colors.TEAL_600
        error_color = ft.Colors.RED_600
        warning_color = ft.Colors.AMBER_600
        accent_color = ft.Colors.PURPLE_600
        
        # شريط علوي احترافي
        app_bar = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WEB_ASSET_ROUNDED, size=32, color=ft.Colors.WHITE),
                ft.Text(
                    "Web Scraper Pro", 
                    size=24, 
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.INFO_OUTLINE,
                    icon_color=ft.Colors.WHITE,
                    tooltip="معلومات التطبيق",
                    on_click=self.show_about
                ),
            ], alignment=ft.MainAxisAlignment.START),
            bgcolor=primary_color,
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            border_radius=ft.border_radius.only(bottom_left=15, bottom_right=15)
        )
        
        # المحتوى الرئيسي مع scroll
        main_scroll = ft.Column(
            [
                # قسم إعدادات الاتصال
                self.create_connection_section(primary_color, accent_color),
                
                # قسم إعدادات الكشط
                self.create_scraping_section(primary_color, secondary_color),
                
                # قسم إعدادات التصدير
                self.create_export_section(primary_color, success_color),
                
                # أزرار التحكم
                self.create_control_section(success_color, error_color, warning_color),
                
                # قسم الإحصائيات
                self.create_stats_section(primary_color, success_color, error_color, warning_color),
                
                # قسم السجل
                self.create_logs_section(primary_color),
                
                # شريط الحالة
                self.create_status_bar(),
                
                # مساحة إضافية في النهاية
                ft.Container(height=20)
            ],
            spacing=20,
            scroll=ft.ScrollMode.ALWAYS,
            auto_scroll=False
        )
        
        # التخطيط الرئيسي
        main_container = ft.Container(
            content=ft.Column([
                app_bar,
                ft.Container(
                    content=main_scroll,
                    padding=ft.padding.all(20),
                    expand=True
                )
            ]),
            expand=True
        )
        
        page.add(main_container)
        
        # تشغيل مؤقت الإحصائيات
        self.start_time = None
        self.update_timer()
    
    def create_connection_section(self, primary_color, accent_color):
        """قسم إعدادات الاتصال المحسن"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # العنوان مع أيقونة
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.COOKIE_ROUNDED, color=accent_color, size=28),
                            ft.Text("🔐 إعدادات الاتصال والمصادقة", 
                                   size=20, weight=ft.FontWeight.BOLD, color=primary_color),
                            ft.Container(expand=True),
                            ft.Chip(
                                label=ft.Text("متقدم", size=12),
                                bgcolor=ft.Colors.PURPLE_50,
                                color=accent_color
                            )
                        ], alignment=ft.MainAxisAlignment.START),
                        margin=ft.margin.only(bottom=15)
                    ),
                    
                    # الحقول في صفوف منظمة
                    ft.Row([
                        ft.Container(
                            content=ft.TextField(
                                label="🌐 النطاق (Domain)",
                                hint_text="مثال: github.com, stackoverflow.com",
                                value="ideabrowser.com",
                                prefix_icon=ft.Icons.DOMAIN_ROUNDED,
                                helper_text="النطاق بدون https:// أو www",
                                border_radius=12,
                                filled=True,
                                bgcolor=ft.Colors.GREY_50,
                                ref=self.create_domain_ref()
                            ),
                            expand=2
                        ),
                        ft.Container(width=15),
                        ft.Container(
                            content=ft.Dropdown(
                                label="🖥 المتصفح",
                                options=[
                                    ft.dropdown.Option("auto", "🔍 البحث التلقائي (موصى به)"),
                                    ft.dropdown.Option("chrome", "🌐 Google Chrome"),
                                    ft.dropdown.Option("firefox", "🦊 Mozilla Firefox"),
                                    ft.dropdown.Option("edge", "🌊 Microsoft Edge"),
                                    ft.dropdown.Option("safari", "🧭 Safari (macOS)"),
                                    ft.dropdown.Option("opera", "🎭 Opera"),
                                ],
                                value="chrome",
                                border_radius=12,
                                filled=True,
                                bgcolor=ft.Colors.GREY_50,
                                ref=self.create_browser_ref()
                            ),
                            expand=1
                        )
                    ]),
                    
                    # زر الاختبار المحسن
                    ft.Container(
                        content=ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.WIFI_FIND_ROUNDED, size=20),
                                ft.Text("استخراج Cookies واختبار الاتصال", size=14, weight=ft.FontWeight.W_500)
                            ], alignment=ft.MainAxisAlignment.CENTER, tight=True),
                            on_click=self.test_cookies,
                            style=ft.ButtonStyle(
                                bgcolor=accent_color,
                                color=ft.Colors.WHITE,
                                padding=ft.padding.symmetric(horizontal=25, vertical=15),
                                shape=ft.RoundedRectangleBorder(radius=12),
                                elevation=3
                            ),
                            width=300
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.symmetric(vertical=10)
                    ),
                    
                    # نصائح محسنة
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.LIGHTBULB_OUTLINE_ROUNDED, color=ft.Colors.AMBER_600, size=20),
                                ft.Text("نصائح للحصول على أفضل النتائج:", 
                                       weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_800)
                            ]),
                            ft.Text("• تأكد من تسجيل دخولك في الموقع المستهدف من المتصفح", size=12),
                            ft.Text("• أغلق المتصفح إذا فشل استخراج Cookies", size=12),
                            ft.Text("• استخدم 'البحث التلقائي' للعثور على Cookies في جميع المتصفحات", size=12),
                        ], spacing=5),
                        bgcolor=ft.Colors.AMBER_50,
                        padding=15,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.AMBER_200)
                    )
                ], spacing=15),
                padding=25
            ),
            elevation=4,
            shadow_color=primary_color,
            surface_tint_color=ft.Colors.INDIGO_50
        )
    
    def create_scraping_section(self, primary_color, secondary_color):
        """قسم إعدادات الكشط المحسن"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # العنوان
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SETTINGS_ROUNDED, color=secondary_color, size=28),
                            ft.Text("⚙️ إعدادات الكشط الذكي", 
                                   size=20, weight=ft.FontWeight.BOLD, color=primary_color),
                            ft.Container(expand=True),
                            ft.Chip(
                                label=ft.Text("ذكي", size=12),
                                bgcolor=ft.Colors.BLUE_50,
                                color=secondary_color
                            )
                        ]),
                        margin=ft.margin.only(bottom=15)
                    ),
                    
                    # رابط الصفحة الرئيسية
                    ft.TextField(
                        label="🔗 رابط الصفحة الرئيسية",
                        hint_text="https://www.ideabrowser.com/idea-of-the-day",
                        value="https://www.ideabrowser.com/idea-of-the-day",
                        prefix_icon=ft.Icons.LINK_ROUNDED,
                        helper_text="الصفحة التي تحتوي على الروابط المطلوب كشطها",
                        border_radius=12,
                        filled=True,
                        bgcolor=ft.Colors.GREY_50,
                        ref=self.create_url_ref()
                    ),
                    
                    # الصف الأول من الإعدادات
                    ft.Row([
                        ft.Container(
                            content=ft.TextField(
                                label="🎯 معرف العنصر (ID/Class)",
                                hint_text="main-wrapper أو .content",
                                value="main-wrapper",
                                prefix_icon=ft.Icons.CODE_ROUNDED,
                                helper_text="العنصر الذي يحتوي على الروابط",
                                border_radius=12,
                                filled=True,
                                bgcolor=ft.Colors.GREY_50,
                                ref=self.create_element_id_ref()
                            ),
                            expand=1
                        ),
                        ft.Container(width=15),
                        ft.Container(
                            content=ft.Dropdown(
                                label="📊 عمق الكشط",
                                options=[
                                    ft.dropdown.Option("1", "🎯 مستوى واحد (سريع)"),
                                    ft.dropdown.Option("2", "📖 مستويين (متوسط)"),
                                    ft.dropdown.Option("3", "📚 ثلاثة مستويات (شامل)"),
                                    ft.dropdown.Option("unlimited", "♾️ غير محدود (عميق)"),
                                ],
                                value="2",
                                border_radius=12,
                                filled=True,
                                bgcolor=ft.Colors.GREY_50,
                                ref=self.create_depth_ref()
                            ),
                            expand=1
                        )
                    ]),
                    
                    # مجلد الحفظ
                    ft.Row([
                        ft.Container(
                            content=ft.TextField(
                                label="📁 مجلد الحفظ",
                                hint_text="اختر مجلد لحفظ الملفات المكشوطة",
                                value=str(Path.home() / "ScrapedContent"),
                                prefix_icon=ft.Icons.FOLDER_ROUNDED,
                                read_only=True,
                                border_radius=12,
                                filled=True,
                                bgcolor=ft.Colors.GREY_50,
                                ref=self.create_folder_ref()
                            ),
                            expand=2
                        ),
                        ft.Container(width=10),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.FOLDER_OPEN_ROUNDED, size=18),
                                ft.Text("استعراض", size=14)
                            ], tight=True),
                            on_click=self.pick_folder,
                            style=ft.ButtonStyle(
                                padding=ft.padding.symmetric(horizontal=20, vertical=15),
                                shape=ft.RoundedRectangleBorder(radius=12)
                            )
                        )
                    ]),
                    
                    # إعدادات التنظيف الذكي
                    ft.ExpansionTile(
                        title=ft.Text("🧹 إعدادات التنظيف الذكي للمحتوى"),
                        subtitle=ft.Text("تنظيف المحتوى من العناصر غير المرغوبة"),
                        leading=ft.Icon(ft.Icons.AUTO_FIX_HIGH_ROUNDED, color=primary_color),
                        controls=[
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("عناصر يتم حذفها تلقائياً:", weight=ft.FontWeight.BOLD, size=14),
                                    ft.Row([
                                        ft.Checkbox(
                                            label="Header/Navigation",
                                            value=True,
                                            ref=self.create_remove_header_ref()
                                        ),
                                        ft.Checkbox(
                                            label="Footer",
                                            value=True,
                                            ref=self.create_remove_footer_ref()
                                        ),
                                        ft.Checkbox(
                                            label="Sidebar",
                                            value=True,
                                            ref=self.create_remove_sidebar_ref()
                                        )
                                    ]),
                                    ft.Row([
                                        ft.Checkbox(
                                            label="إعلانات",
                                            value=True,
                                            ref=self.create_remove_ads_ref()
                                        ),
                                        ft.Checkbox(
                                            label="أزرار المشاركة",
                                            value=True,
                                            ref=self.create_remove_social_ref()
                                        ),
                                        ft.Checkbox(
                                            label="التعليقات",
                                            value=False,
                                            ref=self.create_remove_comments_ref()
                                        )
                                    ]),
                                    ft.TextField(
                                        label="عناصر إضافية للحذف (CSS selectors)",
                                        hint_text=".ads, #popup, .banner",
                                        helper_text="أفصل بفاصلة، مثال: .advertisement, #sidebar",
                                        multiline=True,
                                        min_lines=2,
                                        max_lines=3,
                                        ref=self.create_custom_selectors_ref()
                                    )
                                ], spacing=10),
                                padding=15
                            )
                        ]
                    )
                ], spacing=15),
                padding=25
            ),
            elevation=4,
            shadow_color=secondary_color,
            surface_tint_color=ft.Colors.BLUE_50
        )
    
    def create_export_section(self, primary_color, success_color):
        """قسم إعدادات التصدير المحسن"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # العنوان
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, color=success_color, size=28),
                            ft.Text("📤 إعدادات التصدير المتقدمة", 
                                   size=20, weight=ft.FontWeight.BOLD, color=primary_color),
                            ft.Container(expand=True),
                            ft.Chip(
                                label=ft.Text("Markdown", size=12),
                                bgcolor=ft.Colors.GREEN_50,
                                color=success_color
                            )
                        ]),
                        margin=ft.margin.only(bottom=15)
                    ),
                    
                    # خيارات التصدير
                    ft.Row([
                        ft.Container(
                            content=ft.RadioGroup(
                                content=ft.Column([
                                    ft.Radio(value="markdown", label="📝 Markdown (موصى به)"),
                                    ft.Radio(value="pdf", label="📄 PDF"),
                                    ft.Radio(value="both", label="📑 كلاهما"),
                                ]),
                                value="both",
                                ref=self.create_export_format_ref()
                            ),
                            expand=1
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("مميزات Markdown:", weight=ft.FontWeight.BOLD, size=14),
                                ft.Text("✓ حجم ملف أصغر", size=12, color=ft.Colors.GREEN_700),
                                ft.Text("✓ قابل للبحث والفهرسة", size=12, color=ft.Colors.GREEN_700),
                                ft.Text("✓ يحافظ على التنسيق", size=12, color=ft.Colors.GREEN_700),
                                ft.Text("✓ سهل التحرير", size=12, color=ft.Colors.GREEN_700),
                                ft.Text("✓ متوافق مع Git", size=12, color=ft.Colors.GREEN_700),
                            ], spacing=3),
                            expand=1,
                            bgcolor=ft.Colors.GREEN_50,
                            padding=15,
                            border_radius=10
                        )
                    ]),
                    
                    # إعدادات PDF (عند الحاجة)
                    ft.ExpansionTile(
                        title=ft.Text("🔧 إعدادات PDF (عند التصدير كـ PDF)"),
                        subtitle=ft.Text("تخصيص شكل ملفات PDF"),
                        leading=ft.Icon(ft.Icons.PICTURE_AS_PDF_ROUNDED, color=ft.Colors.RED_600),
                        controls=[
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Container(
                                            content=ft.Dropdown(
                                                label="📏 حجم الصفحة",
                                                options=[
                                                    ft.dropdown.Option("A4", "A4 (موصى به)"),
                                                    ft.dropdown.Option("A3", "A3 (كبير)"),
                                                    ft.dropdown.Option("Letter", "Letter (أمريكي)"),
                                                ],
                                                value="A4",
                                                ref=self.create_page_size_ref()
                                            ),
                                            expand=1
                                        ),
                                        ft.Container(width=15),
                                        ft.Container(
                                            content=ft.Dropdown(
                                                label="📐 الاتجاه",
                                                options=[
                                                    ft.dropdown.Option("Portrait", "📱 عمودي"),
                                                    ft.dropdown.Option("Landscape", "📺 أفقي"),
                                                ],
                                                value="Portrait",
                                                ref=self.create_orientation_ref()
                                            ),
                                            expand=1
                                        )
                                    ]),
                                    ft.Row([
                                        ft.Checkbox(
                                            label="🖼️ تضمين الصور",
                                            value=True,
                                            ref=self.create_images_ref()
                                        ),
                                        ft.Checkbox(
                                            label="🎨 تضمين CSS",
                                            value=True,
                                            ref=self.create_css_ref()
                                        )
                                    ])
                                ], spacing=15),
                                padding=15
                            )
                        ]
                    )
                ], spacing=15),
                padding=25
            ),
            elevation=4,
            shadow_color=success_color,
            surface_tint_color=ft.Colors.GREEN_50
        )
    
    def create_control_section(self, success_color, error_color, warning_color):
        """قسم أزرار التحكم المحسن"""
        self.start_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ROCKET_LAUNCH_ROUNDED, size=22),
                ft.Text("بدء الكشط الذكي", size=16, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, tight=True),
            on_click=self.start_scraping,
            style=ft.ButtonStyle(
                bgcolor=success_color,
                color=ft.Colors.WHITE,
                padding=ft.padding.symmetric(horizontal=40, vertical=18),
                shape=ft.RoundedRectangleBorder(radius=15),
                elevation=5
            ),
            width=220,
            disabled=True
        )
        
        self.pause_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PAUSE_CIRCLE_ROUNDED, size=20),
                ft.Text("إيقاف مؤقت", size=14)
            ], tight=True),
            on_click=self.pause_scraping,
            style=ft.ButtonStyle(
                bgcolor=warning_color,
                color=ft.Colors.WHITE,
                padding=ft.padding.symmetric(horizontal=25, vertical=18),
                shape=ft.RoundedRectangleBorder(radius=15),
                elevation=3
            ),
            width=160,
            disabled=True
        )
        
        self.stop_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.STOP_CIRCLE_ROUNDED, size=20),
                ft.Text("إيقاف", size=14)
            ], tight=True),
            on_click=self.stop_scraping,
            style=ft.ButtonStyle(
                bgcolor=error_color,
                color=ft.Colors.WHITE,
                padding=ft.padding.symmetric(horizontal=30, vertical=18),
                shape=ft.RoundedRectangleBorder(radius=15),
                elevation=3
            ),
            width=140,
            disabled=True
        )
        
        return ft.Container(
            content=ft.Row([
                self.start_btn,
                self.pause_btn,
                self.stop_btn
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            margin=ft.margin.symmetric(vertical=10)
        )
    
    def create_stats_section(self, primary_color, success_color, error_color, warning_color):
        """قسم الإحصائيات المحسن"""
        self.progress_bar = ft.ProgressBar(
            width=600,
            color=primary_color,
            bgcolor=ft.Colors.GREY_200,
            visible=False,
            height=8
        )
        
        self.progress_text = ft.Text(
            "",
            size=13,
            color=ft.Colors.GREY_600,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_500
        )
        
        # كروت الإحصائيات
        stats_cards = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=success_color, size=24),
                        ft.Text("مكشوطة", weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.GREY_700)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text("0", size=28, color=success_color, weight=ft.FontWeight.BOLD, 
                           text_align=ft.TextAlign.CENTER, ref=self.create_scraped_ref())
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                bgcolor=ft.Colors.GREEN_50,
                padding=20,
                border_radius=15,
                border=ft.border.all(1, ft.Colors.GREEN_100),
                expand=1
            ),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.LINK_ROUNDED, color=primary_color, size=24),
                        ft.Text("مكتشفة", weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.GREY_700)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text("0", size=28, color=primary_color, weight=ft.FontWeight.BOLD,
                           text_align=ft.TextAlign.CENTER, ref=self.create_found_ref())
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                bgcolor=ft.Colors.INDIGO_50,
                padding=20,
                border_radius=15,
                border=ft.border.all(1, ft.Colors.INDIGO_100),
                expand=1
            ),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ERROR_ROUNDED, color=error_color, size=24),
                        ft.Text("فاشلة", weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.GREY_700)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text("0", size=28, color=error_color, weight=ft.FontWeight.BOLD,
                           text_align=ft.TextAlign.CENTER, ref=self.create_failed_ref())
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                bgcolor=ft.Colors.RED_50,
                padding=20,
                border_radius=15,
                border=ft.border.all(1, ft.Colors.RED_100),
                expand=1
            ),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TIMER_ROUNDED, color=warning_color, size=24),
                        ft.Text("الوقت", weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.GREY_700)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text("00:00", size=28, color=warning_color, weight=ft.FontWeight.BOLD,
                           text_align=ft.TextAlign.CENTER, ref=self.create_time_ref())
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                bgcolor=ft.Colors.AMBER_50,
                padding=20,
                border_radius=15,
                border=ft.border.all(1, ft.Colors.AMBER_100),
                expand=1
            ),
        ], spacing=15)
        
        return ft.Column([
            ft.Container(
                content=ft.Column([
                    self.progress_bar,
                    self.progress_text
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                margin=ft.margin.symmetric(vertical=15)
            ),
            stats_cards
        ], spacing=10)
    
    def create_logs_section(self, primary_color):
        """قسم السجل المحسن مع tabs"""
        log_tabs = ft.Tabs(
            tabs=[
                ft.Tab(
                    text="📋 السجل العام",
                    icon=ft.Icons.LIST_ALT_ROUNDED,
                    content=ft.Container(
                        content=ft.ListView(
                            height=280,
                            spacing=5,
                            ref=self.create_log_ref()
                        ),
                        padding=15,
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=10
                    )
                ),
                ft.Tab(
                    text="✅ ناجحة",
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
                    content=ft.Container(
                        content=ft.ListView(
                            height=280,
                            spacing=5,
                            ref=self.create_success_log_ref()
                        ),
                        padding=15,
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=10
                    )
                ),
                ft.Tab(
                    text="❌ فاشلة",
                    icon=ft.Icons.ERROR_OUTLINE_ROUNDED,
                    content=ft.Container(
                        content=ft.ListView(
                            height=280,
                            spacing=5,
                            ref=self.create_error_log_ref()
                        ),
                        padding=15,
                        bgcolor=ft.Colors.RED_50,
                        border_radius=10
                    )
                )
            ],
            selected_index=0,
            animation_duration=300
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ARTICLE_ROUNDED, color=primary_color, size=28),
                        ft.Text("📊 سجل العمليات التفصيلي", 
                               size=20, weight=ft.FontWeight.BOLD, color=primary_color)
                    ], spacing=10),
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    log_tabs
                ], spacing=15),
                padding=20
            ),
            elevation=4,
            shadow_color=primary_color,
            surface_tint_color=ft.Colors.INDIGO_50
        )
    
    def create_status_bar(self):
        """شريط الحالة المحسن"""
        self.status_text = ft.Text(
            "🔄 جاهز للعمل - يرجى استخراج Cookies أولاً",
            size=14,
            color=ft.Colors.GREY_700,
            weight=ft.FontWeight.W_500
        )
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color=ft.Colors.GREY_600, size=20),
                self.status_text,
                ft.Container(expand=True),
                ft.Text(
                    f"الإصدار 2.0 - {datetime.now().strftime('%Y')}",
                    size=12,
                    color=ft.Colors.GREY_500
                )
            ], alignment=ft.MainAxisAlignment.START),
            bgcolor=ft.Colors.GREY_100,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_200)
        )
    
    def show_about(self, e):
        """نافذة معلومات التطبيق"""
        def close_dialog(e):
            dialog.open = False
            e.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("حول Web Scraper Pro"),
            content=ft.Column([
                ft.Text("🚀 مكشطة الويب الاحترافية", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("الميزات:", weight=ft.FontWeight.BOLD),
                ft.Text("• كشط ذكي للمواقع المحمية"),
                ft.Text("• تصدير Markdown و PDF"),
                ft.Text("• تنظيف المحتوى تلقائياً"),
                ft.Text("• إحصائيات في الوقت الفعلي"),
                ft.Text("• واجهة عربية احترافية"),
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("إغلاق", on_click=close_dialog)
            ]
        )
        
        e.page.dialog = dialog
        dialog.open = True
        e.page.update()
    
    # إنشاء المراجع للعناصر (نفس الطريقة السابقة لكن محسنة)
    def create_domain_ref(self):
        self.domain_field = ft.Ref[ft.TextField]()
        return self.domain_field
    
    def create_browser_ref(self):
        self.browser_dropdown = ft.Ref[ft.Dropdown]()
        return self.browser_dropdown
    
    def create_url_ref(self):
        self.url_field = ft.Ref[ft.TextField]()
        return self.url_field
    
    def create_element_id_ref(self):
        self.element_id_field = ft.Ref[ft.TextField]()
        return self.element_id_field
    
    def create_depth_ref(self):
        self.depth_dropdown = ft.Ref[ft.Dropdown]()
        return self.depth_dropdown
    
    def create_folder_ref(self):
        self.folder_field = ft.Ref[ft.TextField]()
        return self.folder_field
    
    def create_export_format_ref(self):
        self.export_format = ft.Ref[ft.RadioGroup]()
        return self.export_format
    
    def create_remove_header_ref(self):
        self.remove_header = ft.Ref[ft.Checkbox]()
        return self.remove_header
    
    def create_remove_footer_ref(self):
        self.remove_footer = ft.Ref[ft.Checkbox]()
        return self.remove_footer
    
    def create_remove_sidebar_ref(self):
        self.remove_sidebar = ft.Ref[ft.Checkbox]()
        return self.remove_sidebar
    
    def create_remove_ads_ref(self):
        self.remove_ads = ft.Ref[ft.Checkbox]()
        return self.remove_ads
    
    def create_remove_social_ref(self):
        self.remove_social = ft.Ref[ft.Checkbox]()
        return self.remove_social
    
    def create_remove_comments_ref(self):
        self.remove_comments = ft.Ref[ft.Checkbox]()
        return self.remove_comments
    
    def create_custom_selectors_ref(self):
        self.custom_selectors = ft.Ref[ft.TextField]()
        return self.custom_selectors
    
    def create_page_size_ref(self):
        self.page_size_dropdown = ft.Ref[ft.Dropdown]()
        return self.page_size_dropdown
    
    def create_orientation_ref(self):
        self.orientation_dropdown = ft.Ref[ft.Dropdown]()
        return self.orientation_dropdown
    
    def create_images_ref(self):
        self.images_checkbox = ft.Ref[ft.Checkbox]()
        return self.images_checkbox
    
    def create_css_ref(self):
        self.css_checkbox = ft.Ref[ft.Checkbox]()
        return self.css_checkbox
    
    def create_log_ref(self):
        self.log_view = ft.Ref[ft.ListView]()
        return self.log_view
    
    def create_success_log_ref(self):
        self.success_log_view = ft.Ref[ft.ListView]()
        return self.success_log_view
    
    def create_error_log_ref(self):
        self.error_log_view = ft.Ref[ft.ListView]()
        return self.error_log_view
    
    def create_scraped_ref(self):
        self.scraped_count = ft.Ref[ft.Text]()
        return self.scraped_count
    
    def create_found_ref(self):
        self.found_count = ft.Ref[ft.Text]()
        return self.found_count
    
    def create_failed_ref(self):
        self.failed_count = ft.Ref[ft.Text]()
        return self.failed_count
    
    def create_time_ref(self):
        self.time_display = ft.Ref[ft.Text]()
        return self.time_display
    
    def clean_content(self, soup, url):
        """تنظيف المحتوى من العناصر غير المرغوبة"""
        try:
            # العناصر المشتركة للحذف
            common_selectors = [
                'script', 'style', 'noscript', 'iframe', 'embed', 'object',
                '[hidden]', '.sr-only', '.visually-hidden'
            ]
            
            # حذف العناصر حسب الإعدادات
            if hasattr(self, 'remove_header') and self.remove_header.current and self.remove_header.current.value:
                common_selectors.extend([
                    'header', 'nav', '.header', '.navigation', '.navbar', 
                    '.site-header', '.main-header', '.top-bar', '#header',
                    '.menu', '.main-menu', '.primary-menu'
                ])
            
            if hasattr(self, 'remove_footer') and self.remove_footer.current and self.remove_footer.current.value:
                common_selectors.extend([
                    'footer', '.footer', '.site-footer', '.main-footer', 
                    '#footer', '.page-footer', '.bottom-bar'
                ])
            
            if hasattr(self, 'remove_sidebar') and self.remove_sidebar.current and self.remove_sidebar.current.value:
                common_selectors.extend([
                    'aside', '.sidebar', '.side-bar', '.widget-area',
                    '#sidebar', '.secondary', '.complementary'
                ])
            
            if hasattr(self, 'remove_ads') and self.remove_ads.current and self.remove_ads.current.value:
                common_selectors.extend([
                    '.ad', '.ads', '.advertisement', '.banner', '.promo',
                    '.sponsor', '.google-ads', '.adsense', '[class*="ad-"]',
                    '[id*="ad-"]', '.adsbygoogle'
                ])
            
            if hasattr(self, 'remove_social') and self.remove_social.current and self.remove_social.current.value:
                common_selectors.extend([
                    '.social', '.share', '.sharing', '.social-media',
                    '.share-buttons', '.social-icons', '.follow-us'
                ])
            
            if hasattr(self, 'remove_comments') and self.remove_comments.current and self.remove_comments.current.value:
                common_selectors.extend([
                    '.comments', '.comment', '#comments', '.comment-section',
                    '.disqus', '.fb-comments'
                ])
            
            # إضافة المحددات المخصصة
            if (hasattr(self, 'custom_selectors') and self.custom_selectors.current and 
                self.custom_selectors.current.value):
                custom = [s.strip() for s in self.custom_selectors.current.value.split(',') if s.strip()]
                common_selectors.extend(custom)
            
            # حذف العناصر
            for selector in common_selectors:
                try:
                    for element in soup.select(selector):
                        element.decompose()
                except Exception:
                    continue
            
            # البحث عن المحتوى الرئيسي
            main_content = None
            
            # محاولة العثور على المحتوى الرئيسي
            main_selectors = [
                'main', 'article', '.content', '.main-content', '.post-content',
                '.entry-content', '.article-content', '#content', '.page-content',
                '.post', '.article', '.entry', '[role="main"]'
            ]
            
            for selector in main_selectors:
                try:
                    element = soup.select_one(selector)
                    if element and len(element.get_text(strip=True)) > 100:
                        main_content = element
                        break
                except Exception:
                    continue
            
            # إذا لم نجد محتوى رئيسي، نستخدم body
            if not main_content:
                main_content = soup.find('body') or soup
            
            self.log(f"🧹 تم تنظيف المحتوى من {url}", ft.Colors.BLUE, "success")
            return main_content
            
        except Exception as e:
            self.log(f"⚠️ خطأ في تنظيف المحتوى: {str(e)}", ft.Colors.ORANGE)
            return soup
    
    def save_as_markdown(self, url, content, folder):
        """حفظ المحتوى كـ Markdown"""
        try:
            # تحليل HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # تنظيف المحتوى
            cleaned_soup = self.clean_content(soup, url)
            
            # تحويل إلى Markdown
            markdown_content = self.html_converter.handle(str(cleaned_soup))
            
            # تحسين Markdown
            markdown_content = self.improve_markdown(markdown_content, url)
            
            # إنشاء اسم الملف
            parsed_url = urlparse(url)
            if url == self.main_url:
                filename = "main_page.md"
            else:
                path = parsed_url.path.strip('/')
                if path:
                    filename = path.replace('/', '_').replace('\\', '_')
                    filename = "".join(c for c in filename if c.isalnum() or c in ['_', '-', '.'])
                else:
                    filename = "index"
                filename = f"{filename}.md"
            
            # تجنب الأسماء المكررة
            filepath = os.path.join(folder, filename)
            counter = 1
            while os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filepath = os.path.join(folder, f"{name}_{counter}{ext}")
                counter += 1
            
            # حفظ الملف
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            file_size = os.path.getsize(filepath) / 1024  # KB
            self.log(f"📝 تم حفظ Markdown: {os.path.basename(filepath)} ({file_size:.1f} KB)", 
                    ft.Colors.GREEN, "success")
            
            return True
            
        except Exception as e:
            self.log(f"❌ خطأ في حفظ Markdown: {str(e)}", ft.Colors.RED, "error")
            return False
    
    def improve_markdown(self, markdown_content, url):
        """تحسين محتوى Markdown"""
        try:
            # إضافة metadata في المقدمة
            title = self.extract_title_from_url(url)
            header = f"""---
title: {title}
url: {url}
scraped_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# {title}

> **المصدر:** [{url}]({url})  
> **تاريخ الكشط:** {datetime.now().strftime('%d/%m/%Y الساعة %H:%M')}

---

"""
            
            # تنظيف المحتوى
            # إزالة الأسطر الفارغة المتعددة
            markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
            
            # تنظيف الجداول
            markdown_content = re.sub(r'\|(\s*\|)+', '|', markdown_content)
            
            # تحسين الروابط
            markdown_content = re.sub(r'\[([^\]]*)\]\(\)', r'\1', markdown_content)  # حذف الروابط الفارغة
            
            # تحويل الروابط النسبية إلى مطلقة
            base_url = '/'.join(url.split('/')[:3])
            markdown_content = re.sub(
                r'\[([^\]]*)\]\((/[^)]*)\)', 
                rf'[\1]({base_url}\2)', 
                markdown_content
            )
            
            return header + markdown_content.strip()
            
        except Exception as e:
            self.log(f"⚠️ خطأ في تحسين Markdown: {str(e)}", ft.Colors.ORANGE)
            return markdown_content
    
    def extract_title_from_url(self, url):
        """استخراج عنوان من الرابط"""
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            if path:
                # تحويل المسار إلى عنوان قابل للقراءة
                title = path.replace('/', ' > ').replace('-', ' ').replace('_', ' ')
                return title.title()
            else:
                return parsed.netloc.replace('www.', '').title()
        except Exception:
            return "صفحة ويب"
    
    def save_as_pdf(self, url, content, folder):
        """حفظ المحتوى كـ PDF (محسن) باستخدام WeasyPrint"""
        try:
            # تحليل وتنظيف HTML
            soup = BeautifulSoup(content, 'html.parser')
            cleaned_soup = self.clean_content(soup, url)

            # إنشاء اسم الملف
            parsed_url = urlparse(url)
            if url == self.main_url:
                filename = "main_page.pdf"
            else:
                path = parsed_url.path.strip('/')
                if path:
                    filename = path.replace('/', '_').replace('\\', '_')
                    filename = "".join(c for c in filename if c.isalnum() or c in ['_', '-', '.'])
                else:
                    filename = "index"
                filename = f"{filename}.pdf"

            # تجنب الأسماء المكررة
            filepath = os.path.join(folder, filename)
            counter = 1
            while os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filepath = os.path.join(folder, f"{name}_{counter}{ext}")
                counter += 1

            # إعدادات PDF محسنة باستخدام WeasyPrint
            page_size = self.page_size_dropdown.current.value if hasattr(self, 'page_size_dropdown') else 'A4'
            orientation = self.orientation_dropdown.current.value if hasattr(self, 'orientation_dropdown') else 'Portrait'

            # تحويل HTML إلى PDF باستخدام WeasyPrint
            html_doc = HTML(string=str(cleaned_soup))

            # إعدادات CSS للطباعة
            css_styles = f"""
            @page {{
                size: {page_size} {orientation.lower()};
                margin: 0.75in;
            }}
            """

            css_doc = CSS(string=css_styles)

            # إنشاء ملف PDF
            html_doc.write_pdf(filepath, stylesheets=[css_doc])

            file_size = os.path.getsize(filepath) / 1024  # KB
            self.log(f"📄 تم حفظ PDF: {os.path.basename(filepath)} ({file_size:.1f} KB)",
                    ft.Colors.GREEN, "success")

            return True

        except Exception as e:
            self.log(f"❌ خطأ في حفظ PDF: {str(e)}", ft.Colors.RED, "error")

        return False
    
    def save_content(self, url, content, folder):
        """حفظ المحتوى بالتنسيق المحدد"""
        try:
            export_format = self.export_format.current.value if hasattr(self, 'export_format') else "markdown"
            
            success_markdown = False
            success_pdf = False
            
            if export_format in ["markdown", "both"]:
                success_markdown = self.save_as_markdown(url, content, folder)
            
            if export_format in ["pdf", "both"]:
                success_pdf = self.save_as_pdf(url, content, folder)
            
            # إرجاع النجاح إذا نجح أي من التنسيقات
            if export_format == "markdown":
                return success_markdown
            elif export_format == "pdf":
                return success_pdf
            else:  # both
                return success_markdown or success_pdf
                
        except Exception as e:
            self.log(f"❌ خطأ في حفظ المحتوى: {str(e)}", ft.Colors.RED, "error")
            return False
    
    def log(self, message, color=ft.Colors.BLACK, log_type="general"):
        """إضافة رسالة للسجل المحسن"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # أيقونات محسنة
        icon_map = {
            "general": ft.Icons.INFO_ROUNDED,
            "success": ft.Icons.CHECK_CIRCLE_ROUNDED,
            "error": ft.Icons.ERROR_ROUNDED,
            "warning": ft.Icons.WARNING_ROUNDED
        }
        
        icon = icon_map.get(log_type, ft.Icons.INFO_ROUNDED)
        
        log_item = ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=18),
                ft.Container(
                    content=ft.Text(
                        f"[{timestamp}] {message}", 
                        color=color, 
                        size=12,
                        weight=ft.FontWeight.W_400
                    ),
                    expand=True
                )
            ], spacing=10),
            padding=ft.padding.symmetric(vertical=4, horizontal=8),
            border_radius=6,
            bgcolor=ft.Colors.WHITE if log_type == "general" else None
        )
        
        # إضافة للسجل العام
        if hasattr(self, 'log_view') and self.log_view.current:
            self.log_view.current.controls.append(log_item)
            if len(self.log_view.current.controls) > 200:
                self.log_view.current.controls.pop(0)
            self.log_view.current.update()
        
        # إضافة للسجل المخصص
        if log_type == "success" and hasattr(self, 'success_log_view') and self.success_log_view.current:
            self.success_log_view.current.controls.append(log_item)
            if len(self.success_log_view.current.controls) > 100:
                self.success_log_view.current.controls.pop(0)
            self.success_log_view.current.update()
        
        elif log_type == "error" and hasattr(self, 'error_log_view') and self.error_log_view.current:
            self.error_log_view.current.controls.append(log_item)
            if len(self.error_log_view.current.controls) > 100:
                self.error_log_view.current.controls.pop(0)
            self.error_log_view.current.update()
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        if hasattr(self, 'scraped_count') and self.scraped_count.current:
            self.scraped_count.current.value = str(len(self.scraped_urls))
            self.scraped_count.current.update()
        
        if hasattr(self, 'found_count') and self.found_count.current:
            self.found_count.current.value = str(self.total_found_links)
            self.found_count.current.update()
        
        if hasattr(self, 'failed_count') and self.failed_count.current:
            self.failed_count.current.value = str(len(self.failed_urls))
            self.failed_count.current.update()
    
    def update_timer(self):
        """تحديث مؤقت الوقت"""
        def timer_worker():
            while True:
                if self.start_time and self.is_scraping:
                    elapsed = datetime.now() - self.start_time
                    hours = elapsed.seconds // 3600
                    minutes = (elapsed.seconds % 3600) // 60
                    seconds = elapsed.seconds % 60
                    
                    if hours > 0:
                        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        time_str = f"{minutes:02d}:{seconds:02d}"
                    
                    if hasattr(self, 'time_display') and self.time_display.current:
                        self.time_display.current.value = time_str
                        self.time_display.current.update()
                time.sleep(1)
        
        timer_thread = threading.Thread(target=timer_worker)
        timer_thread.daemon = True
        timer_thread.start()
    
    def pick_folder(self, e):
        """اختيار مجلد محسن"""
        def folder_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.folder_field.current.value = e.path
                self.folder_field.current.update()
                self.log(f"📁 تم اختيار مجلد: {e.path}", ft.Colors.BLUE)
        
        file_picker = ft.FilePicker(on_result=folder_result)
        e.page.overlay.append(file_picker)
        e.page.update()
        file_picker.get_directory_path()
    
    def extract_cookies_from_browser(self, domain, browser_type):
        """استخراج cookies محسن"""
        try:
            self.log(f"🔍 البحث عن cookies في {browser_type}...", ft.Colors.BLUE)
            
            cookies_jar = None
            
            if browser_type == "auto":
                browsers = [
                    ("Chrome", browser_cookie3.chrome),
                    ("Firefox", browser_cookie3.firefox),
                    ("Edge", browser_cookie3.edge),
                    ("Safari", browser_cookie3.safari),
                    ("Opera", browser_cookie3.opera)
                ]
                
                for browser_name, browser_func in browsers:
                    try:
                        self.log(f"🔍 فحص {browser_name}...", ft.Colors.BLUE)
                        cookies_jar = browser_func(domain_name=domain)
                        cookies_list = list(cookies_jar)
                        if cookies_list:
                            self.log(f"✅ تم العثور على {len(cookies_list)} cookie في {browser_name}!", ft.Colors.GREEN)
                            break
                    except Exception:
                        continue
            else:
                browser_funcs = {
                    "chrome": browser_cookie3.chrome,
                    "firefox": browser_cookie3.firefox,
                    "edge": browser_cookie3.edge,
                    "safari": browser_cookie3.safari,
                    "opera": browser_cookie3.opera
                }
                
                if browser_type in browser_funcs:
                    cookies_jar = browser_funcs[browser_type](domain_name=domain)
            
            if not cookies_jar:
                return False
            
            cookies_list = list(cookies_jar)
            if not cookies_list:
                return False
            
            # إضافة cookies للجلسة
            for cookie in cookies_list:
                self.session.cookies.set(
                    cookie.name, 
                    cookie.value,
                    domain=cookie.domain,
                    path=cookie.path
                )
            
            self.log(f"✅ تم استخراج {len(cookies_list)} cookie بنجاح", ft.Colors.GREEN, "success")
            return True
            
        except Exception as e:
            self.log(f"❌ خطأ في استخراج cookies: {str(e)}", ft.Colors.RED, "error")
            return False
    
    def test_cookies(self, e):
        """اختبار cookies محسن"""
        domain = self.domain_field.current.value.strip()
        browser_type = self.browser_dropdown.current.value
        
        if not domain:
            self.log("❌ يرجى إدخال النطاق أولاً", ft.Colors.RED, "error")
            return
        
        self.log("🔄 بدء عملية استخراج cookies...", ft.Colors.BLUE)
        
        if self.extract_cookies_from_browser(domain, browser_type):
            # اختبار الاتصال
            test_url = self.url_field.current.value.strip() if self.url_field.current.value else f"https://{domain}"
            
            try:
                self.log("🧪 اختبار الوصول للصفحة...", ft.Colors.BLUE)
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = self.session.get(test_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.log("✅ نجح اختبار الاتصال! جاهز للكشط", ft.Colors.GREEN, "success")
                    self.start_btn.disabled = False
                    self.start_btn.update()
                    self.status_text.value = "✅ جاهز للكشط - تم التحقق من Cookies"
                    self.status_text.color = ft.Colors.GREEN_700
                    self.status_text.update()
                else:
                    self.log(f"⚠️ رمز الاستجابة: {response.status_code}", ft.Colors.ORANGE)
                    
            except Exception as ex:
                self.log(f"❌ خطأ في الاختبار: {str(ex)}", ft.Colors.RED, "error")
        else:
            self.log("❌ فشل استخراج cookies", ft.Colors.RED, "error")
    
    def get_page_content(self, url):
        """جلب محتوى الصفحة مع معالجة متقدمة"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ar,en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except requests.exceptions.Timeout:
            self.log(f"⏰ انتهت مهلة الاتصال: {url}", ft.Colors.ORANGE, "error")
        except requests.exceptions.RequestException as e:
            self.log(f"❌ خطأ في جلب {url}: {str(e)}", ft.Colors.RED, "error")
        except Exception as e:
            self.log(f"❌ خطأ غير متوقع: {str(e)}", ft.Colors.RED, "error")
        
        return None
    
    def extract_links(self, html, base_url, element_id):
        """استخراج الروابط المتقدم"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # تحديد منطقة البحث
        if base_url == self.main_url:
            self.log(f"🏠 كشط الصفحة الرئيسية - العنصر: {element_id}", ft.Colors.BLUE)
            
            # البحث بـ ID أولاً
            element = soup.find(id=element_id)
            if not element:
                # البحث بـ class
                element = soup.find(class_=element_id)
                if not element:
                    # البحث بـ CSS selector
                    try:
                        element = soup.select_one(element_id)
                    except Exception:
                        pass
                    
                    if not element:
                        self.log(f"⚠️ لم يتم العثور على العنصر: {element_id}", ft.Colors.ORANGE)
                        return links
            
            search_area = element
        else:
            self.log(f"📄 كشط صفحة فرعية", ft.Colors.BLUE)
            search_area = soup
        
        # استخراج الروابط
        for link_tag in search_area.find_all('a', href=True):
            href = link_tag.get('href', '').strip()
            if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            # تحويل إلى رابط كامل
            full_url = urljoin(base_url, href)
            
            # التحقق من النطاق
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                # تنظيف الرابط
                clean_url = full_url.split('#')[0]  # إزالة الأنكور
                clean_url = clean_url.rstrip('/')  # إزالة / في النهاية
                
                if clean_url not in links and clean_url != base_url:
                    links.append(clean_url)
        
        unique_links = list(set(links))
        self.total_found_links += len(unique_links)
        self.log(f"📎 تم العثور على {len(unique_links)} رابط جديد", ft.Colors.BLUE)
        
        return unique_links
    
    def scraping_worker(self):
        """عملية الكشط المتقدمة المحسنة"""
        try:
            url = self.url_field.current.value.strip()
            element_id = self.element_id_field.current.value.strip()
            folder = self.folder_field.current.value.strip()
            max_depth = self.depth_dropdown.current.value
            
            if not all([url, element_id, folder]):
                self.log("❌ يرجى إكمال جميع الحقول المطلوبة", ft.Colors.RED, "error")
                self.stop_scraping(None)
                return
            
            # إنشاء المجلد
            os.makedirs(folder, exist_ok=True)
            
            # إنشاء مجلد فرعي بالتاريخ والوقت
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = urlparse(url).netloc.replace('www.', '')
            session_folder = os.path.join(folder, f"{domain}_{timestamp}")
            os.makedirs(session_folder, exist_ok=True)
            
            self.main_url = url
            self.scraped_urls.clear()
            self.failed_urls.clear()
            self.total_found_links = 0
            
            export_format = self.export_format.current.value
            self.log(f"🚀 بدء الكشط المتقدم من: {url}", ft.Colors.GREEN)
            self.log(f"📁 مجلد الحفظ: {session_folder}", ft.Colors.BLUE)
            self.log(f"📤 تنسيق التصدير: {export_format}", ft.Colors.BLUE)
            
            # قائمة انتظار مع مستوى العمق
            urls_queue = [(url, 0)]  # (url, depth)
            processed_count = 0
            
            while urls_queue and self.is_scraping and not self.is_paused:
                current_url, depth = urls_queue.pop(0)
                
                # فحص العمق المحدد
                if max_depth != "unlimited" and depth >= int(max_depth):
                    continue
                
                if current_url in self.scraped_urls:
                    continue
                
                processed_count += 1
                self.scraped_urls.add(current_url)
                
                # تحديث شريط التقدم
                self.progress_text.value = f"جاري معالجة: {current_url} (العمق: {depth})"
                self.progress_text.update()
                
                self.log(f"🔍 معالجة [{processed_count}]: {current_url}", ft.Colors.BLUE)
                
                # جلب المحتوى
                content = self.get_page_content(current_url)
                if not content:
                    self.failed_urls.add(current_url)
                    self.update_stats()
                    continue
                
                # حفظ المحتوى
                if self.save_content(current_url, content, session_folder):
                    self.log(f"💾 تم حفظ المحتوى بنجاح", ft.Colors.GREEN, "success")
                else:
                    self.failed_urls.add(current_url)
                
                # استخراج الروابط
                new_links = self.extract_links(content, current_url, element_id)
                
                # إضافة الروابط الجديدة للقائمة
                for link in new_links:
                    if link not in self.scraped_urls and not any(link == item[0] for item in urls_queue):
                        urls_queue.append((link, depth + 1))
                
                # تحديث الإحصائيات
                self.update_stats()
                
                # تأخير مهذب
                time.sleep(2)
            
            # النتائج النهائية
            if self.is_scraping:
                self.log("🎉 اكتملت عملية الكشط بنجاح!", ft.Colors.GREEN, "success")
                self.log(f"📊 النتائج النهائية: {len(self.scraped_urls)} صفحة، {len(self.failed_urls)} فاشلة", ft.Colors.BLUE)
                
                # حفظ تقرير
                self.save_report(session_folder)
                self.save_index_file(session_folder)
                    # ضغط المجلد بعد الكشط
                    zip_path = self.zip_folder(session_folder)
                    # إرسال الملف المضغوط إلى البريد الإلكتروني
                    self.send_email_with_attachment(zip_path)
                    # إضافة صف للجدول الملخص
                    project_name = os.path.basename(session_folder)
                    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
                    self.add_summary_entry(project_name, zip_path, date_str)
            
        except Exception as e:
            self.log(f"💥 خطأ كارثي: {str(e)}", ft.Colors.RED, "error")
        
        finally:
            self.stop_scraping(None)
    
    def save_report(self, folder):
        """حفظ تقرير مفصل"""
        try:
            report = {
                "session_info": {
                    "timestamp": datetime.now().isoformat(),
                    "main_url": self.main_url,
                    "export_format": self.export_format.current.value if hasattr(self, 'export_format') else "markdown",
                    "scraping_depth": self.depth_dropdown.current.value if hasattr(self, 'depth_dropdown') else "unlimited"
                },
                "statistics": {
                    "total_scraped": len(self.scraped_urls),
                    "total_failed": len(self.failed_urls),
                    "total_found_links": self.total_found_links,
                    "success_rate": f"{(len(self.scraped_urls)/(len(self.scraped_urls)+len(self.failed_urls))*100):.1f}%" if (len(self.scraped_urls)+len(self.failed_urls)) > 0 else "N/A"
                },
                "urls": {
                    "scraped_urls": list(self.scraped_urls),
                    "failed_urls": list(self.failed_urls)
                },
                "settings": {
                    "cleaning_enabled": True,
                    "remove_header": self.remove_header.current.value if hasattr(self, 'remove_header') and self.remove_header.current else True,
                    "remove_footer": self.remove_footer.current.value if hasattr(self, 'remove_footer') and self.remove_footer.current else True,
                    "remove_sidebar": self.remove_sidebar.current.value if hasattr(self, 'remove_sidebar') and self.remove_sidebar.current else True
                }
            }
            
            report_file = os.path.join(folder, "scraping_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.log(f"📋 تم حفظ التقرير: scraping_report.json", ft.Colors.BLUE, "success")
            
        except Exception as e:
            self.log(f"❌ خطأ في حفظ التقرير: {str(e)}", ft.Colors.RED, "error")
    
    def save_index_file(self, folder):
        """حفظ ملف فهرس بالمحتوى المكشوط"""
        try:
            export_format = self.export_format.current.value if hasattr(self, 'export_format') else "markdown"
            
            if export_format in ["markdown", "both"]:
                index_content = f"""# فهرس المحتوى المكشوط

**المصدر:** {self.main_url}  
**تاريخ الكشط:** {datetime.now().strftime('%d/%m/%Y الساعة %H:%M')}  
**عدد الصفحات:** {len(self.scraped_urls)}

## الصفحات المكشوطة:

"""
                
                for i, url in enumerate(sorted(self.scraped_urls), 1):
                    filename = self.url_to_filename(url, "md")
                    index_content += f"{i}. [{url}](./{filename})\n"
                
                if self.failed_urls:
                    index_content += f"\n## الصفحات الفاشلة ({len(self.failed_urls)}):\n\n"
                    for url in sorted(self.failed_urls):
                        index_content += f"- {url}\n"
                
                with open(os.path.join(folder, "README.md"), 'w', encoding='utf-8') as f:
                    f.write(index_content)
                
                self.log("📑 تم إنشاء ملف الفهرس: README.md", ft.Colors.BLUE, "success")
            
        except Exception as e:
            self.log(f"❌ خطأ في إنشاء ملف الفهرس: {str(e)}", ft.Colors.RED, "error")
    
    def url_to_filename(self, url, extension):
        """تحويل URL إلى اسم ملف"""
        if url == self.main_url:
            return f"main_page.{extension}"
        else:
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            if path:
                filename = path.replace('/', '_').replace('\\', '_')
                filename = "".join(c for c in filename if c.isalnum() or c in ['_', '-', '.'])
            else:
                filename = "index"
            return f"{filename}.{extension}"
    
    def start_scraping(self, e):
        """بدء الكشط"""
        self.is_scraping = True
        self.is_paused = False
        self.start_time = datetime.now()
        
        # تحديث الأزرار
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.pause_btn.disabled = False
        self.progress_bar.visible = True
        
        self.start_btn.update()
        self.stop_btn.update()
        self.pause_btn.update()
        self.progress_bar.update()
        
        self.status_text.value = "🚀 جاري الكشط..."
        self.status_text.color = ft.Colors.BLUE_700
        self.status_text.update()
        
        # بدء thread
        thread = threading.Thread(target=self.scraping_worker)
        thread.daemon = True
        thread.start()
    
    def pause_scraping(self, e):
        """إيقاف مؤقت"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_btn.text = "▶️ متابعة"
            self.log("⏸ تم إيقاف الكشط مؤقتاً", ft.Colors.ORANGE)
            self.status_text.value = "⏸ متوقف مؤقتاً..."
        else:
            self.pause_btn.text = "⏸ إيقاف مؤقت"
            self.log("▶️ تم استئناف الكشط", ft.Colors.GREEN)
            self.status_text.value = "🚀 جاري الكشط..."
        
        self.pause_btn.update()
        self.status_text.update()
    
    def stop_scraping(self, e):
        """إيقاف الكشط"""
        self.is_scraping = False
        self.is_paused = False
        
        # إعادة تعيين الأزرار
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.pause_btn.disabled = True
        self.progress_bar.visible = False
        
        self.start_btn.update()
        self.stop_btn.update()
        self.pause_btn.update()
        self.progress_bar.update()
        
        self.progress_text.value = ""
        self.progress_text.update()
        
        self.status_text.value = "✅ تم إيقاف الكشط"
        self.status_text.color = ft.Colors.GREEN_700
        self.status_text.update()
        
        if e:  # إذا تم الاستدعاء من زر
            self.log("⏹ تم إيقاف الكشط بواسطة المستخدم", ft.Colors.ORANGE)
    
    def zip_folder(self, folder_path: str) -> str:
        """
        ضغط المجلد المحدد إلى ملف ZIP
        Returns: مسار الملف المضغوط
        """
        try:
            zip_path = folder_path.rstrip(os.sep) + ".zip"
            # تجنب تضارب الأسماء
            base, ext = os.path.splitext(zip_path)
            i = 1
            while os.path.exists(zip_path):
                zip_path = f"{base}_{i}{ext}"
                i += 1
            
            # إنشاء الملف المضغوط
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # الحفاظ على المسار النسبي داخل الملف المضغوط
                        rel_path = os.path.relpath(full_path, os.path.dirname(folder_path))
                        zf.write(full_path, arcname=rel_path)
            
            self.log(f"🗜️ تم إنشاء الأرشيف: {os.path.basename(zip_path)}", ft.Colors.BLUE, "success")
            return zip_path
            
        except Exception as e:
            self.log(f"❌ خطأ في ضغط المجلد: {str(e)}", ft.Colors.RED, "error")
            raise
    
    def send_email_with_attachment(self, file_path: str):
        """
        إرسال البريد الإلكتروني مع المرفق إلى dsyemen2020@gmail.com
        """
        try:
            # إعدادات SMTP من متغيرات البيئة
            SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
            SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
            USER = os.environ.get("SMTP_USER", "")
            PASSWORD = os.environ.get("SMTP_PASS", "")
            TO = "dsyemen2020@gmail.com"
            
            if not USER or not PASSWORD:
                self.log("⚠️ لم يتم تعيين بيانات SMTP (SMTP_USER/SMTP_PASS)", ft.Colors.ORANGE, "error")
                return
            
            # إنشاء الرسالة
            msg = EmailMessage()
            msg["Subject"] = f"نتائج كشط الويب - {os.path.basename(file_path)}"
            msg["From"] = USER
            msg["To"] = TO
            
            # محتوى الرسالة
            project_name = os.path.basename(file_path).replace('.zip', '')
            msg.set_content(f"""
السلام عليكم ورحمة الله وبركاته،

تم الانتهاء من عملية كشط الويب بنجاح.

تفاصيل المشروع:
• اسم المشروع: {project_name}
• اسم الملف: {os.path.basename(file_path)}
• التاريخ والوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• حجم الملف: {os.path.getsize(file_path) / (1024*1024):.2f} ميجابايت

مع تحيات،
Web Scraper Pro
""")
            
            # إرفاق الملف المضغوط
            with open(file_path, "rb") as f:
                file_data = f.read()
            msg.add_attachment(file_data, maintype="application", subtype="zip",
                             filename=os.path.basename(file_path))
            
            # إرسال البريد
            context = ssl.create_default_context()
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.starttls(context=context)
                smtp.login(USER, PASSWORD)
                smtp.send_message(msg)
            
            self.log(f"📧 تم إرسال الأرشيف إلى {TO}", ft.Colors.GREEN, "success")
            
        except KeyError as e:
            self.log(f"❌ متغير البيئة مفقود: {str(e)}", ft.Colors.RED, "error")
        except Exception as e:
            self.log(f"❌ خطأ في إرسال البريد: {str(e)}", ft.Colors.RED, "error")
            traceback.print_exc()
    
    def create_summary_section(self):
        """جدول لعرض تفاصيل الأرشيفات السابقة"""
        self.summary_table_ref = ft.Ref[ft.DataTable]()
        
        table = ft.DataTable(
            ref=self.summary_table_ref,
            columns=[
                ft.DataColumn(ft.Text("اسم المشروع", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("الأرشيف (ZIP)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("التاريخ", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("تحميل", weight=ft.FontWeight.BOLD))
            ],
            rows=[],
            visible=False,  # مخفي حتى انتهاء أول عملية كشط
            column_spacing=30,
            border=ft.border.all(1, ft.Colors.GREY_300),
            heading_row_color=ft.Colors.INDIGO_50,
            border_radius=10,
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER_ZIP_ROUNDED, color=ft.Colors.INDIGO_600, size=28),
                        ft.Text("📂 ملخص الأرشيفات المحفوظة", 
                               size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_600),
                        ft.Container(expand=True),
                        ft.Chip(
                            label=ft.Text("تاريخ", size=12),
                            bgcolor=ft.Colors.INDIGO_50,
                            color=ft.Colors.INDIGO_600
                        )
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    table
                ], spacing=15),
                padding=20
            ),
            elevation=4,
            shadow_color=ft.Colors.INDIGO_600,
            surface_tint_color=ft.Colors.INDIGO_50,
            margin=ft.margin.symmetric(vertical=10)
        )
    
    def add_summary_entry(self, project_name: str, zip_path: str, date_str: str):
        """إضافة صف جديد إلى جدول الملخص"""
        table = self.summary_table_ref.current
        if not table:
            return
        
        def download_file(e, path=zip_path):
            """فتح الملف أو المجلد المحتوي عليه"""
            try:
                if os.path.exists(path):
                    # فتح مجلد الملف في مستكشف الملفات
                    folder_path = os.path.dirname(path)
                    if os.name == 'nt':  # Windows
                        os.startfile(folder_path)
                    elif os.name == 'posix':  # macOS and Linux
                        os.system(f'open "{folder_path}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{folder_path}"')
                else:
                    e.page.show_snack_bar(ft.SnackBar(content=ft.Text("الملف غير موجود")))
            except Exception as ex:
                e.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"خطأ في فتح الملف: {str(ex)}")))
        
        zip_name = os.path.basename(zip_path)
        file_size = os.path.getsize(zip_path) / (1024*1024) if os.path.exists(zip_path) else 0
        
        row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(project_name, size=14)),
                ft.DataCell(ft.Text(f"{zip_name} ({file_size:.1f} MB)", size=12, color=ft.Colors.GREY_700)),
                ft.DataCell(ft.Text(date_str, size=12)),
                ft.DataCell(
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=16),
                            ft.Text("تحميل", size=12)
                        ], tight=True),
                        on_click=download_file,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.INDIGO_600,
                            color=ft.Colors.WHITE,
                            padding=ft.padding.symmetric(horizontal=15, vertical=8),
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        height=35
                    )
                )
            ]
        )
        
        table.rows.append(row)
        table.visible = True
        table.update()

def main(page: ft.Page):
    # تثبيت مكتبة html2text إذا لم تكن مثبتة
    try:
        import html2text
    except ImportError:
        page.add(ft.Text("يرجى تثبيت html2text: pip install html2text"))
        return
    
    app = WebScraperApp()
    app.main(page)

if __name__ == "__main__":
    # تشغيل التطبيق كـ web app محسّن للنشر على Render
    port = int(os.environ.get("PORT", 8000))

    # إعدادات محسّنة للبيئات السحابية و Flutter compatibility
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=port,
        host="0.0.0.0",  # مهم للبيئات السحابية
        # إعدادات لتحسين الأداء والاستقرار
        assets_dir=None,
        upload_dir=None,
        web_renderer="html",  # استخدم HTML renderer بدلاً من auto
        # إعدادات للـ CORS والاتصالات
        route_url_strategy="path",
        use_color_emoji=True,
    )