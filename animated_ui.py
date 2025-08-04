# animated_ui.py
import streamlit as st
import time
import random
from typing import Dict, List, Tuple

class AnimatedUI:
    def __init__(self):
        self.colors = {
            'primary': '#00d4ff',
            'secondary': '#ff006e',
            'accent': '#8338ec',
            'success': '#06ffa5',
            'warning': '#ffbe0b',
            'error': '#fb5607',
            'dark': '#1a1a2e',
            'light': '#16213e'
        }
        
    def inject_animated_css(self):
        """Inject animated CSS styles"""
        st.markdown("""
        <style>
        /* Global Animation Styles */
        @keyframes rainbow {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        
        @keyframes pulse {
            0% {transform: scale(1);}
            50% {transform: scale(1.05);}
            100% {transform: scale(1);}
        }
        
        @keyframes slideIn {
            from {opacity: 0; transform: translateX(-100px);}
            to {opacity: 1; transform: translateX(0);}
        }
        
        @keyframes glow {
            0% {box-shadow: 0 0 5px #00d4ff;}
            50% {box-shadow: 0 0 20px #00d4ff, 0 0 30px #00d4ff;}
            100% {box-shadow: 0 0 5px #00d4ff;}
        }
        
        /* Main Container */
        .main-container {
            background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #533483);
            background-size: 400% 400%;
            animation: rainbow 15s ease infinite;
            border-radius: 20px;
            padding: 20px;
            margin: 10px 0;
        }
        
        /* Animated Header */
        .animated-header {
            background: linear-gradient(45deg, #00d4ff, #ff006e, #8338ec);
            background-size: 200% 200%;
            animation: rainbow 3s ease infinite;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            animation: slideIn 1s ease-out;
        }
        
        /* Glowing Cards */
        .glow-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            border: 2px solid transparent;
            background-clip: padding-box;
            animation: glow 2s ease-in-out infinite alternate;
            transition: all 0.3s ease;
        }
        
        .glow-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 212, 255, 0.3);
        }
        
        /* Animated Buttons */
        .stButton > button {
            background: linear-gradient(45deg, #00d4ff, #8338ec) !important;
            border: none !important;
            border-radius: 25px !important;
            color: white !important;
            font-weight: bold !important;
            padding: 10px 30px !important;
            transition: all 0.3s ease !important;
            animation: pulse 2s infinite !important;
        }
        
        .stButton > button:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 5px 15px rgba(131, 56, 236, 0.4) !important;
        }
        
        /* Progress Bar Animation */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #00d4ff, #ff006e, #8338ec) !important;
            animation: rainbow 2s linear infinite !important;
        }
        
        /* Sidebar Styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #1a1a2e, #16213e) !important;
        }
        
        /* Text Input Glow */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 2px solid #00d4ff !important;
            border-radius: 10px !important;
            color: white !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.5) !important;
            border-color: #ff006e !important;
        }
        
        /* Chat Messages */
        .chat-message {
            padding: 15px;
            border-radius: 15px;
            margin: 10px 0;
            animation: slideIn 0.5s ease-out;
        }
        
        .user-message {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            margin-left: 20%;
        }
        
        .bot-message {
            background: linear-gradient(135deg, #8338ec, #6d28d9);
            margin-right: 20%;
        }
        
        /* Loading Animation */
        .loading-dots {
            display: inline-block;
        }
        
        .loading-dots:after {
            content: '⠋';
            animation: loading 1s linear infinite;
        }
        
        @keyframes loading {
            0% { content: '⠋'; }
            10% { content: '⠙'; }
            20% { content: '⠹'; }
            30% { content: '⠸'; }
            40% { content: '⠼'; }
            50% { content: '⠴'; }
            60% { content: '⠦'; }
            70% { content: '⠧'; }
            80% { content: '⠇'; }
            90% { content: '⠏'; }
        }
        
        /* Voice Recording Indicator */
        .recording-indicator {
            width: 20px;
            height: 20px;
            background: #ff006e;
            border-radius: 50%;
            animation: pulse 1s infinite;
            display: inline-block;
            margin-right: 10px;
        }
        
        /* Floating Particles */
        .particle {
            position: absolute;
            background: #00d4ff;
            border-radius: 50%;
            pointer-events: none;
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def create_animated_header(self, title: str):
        """Create an animated rainbow header"""
        st.markdown(f'<h1 class="animated-header">{title}</h1>', unsafe_allow_html=True)
    
    def create_glow_card(self, content: str, card_type: str = "default"):
        """Create a glowing card with content"""
        st.markdown(f'<div class="glow-card">{content}</div>', unsafe_allow_html=True)
    
    def create_chat_message(self, message: str, is_user: bool = True):
        """Create animated chat message"""
        message_class = "user-message" if is_user else "bot-message"
        st.markdown(f'<div class="chat-message {message_class}">{message}</div>', unsafe_allow_html=True)
    
    def show_loading_animation(self, text: str = "Processing"):
        """Show loading animation"""
        return st.markdown(f'<span class="loading-dots">{text}</span>', unsafe_allow_html=True)
    
    def show_recording_indicator(self):
        """Show recording indicator"""
        return st.markdown('<span class="recording-indicator"></span>Recording...', unsafe_allow_html=True)
    
    def create_rgb_progress_bar(self, progress: float):
        """Create animated RGB progress bar"""
        return st.progress(progress)
    
    def generate_particles(self, count: int = 10):
        """Generate floating particles"""
        particles_html = ""
        for i in range(count):
            size = random.randint(3, 8)
            left = random.randint(0, 100)
            delay = random.uniform(0, 6)
            particles_html += f'''
            <div class="particle" style="
                width: {size}px; 
                height: {size}px; 
                left: {left}%; 
                animation-delay: {delay}s;
                opacity: 0.7;
            "></div>
            '''
        
        st.markdown(f'<div style="position: relative; height: 100px; overflow: hidden;">{particles_html}</div>', 
                   unsafe_allow_html=True)
