
import streamlit as st
import threading
import time
from voice_handler import VoiceHandler
from typing import Optional

class VoiceUI:
    def __init__(self, voice_handler: VoiceHandler):
        self.voice_handler = voice_handler
        self.listening_thread = None
        self.stop_listening_event = threading.Event()
        
        # Initialize session state for voice
        if 'voice_enabled' not in st.session_state:
            st.session_state.voice_enabled = False
        if 'voice_input_text' not in st.session_state:
            st.session_state.voice_input_text = ""
        if 'voice_output_enabled' not in st.session_state:
            st.session_state.voice_output_enabled = True
        if 'tts_method' not in st.session_state:
            st.session_state.tts_method = 'gtts'
        if 'tts_language' not in st.session_state:
            st.session_state.tts_language = 'en'
        if 'continuous_listening' not in st.session_state:
            st.session_state.continuous_listening = False
    
    def render_voice_settings(self):
        """Render voice settings in sidebar"""
        st.header("🎤 Voice Settings")
        
        # Voice input toggle
        st.session_state.voice_enabled = st.checkbox(
            "Enable Voice Input", 
            value=st.session_state.voice_enabled,
            help="Enable speech-to-text functionality"
        )
        
        # Voice output toggle
        st.session_state.voice_output_enabled = st.checkbox(
            "Enable Voice Output", 
            value=st.session_state.voice_output_enabled,
            help="Enable text-to-speech for AI responses"
        )
        
        if st.session_state.voice_output_enabled:
            # TTS Method selection
            tts_methods = {
                'Google TTS (Recommended)': 'gtts',
                'Local TTS (Offline)': 'local'
            }
            
            selected_tts = st.selectbox(
                "TTS Method:",
                list(tts_methods.keys()),
                help="Choose text-to-speech method"
            )
            st.session_state.tts_method = tts_methods[selected_tts]
            
            # Language selection for Google TTS
            if st.session_state.tts_method == 'gtts':
                languages = self.voice_handler.get_supported_languages()
                selected_lang = st.selectbox(
                    "TTS Language:",
                    list(languages.keys()),
                    help="Choose language for text-to-speech"
                )
                st.session_state.tts_language = languages[selected_lang]
        
        st.markdown("---")
        
        # Voice controls
        st.subheader("🎛️ Voice Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎤 Test Mic", help="Test microphone functionality"):
                self.voice_handler.test_microphone()
        
        with col2:
            if st.button("🔧 Calibrate", help="Calibrate microphone for ambient noise"):
                self.voice_handler.calibrate_microphone()
        
        # Audio device selection
        if st.button("🔍 Show Audio Devices"):
            devices = self.voice_handler.get_audio_devices()
            if devices:
                st.write("Available microphones:")
                for idx, name in devices.items():
                    st.write(f"  {idx}: {name}")
            else:
                st.write("No audio devices found")
        
        # Continuous listening toggle
        st.session_state.continuous_listening = st.checkbox(
            "Continuous Listening", 
            value=st.session_state.continuous_listening,
            help="Keep listening for voice commands continuously"
        )
        
        if st.session_state.continuous_listening:
            self.start_continuous_listening()
        else:
            self.stop_continuous_listening()
    
    def render_voice_input(self) -> Optional[str]:
        """Render voice input controls and return transcribed text"""
        if not st.session_state.voice_enabled:
            return None
        
        st.markdown("### 🎤 Voice Input")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🎤 Start Recording", type="primary", use_container_width=True):
                with st.spinner("🎤 Recording... Speak now!"):
                    text = self.voice_handler.listen_for_speech(timeout=10, phrase_timeout=5)
                    if text:
                        st.session_state.voice_input_text = text
                        return text
        
        with col2:
            timeout = st.number_input("Timeout (s)", min_value=3, max_value=30, value=10, step=1)
        
        with col3:
            phrase_timeout = st.number_input("Phrase timeout (s)", min_value=1, max_value=10, value=5, step=1)
        
        # Display current voice input
        if st.session_state.voice_input_text:
            st.success(f"🎤 Voice Input: {st.session_state.voice_input_text}")
            
            col_clear, col_use = st.columns(2)
            with col_clear:
                if st.button("🗑️ Clear"):
                    st.session_state.voice_input_text = ""
                    st.rerun()
            
            with col_use:
                if st.button("✅ Use This"):
                    return st.session_state.voice_input_text
        
        return None
    
    def speak_response(self, text: str):
        """Convert AI response to speech"""
        if not st.session_state.voice_output_enabled:
            return
        
        if not text.strip():
            return
        
        # Clean text for better speech
        clean_text = self.clean_text_for_speech(text)
        
        with st.spinner("🔊 Converting to speech..."):
            success = self.voice_handler.speak_text(
                clean_text, 
                method=st.session_state.tts_method,
                language=st.session_state.tts_language
            )
            
            if success:
                st.success("🔊 Audio response played!")
            else:
                st.error("❌ Failed to play audio response")
    
    def clean_text_for_speech(self, text: str) -> str:
        """Clean text to make it more suitable for speech synthesis"""
        import re
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        text = re.sub(r'#{1,6}\s', '', text)          # Headers
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)    # Links
        
        # Remove special characters that don't speak well
        text = re.sub(r'[•▶️📄🌐📚]', '', text)       # Emojis/bullets
        text = re.sub(r'===.*?===', '', text)         # Section separators
        text = re.sub(r'---+', '. ', text)            # Horizontal rules
        
        # Replace common abbreviations
        replacements = {
            'PDF': 'P D F',
            'URL': 'U R L',
            'API': 'A P I',
            'AI': 'A I',
            'etc.': 'etcetera',
            'e.g.': 'for example',
            'i.e.': 'that is'
        }
        
        for abbrev, replacement in replacements.items():
            text = text.replace(abbrev, replacement)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit length for TTS (some services have limits)
        if len(text) > 500:
            text = text[:497] + "..."
        
        return text
    
    def start_continuous_listening(self):
        """Start continuous listening in background"""
        if self.listening_thread and self.listening_thread.is_alive():
            return
        
        self.stop_listening_event.clear()
        
        def on_speech_detected(text):
            st.session_state.voice_input_text = text
            st.success(f"🎤 Continuous: {text}")
        
        self.listening_thread = threading.Thread(
            target=self.voice_handler.continuous_listen,
            args=(on_speech_detected, self.stop_listening_event)
        )
        self.listening_thread.daemon = True
        self.listening_thread.start()
        
        st.info("🎤 Continuous listening started...")
    
    def stop_continuous_listening(self):
        """Stop continuous listening"""
        if self.listening_thread and self.listening_thread.is_alive():
            self.stop_listening_event.set()
            self.listening_thread.join(timeout=2)
            st.info("🛑 Continuous listening stopped")
    
    def render_voice_commands_help(self):
        """Render help for voice commands"""
        with st.expander("🎤 Voice Commands Help"):
            st.markdown("""
            ### Voice Input Tips:
            - **Speak clearly** and at normal pace
            - **Reduce background noise** for better recognition
            - **Use voice commands** like:
              - "Search for [topic]"
              - "Tell me about [subject]"
              - "What is [question]?"
              - "Explain [concept]"
            
            ### Voice Output Features:
            - **Google TTS**: High quality, multiple languages
            - **Local TTS**: Works offline, faster
            - **Auto-cleanup**: Removes formatting for better speech
            
            ### Troubleshooting:
            - **No audio detected**: Check microphone permissions
            - **Poor recognition**: Calibrate microphone
            - **Audio not playing**: Check system volume
            - **Slow response**: Try local TTS method
            """)
    
    def render_voice_stats(self):
        """Render voice usage statistics"""
        if hasattr(st.session_state, 'voice_stats'):
            with st.expander("📊 Voice Statistics"):
                stats = st.session_state.voice_stats
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Voice Inputs", stats.get('inputs', 0))
                
                with col2:
                    st.metric("Voice Outputs", stats.get('outputs', 0))
                
                with col3:
                    st.metric("Recognition Accuracy", f"{stats.get('accuracy', 0):.1f}%")
