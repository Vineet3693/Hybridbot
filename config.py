
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

# Groq Model settings
GROQ_MODEL = "mixtral-8x7b-32768"  # Default model
AVAILABLE_MODELS = {
    "Mixtral 8x7B (Recommended)": "mixtral-8x7b-32768",
    "Llama2 70B": "llama2-70b-4096", 
    "Gemma 7B": "gemma-7b-it",
    "Llama3 8B": "llama3-8b-8192",
    "Llama3 70B": "llama3-70b-8192"
}

MAX_TOKENS = 1000
TEMPERATURE = 0.7

# Embedding settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Search settings
MAX_SEARCH_RESULTS = 5
PDF_SEARCH_RESULTS = 3
WEB_SEARCH_RESULTS = 3
SIMILARITY_THRESHOLD = 0.3
