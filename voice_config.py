
# Voice configuration settings
VOICE_CONFIG = {
    'recognition': {
        'timeout': 10,
        'phrase_timeout': 5,
        'energy_threshold': 300,
        'dynamic_energy': True
    },
    'tts': {
        'rate': 180,
        'volume': 0.9,
        'voice_gender': 'female'  # 'male' or 'female'
    },
    'languages': {
        'default': 'en',
        'supported': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi']
    },
    'wake_words': ['hey ai', 'hello ai', 'assistant', 'bot'],
    'commands': {
        'stop_listening': ['stop', 'quiet', 'silence'],
        'repeat': ['repeat', 'say again', 'again'],
        'louder': ['louder', 'volume up'],
        'quieter': ['quieter', 'volume down']
    }
}
