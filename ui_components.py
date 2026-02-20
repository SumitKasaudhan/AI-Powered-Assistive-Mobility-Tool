# ui_components.py
import streamlit as st
from typing import Optional, Dict, List, Tuple, Callable
import base64
from pathlib import Path

class VisionMateUI:
    """All UI components for VisionMate"""
    
    # ===================== CSS STYLES =====================
    
    @staticmethod
    def load_css():
        """Load all CSS styles"""
        st.markdown("""
<style>

/* ================================
   THEME VARIABLES (AUTO DETECT)
================================ */
:root {
    --bg-main: #f8f9fb;
    --bg-card: #ffffff;
    --bg-soft: #f0f2f6;

    --text-main: #1f2933;
    --text-muted: #6b7280;

    --primary: #4B0082;
    --success: #2e7d32;
    --warning: #c62828;

    --border-soft: #e5e7eb;
}

/* DARK MODE */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-main: #0f172a;
        --bg-card: #111827;
        --bg-soft: #1e293b;

        --text-main: #e5e7eb;
        --text-muted: #9ca3af;

        --primary: #a78bfa;
        --success: #4ade80;
        --warning: #f87171;

        --border-soft: #334155;
    }
}

/* ================================
   GLOBAL TEXT & BACKGROUND
================================ */
html, body, .stApp {
    background-color: var(--bg-main);
    color: var(--text-main);
}

/* ================================
   HEADERS
================================ */
.main-header {
    font-size: 3.2rem;
    font-weight: 700;
    color: var(--primary);
    text-align: center;
    margin-bottom: 1.5rem;
}

.sub-header {
    font-size: 1.4rem;
    color: var(--text-muted);
    text-align: center;
    margin-bottom: 2.5rem;
}

/* ================================
   FEATURE CARDS
================================ */
.feature-card {
    background-color: var(--bg-card);
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-left: 5px solid var(--primary);
    transition: all 0.25s ease;
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.feature-icon {
    font-size: 2.3rem;
    color: var(--primary);
    margin-bottom: 0.8rem;
}

/* ================================
   MODE CARDS
================================ */
.mode-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-soft);
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
}

.mode-card:hover {
    transform: translateY(-8px);
    border-color: var(--primary);
    box-shadow: 0 15px 30px rgba(0,0,0,0.18);
}

.mode-icon {
    font-size: 3rem;
    color: var(--primary);
    margin-bottom: 1rem;
}

/* ================================
   WELCOME HEADER
================================ */
.welcome-header {
    background: linear-gradient(135deg, #667eea, #764ba2);
    padding: 2rem;
    border-radius: 16px;
    color: #ffffff;
    text-align: center;
    margin-bottom: 2rem;
}

/* ================================
   INFO BOXES
================================ */
.info-box {
    background-color: var(--bg-soft);
    padding: 1.2rem;
    border-radius: 10px;
    border-left: 4px solid var(--primary);
}

.warning-box {
    background-color: rgba(248, 113, 113, 0.15);
    padding: 1.2rem;
    border-radius: 10px;
    border-left: 4px solid var(--warning);
}

.success-box {
    background-color: rgba(74, 222, 128, 0.15);
    padding: 1.2rem;
    border-radius: 10px;
    border-left: 4px solid var(--success);
}

/* ================================
   BUTTONS
================================ */
.stButton > button {
    border-radius: 10px !important;
    background-color: var(--primary) !important;
    color: white !important;
    font-weight: 600;
    transition: all 0.25s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.25);
}

/* ================================
   AUDIO STATUS
================================ */
.audio-active {
    background-color: var(--success);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
}

.audio-inactive {
    background-color: var(--warning);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
}

/* ================================
   SIDEBAR
================================ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea, #764ba2);
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* ================================
   SCROLLBAR
================================ */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: var(--border-soft);
    border-radius: 4px;
}

/* ================================
   CLEAN UI
================================ */
#MainMenu, footer, header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)
    
    # ===================== HEADERS & TITLES =====================
    
    @staticmethod
    def page_header(title: str, description: str = None, icon: str = None):
        """Create page header"""
        if icon:
            title = f"{icon} {title}"
        
        st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)
        
        if description:
            st.markdown(f'<p class="sub-header">{description}</p>', unsafe_allow_html=True)
    
    @staticmethod
    def section_header(title: str, level: int = 2):
        """Create section header"""
        if level == 2:
            st.subheader(title)
        elif level == 3:
            st.markdown(f"### {title}")
        else:
            st.markdown(f"#### {title}")
    
    @staticmethod
    def welcome_banner(user_name: str = None):
        """Create welcome banner"""
        if user_name:
            content = f"""
            <div class="welcome-header">
                <h2>👋 Welcome, {user_name}!</h2>
                <p>Choose a mode to start using VisionMate</p>
            </div>
            """
        else:
            content = """
            <div class="welcome-header">
                <h2>👁️ Welcome to VisionMate</h2>
                <p>Enhancing Mobility for the Visually Impaired</p>
            </div>
            """
        
        st.markdown(content, unsafe_allow_html=True)
    
    # ===================== CARDS =====================
    
    @staticmethod
    def feature_card(title: str, description: str, icon: str = "📊", columns: int = 3):
        """Create feature card"""
        card_html = f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """
        return card_html
    
    @staticmethod
    def mode_card(title: str, description: str, icon: str = "📱", detailed_desc: str = None):
        """Create mode card"""
        if detailed_desc:
            description = f"<p>{description}</p><small>{detailed_desc}</small>"
        
        card_html = f"""
        <div class="mode-card">
            <div class="mode-icon">{icon}</div>
            <h3>{title}</h3>
            {description}
        </div>
        """
        return card_html
    
    @staticmethod
    def info_card(title: str, content: str, card_type: str = "info"):
        """Create info card"""
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "success": "✅",
            "error": "❌"
        }
        
        icon = icons.get(card_type, "ℹ️")
        
        card_html = f"""
        <div class="{card_type}-box">
            <h4>{icon} {title}</h4>
            <p>{content}</p>
        </div>
        """
        return card_html
    
    # ===================== BUTTONS =====================
    
    @staticmethod
    def custom_button(
        label: str, 
        key: str, 
        button_type: str = "primary",
        use_container_width: bool = True,
        icon: str = None
    ):
        """Create custom button"""
        if icon:
            label = f"{icon} {label}"
        
        return st.button(
            label,
            key=key,
            type=button_type,
            use_container_width=use_container_width
        )
    
    @staticmethod
    def navigation_buttons():
        """Navigation buttons"""
        col1, col2, col3, col4 = st.columns(4)
        
        buttons = []
        with col1:
            if st.button("🏠 Home", use_container_width=True, key="nav_home"):
                buttons.append("home")
        
        with col2:
            if st.button("📷 Image", use_container_width=True, key="nav_image"):
                buttons.append("image")
        
        with col3:
            if st.button("🎥 Live", use_container_width=True, key="nav_live"):
                buttons.append("live")
        
        with col4:
            if st.button("📤 Video", use_container_width=True, key="nav_video"):
                buttons.append("upload")
        
        return buttons
    
    @staticmethod
    def action_buttons():
        """Action buttons"""
        col1, col2, col3 = st.columns(3)
        
        actions = {}
        with col1:
            if st.button("▶️ Start", type="primary", use_container_width=True, key="btn_start"):
                actions["start"] = True
        
        with col2:
            if st.button("⏹️ Stop", use_container_width=True, key="btn_stop"):
                actions["stop"] = True
        
        with col3:
            if st.button("📸 Capture", use_container_width=True, key="btn_capture"):
                actions["capture"] = True
        
        return actions
    
    # ===================== FORMS & INPUTS =====================
    
    @staticmethod
    def login_form():
        """Login form"""
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                login_submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            with col2:
                demo_submitted = st.form_submit_button("Demo", use_container_width=True)
            
            return {
                'username': username,
                'password': password,
                'login_submitted': login_submitted,
                'demo_submitted': demo_submitted
            }
    
    @staticmethod
    def register_form():
        """Register form"""
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            new_username = st.text_input("Choose a Username*")
            new_name = st.text_input("Your Name*")
            new_password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            
            register_submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            
            return {
                'username': new_username,
                'name': new_name,
                'password': new_password,
                'confirm_password': confirm_password,
                'register_submitted': register_submitted
            }
    
    # ===================== DISPLAY COMPONENTS =====================
    
    @staticmethod
    def image_comparison(original_image, processed_image, original_caption="Original", processed_caption="Processed"):
        """Display image comparison"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(original_caption)
            st.image(original_image, use_container_width=True)
        
        with col2:
            st.subheader(processed_caption)
            st.image(processed_image, use_container_width=True)
    
    @staticmethod
    def video_player(video_path: str, caption: str = "Video Preview"):
        """Video player"""
        try:
            with open(video_path, "rb") as video_file:
                video_bytes = video_file.read()
            
            st.video(video_bytes)
            st.caption(caption)
        except:
            st.warning("Unable to load video")
    
    @staticmethod
    def stats_display(stats: Dict, columns: int = 4):
        """Display statistics"""
        cols = st.columns(columns)
        
        for idx, (key, value) in enumerate(stats.items()):
            with cols[idx % columns]:
                st.metric(key, value)
    
    @staticmethod
    def progress_with_text(progress: float, text: str):
        """Progress bar with text"""
        st.progress(progress)
        st.caption(text)
    
    # ===================== SIDEBAR COMPONENTS =====================
    
    @staticmethod
    def sidebar_header(user_name: str = None):
        """Sidebar header"""
        if user_name:
            st.markdown(f"### 👤 {user_name}")
        else:
            st.markdown("### 👁️ VisionMate")
    
    @staticmethod
    def audio_status_indicator(is_active: bool = True):
        """Audio status indicator"""
        if is_active:
            status_html = '<span class="audio-active">🔊 Audio Active</span>'
        else:
            status_html = '<span class="audio-inactive">🔇 Audio Offline</span>'
        
        st.markdown(status_html, unsafe_allow_html=True)
    
    @staticmethod
    def sidebar_navigation(current_page: str = "home"):
        """Sidebar navigation"""
        st.subheader("Navigation")
        
        pages = {
            "🏠 Home": "home",
            "📷 Image Analysis": "image",
            "🎥 Live Camera": "live",
            "📤 Video Analysis": "upload"
        }
        
        selected_page = current_page
        
        for page_name, page_id in pages.items():
            if st.button(page_name, use_container_width=True, key=f"sb_nav_{page_id}"):
                selected_page = page_id
        
        return selected_page
    
    @staticmethod
    def audio_controls():
        """Audio controls"""
        st.subheader("Audio Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_audio = st.button("🔊 Test", use_container_width=True)
        
        with col2:
            stop_audio = st.button("🔇 Stop", use_container_width=True)
        
        return {
            'test': test_audio,
            'stop': stop_audio
        }
    
    @staticmethod
    def user_info_display(user_info: Dict):
        """Display user info"""
        if user_info:
            st.markdown("---")
            st.caption(f"👤 {user_info.get('name', 'User')}")
            st.caption(f"📅 Member since: {user_info.get('created_at', 'N/A')}")
    
    # ===================== TABS =====================
    
    @staticmethod
    def auth_tabs():
        """Authentication tabs"""
        tab1, tab2 = st.tabs(["Login", "Register"])
        return tab1, tab2
    
    @staticmethod
    def settings_tabs():
        """Settings tabs"""
        tab1, tab2, tab3 = st.tabs(["General", "Audio", "Advanced"])
        return tab1, tab2, tab3
    
    # ===================== ALERTS & MESSAGES =====================
    
    @staticmethod
    def success_message(message: str):
        """Success message"""
        st.success(message)
    
    @staticmethod
    def error_message(message: str):
        """Error message"""
        st.error(message)
    
    @staticmethod
    def warning_message(message: str):
        """Warning message"""
        st.warning(message)
    
    @staticmethod
    def info_message(message: str):
        """Info message"""
        st.info(message)
    
    @staticmethod
    def toast_message(message: str, icon: str = "ℹ️"):
        """Toast message (Streamlit >= 1.28)"""
        try:
            st.toast(f"{icon} {message}")
        except:
            st.info(f"{icon} {message}")
    
    # ===================== LAYOUT HELPERS =====================
    
    @staticmethod
    def create_columns(num_columns: int, spacing: str = "small"):
        """Create columns"""
        return st.columns(num_columns)
    
    @staticmethod
    def create_expander(title: str, expanded: bool = False):
        """Create expander"""
        return st.expander(title, expanded=expanded)
    
    @staticmethod
    def create_container():
        """Create container"""
        return st.container()
    
    # ===================== SPECIAL COMPONENTS =====================
    
    @staticmethod
    def file_uploader(
        label: str, 
        file_types: List[str] = None, 
        help_text: str = None,
        key: str = "file_upload"
    ):
        """File uploader"""
        if file_types is None:
            file_types = ["jpg", "jpeg", "png"]
        
        return st.file_uploader(
            label,
            type=file_types,
            help=help_text,
            key=key
        )
    
    @staticmethod
    def camera_input(label: str = "Take a picture", key: str = "camera"):
        """Camera input"""
        return st.camera_input(label, key=key)
    
    @staticmethod
    def slider_with_icon(
        label: str,
        min_value: float,
        max_value: float,
        value: float,
        icon: str = "🎚️",
        help_text: str = None,
        key: str = "slider"
    ):
        """Slider with icon"""
        if icon:
            label = f"{icon} {label}"
        
        return st.slider(
            label,
            min_value=min_value,
            max_value=max_value,
            value=value,
            help=help_text,
            key=key
        )
    
    @staticmethod
    def selectbox_with_icon(
        label: str,
        options: List[str],
        icon: str = "📋",
        help_text: str = None,
        key: str = "selectbox"
    ):
        """Selectbox with icon"""
        if icon:
            label = f"{icon} {label}"
        
        return st.selectbox(
            label,
            options=options,
            help=help_text,
            key=key
        )
    
    @staticmethod
    def checkbox_with_description(
        label: str,
        value: bool = False,
        description: str = None,
        icon: str = "✓",
        key: str = "checkbox"
    ):
        """Checkbox with description"""
        if icon:
            label = f"{icon} {label}"
        
        checkbox = st.checkbox(label, value=value, key=key)
        
        if description and checkbox:
            st.caption(description)
        
        return checkbox
    
    # ===================== FOOTER =====================
    
    @staticmethod
    def footer(version: str = "2.0", show_time: bool = True):
        """Footer"""
        from datetime import datetime
        
        footer_text = f"VisionMate Enhanced v{version}"
        
        if show_time:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            footer_text += f" • {current_time}"
        
        st.markdown("---")
        st.caption(footer_text)