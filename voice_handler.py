
import streamlit as st
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import pygame
import tempfile
import os
import base64
import io
import wave
import threading
from typing import Optional, Callable
import time
import json

class VoiceHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = None
        self.is_listening = False
        self.is_speaking = False
        
        # Initialize TTS engine
        self.init_tts_engine()
        
        # Initialize pygame for audio playback
        try:
            pygame.mixer.init()
        except Exception as e:
            st.warning(f"Audio playback initialization failed: {e}")
    
    def init_tts_engine(self):
        """Initialize the TTS engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Set properties
            self.tts_engine.setProperty('rate', 180)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Set to female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            st.warning(f"TTS engine initialization failed: {e}")
            self.tts_engine = None
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                st.info("🎤 Calibrating microphone... Please stay quiet for a moment.")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                st.success("✅ Microphone calibrated!")
                return True
        except Exception as e:
            st.error(f"Microphone calibration failed: {e}")
            return False
    
    def listen_for_speech(self, timeout: int = 5, phrase_timeout: int = 2) -> Optional[str]:
        """Listen for speech input and convert to text"""
        try:
            with self.microphone as source:
                st.info("🎤 Listening... Speak now!")
                
                # Listen for speech
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_timeout
                )
                
                st.info("🔄 Processing speech...")
                
                # Convert speech to text using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                st.success(f"✅ Heard: {text}")
                return text
                
        except sr.WaitTimeoutError:
            st.warning("⏰ No speech detected. Please try again.")
            return None
        except sr.UnknownValueError:
            st.warning("❓ Could not understand the speech. Please try again.")
            return None
        except sr.RequestError as e:
            st.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            st.error(f"Speech recognition error: {e}")
            return None
    
    def continuous_listen(self, callback: Callable[[str], None], stop_event: threading.Event):
        """Continuously listen for speech in background"""
        while not stop_event.is_set():
            try:
                with self.microphone as source:
                    # Shorter timeout for continuous listening
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    
                    try:
                        text = self.recognizer.recognize_google(audio)
                        if text.strip():
                            callback(text)
                    except (sr.UnknownValueError, sr.RequestError):
                        # Ignore recognition errors in continuous mode
                        pass
                        
            except sr.WaitTimeoutError:
                # Continue listening
                continue
            except Exception as e:
                st.error(f"Continuous listening error: {e}")
                break
    
    def speak_text_local(self, text: str) -> bool:
        """Convert text to speech using local TTS engine"""
        if not self.tts_engine:
            return False
        
        try:
            self.is_speaking = True
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.is_speaking = False
            return True
        except Exception as e:
            st.error(f"Local TTS error: {e}")
            self.is_speaking = False
            return False
    
    def speak_text_gtts(self, text: str, language: str = 'en') -> bool:
        """Convert text to speech using Google TTS"""
        try:
            self.is_speaking = True
            
            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                tts.save(temp_file.name)
                temp_filename = temp_file.name
            
            # Play the audio file
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Clean up
            os.unlink(temp_filename)
            self.is_speaking = False
            return True
            
        except Exception as e:
            st.error(f"Google TTS error: {e}")
            self.is_speaking = False
            return False
    
    def speak_text(self, text: str, method: str = 'gtts', language: str = 'en') -> bool:
        """Convert text to speech using specified method"""
        if method == 'local':
            return self.speak_text_local(text)
        else:
            return self.speak_text_gtts(text, language)
    
    def get_audio_devices(self) -> dict:
        """Get available audio input devices"""
        devices = {}
        try:
            for i, device_name in enumerate(sr.Microphone.list_microphone_names()):
                devices[i] = device_name
        except Exception as e:
            st.error(f"Error getting audio devices: {e}")
        
        return devices
    
    def set_microphone_device(self, device_index: int):
        """Set specific microphone device"""
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            return True
        except Exception as e:
            st.error(f"Error setting microphone device: {e}")
            return False
    
    def test_microphone(self) -> bool:
        """Test microphone functionality"""
        try:
            with self.microphone as source:
                st.info("🎤 Testing microphone... Say something!")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=2)
                text = self.recognizer.recognize_google(audio)
                st.success(f"✅ Microphone test successful! Heard: {text}")
                return True
        except Exception as e:
            st.error(f"❌ Microphone test failed: {e}")
            return False
    
    def get_supported_languages(self) -> dict:
        """Get supported languages for TTS"""
        return {
            'English': 'en',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Italian': 'it',
            'Portuguese': 'pt',
            'Russian': 'ru',
            'Japanese': 'ja',
            'Korean': 'ko',
            'Chinese (Mandarin)': 'zh',
            'Arabic': 'ar',
            'Hindi': 'hi'
        }
    
    def create_audio_player(self, audio_bytes: bytes) -> str:
        """Create HTML5 audio player for web playback"""
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio controls autoplay style="width: 100%;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        return audio_html
