import streamlit as st
import cv2
import numpy as np
from PIL import Image
import json
import os
import bcrypt
import base64
from io import BytesIO
import tempfile
import time
from datetime import datetime

# Import UI components
from ui_components import VisionMateUI

# AI Libraries
try:
    from ultralytics import YOLO
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    from gtts import gTTS
except ImportError as e:
    st.error(f"Missing required library: {e}. Please install all dependencies.")
    st.stop()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'audio_enabled' not in st.session_state:
    st.session_state.audio_enabled = True
if 'detection_active' not in st.session_state:
    st.session_state.detection_active = False
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'welcome_played' not in st.session_state:
    st.session_state.welcome_played = False

# File paths
USER_DATA_FILE = "users.json"

# ============== AUTHENTICATION MODULE ==============

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username, name, password):
    """Register a new user"""
    users = load_users()
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        'password': hash_password(password),
        'name': name,
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }
    save_users(users)
    return True, "Registration successful"

def login_user(username, password):
    """Authenticate user"""
    users = load_users()
    if username not in users:
        return False, "User not found", None
    
    user_data = users[username]
    
    # Handle old format (string) and new format (dict)
    if isinstance(user_data, str):
        hashed_password = user_data
        user_name = username
    else:
        hashed_password = user_data['password']
        user_name = user_data.get('name', username)
    
    if verify_password(password, hashed_password):
        return True, "Login successful", user_name
    return False, "Incorrect password", None

def text_to_speech(text):
    """Convert text to speech and return audio HTML"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_base64 = base64.b64encode(fp.read()).decode()
        audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
        return audio_html
    except Exception as e:
        st.error(f"Speech error: {e}")
        return None

def auth_page():
    """Authentication UI with integrated components"""
    # Load CSS
    VisionMateUI.load_css()
    
    # Welcome banner
    VisionMateUI.welcome_banner()
    
    # Create tabs
    tab1, tab2 = VisionMateUI.auth_tabs()
    
    with tab1:
        st.subheader("🔐 Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                login_submitted = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
            with col2:
                demo_submitted = st.form_submit_button("👁️ Demo Mode", use_container_width=True)
            
            if login_submitted:
                if username and password:
                    success, message, user_name = login_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_name = user_name
                        VisionMateUI.success_message(message)
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        VisionMateUI.error_message(message)
                else:
                    VisionMateUI.warning_message("Please enter both username and password")
            
            if demo_submitted:
                st.session_state.authenticated = True
                st.session_state.username = "demo_user"
                st.session_state.user_name = "Demo User"
                VisionMateUI.success_message("Welcome to Demo Mode!")
                time.sleep(0.5)
                st.rerun()
    
    with tab2:
        st.subheader("✨ Create New Account")
        
        with st.form("register_form"):
            new_username = st.text_input("Choose Username", key="reg_username")
            new_name = st.text_input("Your Name", key="reg_name")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            register_submitted = st.form_submit_button("📝 Create Account", type="primary", use_container_width=True)
            
            if register_submitted:
                if new_username and new_name and new_password and confirm_password:
                    if new_password != confirm_password:
                        VisionMateUI.error_message("Passwords do not match")
                    elif len(new_password) < 6:
                        VisionMateUI.error_message("Password must be at least 6 characters")
                    else:
                        success, message = register_user(new_username, new_name, new_password)
                        if success:
                            VisionMateUI.success_message(message)
                            VisionMateUI.info_message("You can now login with your credentials")
                        else:
                            VisionMateUI.error_message(message)
                else:
                    VisionMateUI.warning_message("Please fill all fields")
    
    # Footer
    VisionMateUI.footer(version="2.0", show_time=True)

# ============== VISION AI SYSTEM ==============

@st.cache_resource
def load_models():
    """Load YOLOv8 and BLIP models"""
    try:
        yolo_model = YOLO('yolov8n.pt')
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
        
        return yolo_model, blip_processor, blip_model, device
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None, None

def detect_objects(image, yolo_model):
    """Detect objects using YOLOv8"""
    results = yolo_model(image)
    return results[0]

def draw_boxes(image, results):
    """Draw bounding boxes on image"""
    annotated_image = image.copy()
    
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = f"{results.names[cls]} {conf:.2f}"
        
        cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated_image, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)
        cv2.putText(annotated_image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    return annotated_image

def generate_caption(image_pil, blip_processor, blip_model, device):
    """Generate image caption using BLIP"""
    try:
        inputs = blip_processor(image_pil, return_tensors="pt").to(device)
        out = blip_model.generate(**inputs, max_length=50)
        caption = blip_processor.decode(out[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        return f"Caption error: {e}"

def create_detection_description(results):
    """Create natural language description of detections"""
    if len(results.boxes) == 0:
        return "No objects detected in the scene."
    
    object_counts = {}
    for box in results.boxes:
        cls = int(box.cls[0])
        name = results.names[cls]
        object_counts[name] = object_counts.get(name, 0) + 1
    
    description = f"Detected {len(results.boxes)} object{'s' if len(results.boxes) > 1 else ''}: "
    items = [f"{count} {name}{'s' if count > 1 else ''}" for name, count in object_counts.items()]
    description += ", ".join(items)
    
    return description

def home_page():
    """Home page with mode selection"""
    VisionMateUI.load_css()
    
    # Welcome banner with user name
    VisionMateUI.welcome_banner(st.session_state.user_name)
    
    # Play welcome audio once
    if not st.session_state.welcome_played:
        welcome_msg = f"Welcome to Vision Mate, {st.session_state.user_name}"
        if st.session_state.audio_enabled:
            audio_html = text_to_speech(welcome_msg)
            if audio_html:
                st.markdown(audio_html, unsafe_allow_html=True)
        st.session_state.welcome_played = True
    
    # Feature cards
    st.markdown("### 🌟 Key Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(VisionMateUI.feature_card(
            "Object Detection",
            "Real-time identification of objects in your environment",
            "🎯"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(VisionMateUI.feature_card(
            "Scene Description",
            "AI-powered descriptions of visual scenes",
            "🖼️"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(VisionMateUI.feature_card(
            "Audio Feedback",
            "Voice announcements for accessibility",
            "🔊"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mode selection
    st.markdown("### 📱 Choose Your Mode")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(VisionMateUI.mode_card(
            "Image Analysis",
            "Analyze uploaded images",
            "📷",
            "Upload photos for detailed analysis"
        ), unsafe_allow_html=True)
        if st.button("Start Image Mode", key="btn_image_mode", use_container_width=True):
            st.session_state.current_page = 'image'
            st.rerun()
    
    with col2:
        st.markdown(VisionMateUI.mode_card(
            "Live Camera",
            "Real-time camera analysis",
            "🎥",
            "Use your webcam for live detection"
        ), unsafe_allow_html=True)
        if st.button("Start Live Mode", key="btn_live_mode", use_container_width=True):
            st.session_state.current_page = 'live'
            st.rerun()
    
    with col3:
        st.markdown(VisionMateUI.mode_card(
            "Video Analysis",
            "Analyze video files",
            "🎬",
            "Upload videos for processing"
        ), unsafe_allow_html=True)
        if st.button("Start Video Mode", key="btn_video_mode", use_container_width=True):
            st.session_state.current_page = 'video'
            st.rerun()

def process_image_page():
    """Image analysis page with UI components"""
    VisionMateUI.load_css()
    VisionMateUI.page_header("Image Analysis", "Upload and analyze images", "📷")
    
    # Back button
    if st.button("⬅️ Back to Home", key="back_from_image"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("---")
    
    # File uploader with UI component
    uploaded_file = VisionMateUI.file_uploader(
        "Upload an image for analysis",
        file_types=['jpg', 'jpeg', 'png'],
        help_text="Supported formats: JPG, JPEG, PNG",
        key="image_upload_main"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        if VisionMateUI.custom_button("🔍 Analyze Image", "analyze_img_btn", "primary"):
            with st.spinner("🤖 Analyzing image..."):
                VisionMateUI.progress_with_text(0.3, "Loading models...")
                
                # Convert PIL to numpy
                image_np = np.array(image)
                image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                
                VisionMateUI.progress_with_text(0.5, "Detecting objects...")
                
                # Object detection
                results = detect_objects(image_cv, st.session_state.yolo_model)
                annotated = draw_boxes(image_cv, results)
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                
                VisionMateUI.progress_with_text(0.8, "Generating description...")
                
                # Generate descriptions
                detection_desc = create_detection_description(results)
                caption = generate_caption(image, st.session_state.blip_processor, 
                                         st.session_state.blip_model, st.session_state.device)
                
                VisionMateUI.progress_with_text(1.0, "Complete!")
                
                # Display results
                st.markdown("### 📊 Analysis Results")
                
                # Image comparison
                VisionMateUI.image_comparison(image, annotated_rgb, "Original", "Detected Objects")
                
                # Description
                full_description = f"{detection_desc}. Scene description: {caption}"
                
                st.markdown(VisionMateUI.info_card(
                    "Analysis Result",
                    full_description,
                    "success"
                ), unsafe_allow_html=True)
                
                # Audio output
                if st.session_state.audio_enabled:
                    audio_html = text_to_speech(full_description)
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)
                
                VisionMateUI.toast_message("Analysis complete!", "✅")

def process_live_page():
    """Live camera page with UI components"""
    VisionMateUI.load_css()
    VisionMateUI.page_header("Live Camera", "Real-time object detection", "🎥")
    
    # Back button
    if st.button("⬅️ Back to Home", key="back_from_live"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("---")
    
    st.markdown(VisionMateUI.info_card(
        "Camera Permissions",
        "Please allow camera access in your browser to use this feature.",
        "info"
    ), unsafe_allow_html=True)
    
    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start Detection", type="primary", use_container_width=True, key="start_live_btn"):
            st.session_state.detection_active = True
    with col2:
        if st.button("⏹️ Stop Detection", use_container_width=True, key="stop_live_btn"):
            st.session_state.detection_active = False
    
    # Camera input
    camera_image = st.camera_input("📸 Take a picture", key="camera_live")
    
    if camera_image and st.session_state.detection_active:
        with st.spinner("Analyzing..."):
            image = Image.open(camera_image).convert("RGB")
            image_np = np.array(image)
            image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            # Object detection
            results = detect_objects(image_cv, st.session_state.yolo_model)
            annotated = draw_boxes(image_cv, results)
            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            
            st.image(annotated_rgb, caption="Detection Results", use_container_width=True)
            
            # Generate descriptions
            detection_desc = create_detection_description(results)
            caption = generate_caption(image, st.session_state.blip_processor, 
                                     st.session_state.blip_model, st.session_state.device)
            
            full_description = f"{detection_desc}. Scene description: {caption}"
            
            st.markdown(VisionMateUI.info_card(
                "Detection Result",
                full_description,
                "success"
            ), unsafe_allow_html=True)
            
            if st.session_state.audio_enabled:
                audio_html = text_to_speech(full_description)
                if audio_html:
                    st.markdown(audio_html, unsafe_allow_html=True)

def process_video_page():
    """Video analysis page with UI components - Auto-complete processing"""
    VisionMateUI.load_css()
    VisionMateUI.page_header("Video Analysis", "Upload and analyze video files", "🎬")
    
    # Back button
    if st.button("⬅️ Back to Home", key="back_from_video"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("---")
    
    # Video uploader
    uploaded_video = st.file_uploader("Upload a video", type=['mp4', 'avi', 'mov'], key="video_upload_main")
    
    if uploaded_video:
        # Save video temporarily
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_video.read())
        video_path = tfile.name
        
        st.video(video_path)
        
        # Get video information
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()
        
        # Display video info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Duration", f"{duration:.1f}s")
        with col2:
            st.metric("Total Frames", total_frames)
        with col3:
            st.metric("FPS", fps)
        
        st.markdown("---")
        
        # Start analysis button
        if st.button("🎬 Start Video Analysis", type="primary", use_container_width=True, key="start_video_btn"):
            process_video_stream_complete(video_path, total_frames, fps)

def process_video_stream_complete(video_path, total_frames, fps):
    """Process entire video automatically without voice overlap"""
    cap = cv2.VideoCapture(video_path)
    
    # Create placeholders
    progress_bar = st.progress(0)
    status_text = st.empty()
    frame_display = st.empty()
    results_container = st.container()
    
    # Storage for detections throughout video
    all_detections = []
    detection_timeline = []
    frame_count = 0
    analysis_interval = max(1, fps // 2)  # Analyze 2 times per second
    
    status_text.info("🎬 Starting video analysis...")
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Update progress
            progress = frame_count / total_frames
            progress_bar.progress(progress)
            status_text.info(f"📊 Processing: {frame_count}/{total_frames} frames ({progress*100:.1f}%)")
            
            # Analyze frame at intervals
            if frame_count % analysis_interval == 0:
                # Object detection
                results = detect_objects(frame, st.session_state.yolo_model)
                annotated = draw_boxes(frame, results)
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                
                # Display current frame
                frame_display.image(annotated_rgb, channels="RGB", use_container_width=True)
                
                # Store detection data
                if len(results.boxes) > 0:
                    timestamp = frame_count / fps
                    object_counts = {}
                    for box in results.boxes:
                        cls = int(box.cls[0])
                        name = results.names[cls]
                        object_counts[name] = object_counts.get(name, 0) + 1
                    
                    detection_timeline.append({
                        'timestamp': timestamp,
                        'frame': frame_count,
                        'objects': object_counts,
                        'total': len(results.boxes)
                    })
                    
                    # Add to all detections
                    for obj_name in object_counts.keys():
                        if obj_name not in all_detections:
                            all_detections.append(obj_name)
        
        cap.release()
        
        # Complete progress
        progress_bar.progress(1.0)
        status_text.success("✅ Video analysis complete!")
        
        # Display comprehensive results
        st.markdown("---")
        st.markdown("### 📊 Video Analysis Results")
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Objects Detected", len(all_detections))
        with col2:
            st.metric("Detection Points", len(detection_timeline))
        with col3:
            st.metric("Frames Analyzed", frame_count)
        
        # Detected objects list
        if all_detections:
            st.markdown("### 🎯 Objects Found in Video")
            st.write(", ".join(all_detections))
            
            # Create detailed timeline
            st.markdown("### ⏱️ Detection Timeline")
            
            timeline_text = ""
            for i, detection in enumerate(detection_timeline[:10]):  # Show first 10
                timestamp_str = f"{int(detection['timestamp']//60):02d}:{int(detection['timestamp']%60):02d}"
                objects_str = ", ".join([f"{count} {name}" for name, count in detection['objects'].items()])
                timeline_text += f"**{timestamp_str}** - {objects_str}\n\n"
            
            if len(detection_timeline) > 10:
                timeline_text += f"*... and {len(detection_timeline) - 10} more detection points*"
            
            st.markdown(timeline_text)
            
            # Generate comprehensive summary
            summary_text = f"Video analysis completed. The video contains {len(all_detections)} different types of objects: {', '.join(all_detections)}. "
            summary_text += f"Total of {len(detection_timeline)} detection points were analyzed throughout the {total_frames} frames."
            
            st.markdown(VisionMateUI.info_card(
                "Complete Analysis Summary",
                summary_text,
                "success"
            ), unsafe_allow_html=True)
            
            # Play audio summary ONCE at the end (no overlap)
            if st.session_state.audio_enabled:
                st.info("🔊 Playing audio summary...")
                audio_summary = f"Video analysis complete. Detected {len(all_detections)} different objects: {', '.join(all_detections)}."
                audio_html = text_to_speech(audio_summary)
                if audio_html:
                    st.markdown(audio_html, unsafe_allow_html=True)
        else:
            st.warning("No objects were detected in the video.")
            if st.session_state.audio_enabled:
                audio_html = text_to_speech("No objects were detected in the video.")
                if audio_html:
                    st.markdown(audio_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error processing video: {e}")
        cap.release()
    
    finally:
        # Cleanup
        if os.path.exists(video_path):
            try:
                os.unlink(video_path)
            except:
                pass

def process_video_stream(video_path):
    """Legacy function - kept for compatibility"""
    cap = cv2.VideoCapture(video_path)
    
    stframe = st.empty()
    status_text = st.empty()
    
    frame_count = 0
    last_caption_time = time.time()
    caption_interval = 3
    
    while st.session_state.detection_active and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Object detection
        results = detect_objects(frame, st.session_state.yolo_model)
        annotated = draw_boxes(frame, results)
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        
        stframe.image(annotated_rgb, channels="RGB", use_container_width=True)
        
        # Generate caption periodically
        current_time = time.time()
        if current_time - last_caption_time >= caption_interval:
            detection_desc = create_detection_description(results)
            status_text.info(f"🔊 {detection_desc}")
            
            if st.session_state.audio_enabled:
                audio_html = text_to_speech(detection_desc)
                if audio_html:
                    st.markdown(audio_html, unsafe_allow_html=True)
            
            last_caption_time = current_time
        
        if frame_count % 2 == 0:
            time.sleep(0.03)
    
    cap.release()
    status_text.success("✅ Video processing stopped")

def main_app():
    """Main application with sidebar"""
    VisionMateUI.load_css()
    
    # Sidebar
    with st.sidebar:
        VisionMateUI.sidebar_header(st.session_state.user_name)
        
        st.markdown("---")
        
        # Audio controls
        VisionMateUI.audio_status_indicator(st.session_state.audio_enabled)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        
        if st.button("🏠 Home", use_container_width=True, key="nav_home_sb"):
            st.session_state.current_page = 'home'
            st.rerun()
        
        if st.button("📷 Image Analysis", use_container_width=True, key="nav_image_sb"):
            st.session_state.current_page = 'image'
            st.rerun()
        
        if st.button("🎥 Live Camera", use_container_width=True, key="nav_live_sb"):
            st.session_state.current_page = 'live'
            st.rerun()
        
        if st.button("🎬 Video Analysis", use_container_width=True, key="nav_video_sb"):
            st.session_state.current_page = 'video'
            st.rerun()
        
        st.markdown("---")
        
        # Audio toggle
        st.session_state.audio_enabled = st.checkbox(
            "🔊 Audio Enabled",
            value=st.session_state.audio_enabled,
            key="audio_toggle_sb"
        )
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True, key="logout_sb"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_name = None
            st.session_state.welcome_played = False
            st.session_state.current_page = 'home'
            st.rerun()
        
        # User info
        st.markdown("---")
        st.caption(f"👤 {st.session_state.user_name}")
        st.caption(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    
    # Load models
    if not st.session_state.models_loaded:
        with st.spinner("🤖 Loading AI models (first run may take a few minutes)..."):
            yolo_model, blip_processor, blip_model, device = load_models()
            if yolo_model and blip_model:
                st.session_state.yolo_model = yolo_model
                st.session_state.blip_processor = blip_processor
                st.session_state.blip_model = blip_model
                st.session_state.device = device
                st.session_state.models_loaded = True
                VisionMateUI.success_message("✅ Models loaded successfully!")
            else:
                VisionMateUI.error_message("Failed to load models. Please check your installation.")
                return
    
    # Route to current page
    if st.session_state.current_page == 'home':
        home_page()
    elif st.session_state.current_page == 'image':
        process_image_page()
    elif st.session_state.current_page == 'live':
        process_live_page()
    elif st.session_state.current_page == 'video':
        process_video_page()
    
    # Footer
    VisionMateUI.footer(version="2.0", show_time=True)

# ============== MAIN APPLICATION ==============

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="VisionMate - AI Assistant",
        page_icon="👁️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Route to appropriate page
    if not st.session_state.authenticated:
        auth_page()
    else:
        main_app()

if __name__ == "__main__":
    main()