import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetricsa
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import io
import pytz
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
else:
    openai_client = None
    st.warning("OpenAI API key not found. Translation features will be limited.")

# Page config
st.set_page_config(
    page_title="Production Risk Assessment Report",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chinese cities dictionary
CHINESE_CITIES = {
    "Guangzhou": "广东",
    "Shenzhen": "深圳",
    "Dongguan": "东莞",
    "Foshan": "佛山",
    "Zhongshan": "中山",
    "Huizhou": "惠州",
    "Zhuhai": "珠海",
    "Jiangmen": "江门",
    "Zhaoqing": "肇庆",
    "Shanghai": "上海",
    "Beijing": "北京",
    "Suzhou": "苏州",
    "Hangzhou": "杭州",
    "Ningbo": "宁波",
    "Wenzhou": "温州",
    "Wuhan": "武汉",
    "Chengdu": "成都",
    "Chongqing": "重庆",
    "Tianjin": "天津",
    "Nanjing": "南京",
    "Xi'an": "西安",
    "Qingdao": "青岛",
    "Dalian": "大连",
    "Shenyang": "沈阳",
    "Changsha": "长沙",
    "Zhengzhou": "郑州",
    "Jinan": "济南",
    "Harbin": "哈尔滨",
    "Changchun": "长春",
    "Taiyuan": "太原",
    "Shijiazhuang": "石家庄",
    "Lanzhou": "兰州",
    "Xiamen": "厦门",
    "Fuzhou": "福州",
    "Nanning": "南宁",
    "Kunming": "昆明",
    "Guiyang": "贵阳",
    "Haikou": "海口",
    "Ürümqi": "乌鲁木齐",
    "Lhasa": "拉萨"
}

# Custom icons for better UI
ICONS = {
    "title": "📋",
    "basic_info": "📋",
    "risk_assessment": "🔍",
    "style_risk": "👟",
    "material_risk": "🧵",
    "factory_risk": "🏭",
    "package_risk": "📦",
    "other_risks": "📝",
    "conclusion": "✅",
    "signatures": "✍️",
    "generate": "📊",
    "download": "📥",
    "settings": "⚙️",
    "language": "🌐",
    "location": "📍",
    "time": "🕐",
    "info": "ℹ️",
    "factory": "🏭",
    "brand": "🏷️",
    "po": "📄",
    "style": "👕",
    "description": "📄",
    "sales": "👔",
    "tech": "🔧",
    "qc": "👁️",
    "assessment": "📋",
    "success": "✅",
    "error": "⚠️",
    "warning": "⚠️",
    "upload": "📤",
    "photo": "📷",
    "process": "🔄",
    "cap": "🔄",
    
}

# Custom CSS with enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        padding: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .section-header {
        font-size: 1.9rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding: 0.8rem 1.2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-header-icon {
        font-size: 1.8rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        padding: 1rem 2.5rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .stButton>button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: 0.5s;
    }
    .stButton>button:hover:before {
        left: 100%;
    }
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem;
        border-radius: 15px;
        color: white;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-right: 1px solid #dee2e6;
    }
    .stSelectbox, .stTextInput, .stTextArea, .stRadio {
        background-color: white;
        border-radius: 10px;
        padding: 0.8rem;
        box-shadow: 0 3px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
    }
    .stSelectbox:hover, .stTextInput:hover, .stTextArea:hover, .stRadio:hover {
        border-color: #667eea;
        box-shadow: 0 5px 10px rgba(102, 126, 234, 0.1);
    }
    .stExpander {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.2rem;
        border: 1px solid #e0e0e0;
        overflow: hidden;
    }
    .stExpander > div:first-child {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px 12px 0 0;
    }
    div[data-baseweb="tab"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px !important;
        padding: 0.5rem;
        margin: 0.2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .location-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        margin-top: 2rem;
        border-top: 3px solid #667eea;
    }
    .risk-level-low {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    .risk-level-medium {
        background-color: #fff3cd;
        color: #856404;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    .risk-level-high {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    .risk-warning {
        font-size: 2rem;
        animation: pulse 2s infinite;
        display: inline-block;
        margin-right: 15px;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "en"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "en"
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Shanghai"
if 'translations_cache' not in st.session_state:
    st.session_state.translations_cache = {}

# Translation function using GPT-4o mini - FIXED VERSION
def translate_text(text, target_language="zh"):
    """Translate text using GPT-4o mini with caching"""
    if not text or not text.strip():
        return text
    
    # Check cache first
    cache_key = f"{text}_{target_language}"
    if cache_key in st.session_state.translations_cache:
        return st.session_state.translations_cache[cache_key]
    
    # Don't translate numbers or alphanumeric codes
    if text.strip().replace('.', '').replace(',', '').replace('-', '').isdigit():
        st.session_state.translations_cache[cache_key] = text
        return text
    
    if not openai_client:
        # Fallback to simple translations if no API key
        st.session_state.translations_cache[cache_key] = text
        return text
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_language}. Only return the translation, no explanations. Preserve any numbers, dates, and special formatting."},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        translated_text = response.choices[0].message.content.strip()
        st.session_state.translations_cache[cache_key] = translated_text
        return translated_text
    except Exception as e:
        st.warning(f"Translation failed: {str(e)}. Using original text.")
        st.session_state.translations_cache[cache_key] = text
        return text

def translate_list(text_list, target_language="zh"):
    """Translate a list of texts"""
    return [translate_text(text, target_language) for text in text_list]

# Helper function to get translated text with caching
def get_text(key, fallback=None):
    """Get translated text based on current UI language"""
    lang = st.session_state.ui_language
    
    # Base English texts
    texts = {
        "title": "Production Risk Assessment Report",
        "basic_info": "Basic Information",
        "risk_assessment": "Risk Assessment",
        "style_risk": "1. Style & Construction Risk",
        "material_risk": "2. Raw Material Risk",
        "factory_risk": "3. Factory Performance Risk",
        "package_risk": "4. Package Risk",
        "other_risks": "5. Other Risks",
        "cap_description": "Corrective Action Plan (CAP) Description",
        "conclusion": "Conclusion",
        "signatures": "Signatures & Approvals",
        "generate_pdf": "Generate PDF Report",
        "download_pdf": "Download PDF Report",
        "po_number": "PO / Order Number",
        "factory": "Factory Name",
        "style": "Style / Model",
        "brand": "Brand / Trademark",
        "sales": "Sales / Business",
        "shoe_photo": "Shoe Photo",
        "risk_stage": "Risk Stage",
        "description": "Description (Sales, Tech & QC Manager write)",
        "cap_desc": "CAP Description",
        "prepared_by": "Prepared By",
        "approved_by": "Approved By",
        "overall_result": "Overall Result",
        "footer_text": "Production Risk Assessment System",
        "generate_success": "PDF Generated Successfully!",
        "fill_required": "Please fill in at least PO Number and Factory Name!",
        "creating_pdf": "Creating your professional PDF report...",
        "pdf_details": "PDF Details",
        "report_language": "Report Language",
        "generated": "Generated",
        "location": "Location",
        "error_generating": "Error generating PDF",
        "select_location": "Select Location",
        "user_interface_language": "User Interface Language",
        "pdf_report_language": "PDF Report Language",
        "test_location": "Assessment Location",
        "local_time": "Local Time",
        "quick_guide": "Quick Guide",
        "powered_by": "Powered by Streamlit",
        "copyright": "© 2025 - Production Risk Assessment Platform",
        "upload_photo": "Upload Shoe Photo",
        "sales_comments": "Sales Comments",
        "tech_comments": "Technical Comments",
        "qc_comments": "QC Manager Comments",
        "process_flow": "Process Flow",
        "risk_level": "Risk Level"
    }
    
    text = texts.get(key, fallback or key)
    
    # Translate if needed
    if lang == "zh" and openai_client:
        return translate_text(text, "zh")
    return text

def translate_pdf_content(text, pdf_lang):
    """Translate text for PDF based on selected language"""
    if pdf_lang == "en" or not openai_client:
        return text
    return translate_text(text, "zh")

# Enhanced PDF Generation with Headers and Footers
class PDFWithHeaderFooter(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self.header_text = kwargs.pop('header_text', '')
        self.location = kwargs.pop('location', '')
        self.pdf_language = kwargs.pop('pdf_language', 'en')
        self.selected_city = kwargs.pop('selected_city', '')
        self.chinese_city = kwargs.pop('chinese_city', '')
        self.chinese_font = kwargs.pop('chinese_font', 'Helvetica')
        super().__init__(*args, **kwargs)
        
    def afterFlowable(self, flowable):
        """Add header and footer"""
        if isinstance(flowable, PageBreak):
            return
            
        # Add header on all pages except first
        if self.page > 1:
            self.canv.saveState()
            # Header with gradient effect
            self.canv.setFillColor(colors.HexColor('#667eea'))
            self.canv.rect(0, self.pagesize[1] - 0.6*inch, self.pagesize[0], 0.6*inch, fill=1, stroke=0)
            
            # Use Chinese font if needed
            font_size = 12
            if self.pdf_language == "zh":
                self.canv.setFont(self.chinese_font, font_size)
            else:
                self.canv.setFont('Helvetica-Bold', font_size)
                
            self.canv.setFillColor(colors.white)
            header_title = "PRODUCTION RISK ASSESSMENT REPORT"
            self.canv.drawCentredString(
                self.pagesize[0]/2.0, 
                self.pagesize[1] - 0.4*inch, 
                header_title
            )
            self.canv.restoreState()
            
        # Footer on all pages
        self.canv.saveState()
        
        # Footer background with subtle gradient
        self.canv.setFillColor(colors.HexColor('#f8f9fa'))
        self.canv.rect(0, 0, self.pagesize[0], 0.7*inch, fill=1, stroke=0)
        
        # Top border
        self.canv.setStrokeColor(colors.HexColor('#667eea'))
        self.canv.setLineWidth(1)
        self.canv.line(0, 0.7*inch, self.pagesize[0], 0.7*inch)
        
        # Footer text - use Chinese font if needed
        font_size = 8
        if self.pdf_language == "zh":
            self.canv.setFont(self.chinese_font, font_size)
        else:
            self.canv.setFont('Helvetica', font_size)
            
        self.canv.setFillColor(colors.HexColor('#666666'))
        
        # Left: Location - Show Chinese city only for Mandarin PDFs
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(china_tz)
        
        if self.pdf_language == "zh" and self.chinese_city:
            location_info = f"地点: {self.selected_city} ({self.chinese_city})"
        else:
            location_info = f"Location: {self.selected_city}"
        
        self.canv.drawString(0.5*inch, 0.25*inch, location_info)
        
        # Center: Timestamp
        timestamp = f"Generated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.canv.drawCentredString(self.pagesize[0]/2.0, 0.25*inch, timestamp)
        
        # Right: Page number
        page_num = f"Page {self.page}"
        self.canv.drawRightString(self.pagesize[0] - 0.5*inch, 0.25*inch, page_num)
        
        self.canv.restoreState()

def generate_pdf():
    """Generate PDF report"""
    buffer = io.BytesIO()
    
    # Get location info
    selected_city = st.session_state.selected_city
    chinese_city = CHINESE_CITIES[selected_city]
    pdf_lang = st.session_state.pdf_language
    
    # Register Chinese font if needed
    chinese_font = 'Helvetica'  # Default font
    
    if pdf_lang == "zh":
        try:
            # Try to use built-in Chinese font from ReportLab
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                chinese_font = 'STSong-Light'
            except Exception as e1:
                st.warning(f"STSong-Light not available: {str(e1)}")
                try:
                    # Try other common Chinese fonts
                    pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
                    chinese_font = 'SimSun'
                except Exception as e2:
                    st.warning(f"SimSun not available: {str(e2)}")
                    try:
                        pdfmetrics.registerFont(TTFont('YaHei', 'msyh.ttc'))
                        chinese_font = 'YaHei'
                    except Exception as e3:
                        # Fall back to Helvetica
                        chinese_font = 'Helvetica'
                        st.warning("Chinese fonts not found. Using Helvetica as fallback.")
        except Exception as e:
            st.warning(f"Could not register Chinese font: {str(e)}")
            chinese_font = 'Helvetica'
    
    # Create PDF with custom header/footer
    doc = PDFWithHeaderFooter(
        buffer, 
        pagesize=A4,
        topMargin=0.8*inch,
        bottomMargin=0.8*inch,
        header_text="PRODUCTION RISK ASSESSMENT REPORT",
        location=f"{selected_city}",
        pdf_language=pdf_lang,
        selected_city=selected_city,
        chinese_city=chinese_city,
        chinese_font=chinese_font
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Create styles with appropriate fonts
    title_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    normal_font = 'Helvetica' if pdf_lang != "zh" else chinese_font
    bold_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    
    # Improved title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName=bold_font,
        underlineWidth=1,
        underlineColor=colors.HexColor('#764ba2'),
        underlineOffset=-3
    )
    
    # Company header style
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName=bold_font
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#764ba2'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName=bold_font
    )
    
    # Heading style for sections
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.white,
        spaceAfter=8,
        spaceBefore=12,
        fontName=bold_font,
        borderPadding=6,
        borderColor=colors.HexColor('#667eea'),
        borderWidth=1,
        borderRadius=4,
        backColor=colors.HexColor('#667eea'),
        alignment=TA_LEFT
    )
    
    # Subheading style
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6,
        fontName=bold_font,
        alignment=TA_LEFT
    )
    
    # Risk description style
    risk_desc_style = ParagraphStyle(
        'RiskDescription',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#555555'),
        leading=12,
        alignment=TA_JUSTIFY,
        fontName=normal_font
    )
    
    # Normal style
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName=normal_font
    )
    
    # Company Header
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("PRODUCTION RISK ASSESSMENT REPORT", company_style))
    
    # Title
    report_title = translate_pdf_content("Production Risk Assessment Report", pdf_lang)
    elements.append(Paragraph(report_title, title_style))
    
    # Location and date
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    
    if pdf_lang == "zh":
        location_text = translate_pdf_content(f"地点: {selected_city} ({chinese_city})", pdf_lang)
    else:
        location_text = f"Location: {selected_city}"
    
    date_text = translate_pdf_content(f"Report Date: {current_time.strftime('%Y-%m-%d')}", pdf_lang)
    
    elements.append(Paragraph(location_text, subtitle_style))
    elements.append(Paragraph(date_text, subtitle_style))
    
    # Decorative line
    elements.append(Paragraph("<hr width='80%' color='#667eea'/>", normal_style))
    elements.append(Spacer(1, 15))
    
    # Helper function for creating paragraphs
    def create_paragraph(text, style=normal_style, bold=False):
        """Create paragraph with appropriate font"""
        if bold:
            font_name = bold_font
        else:
            font_name = normal_font
        
        custom_style = ParagraphStyle(
            f"CustomStyle_{bold}",
            parent=style,
            fontName=font_name
        )
        
        return Paragraph(text, custom_style)
    
    # 1. Basic Information Table
    basic_title = translate_pdf_content("1. BASIC INFORMATION", pdf_lang)
    elements.append(Paragraph(basic_title, heading_style))
    elements.append(Spacer(1, 5))
    
    # Get values from session state or use defaults
    po_number_val = st.session_state.get('po_number', '')
    style_val = st.session_state.get('style', '')
    brand_val = st.session_state.get('brand', '')
    sales_person_val = st.session_state.get('sales', '')
    factory_val = st.session_state.get('factory', '')
    assessment_date_val = st.session_state.get('assessment_date', datetime.now())
    
    basic_data = [
        [
            create_paragraph(translate_pdf_content("PO / Order Number:", pdf_lang), bold=True), 
            create_paragraph(po_number_val), 
            create_paragraph(translate_pdf_content("Style / Model:", pdf_lang), bold=True), 
            create_paragraph(style_val)
        ],
        [
            create_paragraph(translate_pdf_content("Brand / Trademark:", pdf_lang), bold=True), 
            create_paragraph(brand_val), 
            create_paragraph(translate_pdf_content("Sales / Business:", pdf_lang), bold=True), 
            create_paragraph(sales_person_val)
        ],
        [
            create_paragraph(translate_pdf_content("Factory Name:", pdf_lang), bold=True), 
            create_paragraph(factory_val), 
            create_paragraph(translate_pdf_content("Assessment Date:", pdf_lang), bold=True), 
            create_paragraph(assessment_date_val.strftime('%Y-%m-%d') if hasattr(assessment_date_val, 'strftime') else str(assessment_date_val))
        ]
    ]
    
    basic_table = Table(basic_data, colWidths=[1.5*inch, 2.0*inch, 1.5*inch, 2.0*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f4ff')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f4ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (2, 0), (2, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d4d4d4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9ff')])
    ]))
    elements.append(basic_table)
    elements.append(Spacer(1, 15))
    
    # 2. Risk Assessment Matrix
    risk_title = translate_pdf_content("2. RISK ASSESSMENT MATRIX", pdf_lang)
    elements.append(Paragraph(risk_title, heading_style))
    elements.append(Spacer(1, 5))
    
    # Get risk descriptions from session state
    style_risk_desc = st.session_state.get('style_risk_desc', '')
    style_cap_desc_val = st.session_state.get('style_cap_desc', '')
    material_risk_desc = st.session_state.get('material_risk_desc', '')
    material_cap_desc_val = st.session_state.get('material_cap_desc', '')
    factory_risk_desc = st.session_state.get('factory_risk_desc', '')
    factory_cap_desc_val = st.session_state.get('factory_cap_desc', '')
    package_risk_desc = st.session_state.get('package_risk_desc', '')
    package_cap_desc_val = st.session_state.get('package_cap_desc', '')
    other_risk_desc = st.session_state.get('other_risk_desc', '')
    other_cap_desc_val = st.session_state.get('other_cap_desc', '')
    
    # Risk stage descriptions
    risk_descriptions = [
        {
            "title": "1. Style & Construction Risk",
            "subtitle": translate_pdf_content("Potential production risk generated by styling features on this product", pdf_lang),
            "content": style_risk_desc,
            "cap": style_cap_desc_val
        },
        {
            "title": "2. Raw Material Risk",
            "subtitle": translate_pdf_content("Potential risk presented to manufacture by properties of the material", pdf_lang),
            "content": material_risk_desc,
            "cap": material_cap_desc_val
        },
        {
            "title": "3. Factory Performance Risk",
            "subtitle": translate_pdf_content("Factory production potential risks (including finishing etc.)", pdf_lang),
            "content": factory_risk_desc,
            "cap": factory_cap_desc_val
        },
        {
            "title": "4. Package Risk",
            "subtitle": translate_pdf_content("Packaging related risks", pdf_lang),
            "content": package_risk_desc,
            "cap": package_cap_desc_val
        },
        {
            "title": "5. Other Risks",
            "subtitle": translate_pdf_content("Any other potential risks", pdf_lang),
            "content": other_risk_desc,
            "cap": other_cap_desc_val
        }
    ]
    
    # Create risk assessment table
    risk_headers = [
        create_paragraph(translate_pdf_content("Risk Stage", pdf_lang), bold=True),
        create_paragraph(translate_pdf_content("Description", pdf_lang), bold=True),
        create_paragraph(translate_pdf_content("CAP Description", pdf_lang), bold=True)
    ]
    
    risk_data = [risk_headers]
    
    for i, risk in enumerate(risk_descriptions):
        risk_data.append([
            create_paragraph(translate_pdf_content(risk["title"], pdf_lang), bold=True),
            create_paragraph(risk["content"] if risk["content"] else "-", risk_desc_style),
            create_paragraph(risk["cap"] if risk["cap"] else "-", risk_desc_style)
        ])
    
    risk_table = Table(risk_data, colWidths=[1.8*inch, 2.5*inch, 2.5*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9ff')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6)
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 20))
    
    # 3. Department Comments
    elements.append(PageBreak())
    
    comments_title = translate_pdf_content("3. DEPARTMENT COMMENTS", pdf_lang)
    elements.append(Paragraph(comments_title, heading_style))
    elements.append(Spacer(1, 10))
    
    # Get comments from session state
    sales_comments_val = st.session_state.get('sales_comments', '')
    tech_comments_val = st.session_state.get('tech_comments', '')
    qc_comments_val = st.session_state.get('qc_comments', '')
    conclusion_val = st.session_state.get('conclusion', '')
    
    # Sales Comments
    sales_title = translate_pdf_content("Sales Comments:", pdf_lang)
    elements.append(Paragraph(sales_title, subheading_style))
    
    if sales_comments_val:
        sales_para = create_paragraph(sales_comments_val, risk_desc_style)
        elements.append(sales_para)
    else:
        elements.append(create_paragraph("-", risk_desc_style))
    
    elements.append(Spacer(1, 8))
    
    # Technical Comments
    tech_title = translate_pdf_content("Technical Comments:", pdf_lang)
    elements.append(Paragraph(tech_title, subheading_style))
    
    if tech_comments_val:
        tech_para = create_paragraph(tech_comments_val, risk_desc_style)
        elements.append(tech_para)
    else:
        elements.append(create_paragraph("-", risk_desc_style))
    
    elements.append(Spacer(1, 8))
    
    # QC Manager Comments
    qc_title = translate_pdf_content("QC Manager Comments:", pdf_lang)
    elements.append(Paragraph(qc_title, subheading_style))
    
    if qc_comments_val:
        qc_para = create_paragraph(qc_comments_val, risk_desc_style)
        elements.append(qc_para)
    else:
        elements.append(create_paragraph("-", risk_desc_style))
    
    elements.append(Spacer(1, 15))
    
    # 4. Conclusion and Signatures
    conclusion_title = translate_pdf_content("4. CONCLUSION & APPROVALS", pdf_lang)
    elements.append(Paragraph(conclusion_title, heading_style))
    elements.append(Spacer(1, 10))
    
    # Conclusion
    conclusion_text = translate_pdf_content("Conclusion:", pdf_lang)
    elements.append(Paragraph(conclusion_text, subheading_style))
    
    if conclusion_val:
        conclusion_para = create_paragraph(conclusion_val, risk_desc_style)
        elements.append(conclusion_para)
    else:
        elements.append(create_paragraph("-", risk_desc_style))
    
    elements.append(Spacer(1, 15))
    
    # Get signature data from session state
    sales_signature_val = st.session_state.get('sales_signature', '')
    sales_date_val = st.session_state.get('sales_date', datetime.now())
    tech_signature_val = st.session_state.get('tech_signature', '')
    tech_date_val = st.session_state.get('tech_date', datetime.now())
    qc_signature_val = st.session_state.get('qc_signature', '')
    qc_date_val = st.session_state.get('qc_date', datetime.now())
    
    # Signature table
    sig_data = [
        [
            create_paragraph(translate_pdf_content("Sales:", pdf_lang), bold=True),
            create_paragraph(sales_signature_val if sales_signature_val else "_________________"),
            create_paragraph(translate_pdf_content("Date:", pdf_lang), bold=True),
            create_paragraph(sales_date_val.strftime('%Y-%m-%d') if hasattr(sales_date_val, 'strftime') else "__________")
        ],
        [
            create_paragraph(translate_pdf_content("Technical:", pdf_lang), bold=True),
            create_paragraph(tech_signature_val if tech_signature_val else "_________________"),
            create_paragraph(translate_pdf_content("Date:", pdf_lang), bold=True),
            create_paragraph(tech_date_val.strftime('%Y-%m-%d') if hasattr(tech_date_val, 'strftime') else "__________")
        ],
        [
            create_paragraph(translate_pdf_content("QC Manager:", pdf_lang), bold=True),
            create_paragraph(qc_signature_val if qc_signature_val else "_________________"),
            create_paragraph(translate_pdf_content("Date:", pdf_lang), bold=True),
            create_paragraph(qc_date_val.strftime('%Y-%m-%d') if hasattr(qc_date_val, 'strftime') else "__________")
        ]
    ]
    
    sig_table = Table(sig_data, colWidths=[1.2*inch, 2.3*inch, 0.8*inch, 1.5*inch])
    sig_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f4ff')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f4ff')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (2, 0), (2, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(sig_table)
    
    # Final note about report distribution
    elements.append(Spacer(1, 20))
    process_note = translate_pdf_content(
        "Note: QC will send this report to office together with final inspection report. "
        "Office assistant will upload to ERP system and send email to factory/agent accordingly.",
        pdf_lang
    )
    elements.append(Paragraph(process_note, normal_style))
    
    # Confidential footer
    elements.append(Spacer(1, 10))
    footer_note = translate_pdf_content(
        "This report is confidential and property of the company. Unauthorized distribution is prohibited.",
        pdf_lang
    )
    elements.append(Paragraph(footer_note, normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Sidebar with enhanced filters
with st.sidebar:
    st.markdown(f'### {ICONS["settings"]} Settings & Filters')
    
    # Language filters with icons
    st.markdown(f'#### {ICONS["language"]} Language Settings')
    ui_language = st.selectbox(
        "User Interface Language",
        ["English", "Mandarin"],
        index=0 if st.session_state.ui_language == "en" else 1,
        key="ui_lang_select"
    )
    st.session_state.ui_language = "en" if ui_language == "English" else "zh"
    
    pdf_language = st.selectbox(
        "PDF Report Language",
        ["English", "Mandarin"],
        index=0 if st.session_state.pdf_language == "en" else 1,
        key="pdf_lang_select"
    )
    st.session_state.pdf_language = "en" if pdf_language == "English" else "zh"
    
    # Location filter with enhanced UI
    st.markdown(f'#### {ICONS["location"]} Location Settings')
    selected_city = st.selectbox(
        "Select Assessment Location",
        list(CHINESE_CITIES.keys()),
        index=list(CHINESE_CITIES.keys()).index(st.session_state.selected_city) 
        if st.session_state.selected_city in CHINESE_CITIES else 0,
        key="city_select"
    )
    st.session_state.selected_city = selected_city
    
    # Display selected location in a badge
    st.markdown(f"""
    <div class="location-badge">
        {ICONS["location"]} {selected_city} ({CHINESE_CITIES[selected_city]})
    </div>
    """, unsafe_allow_html=True)
    
    # Timezone information
    st.markdown(f'#### {ICONS["time"]} Timezone Info')
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    st.metric(
        "Local Time", 
        current_time.strftime('%H:%M:%S'),
        current_time.strftime('%Y-%m-%d')
    )
    
    # Translation status
    if openai_client:
        st.success(f"{ICONS['success']} Translation API: Active")
    else:
        st.warning(f"{ICONS['warning']} Translation API: Not Configured")
    
    st.markdown("---")
    
    # Process Flow Information
    st.markdown(f'#### {ICONS["process"]} Process Flow')
    st.info(f"""
    {ICONS["process"]} **Report Workflow:**
    1. {ICONS["sales"]} Sales opens form
    2. {ICONS["tech"]} Discuss with Technical department
    3. {ICONS["factory"]} Send to factory
    4. {ICONS["qc"]} QC follows up
    5. {ICONS["download"]} Final report distribution
    """)
    
    st.markdown("---")
    st.markdown(f'### {ICONS["info"]} Instructions')
    st.info(f"""
    {ICONS["info"]} **Quick Guide:**
    1. {ICONS["basic_info"]} Fill all required fields
    2. {ICONS["risk_assessment"]} Complete risk assessments
    3. {ICONS["language"]} Select preferred languages
    4. {ICONS["location"]} Choose assessment location
    5. {ICONS["generate"]} Generate PDF report
    """)

# Title with enhanced styling
st.markdown(f"""
<div class="main-header">
    <span class="risk-warning"></span> Production Risk Assessment Report
</div>
""", unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs([
    f"{ICONS['basic_info']} Basic Info",
    f"{ICONS['risk_assessment']} Risk Assessment",
    f"{ICONS['signatures']} Signatures"
])

with tab1:
    # Basic Information Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["basic_info"]}</span>
        {get_text("basic_info")}
    </div>
    """, unsafe_allow_html=True)
    
    # Main basic info in columns
    col1, col2 = st.columns(2)
    
    with col1:
        po_number = st.text_input(
            f"{ICONS['po']} {get_text('po_number')}", 
            placeholder="PO-2024-001",
            key="po_number"
        )
        
        style = st.text_input(
            f"{ICONS['style']} {get_text('style')}", 
            placeholder="Model XYZ-2024",
            key="style"
        )
        
        factory = st.text_input(
            f"{ICONS['factory']} {get_text('factory')}", 
            placeholder="ABC Manufacturing Co., Ltd.",
            key="factory"
        )
    
    with col2:
        brand = st.text_input(
            f"{ICONS['brand']} {get_text('brand')}", 
            placeholder="Brand Name",
            key="brand"
        )
        
        sales_person = st.text_input(
            f"{ICONS['sales']} {get_text('sales')}", 
            placeholder="Sales Representative Name",
            key="sales"
        )
        
        assessment_date = st.date_input(
            f"{ICONS['time']} Assessment Date", 
            datetime.now(),
            key="assessment_date"
        )
    
    
with tab2:
    # Risk Assessment Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["risk_assessment"]}</span>
        {get_text("risk_assessment")}
    </div>
    """, unsafe_allow_html=True)
    
    # 1. Style & Construction Risk
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["style_risk"]}</span>
        {get_text("style_risk")}
    </div>
    """, unsafe_allow_html=True)
    
    style_risk_description = st.text_area(
        f"{ICONS['description']} {get_text('description')}",
        placeholder="Describe potential risks related to style and construction...",
        height=120,
        key="style_risk_desc"
    )
    
    style_cap_description = st.text_area(
        f"{ICONS['cap']} {get_text('cap_desc')}",
        placeholder="Describe corrective action plan for style risks...",
        height=100,
        key="style_cap_desc"
    )
    
    # 2. Raw Material Risk
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["material_risk"]}</span>
        {get_text("material_risk")}
    </div>
    """, unsafe_allow_html=True)
    
    material_risk_description = st.text_area(
        f"{ICONS['description']} {get_text('description')}",
        placeholder="Describe potential risks related to raw materials...",
        height=120,
        key="material_risk_desc"
    )
    
    material_cap_description = st.text_area(
        f"{ICONS['cap']} {get_text('cap_desc')}",
        placeholder="Describe corrective action plan for material risks...",
        height=100,
        key="material_cap_desc"
    )
    
    # 3. Factory Performance Risk
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["factory_risk"]}</span>
        {get_text("factory_risk")}
    </div>
    """, unsafe_allow_html=True)
    
    factory_risk_description = st.text_area(
        f"{ICONS['description']} {get_text('description')}",
        placeholder="Describe potential risks related to factory performance...",
        height=120,
        key="factory_risk_desc"
    )
    
    factory_cap_description = st.text_area(
        f"{ICONS['cap']} {get_text('cap_desc')}",
        placeholder="Describe corrective action plan for factory risks...",
        height=100,
        key="factory_cap_desc"
    )
    
    # 4. Package Risk
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["package_risk"]}</span>
        {get_text("package_risk")}
    </div>
    """, unsafe_allow_html=True)
    
    package_risk_description = st.text_area(
        f"{ICONS['description']} {get_text('description')}",
        placeholder="Describe potential risks related to packaging...",
        height=120,
        key="package_risk_desc"
    )
    
    package_cap_description = st.text_area(
        f"{ICONS['cap']} {get_text('cap_desc')}",
        placeholder="Describe corrective action plan for packaging risks...",
        height=100,
        key="package_cap_desc"
    )
    
    # 5. Other Risks
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["other_risks"]}</span>
        {get_text("other_risks")}
    </div>
    """, unsafe_allow_html=True)
    
    other_risk_description = st.text_area(
        f"{ICONS['description']} {get_text('description')}",
        placeholder="Describe any other potential risks...",
        height=120,
        key="other_risk_desc"
    )
    
    other_cap_description = st.text_area(
        f"{ICONS['cap']} {get_text('cap_desc')}",
        placeholder="Describe corrective action plan for other risks...",
        height=100,
        key="other_cap_desc"
    )

with tab3:
    # Department Comments and Signatures
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["signatures"]}</span>
        {get_text("signatures")}
    </div>
    """, unsafe_allow_html=True)
    
    # Department Comments
    st.markdown(f"#### {ICONS['sales']} {get_text('sales_comments')}")
    sales_comments = st.text_area(
        "Sales department comments and observations",
        placeholder="Enter sales department comments here...",
        height=120,
        key="sales_comments",
        label_visibility="collapsed"
    )
    
    st.markdown(f"#### {ICONS['tech']} {get_text('tech_comments')}")
    tech_comments = st.text_area(
        "Technical department comments and observations",
        placeholder="Enter technical department comments here...",
        height=120,
        key="tech_comments",
        label_visibility="collapsed"
    )
    
    st.markdown(f"#### {ICONS['qc']} {get_text('qc_comments')}")
    qc_comments = st.text_area(
        "QC Manager comments and observations",
        placeholder="Enter QC Manager comments here...",
        height=120,
        key="qc_comments",
        label_visibility="collapsed"
    )
    
    # Conclusion
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["conclusion"]}</span>
        {get_text("conclusion")}
    </div>
    """, unsafe_allow_html=True)
    
    conclusion = st.text_area(
        "Overall conclusion and summary",
        placeholder="Enter overall conclusion and summary here...",
        height=120,
        key="conclusion"
    )
    
    # Signatures
    st.markdown(f"#### {ICONS['signatures']} Signatures")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sales_signature = st.text_input(
            "Sales Signature",
            placeholder="Sales representative name",
            key="sales_signature"
        )
        sales_date = st.date_input(
            "Sales Date",
            datetime.now(),
            key="sales_date"
        )
        
        tech_signature = st.text_input(
            "Technical Signature",
            placeholder="Technical expert name",
            key="tech_signature"
        )
        tech_date = st.date_input(
            "Technical Date",
            datetime.now(),
            key="tech_date"
        )
    
    with col2:
        qc_signature = st.text_input(
            "QC Manager Signature",
            placeholder="QC Manager name",
            key="qc_signature"
        )
        qc_date = st.date_input(
            "QC Date",
            datetime.now(),
            key="qc_date"
        )

# Generate PDF Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(f"{ICONS['generate']} {get_text('generate_pdf')}", use_container_width=True):
        if not st.session_state.get('po_number') or not st.session_state.get('factory'):
            st.error(f"{ICONS['error']} {get_text('fill_required')}")
        else:
            with st.spinner(f"{ICONS['time']} {get_text('creating_pdf')}"):
                try:
                    pdf_buffer = generate_pdf()
                    st.success(f"{ICONS['success']} {get_text('generate_success')}")
                    
                    # Display PDF preview info
                    with st.expander(f"{ICONS['info']} {get_text('pdf_details')}"):
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric(get_text("location"), f"{selected_city} ({CHINESE_CITIES[selected_city]})")
                            st.metric(get_text("report_language"), "Mandarin" if st.session_state.pdf_language == "zh" else "English")
                        with col_info2:
                            china_tz = pytz.timezone('Asia/Shanghai')
                            current_time = datetime.now(china_tz)
                            st.metric(get_text("generated"), current_time.strftime('%H:%M:%S'))
                    
                    # Download button
                    filename = f"Risk_Assessment_Report_{st.session_state.get('po_number', '')}_{selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label=f"{ICONS['download']} {get_text('download_pdf')}",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"{ICONS['error']} {get_text('error_generating')}: {str(e)}")
                    st.error(f"Detailed error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <p style='font-size: 1.2rem; font-weight: 600; color: #667eea; margin-bottom: 0.5rem;'>
        {ICONS['title']} {get_text('footer_text')}
    </p>
    <p style='font-size: 0.9rem; color: #666666;'>
        {ICONS['location']} {get_text('location')}: {selected_city} ({CHINESE_CITIES[selected_city]}) | 
        {ICONS['language']} {get_text('report_language')}: {'Mandarin' if st.session_state.pdf_language == 'zh' else 'English'}
    </p>
    <p style='font-size: 0.8rem; color: #999999; margin-top: 1rem;'>
        {get_text('powered_by')} | {get_text('copyright')}
    </p>
</div>
""", unsafe_allow_html=True)

# Create .env file instructions in sidebar
with st.sidebar:
    with st.expander(f"{ICONS['info']} API Setup"):
        st.code("""
# Create .env file in your project folder
OPENAI_API_KEY=your-api-key-here
""")
        st.info("Restart the app after adding your API key to enable translations.")
