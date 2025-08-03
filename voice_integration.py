
import streamlit as st
from voice_handler import VoiceHandler
from voice_ui import VoiceUI
import threading
import time

class VoiceIntegration:
    def __init__(self):
        # Initialize voice components
        if 'voice_handler' not in st.session_state:
            st.session_state.voice_handler = VoiceHandler()
        
        if 'voice_ui' not in st.session_state:
            st.session_state.voice_ui = VoiceUI(st.session_state.voice_handler)
        
        # Initialize voice statistics
        if 'voice_stats' not in st.session_state:
            st.session_state.voice_stats = {
                'inputs': 0,
                'outputs': 0,
                'accuracy': 95.0,
                'total_time': 0
            }
    
    def handle_voice_input(self) -> str:
        """Handle voice input and return transcribed text"""
        voice_text = st.session_state.voice_ui.render_voice_input()
        
        if voice_text:
            # Update statistics
            st.session_state.voice_stats['inputs'] += 1
            return voice_text
        
        return ""
    
    def handle_voice_output(self, text: str):
        """Handle voice output for AI responses"""
        if st.session_state.voice_output_enabled and text:
            # Run TTS in background thread to avoid blocking UI
            def speak_in_background():
                st.session_state.voice_ui.speak_response(text)
                st.session_state.voice_stats['outputs'] += 1
            
            thread = threading.Thread(target=speak_in_background)
            thread.daemon = True
            thread.start()
    
    def render_voice_sidebar(self):
        """Render voice controls in sidebar"""
        st.session_state.voice_ui.render_voice_settings()
        st.session_state.voice_ui.render_voice_commands_help()
        st.session_state.voice_ui.render_voice_stats()
    
    def check_voice_wake_word(self, text: str) -> bool:
        """Check if text contains wake words for voice activation"""
        wake_words = ['hey ai', 'hello ai', 'assistant', 'bot']
        text_lower = text.lower()
        
        for wake_word in wake_words:
            if wake_word in text_lower:
                return True
        return False
    
    def process_voice_command(self, text: str) -> dict:
        """Process voice command and extract intent"""
        text_lower = text.lower()
        
        command_types = {
            'search': ['search for', 'find', 'look up', 'tell me about'],
            'question': ['what is', 'how to', 'why', 'when', 'where', 'who'],
            'action': ['open', 'close', 'clear', 'export', 'save'],
            'navigation': ['go to', 'show me', 'display']
        }
        
        for cmd_type, keywords in command_types.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return {
                        'type': cmd_type,
                        'text': text,
                        'keyword': keyword,
                        'query': text_lower.replace(keyword, '').strip()
                    }
        
        return {
            'type': 'general',
            'text': text,
            'keyword': None,
            'query': text
        }
