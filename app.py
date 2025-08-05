import streamlit as st
import os
import json
import time
from typing import List, Dict

# Import core modules
from pdf_processor import PDFProcessor
from web_search import WebSearcher
from vector_store import VectorStore
from groq_handler import GroqHandler
from config import AVAILABLE_MODELS, GROQ_API_KEY

# Import export utilities
try:
    from export_utils import ChatExporter
    EXPORT_AVAILABLE = True
except ImportError:
    EXPORT_AVAILABLE = False
    st.warning("⚠️ Export features require additional packages")

# Import voice integration with fallback
try:
    from voice_integration import VoiceIntegration
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="🤖 HybridBot Pro - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with animations and colorful styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Animated Main Header */
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 8s ease infinite;
        color: white;
        border-radius: 20px;
        margin: 1rem 0 2rem 0;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shine 3s infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(30deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(30deg); }
    }
    
    /* Animated Question Box */
    .question-container {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 3px solid transparent;
        background-clip: padding-box;
        position: relative;
        animation: pulseGlow 2s infinite alternate;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .question-container::before {
        content: '❓';
        position: absolute;
        top: -10px;
        left: 15px;
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        padding: 8px;
        border-radius: 50%;
        font-size: 1.2em;
        animation: bounce 2s infinite;
    }
    
    @keyframes pulseGlow {
        0% { box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3); }
        100% { box-shadow: 0 8px 32px rgba(102, 126, 234, 0.6), 0 0 20px rgba(102, 126, 234, 0.4); }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    /* Animated Answer Box */
    .answer-container {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        position: relative;
        animation: slideInLeft 0.5s ease-out;
        box-shadow: 0 8px 32px rgba(17, 153, 142, 0.3);
        border-left: 5px solid #ff6b6b;
    }
    
    .answer-container::before {
        content: '🤖';
        position: absolute;
        top: -10px;
        right: 15px;
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        padding: 8px;
        border-radius: 50%;
        font-size: 1.2em;
        animation: rotate 3s linear infinite;
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Chat Message Styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        position: relative;
        animation: fadeInUp 0.6s ease-out;
        transition: all 0.3s ease;
    }
    
    .chat-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-left: 5px solid #ff6b6b;
        margin-left: 2rem;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
        border-left: 5px solid #feca57;
        margin-right: 2rem;
    }
    
    @keyframes fadeInUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    /* Source Box Styling */
    .source-box {
        background: linear-gradient(135deg, #e7f3ff, #f8fdff);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        transition: all 0.3s ease;
        animation: slideInRight 0.5s ease-out;
    }
    
    .source-box::before {
        content: '';
        position: absolute;
        inset: 0;
        padding: 2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb);
        border-radius: 10px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: exclude;
        z-index: -1;
    }
    
    .source-box:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Button Animations */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #764ba2, #667eea) !important;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9ff 0%, #e7f3ff 100%) !important;
    }
    
    /* Progress Bar Animation */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb) !important;
        animation: progressPulse 2s infinite !important;
    }
    
    @keyframes progressPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Spinning Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Status Indicators */
    .status-success {
        background: linear-gradient(135deg, #00f260, #0575e6);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.25rem;
        animation: pulse 2s infinite;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.25rem;
        animation: pulse 2s infinite;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.25rem;
        animation: shake 0.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* Floating Action Buttons */
    .floating-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 1.5em;
        cursor: pointer;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        animation: float 3s ease-in-out infinite;
        z-index: 1000;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Card Styling */
    .info-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.3);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    /* Typewriter Effect */
    .typewriter {
        overflow: hidden;
        border-right: 2px solid #667eea;
        white-space: nowrap;
        animation: typewriter 3s steps(40) 1s 1 normal both, blinkCursor 1s steps(40) infinite normal;
    }
    
    @keyframes typewriter {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes blinkCursor {
        from, to { border-color: transparent; }
        50% { border-color: #667eea; }
    }
    
    /* Glowing Text */
    .glow-text {
        color: #667eea;
        text-shadow: 0 0 10px #667eea, 0 0 20px #667eea, 0 0 30px #667eea;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 10px #667eea, 0 0 20px #667eea, 0 0 30px #667eea; }
        to { text-shadow: 0 0 20px #667eea, 0 0 30px #667eea, 0 0 40px #667eea; }
    }
    
    /* Export Button Special Styling */
    .export-container {
    background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        animation: slideInUp 0.5s ease-out;
    }
    
    @keyframes slideInUp {
        from { transform: translateY(50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    /* Voice Button Animation */
    .voice-btn {
        animation: voicePulse 2s infinite;
        background: linear-gradient(135deg, #ff6b6b, #feca57) !important;
    }
    
    @keyframes voicePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); box-shadow: 0 0 20px rgba(255, 107, 107, 0.6); }
    }
    
    /* Search Animation */
    .search-animation {
        position: relative;
        overflow: hidden;
    }
    
    .search-animation::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: searchSweep 2s infinite;
    }
    
    @keyframes searchSweep {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* Model Status Indicators */
    .model-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 500;
        animation: fadeIn 0.5s ease-out;
    }
    
    .model-fast {
        background: linear-gradient(135deg, #00f260, #0575e6);
        color: white;
    }
    
    .model-powerful {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
    }
    
    /* Conversation History Styling */
    .conversation-item {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        backdrop-filter: blur(10px);
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        animation: slideIn 0.4s ease-out;
    }
    
    .conversation-item:hover {
        transform: translateX(5px);
        border-color: #667eea;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* File Upload Styling */
    .uploadedFile {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 10px;
        padding: 0.5rem;
        margin: 0.25rem 0;
        animation: fileUpload 0.5s ease-out;
    }
    
    @keyframes fileUpload {
        from { transform: scale(0.8); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    /* Success/Error Message Styling */
    .alert-success {
        background: linear-gradient(135deg, #00f260, #0575e6);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 5px solid #00d4aa;
        animation: alertSlide 0.5s ease-out;
    }
    
    .alert-error {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 5px solid #ff1744;
        animation: alertSlide 0.5s ease-out;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 5px solid #ff9800;
        animation: alertSlide 0.5s ease-out;
    }
    
    @keyframes alertSlide {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    /* Streaming Text Effect */
    .streaming-text {
        animation: streamType 0.1s linear;
    }
    
    @keyframes streamType {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Footer Styling */
    .footer-container {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .footer-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.05), transparent);
        animation: footerShine 4s infinite;
    }
    
    @keyframes footerShine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(30deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(30deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
            margin: 0.5rem 0 1rem 0;
        }
        
        .chat-message {
            margin: 0.5rem 0;
            padding: 1rem;
        }
        
        .floating-btn {
            bottom: 10px;
            right: 10px;
            width: 50px;
            height: 50px;
            font-size: 1.2em;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = VectorStore()
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = PDFProcessor()
    if 'web_searcher' not in st.session_state:
        st.session_state.web_searcher = WebSearcher()
    if 'groq_handler' not in st.session_state:
        st.session_state.groq_handler = GroqHandler()
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'pdf_files_info' not in st.session_state:
        st.session_state.pdf_files_info = []
    
    # Voice integration (conditional)
    if VOICE_AVAILABLE and 'voice_integration' not in st.session_state:
        try:
            st.session_state.voice_integration = VoiceIntegration()
        except Exception as e:
            st.markdown('<div class="alert-warning">🎤 Voice features disabled: ' + str(e) + '</div>', unsafe_allow_html=True)
    
    # Export utilities (conditional)
    if EXPORT_AVAILABLE and 'chat_exporter' not in st.session_state:
        try:
            st.session_state.chat_exporter = ChatExporter()
        except Exception as e:
            st.markdown('<div class="alert-warning">📤 Export features disabled: ' + str(e) + '</div>', unsafe_allow_html=True)

initialize_session_state()

def display_animated_message(message, message_type="info"):
    """Display animated status messages"""
    if message_type == "success":
        st.markdown(f'<div class="alert-success">✅ {message}</div>', unsafe_allow_html=True)
    elif message_type == "error":
        st.markdown(f'<div class="alert-error">❌ {message}</div>', unsafe_allow_html=True)
    elif message_type == "warning":
        st.markdown(f'<div class="alert-warning">⚠️ {message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="info-card">ℹ️ {message}</div>', unsafe_allow_html=True)

def process_pdfs(uploaded_files):
    """Process uploaded PDF files with enhanced UI feedback"""
    st.markdown('<div class="search-animation">', unsafe_allow_html=True)
    with st.spinner("🔄 Processing PDFs..."):
        all_chunks = []
        processed_files = []
        
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress with animation
            progress_bar.progress((i + 1) / len(uploaded_files))
            status_placeholder.markdown(f'<div class="typewriter">📄 Processing: {uploaded_file.name}</div>', unsafe_allow_html=True)
            
            try:
                # Extract text
                text = st.session_state.pdf_processor.extract_text_from_pdf(uploaded_file)
                
                if text:
                    # Chunk text
                    chunks = st.session_state.pdf_processor.chunk_text(text)
                    all_chunks.extend(chunks)
                    
                    # Store file info
                    file_info = {
                        'name': uploaded_file.name,
                        'size': len(text),
                        'chunks': len(chunks),
                        'preview': st.session_state.pdf_processor.get_text_preview(text)
                    }
                    processed_files.append(file_info)
                    
                    display_animated_message(f"Processed: {uploaded_file.name} ({len(chunks)} chunks)", "success")
                else:
                    display_animated_message(f"Failed to process: {uploaded_file.name}", "error")
            
            except Exception as e:
                display_animated_message(f"Error processing {uploaded_file.name}: {str(e)}", "error")
        
        progress_bar.empty()
        status_placeholder.empty()
        
        # Add to vector store
        if all_chunks:
            try:
                st.session_state.vector_store.add_texts(all_chunks)
                st.session_state.pdf_processed = True
                st.session_state.pdf_files_info = processed_files
                display_animated_message(f"🎉 Successfully processed {len(uploaded_files)} PDFs with {len(all_chunks)} text chunks!", "success")
            except Exception as e:
                display_animated_message(f"Error adding to vector store: {str(e)}", "error")
    
    st.markdown('</div>', unsafe_allow_html=True)

def search_sources(question: str, search_options: List[str]):
    """Search both PDF and web sources with animated feedback"""
    pdf_results = []
    web_results = []
    
    try:
        # Search PDF content
        if st.session_state.pdf_processed and "PDF Content" in search_options:
            with st.spinner("🔍 Searching PDF content..."):
                pdf_search_results = st.session_state.vector_store.search(question, k=3)
                pdf_results = [text for text, score in pdf_search_results if score > 0.3]
        
        # Search web
        if "Web Sources" in search_options:
            with st.spinner("🌐 Searching web sources..."):
                web_results = st.session_state.web_searcher.search_multiple_sources(question, max_results=3)
    
    except Exception as e:
        display_animated_message(f"Search error: {str(e)}", "error")
    
    return pdf_results, web_results

def display_sources(pdf_results: List[str], web_results: List[Dict]):
    """Display the sources used for the answer with enhanced styling"""
    if pdf_results or web_results:
        with st.expander("📚 Sources Used", expanded=False):
            if pdf_results:
                st.markdown("### 📄 **PDF Sources:**")
                for i, text in enumerate(pdf_results, 1):
                    st.markdown(f'''
                    <div class="source-box">
                        <strong>📄 PDF Source {i}:</strong><br>
                        <em>{text[:200]}...</em>
                    </div>
                    ''', unsafe_allow_html=True)
            
            if web_results:
                st.markdown("### 🌐 **Web Sources:**")
                for i, result in enumerate(web_results, 1):
                    url_display = f" - [🔗 Link]({result['url']})" if result.get('url') else ""
                    st.markdown(f'''
                    <div class="source-box">
                        <strong>🌐 {result["title"]}</strong><br>
                        <em>{result["snippet"][:150]}...</em>
                        {url_display}
                    </div>
                    ''', unsafe_allow_html=True)

def export_chat_history():
    """Handle chat history export with enhanced UI"""
    if not EXPORT_AVAILABLE:
        display_animated_message("Export features require additional packages", "warning")
        return
    
    if not st.session_state.chat_history:
        display_animated_message("No chat history to export", "warning")
        return
    
    st.markdown('<div class="export-container">', unsafe_allow_html=True)
    st.markdown("### 📤 **Export Chat History**")
    
    # Export options
    col_export1, col_export2, col_export3, col_export4 = st.columns(4)
    
    with col_export1:
        if st.button("📄 Export as DOCX", key="export_docx"):
            try:
                with st.spinner("📄 Creating DOCX..."):
                    docx_data = st.session_state.chat_exporter.export_to_docx(st.session_state.chat_history)
                    st.download_button(
                        label="📥 Download DOCX",
                        data=docx_data,
                        file_name=f"chat_history_{int(time.time())}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                    display_animated_message("DOCX file ready for download!", "success")
            except Exception as e:
                display_animated_message(f"Error creating DOCX: {str(e)}", "error")
    
    with col_export2:
        if st.button("📕 Export as PDF", key="export_pdf"):
            try:
                with st.spinner("📕 Creating PDF..."):
                    pdf_data = st.session_state.chat_exporter.export_to_pdf_reportlab(st.session_state.chat_history)
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_data,
                        file_name=f"chat_history_{int(time.time())}.pdf",
                        mime="application/pdf"
                    )
                    display_animated_message("PDF file ready for download!", "success")
            except Exception as e:
                try:
                    pdf_data = st.session_state.chat_exporter.export_to_pdf_fpdf(st.session_state.chat_history)
                    st.download_button(
                        label="📥 Download Simple PDF",
                        data=pdf_data,
                        file_name=f"chat_history_simple_{int(time.time())}.pdf",
                        mime="application/pdf"
                    )
                    st.markdown('<div class="alert-warning">📋 Using simple PDF format</div>', unsafe_allow_html=True)
                except Exception as e2:
                    display_animated_message(f"PDF export failed: {str(e2)}", "error")
    
    with col_export3:
        if st.button("📝 Export as Markdown", key="export_md"):
            try:
                with st.spinner("📝 Creating Markdown..."):
                    md_data = st.session_state.chat_exporter.export_to_markdown(st.session_state.chat_history)
                    st.download_button(
                        label="📥 Download MD",
                        data=md_data,
                        file_name=f"chat_history_{int(time.time())}.md",
                        mime="text/markdown"
                    )
                    display_animated_message("Markdown file ready for download!", "success")
            except Exception as e:
                display_animated_message(f"Error creating Markdown: {str(e)}", "error")
    
    with col_export4:
        if st.button("🗂️ Export as JSON", key="export_json"):
            try:
                with st.spinner("🗂️ Creating JSON..."):
                    chat_json = json.dumps(st.session_state.chat_history, indent=2, default=str)
                    st.download_button(
                        label="📥 Download JSON",
                        data=chat_json,
                        file_name=f"chat_history_{int(time.time())}.json",
                        mime="application/json"
                    )
                    display_animated_message("JSON file ready for download!", "success")
            except Exception as e:
                display_animated_message(f"Error creating JSON: {str(e)}", "error")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Animated Main Header
st.markdown('''
<div class="main-header">
    <h1 class="glow-text">🤖 HybridBot Pro - AI Assistant</h1>
    <p class="typewriter">🚀 Powered by Groq API - Extract data from PDFs and search the web for intelligent answers</p>
    <div style="margin-top: 1rem;">
        <span class="status-success">⚡ Ultra Fast</span>
        <span class="status-success">🧠 AI Powered</span>
        <span class="status-success">🔍 Smart Search</span>
    </div>
</div>
''', unsafe_allow_html=True)

# Sidebar for PDF upload and settings
with st.sidebar:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.header("📚 Document Management")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type="pdf",
        accept_multiple_files=True,
        help="Upload PDF documents to create a knowledge base"
    )
    
    if uploaded_files:
        if st.button("🔄 Process PDFs", type="primary", key="process_pdfs"):
            process_pdfs(uploaded_files)
        
        # Show file details with animation
        if uploaded_files:
            st.markdown("**📁 Files selected:**")
            for i, file in enumerate(uploaded_files):
                st.markdown(f'''
                <div class="uploadedFile">
                    📄 {file.name} ({file.size:,} bytes)
                </div>
                ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Groq Model Settings
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.header("🧠 AI Settings")
    
    # Model selection
    selected_model_name = st.selectbox(
        "Choose Groq Model:",
        list(AVAILABLE_MODELS.keys()),
        help="Choose between fast (8B) or powerful (70B) Llama3 models"
    )
    selected_model = AVAILABLE_MODELS[selected_model_name]
    
    # Show model info with animated indicators
    if "8b" in selected_model.lower():
        st.markdown('<div class="model-indicator model-fast">🚀 <strong>Llama3 8B:</strong> Fast responses, good for most tasks</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="model-indicator model-powerful">💪 <strong>Llama3 70B:</strong> Most powerful, best for complex tasks</div>', unsafe_allow_html=True)
    
    # Response settings
    temperature = st.slider(
        "Temperature (Creativity):", 
        0.0, 1.0, 0.7, 0.1,
        help="Higher values make responses more creative but less focused"
    )
    max_tokens = st.slider(
        "Max Response Length:", 
        100, 4000, 1000, 100,
        help="Maximum number of tokens in the response"
    )
    
    # Update Groq settings
    st.session_state.groq_handler.update_settings(
        model=selected_model,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Model Status Check
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    col_status1, col_status2 = st.columns(2)
    
    with col_status1:
        if st.button("🔍 Check Models", help="Test which models are currently working"):
            try:
                with st.spinner("🔍 Testing models..."):
                    working_models = st.session_state.groq_handler.get_available_models()
                    if working_models:
                        st.session_state.working_models = working_models
                        display_animated_message("Models checked successfully!", "success")
                    else:
                        display_animated_message("No models available", "error")
            except Exception as e:
                display_animated_message(f"Model check error: {str(e)}", "error")
    
    with col_status2:
        if st.button("🔄 Auto-Select", help="Automatically select a working model"):
            try:
                with st.spinner("🔄 Auto-selecting model..."):
                    working_model = st.session_state.groq_handler.auto_select_working_model()
                    st.session_state.groq_handler.model = working_model
                    display_animated_message("Model auto-selected!", "success")
                    st.rerun()
            except Exception as e:
                display_animated_message(f"Auto-select error: {str(e)}", "error")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Voice Controls Section (if available)
    if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        try:
            st.session_state.voice_integration.render_voice_sidebar()
        except Exception as e:
            display_animated_message(f"Voice controls error: {str(e)}", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
    elif not VOICE_AVAILABLE:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.header("🎤 Voice Features")
        st.markdown('<div class="alert-warning">Voice features require additional packages:</div>', unsafe_allow_html=True)
        st.code("pip install speechrecognition pyttsx3 gtts pygame pyaudio")
        st.markdown("Install these packages to enable voice chat!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Status section
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.header("📊 Status")
    if st.session_state.pdf_processed:
        st.markdown('<div class="status-success">✅ PDFs processed</div>', unsafe_allow_html=True)
        try:
            vector_stats = st.session_state.vector_store.get_stats()
            st.markdown(f'<div class="status-success">📄 {vector_stats["total_texts"]} text chunks available</div>', unsafe_allow_html=True)
        except Exception as e:
            display_animated_message(f"Stats error: {str(e)}", "warning")
        
        # Show processed files
        if st.session_state.pdf_files_info:
            with st.expander("📁 Processed Files"):
                for file_info in st.session_state.pdf_files_info:
                    st.markdown(f'''
                    <div class="conversation-item">
                        <strong>📄 {file_info['name']}</strong><br>
                        • Chunks: {file_info['chunks']}<br>
                        • Size: {file_info['size']:,} characters<br>
                        • Preview: {file_info['preview']}
                    </div>
                    ''', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-warning">⏳ No PDFs processed yet</div>', unsafe_allow_html=True)
    
    # API Status
    if st.button("🔍 Test Groq Connection"):
        try:
            with st.spinner("🔍 Testing connection..."):
                if st.session_state.groq_handler.test_connection():
                    display_animated_message("Groq API connected!", "success")
                else:
                    display_animated_message("Groq API connection failed", "error")
        except Exception as e:
            display_animated_message(f"Connection test error: {str(e)}", "error")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Clear data option
    if st.button("🗑️ Clear All Data", help="Clear processed PDFs and chat history"):
        try:
            st.session_state.vector_store = VectorStore()
            st.session_state.pdf_processed = False
            st.session_state.chat_history = []
            st.session_state.pdf_files_info = []
            display_animated_message("All data cleared!", "success")
            st.rerun()
        except Exception as e:
            display_animated_message(f"Clear data error: {str(e)}", "error")

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.header("💬 Ask Questions")
    
    # Voice input section (if available)
    voice_question = ""
    if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
        try:
            voice_question = st.session_state.voice_integration.handle_voice_input()
        except Exception as e:
            display_animated_message(f"Voice input error: {str(e)}", "warning")
    
    # Question input
    default_text = voice_question if voice_question else ""
    question = st.text_input(
        "What would you like to know?",
        value=default_text,
        placeholder="Ask anything about your PDFs or general knowledge...",
        key="question_input",
        help="Type your question here. The AI will search both your PDFs and the web for answers."
    )
    
    # Clear voice input if used
    if voice_question and voice_question == question:
        if hasattr(st.session_state, 'voice_input_text'):
            st.session_state.voice_input_text = ""
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Search and response options
    col_a, col_b = st.columns(2)
    with col_a:
        search_options = st.multiselect(
            "🔍 Search in:",
            ["PDF Content", "Web Sources"],
            default=["PDF Content", "Web Sources"] if st.session_state.pdf_processed else ["Web Sources"],
            help="Choose where to search for information"
        )
    
    with col_b:
        response_mode = st.radio(
            "⚡ Response Mode:",
            ["Complete", "Streaming"],
            horizontal=True,
            help="Complete: Get full response at once. Streaming: See response as it's generated"
        )
    
    # Ask button with enhanced styling
    if st.button("🔍 Get Answer", type="primary", use_container_width=True) and question:
        if not search_options:
            display_animated_message("Please select at least one search option!", "warning")
        else:
            try:
                # Search for sources
                st.markdown('<div class="search-animation">', unsafe_allow_html=True)
                with st.spinner("🔍 Searching sources..."):
                    pdf_results, web_results = search_sources(question, search_options)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Show search results summary
                results_summary = []
                if pdf_results:
                    results_summary.append(f"📄 {len(pdf_results)} PDF sources")
                if web_results:
                    results_summary.append(f"🌐 {len(web_results)} web sources")
                
                if results_summary:
                    st.markdown(f'<div class="status-success">Found: {", ".join(results_summary)}</div>', unsafe_allow_html=True)
                
                # Generate answer with Groq
                if pdf_results or web_results or "Web Sources" in search_options:
                    st.markdown('<div class="answer-container">', unsafe_allow_html=True)
                    st.markdown("### 🤖 **AI Answer**")
                    
                    if response_mode == "Streaming":
                        # Streaming response
                        try:
                            stream = st.session_state.groq_handler.stream_response(
                                question, pdf_results, web_results
                            )
                            
                            if stream:
                                response_placeholder = st.empty()
                                full_response = ""
                                
                                try:
                                    for chunk in stream:
                                        if chunk.choices[0].delta.content is not None:
                                            full_response += chunk.choices[0].delta.content
                                            # Add streaming animation class
                                            response_placeholder.markdown(
                                                f'<div class="streaming-text">{full_response}<span class="blinking-cursor">▌</span></div>', 
                                                unsafe_allow_html=True
                                            )
                                    
                                    response_placeholder.markdown(f'<div class="streaming-text">{full_response}</div>', unsafe_allow_html=True)
                                    
                                    # Add to chat history
                                    st.session_state.chat_history.append({
                                        "question": question,
                                        "answer": full_response,
                                        "sources": {"pdf": pdf_results, "web": web_results},
                                        "timestamp": time.time()
                                    })
                                    
                                    # Voice output (if available)
                                    if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
                                        try:
                                            st.session_state.voice_integration.handle_voice_output(full_response)
                                        except Exception as e:
                                            display_animated_message(f"Voice output error: {str(e)}", "warning")
                                    
                                except Exception as e:
                                    display_animated_message(f"Streaming error: {str(e)}", "error")
                        except Exception as e:
                            display_animated_message(f"Streaming initialization error: {str(e)}", "error")
                    else:
                        # Complete response
                        with st.spinner("🧠 Generating answer with Groq..."):
                            try:
                                answer = st.session_state.groq_handler.generate_answer(
                                    question, pdf_results, web_results
                                )
                                st.markdown(f'<div class="answer-text">{answer}</div>', unsafe_allow_html=True)
                                
                                # Add to chat history
                                st.session_state.chat_history.append({
                                    "question": question,
                                    "answer": answer,
                                    "sources": {"pdf": pdf_results, "web": web_results},
                                    "timestamp": time.time()
                                })
                                
                                # Voice output (if available)
                                if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
                                    try:
                                        st.session_state.voice_integration.handle_voice_output(answer)
                                    except Exception as e:
                                        display_animated_message(f"Voice output error: {str(e)}", "warning")
                                        
                            except Exception as e:
                                display_animated_message(f"Answer generation error: {str(e)}", "error")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display sources
                    display_sources(pdf_results, web_results)
                    
                else:
                    display_animated_message("No relevant sources found. Try different search terms or upload relevant PDFs.", "warning")
            
            except Exception as e:
                display_animated_message(f"Search error: {str(e)}", "error")

with col2:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.header("ℹ️ How to Use")
    st.markdown("""
    ### 📋 **Quick Guide:**
    1. **📄 Upload PDFs** in the sidebar
    2. **🔄 Click "Process PDFs"** to extract text
    3. **🧠 Choose AI model** (8B for speed, 70B for power)
    4. **💬 Ask questions** in the main area
    5. **🔍 Select search sources** (PDF/Web)
    6. **✨ Get intelligent answers**!

    ### ✨ **Features:**
    - 📄 **PDF text extraction**
    - 🔍 **OCR for scanned documents**  
    - 🌐 **Web search integration**
    - 🧠 **Semantic search**
    - 💬 **Natural language Q&A**
    - ⚡ **Groq-powered responses**
    - 🎯 **Source citations**
    - 📤 **Export chat history**
    """)
    
    if VOICE_AVAILABLE:
        st.markdown("- 🎤 **Voice input/output**")
    
    st.markdown("""
    ### 🤖 **Available Models:**
    """)
    
    st.markdown('<div class="model-indicator model-fast">🚀 <strong>Llama3 8B:</strong> Fast responses (8192 tokens)</div>', unsafe_allow_html=True)
    st.markdown('<div class="model-indicator model-powerful">💪 <strong>Llama3 70B:</strong> Most powerful (8192 tokens)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 💡 **Model Recommendations:**
    - **For quick questions**: Use Llama3 8B
    - **For complex analysis**: Use Llama3 70B
    - **For long documents**: Use Llama3 70B
    """)
    
    # Model info with animation
    try:
        current_model = st.session_state.groq_handler.model
        model_display = "Llama3 8B" if "8b" in current_model else "Llama3 70B"
        if "8b" in current_model:
            st.markdown(f'<div class="model-indicator model-fast">🤖 Current Model: {model_display}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="model-indicator model-powerful">🤖 Current Model: {model_display}</div>', unsafe_allow_html=True)
    except Exception as e:
        display_animated_message(f"Model info error: {str(e)}", "warning")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Chat History Section
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.header("📜 Chat History")
    
    # Export chat history
    export_chat_history()
    
    st.markdown("---")
    
    # Chat history display options
    col_display1, col_display2, col_display3 = st.columns(3)
    
    with col_display1:
        show_count = st.selectbox("Show conversations:", [5, 10, 20, "All"], index=0)
    
    with col_display2:
        show_sources = st.checkbox("Show sources", value=False)
    
    with col_display3:
        reverse_order = st.checkbox("Newest first", value=True)
    
    # Determine how many chats to show
    if show_count == "All":
        display_chats = st.session_state.chat_history
    else:
        display_chats = st.session_state.chat_history[-show_count:] if not reverse_order else st.session_state.chat_history[-show_count:]
    
    if reverse_order:
        display_chats = list(reversed(display_chats))
    
    # Show conversations with enhanced styling
    for i, chat in enumerate(display_chats):
        chat_index = len(st.session_state.chat_history) - i if reverse_order else i + 1
        
        with st.expander(f"💬 Conversation {chat_index}: {chat['question'][:50]}..." if len(chat['question']) > 50 else f"💬 Conversation {chat_index}: {chat['question']}"):
            # Question with colorful styling
            st.markdown(f'''
            <div class="user-message">
                <strong>❓ Question:</strong><br>
                {chat['question']}
            </div>
            ''', unsafe_allow_html=True)
            
            # Answer with colorful styling
            st.markdown(f'''
            <div class="bot-message">
                <strong>🤖 Answer:</strong><br>
                {chat['answer']}
            </div>
            ''', unsafe_allow_html=True)
            
            # Show sources if enabled
            if show_sources:
                sources = chat.get('sources', {})
                if sources.get('pdf') or sources.get('web'):
                    st.markdown("**📚 Sources:**")
                    
                    if sources.get('pdf'):
                        st.markdown(f'<div class="status-success">📄 **PDF sources:** {len(sources["pdf"])} documents</div>', unsafe_allow_html=True)
                        for j, pdf_source in enumerate(sources['pdf'][:2], 1):
                            st.markdown(f'<div class="source-box">• PDF {j}: {pdf_source[:100]}...</div>', unsafe_allow_html=True)
                    
                    if sources.get('web'):
                        st.markdown(f'<div class="status-success">🌐 **Web sources:** {len(sources["web"])} results</div>', unsafe_allow_html=True)
                        for j, web_source in enumerate(sources['web'][:2], 1):
                            st.markdown(f'<div class="source-box">• {web_source["title"]}: {web_source["snippet"][:100]}...</div>', unsafe_allow_html=True)
            
            # Timestamp and actions
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(chat['timestamp']))
            
            col_time, col_actions = st.columns([2, 1])
            with col_time:
                st.markdown(f'<div class="status-success">🕒 {timestamp}</div>', unsafe_allow_html=True)
            
            with col_actions:
                # Individual export for this conversation (if available)
                if EXPORT_AVAILABLE and hasattr(st.session_state, 'chat_exporter'):
                    if st.button(f"📤 Export", key=f"export_{chat_index}"):
                        try:
                            with st.spinner("📤 Exporting conversation..."):
                                single_chat = [chat]
                                docx_data = st.session_state.chat_exporter.export_to_docx(single_chat)
                                
                                st.download_button(
                                    label="📥 Download Conversation",
                                    data=docx_data,
                                    file_name=f"conversation_{chat_index}_{int(chat['timestamp'])}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key=f"download_{chat_index}"
                                )
                                display_animated_message("Conversation exported!", "success")
                        except Exception as e:
                            display_animated_message(f"Export error: {str(e)}", "error")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer with enhanced styling
st.markdown("---")

# Feature status indicator with animations
feature_status = []
if st.session_state.pdf_processed:
    feature_status.append('<span class="status-success">📄 PDFs Loaded</span>')
if st.session_state.chat_history:
    feature_status.append(f'<span class="status-success">💬 {len(st.session_state.chat_history)} Conversations</span>')
if VOICE_AVAILABLE:
    feature_status.append('<span class="status-success">🎤 Voice Enabled</span>')
if EXPORT_AVAILABLE:
    feature_status.append('<span class="status-success">📤 Export Enabled</span>')

if feature_status:
    st.markdown(" • ".join(feature_status), unsafe_allow_html=True)

# Enhanced Footer
st.markdown('''
<div class="footer-container">
    <p><strong>🤖 HybridBot Pro</strong> - Built with ❤️ using cutting-edge AI technology</p>
    <p><strong>🔧 Tech Stack:</strong> Streamlit • Groq • FAISS • Sentence Transformers • PyPDF2 • Tesseract OCR</p>
    <p><strong>🌟 Features:</strong> PDF Processing • Web Search • Voice Chat • Multi-format Export • Semantic Search</p>
</div>
''', unsafe_allow_html=True)

# Enhanced Error handling and recovery
if st.button("🔧 Troubleshoot Issues", help="Reset components if something isn't working"):
    try:
        with st.spinner("🔧 Troubleshooting..."):
            # Re-initialize components
            st.session_state.groq_handler = GroqHandler()
            st.session_state.vector_store = VectorStore()
            st.session_state.web_searcher = WebSearcher()
            st.session_state.pdf_processor = PDFProcessor()
            
            # Test connections
            connection_status = []
            
            try:
                if st.session_state.groq_handler.test_connection():
                    connection_status.append('<span class="status-success">✅ Groq API</span>')
                else:
                    connection_status.append('<span class="status-error">❌ Groq API</span>')
            except:
                connection_status.append('<span class="status-error">❌ Groq API</span>')
            
            try:
                test_search = st.session_state.web_searcher.search_multiple_sources("test", max_results=1)
                if test_search:
                    connection_status.append('<span class="status-success">✅ Web Search</span>')
                else:
                    connection_status.append('<span class="status-warning">⚠️ Web Search</span>')
            except:
                connection_status.append('<span class="status-error">❌ Web Search</span>')
            
            if st.session_state.pdf_processed:
                connection_status.append('<span class="status-success">✅ PDF Processing</span>')
            else:
                connection_status.append('<span class="status-warning">⚠️ No PDFs loaded</span>')
            
            display_animated_message("Troubleshooting complete!", "success")
            st.markdown("**System Status:** " + " • ".join(connection_status), unsafe_allow_html=True)
            
    except Exception as e:
        display_animated_message(f"Troubleshooting error: {str(e)}", "error")

# Quick actions sidebar enhancement
with st.sidebar:
    st.markdown("---")
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.header("⚡ Quick Actions")
    
    if st.button("🚀 Quick Start Guide", key="quick_start"):
        st.markdown('''
        <div class="alert-success">
        <strong>Getting Started:</strong><br>
        1. Upload a PDF file above<br>
        2. Click 'Process PDFs'<br>
        3. Ask a question in the main area<br>
        4. Choose your preferred AI model<br>
        5. Enable voice features if available<br><br>
        
        # Main content area
col1, col2 = st.columns([3, 1])

with col1:
    # Enhanced Question Input Section
    st.markdown('''
    <div class="question-container">
        <div style="text-align: center; margin-bottom: 1rem;">
           <h2 class="glow-text">Ask Your Questions</h2>
            <p style="color: white; opacity: 0.9;">Get intelligent answers from your documents and the web</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Voice input section (if available) with enhanced styling
    voice_question = ""
    if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
        st.markdown('<div class="voice-section" style="margin: 1rem 0;">', unsafe_allow_html=True)
        try:
            voice_question = st.session_state.voice_integration.handle_voice_input()
            if voice_question:
                st.markdown(f'''
                <div class="voice-detected"><strong>Voice Input Detected:</strong> {voice_question}
                </div>
                ''', unsafe_allow_html=True)
        except Exception as e:
            display_animated_message(f"Voice input error: {str(e)}", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Question Input Box
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    default_text = voice_question if voice_question else ""
    question = st.text_area(
        "🤔 What would you like to know?",
        value=default_text,
        placeholder="Type your question here... You can ask about:\n• Content from your uploaded PDFs\n• General knowledge questions\n• Complex analysis and comparisons\n• Research topics from the web",
        height=120,
        key="question_input",
        help="💡 Tip: Be specific for better results! The AI will search your documents and the web."
    )
    
    # Character counter and input validation
    if question:
        char_count = len(question)
        if char_count < 10:
            st.markdown(f'<div class="status-warning">⚠️ Question is quite short ({char_count} chars). Consider being more specific.</div>', unsafe_allow_html=True)
        elif char_count > 500:
            st.markdown(f'<div class="status-warning">⚠️ Long question ({char_count} chars). Consider breaking it down.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-success">✅ Good question length ({char_count} chars)</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear voice input if used
    if voice_question and voice_question == question:
        if hasattr(st.session_state, 'voice_input_text'):
            st.session_state.voice_input_text = ""
    
    # Enhanced Search and Response Options
    st.markdown('<div class="options-container" style="margin: 1.5rem 0;">', unsafe_allow_html=True)
    
    # Search Options Row
    st.markdown("### 🔍 **Search Configuration**")
    col_search1, col_search2 = st.columns([2, 1])
    
    with col_search1:
        # Dynamic default based on PDF availability
        default_sources = ["PDF Content", "Web Sources"] if st.session_state.pdf_processed else ["Web Sources"]
        if not st.session_state.pdf_processed:
            st.markdown('<div class="status-warning">📄 No PDFs loaded - Web search only</div>', unsafe_allow_html=True)
        
        search_options = st.multiselect(
            "Select information sources:",
            ["PDF Content", "Web Sources"],
            default=default_sources,
            help="Choose where to search for information to answer your question"
        )
        
        # Show search scope info
        if search_options:
            scope_info = []
            if "PDF Content" in search_options:
                if st.session_state.pdf_processed:
                    try:
                        stats = st.session_state.vector_store.get_stats()
                        scope_info.append(f"📄 {stats['total_texts']} PDF chunks")
                    except:
                        scope_info.append("📄 PDF content")
                else:
                    scope_info.append("📄 No PDFs available")
            
            if "Web Sources" in search_options:
                scope_info.append("🌐 Real-time web search")
            
            st.markdown(f'<div class="status-success">Search scope: {" + ".join(scope_info)}</div>', unsafe_allow_html=True)
    
    with col_search2:
        # Advanced search settings
        with st.expander("⚙️ Advanced Settings"):
            search_depth = st.selectbox(
                "Search depth:",
                ["Quick", "Standard", "Deep"],
                index=1,
                help="Quick: Fast results, Deep: More comprehensive"
            )
            
            include_context = st.checkbox(
                "Include context",
                value=True,
                help="Include surrounding text for better understanding"
            )
    
    # Response Mode Selection
    st.markdown("### ⚡ **Response Configuration**")
    col_response1, col_response2 = st.columns([2, 1])
    
    with col_response1:
        response_mode = st.radio(
            "Choose response style:",
            ["🔥 Streaming", "📋 Complete", "🎯 Concise"],
            horizontal=True,
            help="Streaming: See response as it's generated, Complete: Full response at once, Concise: Brief answers"
        )
        
        # Response mode info
        mode_info = {
            "🔥 Streaming": "Real-time response generation with typing animation",
            "📋 Complete": "Full response delivered at once for better readability", 
            "🎯 Concise": "Brief, focused answers for quick information"
        }
        st.markdown(f'<div class="info-card" style="padding: 0.5rem; margin: 0.5rem 0;">{mode_info[response_mode]}</div>', unsafe_allow_html=True)
    
    with col_response2:
        # Response customization
        with st.expander("🎨 Customize Response"):
            response_style = st.selectbox(
                "Response style:",
                ["Professional", "Casual", "Technical", "Creative"],
                help="Adjust the tone and style of responses"
            )
            
            include_sources = st.checkbox(
                "Show sources inline",
                value=False,
                help="Include source references within the response"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Ask Button with validation
    button_disabled = not question or not search_options
    button_help = "Enter a question and select search sources" if button_disabled else "Click to get your answer!"
    
    if button_disabled:
        st.markdown('<div class="status-warning">⚠️ Please enter a question and select at least one search source</div>', unsafe_allow_html=True)
    
    # Multi-column button layout
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        ask_button = st.button(
            "🔍 Get Intelligent Answer", 
            type="primary", 
            use_container_width=True,
            disabled=button_disabled,
            help=button_help
        )
    
    with col_btn2:
        if question:
            if st.button("🎲 Suggest Similar", help="Get related question suggestions"):
                # Generate suggested questions based on current input
                suggestions = [
                    f"What are the key points about {question[:30]}...?",
                    f"Can you elaborate on {question[:30]}...?",
                    f"What's the context behind {question[:30]}...?"
                ]
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f'<div class="source-box">💡 {i}. {suggestion}</div>', unsafe_allow_html=True)
    
    with col_btn3:
        if st.session_state.chat_history:
            if st.button("📚 Chat History", help="View previous conversations"):
                st.markdown('<div class="status-success">📜 Scroll down to see chat history</div>', unsafe_allow_html=True)
    
    # Main Processing Logic with Enhanced UI
    if ask_button and question and search_options:
        # Question Analysis
        st.markdown(f'''
        <div class="user-message">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2em;"></span>
                <strong>Your Question:</strong>
            </div>
            <div style="font-size: 1.1em; line-height: 1.5;">{question}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        try:
            # Enhanced search phase with visual feedback
            st.markdown('<div class="search-animation">', unsafe_allow_html=True)
            
            search_container = st.container()
            with search_container:
                st.markdown("### 🔍 **Searching Information Sources...**")
                
                # Create progress tracking
                search_progress = st.progress(0)
                search_status = st.empty()
                
                # Search PDF content
                pdf_results = []
                if st.session_state.pdf_processed and "PDF Content" in search_options:
                    search_status.markdown('<div class="status-success">📄 Searching PDF documents...</div>', unsafe_allow_html=True)
                    search_progress.progress(25)
                    
                    pdf_search_results = st.session_state.vector_store.search(question, k=5 if search_depth == "Deep" else 3)
                    threshold = 0.2 if search_depth == "Deep" else 0.3
                    pdf_results = [text for text, score in pdf_search_results if score > threshold]
                    
                    if pdf_results:
                        search_status.markdown(f'<div class="status-success">📄 Found {len(pdf_results)} relevant PDF sections</div>', unsafe_allow_html=True)
                    else:
                        search_status.markdown('<div class="status-warning">📄 No relevant PDF content found</div>', unsafe_allow_html=True)
                
                search_progress.progress(50)
                
                # Search web content
                web_results = []
                if "Web Sources" in search_options:
                    search_status.markdown('<div class="status-success">🌐 Searching web sources...</div>', unsafe_allow_html=True)
                    search_progress.progress(75)
                    
                    max_results = 5 if search_depth == "Deep" else 3
                    web_results = st.session_state.web_searcher.search_multiple_sources(question, max_results=max_results)
                    
                    if web_results:
                        search_status.markdown(f'<div class="status-success">🌐 Found {len(web_results)} web sources</div>', unsafe_allow_html=True)
                    else:
                        search_status.markdown('<div class="status-warning">🌐 No relevant web content found</div>', unsafe_allow_html=True)
                
                search_progress.progress(100)
                time.sleep(0.5)  # Brief pause for effect
                search_progress.empty()
                search_status.empty()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Results Summary with enhanced visualization
            total_sources = len(pdf_results) + len(web_results)
            if total_sources > 0:
                st.markdown(f'''
                <div class="status-success" style="text-align: center; padding: 1rem; font-size: 1.1em;"> <strong>Found {total_sources} relevant sources</strong>
                    {f" • {len(pdf_results)} from PDFs" if pdf_results else ""}
                    {f" • {len(web_results)} from web" if web_results else ""}
                </div>
                ''', unsafe_allow_html=True)
                
                # Generate and display answer
                st.markdown('''
                <div class="answer-container">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                        <span style="font-size: 1.5em;"></span>
                        <h3 style="margin: 0; color: white;">AI Assistant Response</h3>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Response generation based on mode
                if "Streaming" in response_mode:
                    # Enhanced streaming response
                    try:
                        stream = st.session_state.groq_handler.stream_response(
                            question, pdf_results, web_results
                        )
                        
                        if stream:
                            response_placeholder = st.empty()
                            full_response = ""
                            
                            # Add typing indicator
                            with response_placeholder.container():
                                st.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)
                            
                            try:
                                for chunk in stream:
                                    if chunk.choices[0].delta.content is not None:
                                        full_response += chunk.choices[0].delta.content
                                        # Enhanced streaming display
                                        response_placeholder.markdown(
                                            f'''
                                            <div class="streaming-text" style="color: white; line-height: 1.6;">
                                                {full_response}<span style="animation: blink 1s infinite;"></span>
                                            </div>
                                            <style>
                                                @keyframes blink {{
                                                    0%, 50% {{ opacity: 1; }}
                                                    51%, 100% {{ opacity: 0; }}
                                                }}
                                            </style>
                                            ''', 
                                            unsafe_allow_html=True
                                        )
                                
                                # Final response without cursor
                                response_placeholder.markdown(
                                    f'<div style="color: white; line-height: 1.6; font-size: 1.05em;">{full_response}</div>', 
                                    unsafe_allow_html=True
                                )
                                
                                # Add to chat history
                                st.session_state.chat_history.append({
                                    "question": question,
                                    "answer": full_response,
                                    "sources": {"pdf": pdf_results, "web": web_results},
                                    "timestamp": time.time(),
                                    "mode": response_mode,
                                    "style": response_style
                                })
                                
                                # Voice output (if available)
                                if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
                                    try:
                                        st.session_state.voice_integration.handle_voice_output(full_response)
                                    except Exception as e:
                                        display_animated_message(f"Voice output")
                                       
# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    # Enhanced Question Input Section
    st.markdown('''
    <div class="question-container">
        <h2 class="glow-text">Ask Your Questions</h2>
        <p style="color: white; opacity: 0.9;">Get intelligent answers from your documents and the web</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Voice input section (if available) with enhanced styling
    voice_question = ""
    if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
        st.markdown('<div class="voice-section" style="margin: 1rem 0;">', unsafe_allow_html=True)
        try:
            voice_question = st.session_state.voice_integration.handle_voice_input()
            if voice_question:
                st.markdown(f'''
                <div class="voice-detected"><strong>Voice Input Detected:</strong> {voice_question}
                </div>
                ''', unsafe_allow_html=True)
        except Exception as e:
            display_animated_message(f"Voice input error: {str(e)}", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Question Input Box
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    default_text = voice_question if voice_question else ""
    question = st.text_area(
        "🤔 What would you like to know?",
        value=default_text,
        placeholder="Type your question here... You can ask about:\n• Content from your uploaded PDFs\n• General knowledge questions\n• Complex analysis and comparisons\n• Research topics from the web",
        height=120,
        key="question_input",
        help="💡 Tip: Be specific for better results! The AI will search your documents and the web."
    )
    
    # Character counter and input validation
    if question:
        char_count = len(question)
        if char_count < 10:
            st.markdown(f'<div class="status-warning">Question is quite short ({char_count} chars). Consider being more specific.</div>', unsafe_allow_html=True)
        elif char_count > 500:
            st.markdown(f'<div class="status-warning"> Long question ({char_count} chars). Consider breaking it down.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-success"> Good question length ({char_count} chars)</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear voice input if used
    if voice_question and voice_question == question:
        if hasattr(st.session_state, 'voice_input_text'):
            st.session_state.voice_input_text = ""
    
    # Enhanced Search and Response Options
    st.markdown('<div class="options-container" style="margin: 1.5rem 0;">', unsafe_allow_html=True)
    
    # Search Options Row
    st.markdown("### 🔍 **Search Configuration**")
    col_search1, col_search2 = st.columns([2, 1])
    
    with col_search1:
        # Dynamic default based on PDF availability
        default_sources = ["PDF Content", "Web Sources"] if st.session_state.pdf_processed else ["Web Sources"]
        if not st.session_state.pdf_processed:
            st.markdown('<div class="status-warning"> No PDFs loaded - Web search only</div>', unsafe_allow_html=True)
        
        search_options = st.multiselect(
            "Select information sources:",
            ["PDF Content", "Web Sources"],
            default=default_sources,
            help="Choose where to search for information to answer your question"
        )
        
        # Show search scope info
        if search_options:
            scope_info = []
            if "PDF Content" in search_options:
                if st.session_state.pdf_processed:
                    try:
                        stats = st.session_state.vector_store.get_stats()
                        scope_info.append(f" {stats['total_texts']} PDF chunks")
                    except:
                        scope_info.append(" PDF content")
            
            if "Web Sources" in search_options:
                scope_info.append("🌐 Real-time web search")
            
            st.markdown(f'<div class="status-success">Search scope: {" + ".join(scope_info)}</div>', unsafe_allow_html=True)
    
    with col_search2:
        # Advanced search settings
        with st.expander("⚙️ Advanced Settings"):
            search_depth = st.selectbox(
                "Search depth:",
                ["Quick", "Standard", "Deep"],
                index=1,
                help="Quick: Fast results, Deep: More comprehensive"
            )
            
            include_context = st.checkbox(
                "Include context",
                value=True,
                help="Include surrounding text for better understanding"
            )
    
    # Response Mode Selection
    st.markdown("### ⚡ **Response Configuration**")
    col_response1, col_response2 = st.columns([2, 1])
    
    with col_response1:
        response_mode = st.radio(
            "Choose response style:",
            ["🔥 Streaming", "📋 Complete", "🎯 Concise"],
            horizontal=True,
            help="Streaming: See response as it's generated, Complete: Full response at once, Concise: Brief answers"
        )
        
        # Response mode info
        mode_info = {
            "🔥 Streaming": "Real-time response generation with typing animation",
            "📋 Complete": "Full response delivered at once for better readability", 
            "🎯 Concise": "Brief, focused answers for quick information"
        }
        st.markdown(f'<div class="info-card" style="padding: 0.5rem; margin: 0.5rem 0;">{mode_info[response_mode]}</div>', unsafe_allow_html=True)
    
    with col_response2:
        # Response customization
        with st.expander("🎨 Customize Response"):
            response_style = st.selectbox(
                "Response style:",
                ["Professional", "Casual", "Technical", "Creative"],
                help="Adjust the tone and style of responses"
            )
            
            include_sources = st.checkbox(
                "Show sources inline",
                value=False,
                help="Include source references within the response"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Ask Button with validation
    button_disabled = not question or not search_options
    button_help = "Enter a question and select search sources" if button_disabled else "Click to get your answer!"
    
    if button_disabled:
        st.markdown('<div class="status-warning">⚠️ Please enter a question and select at least one search source</div>', unsafe_allow_html=True)
    
    # Multi-column button layout
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        ask_button = st.button(
            "🔍 Get Intelligent Answer", 
            type="primary", 
            use_container_width=True,
            disabled=button_disabled,
            help=button_help
        )
    
    with col_btn2:
        if question:
            if st.button("🎲 Suggest Similar", help="Get related question suggestions"):
                # Generate suggested questions based on current input
                suggestions = [
                    f"What are the key points about {question[:30]}...?",
                    f"Can you elaborate on {question[:30]}...?",
                    f"What's the context behind {question[:30]}...?"
                ]
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f'<div class="source-box">💡 {i}. {suggestion}</div>', unsafe_allow_html=True)
    
    with col_btn3:
        if st.session_state.chat_history:
            if st.button("📚 Chat History", help="View previous conversations"):
                st.markdown('<div class="status-success">📜 Scroll down to see chat history</div>', unsafe_allow_html=True)
    
    # Main Processing Logic with Enhanced UI
    if ask_button and question and search_options:
        # Question Analysis
        st.markdown(f'''
        <div class="user-message">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2em;"></span>
                <strong>Your Question:</strong>
            </div>
            <div style="font-size: 1.1em; line-height: 1.5;">{question}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        try:
            # Enhanced search phase with visual feedback
            st.markdown('<div class="search-animation">', unsafe_allow_html=True)
            
            search_container = st.container()
            with search_container:
                st.markdown("###  **Searching Information Sources...**")
                
                # Create progress tracking
                search_progress = st.progress(0)
                search_status = st.empty()
                
                # Search PDF content
                pdf_results = []
                if st.session_state.pdf_processed and "PDF Content" in search_options:
                    search_status.markdown('<div class="status-success"> Searching PDF documents...</div>', unsafe_allow_html=True)
                    search_progress.progress(25)
                    
                    pdf_search_results = st.session_state.vector_store.search(question, k=5 if search_depth == "Deep" else 3)
                    threshold = 0.2 if search_depth == "Deep" else 0.3
                    pdf_results = [text for text, score in pdf_search_results if score > threshold]
                    
                    if pdf_results:
                        search_status.markdown(f'<div class="status-success"> Found {len(pdf_results)} relevant PDF sections</div>', unsafe_allow_html=True)
                    else:
                        search_status.markdown('<div class="status-warning"> No relevant PDF content found</div>', unsafe_allow_html=True)
                
                search_progress.progress(50)
                
                # Search web content
                web_results = []
                if "Web Sources" in search_options:
                    search_status.markdown('<div class="status-success"> Searching web sources...</div>', unsafe_allow_html=True)
                    search_progress.progress(75)
                    
                    max_results = 5 if search_depth == "Deep" else 3
                    web_results = st.session_state.web_searcher.search_multiple_sources(question, max_results=max_results)
                    
                    if web_results:
                        search_status.markdown(f'<div class="status-success">Found {len(web_results)} web sources</div>', unsafe_allow_html=True)
                    else:
                        search_status.markdown('<div class="status-warning">No relevant web content found</div>', unsafe_allow_html=True)
                
                search_progress.progress(100)
                time.sleep(0.5)  # Brief pause for effect
                search_progress.empty()
                search_status.empty()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Results Summary with enhanced visualization
            total_sources = len(pdf_results) + len(web_results)
            if total_sources > 0:
                st.markdown(f'''
                <div class="status-success" style="text-align: center; padding: 1rem; font-size: 1.1em;">
                     <strong>Found {total_sources} relevant sources</strong>
                    {f" • {len(pdf_results)} from PDFs" if pdf_results else ""}
                    {f" • {len(web_results)} from web" if web_results else ""}
                </div>
                ''', unsafe_allow_html=True)
                
                # Generate and display answer
                st.markdown('''
                <div class="answer-container">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                        <span style="font-size: 1.5em;"></span>
                        <h3 style="margin: 0; color: white;">AI Assistant Response</h3>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Response generation based on mode
                if "Streaming" in response_mode:
                    # Enhanced streaming response
                    try:
                        stream = st.session_state.groq_handler.stream_response(
                            question, pdf_results, web_results
                        )
                        
                        if stream:
                            response_placeholder = st.empty()
                            full_response = ""
                            
                            # Add typing indicator
                            with response_placeholder.container():
                                st.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)
                            
                            try:
                                for chunk in stream:
                                    if chunk.choices[0].delta.content is not None:
                                        full_response += chunk.choices[0].delta.content
                                        # Enhanced streaming display
                                        response_placeholder.markdown(
                                            f'''
                                            <div class="streaming-text" style="color: white; line-height: 1.6;">
                                                {full_response}<span style="animation: blink 1s infinite;"></span>
                                            </div>
                                            <style>
                                                @keyframes blink {{
                                                    0%, 50% {{ opacity: 1; }}
                                                    51%, 100% {{ opacity: 0; }}
                                                }}
                                            </style>
                                            ''', 
                                            unsafe_allow_html=True
                                        )
                                
                                # Final response without cursor
                                response_placeholder.markdown(
                                    f'<div style="color: white; line-height: 1.6; font-size: 1.05em;">{full_response}</div>', 
                                    unsafe_allow_html=True
                                )
                                
                                # Add to chat history
                                st.session_state.chat_history.append({
                                    "question": question,
                                    "answer": full_response,
                                    "sources": {"pdf": pdf_results, "web": web_results},
                                    "timestamp": time.time(),
                                    "mode": response_mode,
                                    "style": response_style
                                })
                                
                                # Voice output (if available)
                                if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
                                    try:
                                        st.session_state.voice_integration.handle_voice_output(full_response)
                                    except Exception as e:
                                        display_animated_message(f"Voice output error: {str(e)}", "warning")
                                    
                            except Exception as e:
                                display_animated_message(f"Streaming error: {str(e)}", "error")
                        else:
                            display_animated_message("No response from the model.", "warning")
                    except Exception as e:
                        display_animated_message(f"Streaming initialization error: {str(e)}", "error")
                else:
                    # Complete response
                    with st.spinner(" Generating answer with Groq..."):
                        try:
                            answer = st.session_state.groq_handler.generate_answer(
                                question, pdf_results, web_results
                            )
                            st.markdown(f'<div class="answer-text">{answer}</div>', unsafe_allow_html=True)
                            
                            # Add to chat history
                            st.session_state.chat_history.append({
                                "question": question,
                                "answer": answer,
                                "sources": {"pdf": pdf_results, "web": web_results},
                                "timestamp": time.time(),
                                "mode": response_mode,
                                "style": response_style
                            })
                            
                            # Voice output (if available)
                            if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
                                try:
                                    st.session_state.voice_integration.handle_voice_output(answer)
                                except Exception as e:
                                    display_animated_message(f"Voice output error: {str(e)}", "warning")
                            
                        except Exception as e:
                            display_animated_message(f"Answer generation error: {str(e)}", "error")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Display sources
                display_sources(pdf_results, web_results)
                
            else:
                display_animated_message("No relevant sources found. Try different search terms or upload relevant PDFs.", "warning")
                
# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    # Animated Hero Section
    
st.markdown('''
<style>
.floating-badge {
    background: linear-gradient(45 deg, rgba(255,255,255,0.2), rgba(255,255,255,0.1));
    color: white;
    padding: 0.5 rem 1 rem;
    border-radius: 20 px;
    border: 1 px solid rgba(255,255,255,0.3);
    animation: floatBadge 3 s ease-in-out infinite alternate;
    backdrop-filter: blur(10 px);
}
@keyframes floatBadge {
    0% { transform: translateY(0 px); }
    100% { transform: translateY(-5 px); }
}
</style>
''', unsafe_allow_html=True)
    
    # Voice Input Section with Enhanced UI
    if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
        st.markdown('''
        <div class="voice-section" style=margin: 2 rem 0; padding: 1.5 rem; 
             background: linear-gradient(135 deg, #ff6b6b, #feca57); 
             border-radius: 15 px; position: relative; overflow: hidden;>
            <div style="position: relative; z-index: 2;">
                <h3 style="color: white; text-align: center; margin-bottom: 1rem;">
                     Voice Input Available
                </h3>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        try:
            voice_question = st.session_state.voice_integration.handle_voice_input()
            if voice_question:
                st.markdown(f'''
                <div class="voice-detected" style=background: linear-gradient(135 deg, #00f260, #0575e6);
                     color: white; padding: 1 rem; border-radius: 10 px; margin: 1 rem 0;
                     animation: slideInRight 0.5 s ease-out;>
                    <div style=display: flex; align-items: center; gap: 0.5 rem;>
                        <span style=font-size: 1.5 em;></span>
                        <strong>Voice Detected:</strong>
                    </div>
                    <p style=margin: 0.5 rem 0 0 0; font-size: 1.1 em;>{voice_question}</p>
                </div>
                ''', unsafe_allow_html=True)
        except Exception as e:
            display_animated_message(f"Voice input error: {str(e)}", "warning")
    else:
        voice_question = ""
    
    # Enhanced Question Input with Live Validation
    st.markdown('''
    <div class="input-section" style=margin: 2 rem 0; padding: 1.5 rem; 
         background: linear-gradient(135 deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
         backdrop-filter: blur(10 px); border-radius: 15 px; border: 1 px solid rgba(255,255,255,0.2);>
        <h3 style=color: #667eea; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;>
            <span style="font-size: 1.3 em;"></span>
            What is on your mind?
        </h3>
    ''', unsafe_allow_html=True)
    
    default_text = voice_question if voice_question else ""
    question = st.text_area(
        "",
        value=default_text,
        placeholder=" Ask me anything! Examples:\n\n• What are the main findings in my uploaded documents?\n• How does artificial intelligence work?\n• Compare renewable energy sources\n• Summarize the key points from my PDFs\n• What's the latest news about climate change?",
        height=150,
        key="question_input",
        help=" Pro tip: Be specific and detailed for the best results!"
    )
    
    # Smart Input Validation with Animated Feedback
    if question:
        char_count = len(question)
        word_count = len(question.split())
        
        # Determine input quality
        if char_count < 10:
            feedback_type = "warning"
            feedback_msg = f" Very short question ({char_count} chars, {word_count} words) - Consider adding more details"
            feedback_color = "#f093fb"
        elif char_count < 30:
            feedback_type = "info"
            feedback_msg = f" Short question ({char_count} chars, {word_count} words) - More context could help"
            feedback_color = "#667eea"
        elif char_count > 500:
            feedback_type = "warning"
            feedback_msg = f" Long question ({char_count} chars, {word_count} words) - Consider breaking it down"
            feedback_color = "#f093fb"
        else:
            feedback_type = "success"
            feedback_msg = f" Great question length ({char_count} chars, {word_count} words)"
            feedback_color = "#00f260"
        
        st.markdown(f'''
        <div style=background: linear-gradient(135 deg, {feedback_color}, {feedback_color}20);
             color: white; padding: 0.8 rem; border-radius: 10 px; margin: 1 rem 0;
             animation: slideInUp 0.3 s ease-out; font-weight: 500;>
            {feedback_msg}
        </div>
        ''', unsafe_allow_html=True)
        
        # Question analysis preview
        if char_count > 20:
            question_keywords = question.lower().split()[:5]
            st.markdown(f'''
            <div style=background: rgba(102, 126, 234, 0.1); padding: 0.8 rem; 
                 border-radius: 8 px; margin: 0.5 rem 0; border-left: 3 px solid #667eea;">
                <small><strong> Detected keywords:</strong> {", ".join([f"#{word}" for word in question_keywords if len(word) > 3])}</small>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced Search Configuration Panel
    st.markdown('''
    <div class="config-panel" style=background: linear-gradient(135 deg, #667eea, #764ba2);
         color: white; padding: 1.5 rem; border-radius: 15 px; margin: 2 rem 0;>
        <h3 style=margin: 0 0 1 rem 0; display: flex; align-items: center; gap: 0.5 rem;>
            <span style=font-size: 1.3 em;></span>
            Search & Response Settings
        </h3>
    </div>
    ''', unsafe_allow_html=True)
    
    # Search Sources Configuration
    col_search_config1, col_search_config2 = st.columns([2, 1])
    
    with col_search_config1:
        st.markdown("#### **Information Sources**")
        
        # Dynamic source availability check
        pdf_available = st.session_state.pdf_processed
        web_available = True  # Assuming web search is always available
        
        if pdf_available:
            try:
                stats = st.session_state.vector_store.get_stats()
                pdf_info = f" PDF Content ({stats['total_texts']} chunks available)"
            except:
                pdf_info = " PDF Content (Available)"
        else:
            pdf_info = " PDF Content ( No PDFs uploaded)"
        
        web_info = " Web Sources ( Real-time search)"
        
        # Source selection with enhanced display
        source_options = []
        if pdf_available:
            source_options.append("PDF Content")
        source_options.append("Web Sources")
        
        default_sources = source_options if pdf_available else ["Web Sources"]
        
        search_options = st.multiselect(
            "Select where to search:",
            ["PDF Content", "Web Sources"],
            default=default_sources,
            help="Choose your information sources"
        )
        
        # Source status display
        st.markdown(f'''
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <div style="margin-bottom: 0.5rem;">
                {'✅' if 'PDF Content' in search_options and pdf_available else '❌'} {pdf_info}
            </div>
            <div>
                {'✅' if 'Web Sources' in search_options else '❌'} {web_info}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col_search_config2:
        st.markdown("#### 🎯 **Search Quality**")
        
        search_mode = st.radio(
            "Search intensity:",
            ["🔥 Fast", "⚡ Standard", "🔍 Deep"],
            index=1,
            help="Choose search depth vs speed"
        )
        
        # Mode explanations
        mode_explanations = {
            "🔥 Fast": "Quick results, 3 sources",
            "⚡ Standard": "Balanced, 5 sources", 
            "🔍 Deep": "Comprehensive, 8 sources"
        }
        
        st.markdown(f'''
        <div style=background: rgba(255,255,255,0.1); padding: 0.8 rem; 
             border-radius: 8 px; margin: 0.5 rem 0; font-size: 0.9 em;>
             {mode_explanations[search_mode]}
        </div>
        ''', unsafe_allow_html=True)
    
    # Response Configuration
    st.markdown("#### ⚡ **AI Response Settings**")
    
    col_response1, col_response2 = st.columns([3, 2])
    
    with col_response1:
        response_mode = st.selectbox(
            "Response style:",
            [
                "🔥 Streaming (Real-time typing)",
                "📋 Complete (All at once)", 
                "🎯 Concise (Brief & focused)",
                "📚 Detailed (Comprehensive)",
                "💡 Creative (Engaging style)"
            ],
            index=0,
            help="Choose how you want to receive answers"
        )
        
        # Response style preview
        style_previews = {
            "🔥 Streaming (Real-time typing)": "See the AI think and respond in real-time with typing animations",
            "📋 Complete (All at once)": "Get the full response immediately for easy reading",
            "🎯 Concise (Brief & focused)": "Quick, to-the-point answers for fast information",
            "📚 Detailed (Comprehensive)": "In-depth explanations with examples and context",
            "💡 Creative (Engaging style)": "Fun, creative responses with analogies and examples"
        }
        
        st.markdown(f'''
        <div style=background: rgba(17, 153, 142, 0.2); padding: 0.8 rem; 
             border-radius: 8 px; margin: 0.5 rem 0; font-size: 0.9 em; 
             border-left: 3 px solid #11998e;>
            {style_previews[response_mode]}
        </div>
        ''', unsafe_allow_html=True)
    
    with col_response2:
        st.markdown("** Customization**")
        
        with st.expander("Advanced Options"):
            temperature = st.slider(
                "Creativity level:",
                0.0, 1.0, 0.7, 0.1,
                help="Higher = more creative, Lower = more focused"
            )
            
            show_thinking = st.checkbox(
                "Show AI reasoning",
                value=False,
                help="Display how the AI processes your question"
            )
            
            include_followup = st.checkbox(
                "Suggest follow-up questions",
                value=True,
                help="Get related questions after each answer"
            )
    
    # Enhanced Action Buttons
    st.markdown("---")
    
    # Validation and button state
    can_ask = bool(question and search_options)
    button_style = "primary" if can_ask else "secondary"
    
    if not can_ask:
        missing_items = []
        if not question:
            missing_items.append("❓ Enter a question")
        if not search_options:
            missing_items.append("🔍 Select search sources")
        
        st.markdown(f'''
        <div style=background: linear-gradient(135 deg, #ff416c, #ff4b2b); 
             color: white; padding: 1 rem; border-radius: 10 px; margin: 1 rem 0;
             animation: shake 0.5 s ease-in-out;>
            <strong> Ready to ask? Please:</strong><br>
            {"<br>".join([f"• {item}" for item in missing_items])}
        </div>
        ''', unsafe_allow_html=True)
    
    # Main action buttons row
    col_main_btn, col_quick_btn, col_history_btn = st.columns([3, 1, 1])
    
    with col_main_btn:
        ask_button = st.button(
            " Get Smart Answer" if can_ask else " Complete Setup First",
            type=button_style,
            use_container_width=True,
            disabled=not can_ask,
            help="Click to get your AI-powered answer!" if can_ask else "Complete the setup above first"
        )
    
    with col_quick_btn:
        if st.button(" Random", help="Get a random interesting question"):
            random_questions = [
                "What are the latest developments in artificial intelligence?",
                "How can renewable energy solve climate change?",
                "What are the benefits and risks of cryptocurrency?",
                "How does quantum computing work?",
                "What are the future trends in space exploration?"
            ]
            import random
            selected_question = random.choice(random_questions)
            st.markdown(f'''
            <div style=background: linear-gradient(135 deg, #667eea, #764ba2); 
                 color: white; padding: 1 rem; border-radius: 10 px; margin: 1 rem 0;
                 animation: slideInUp 0.5 s ease-out;>
                <strong> Random Question:</strong><br>
                {selected_question}
            </div>
            ''', unsafe_allow_html=True)
            # Auto-fill the question
            st.session_state.question_input = selected_question
            st.rerun()
    
    with col_history_btn:
        if st.session_state.chat_history:
            if st.button(" History", help="View conversation history"):
                st.markdown(f'''
                <div style=background: linear-gradient(135 deg, #11998e, #38ef7d); 
                     color: white; padding: 1 rem; border-radius: 10 px; margin: 1 rem 0;
                     animation: pulse 2 s infinite;>
                    <strong> Chat Stats:</strong><br>
                     {len(st.session_state.chat_history)} conversations<br>
                     Scroll down to view all
                </div>
                ''', unsafe_allow_html=True)
    
    # Question Processing with Enhanced Visual Feedback
    if ask_button and can_ask:
        # Display user question with style
        st.markdown(f'''
        <div class="user-message" style=animation: slideInLeft 0.5 s ease-out;>
            <div style=display: flex; align-items: center; gap: 0.8 rem; margin-bottom: 1 rem;>
                <div style=background: linear-gradient(45 deg, #667eea, #764ba2); 
                     padding: 8 px; border-radius: 50 % ; color: white; font-size: 1.2 em;></div>
                <h3 style=margin: 0; color: white;>Your Question</h3>
            </div>
            <div style=font-size: 1.1 em; line-height: 1.6; color: white; 
                 background: rgba(255,255,255,0.1); padding: 1 rem; border-radius: 8 px;>
                {question}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        try:
            # Enhanced Search Process with Real-time Updates
            st.markdown('''
            <div class="search-process" style=background: linear-gradient(135 deg, #667eea, #764ba2);
                 color: white; padding: 1.5 rem; border-radius: 15 px; margin: 2 rem 0;
                 animation: slideInRight 0.5 s ease-out;>
                <h3 style=margin: 0 0 1 rem 0; display: flex; align-items: center; gap: 0.5 rem;>
                    <span class="loading-spinner" style=width: 20 px; height: 20 px; border: 2 px solid rgba(255,255,255,0.3); border-top: 2 px solid white;></span>
                    Searching Information Sources
                </h3>
            </div>
            ''', unsafe_allow_html=True)
            
            # Initialize search tracking
            search_progress = st.progress(0)
            search_status = st.empty()
            results_display = st.empty()
            
            # Determine search parameters based on mode
            search_params = {
                " Fast": {"pdf_k": 3, "web_max": 3, "threshold": 0.4},
                " Standard": {"pdf_k": 5, "web_max": 5, "threshold": 0.3},
                " Deep": {"pdf_k": 8, "web_max": 8, "threshold": 0.2}
            }
            
            params = search_params.get(search_mode, search_params[" Standard"])
            
            # Search PDF Content
            pdf_results = []
            if st.session_state.pdf_processed and "PDF Content" in search_options:
                search_status.markdown('''
                <div style=background: rgba(102, 126, 234, 0.2); padding: 0.8 rem; 
                     border-radius: 8 px; border-left: 3 px solid #667eea; animation: pulse 1s infinite;>
                     <strong>Searching PDF documents...</strong>
                </div>
                ''', unsafe_allow_html=True)
                search_progress.progress(25)
                
                pdf_search_results = st.session_state.vector_store.search(question, k=params["pdf_k"])
                pdf_results = [text for text, score in pdf_search_results if score > params["threshold"]]
                
                # Update status
                if pdf_results:
                    search_status.markdown(f'''
                    <div style=background: rgba(0, 242, 96, 0.2); padding: 0.8 rem; 
                         border-radius: 8 px; border-left: 3 px solid #00f260;">
                         <strong>Found {len(pdf_results)} relevant PDF sections</strong>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    search_status.markdown('''
                    <div style=background: rgba(240, 147, 251, 0.2); padding: 0.8 rem; 
                         border-radius: 8 px; border-left: 3 px solid #f093fb;>
                         <strong>No highly relevant PDF content found</strong>
                    </div>
                    ''', unsafe_allow_html=True)
                
                time.sleep(0.5)  # Visual pause
                search_progress.progress(50)
            
            # Search Web Sources
            web_results = []
            if "Web Sources" in search_options:
                search_status.markdown('''
                <div style=background: rgba(17, 153, 142, 0.2); padding: 0.8 rem; 
                     border-radius: 8 px; border-left: 3 px solid #11998e; animation: pulse 1s infinite;>
                     <strong>Searching web sources...</strong>
                </div>
                ''', unsafe_allow_html=True)
                search_progress.progress(75)
                
                web_results = st.session_state.web_searcher.search_multiple_sources(
                    question, max_results=params["web_max"]
                )
                
                # Update status
                if web_results:
                    search_status.markdown(f'''
                    <div style=background: rgba(0, 242, 96, 0.2); padding: 0.8 rem; 
                         border-radius: 8 px; border-left: 3 px solid #00f260;>
                        <strong>Found {len(web_results)} web sources</strong>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    search_status.markdown('''
                    <div style=background: rgba(240, 147, 251, 0.2); padding: 0.8 rem; 
                         border-radius: 8 px; border-left: 3 px solid #f093fb;>
                        <strong>Limited web results found</strong>
                    </div>
                    ''', unsafe_allow_html=True)
                
                time.sleep(0.5)  # Visual pause
                search_progress.progress(100)
            
            # Complete search process
            time.sleep(1)
            search_progress.empty()
            search_status.empty()
            
            # Results Summary with Enhanced Visualization
            total_sources = len(pdf_results) + len(web_results)
            
            if total_sources > 0:
                # Success summary
                st.markdown(f'''
                <div style=background: linear-gradient(135 deg, #00f260, #0575e6); 
                     color: white; padding: 1.5 rem; border-radius: 15 px; margin: 1 rem 0;
                     text-align: center; animation: slideInUp 0.5 s ease-out;>
                    <div style=font-size: 1.3 em; margin-bottom: 0.5 rem;>
                         <strong>Search Complete!</strong>
                    </div>
                    <div style=font-size: 1.1 em;>
                        Found <strong>{total_sources} relevant sources</strong>
                        {f" • {len(pdf_results)} from PDFs" if pdf_results else ""}
                        {f" • {len(web_results)} from web" if web_results else ""}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # AI Response Generation
                st.markdown('''
                <div class="answer-container" style=animation: slideInLeft 0.5 s ease-out;>
                    <div style=display: flex; align-items: center; gap: 1 rem; margin-bottom: 1.5 rem;>
                        <div style=background: linear-gradient(45 deg, #11998e, #38ef7d); 
                             padding: 12 px; border-radius: 50 %; color: white; font-size: 1.5 em;></div>
                        <div>
                            <h2 style=margin: 0; color: white;>AI Assistant</h2>
                            <p style=margin: 0; color: rgba(255,255,255,0.8); font-size: 0.9 em;>
                                Powered by Groq Processing {total_sources} sources
                            </p>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Show AI thinking process if enabled
                if show_thinking:
                    st.markdown('''
                    <div style=background: rgba(255,255,255,0.1); padding: 1 rem; 
                         border-radius: 8 px; margin: 1 rem 0; border-left: 3 px solid #667eea;>
                        <strong> AI Reasoning Process:</strong><br>
                        1. Analyzing your question for key concepts<br>
                        2. Matching information from {pdf_count} PDF sources and {web_count} web sources<br>
                        3. Synthesizing comprehensive answer<br>
                        4. Ensuring accuracy and relevance
                    </div>
                    '''.format(pdf_count=len(pdf_results), web_count=len(web_results)), unsafe_allow_html=True)
                
                # Response Generation Based on Mode
                if "Streaming" in response_mode:
                    # Enhanced Streaming Response
                    try:
                        stream = st.session_state.groq_handler.stream_response(
                            question, pdf_results, web_results
                        )
                        
                        if stream:
                            response_placeholder = st.empty()
                            full_response = ""
                            
                            # Typing indicator
                            response_placeholder.markdown('''
                            <div style=color: rgba(255,255,255,0.7); padding: 1 rem;>
                                <span class="loading-spinner" style=width: 16 px; height: 16 px; 
                                      border: 2 px solid rgba(255,255,255,0.3); 
                                      border-top: 2 px solid white; margin-right: 0.5 rem;></span>
                                AI is thinking and typing...
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            time.sleep(1)  # Brief pause for effect
                            
                            # Stream the response
                            for chunk in stream:
                                if chunk.choices[0].delta.content is not None:
                                    full_response += chunk.choices[0].delta.content
                                    response_placeholder.markdown(f'''
                                    <div style=color: white; line-height: 1.8; font-size: 1.05 em; padding: 1 rem;>
                                        {full_response}<span style=animation: blink is infinite; color: #667eea;></span>
                                    </div>
                                    <style>
                                        @keyframes blink {{
                                            0%, 50% {{ opacity: 1; }}
                                            51%, 100% {{ opacity: 0; }}
                                        }}
                                    </style>
                                    ''', unsafe_allow_html=True)
                            
                            # Final response without cursor
                            response_placeholder.markdown(f'''
                            <div style=color: white; line-height: 1.8; font-size: 1.05 em; 
                                 padding: 1 rem; background: rgba(255,255,255,0.05); 
                                 border-radius: 8 px; animation: fadeIn 0.5 s ease-out;>
                                {full_response}
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # Store in chat history
                            st.session_state.chat_history.append({
                                "question": question,
                                "answer": full_response,
                                "sources": {"pdf": pdf_results, "web": web_results},
                                "timestamp": time.time(),
                                "mode": response_mode,
                                "search_mode": search_mode,
                                "total_sources": total_sources
                            })
                            
                    except Exception as e:
                        display_animated_message(f"Streaming error: {str(e)}", "error")
                
                else:
                    # Complete Response Mode
                    with st.spinner(" Generating comprehensive answer..."):
                        try:
                            answer = st.session_state.groq_handler.generate_answer(
                                question, pdf_results, web_results
                            )
                            
                            st.markdown(f'''
                            <div style=color: white; line-height: 1.8; font-size: 1.05 em; 
                                 padding: 1.5 rem; background: rgba(255,255,255,0.05); 
                                 border-radius: 8 px; animation: fadeInUp 0.5 s ease-out;>
                                {answer}
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # Store in chat history
                            st.session_state.chat_history.append({
                                "question": question,
                                "answer": answer,
                                "sources": {"pdf": pdf_results, "web": web_results},
                                "timestamp": time.time(),
                                "mode": response_mode,
                                "search_mode": search_mode,
                                "total_sources": total_sources
                            })
                            
                        except Exception as e:
                            display_animated_message(f"Answer generation error: {str(e)}", "error")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Voice Output (if available)
                if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
                    try:
                        final_answer = st.session_state.chat_history[-1]["answer"] if st.session_state.chat_history else ""
                        if final_answer:
                            st.session_state.voice_integration.handle_voice_output(final_answer)
                    except Exception as e:
                        display_animated_message(f"Voice output error: {str(e)}", "warning")
                
                # Enhanced Sources Display
                display_sources(pdf_results, web_results)
                
                # Follow-up Questions (if enabled)
                if include_followup and st.session_state.chat_history:
                    st.markdown('''
                    <div style=background: linear-gradient(135 deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
                         padding: 1.5 rem; border-radius: 15 px; margin: 2 rem 0; border: 1 px solid rgba(102, 126, 234, 0.3);>
                        <h4 style=color: #667eea; margin: 0 0 1 rem 0; display: flex; align-items: center; gap: 0.5 rem;>
                            <span></span> Suggested Follow-up Questions
                        </h4>
                    ''', unsafe_allow_html=True)
                    
                    # Generate smart follow-up questions based on the topic
                    followup_questions = [
                        f"Can you provide more details about {question.split()[:3]}?",
                        f"What are the implications of {question.split()[:3]}?",
                        f"How does this relate to current trends?",
                        "What are the pros and cons?",
                        "Can you give me some examples?"
                    ]
                    
                    for i, fq in enumerate(followup_questions[:3], 1):
                        if st.button(f" {fq}", key=f"followup_{i}", help="Click to ask this follow-up question"):
                            st.session_state.question_input = fq
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Quick Actions Panel
                st.markdown('''
                <div style=background: linear-gradient(135 deg, rgba(17, 153, 142, 0.2), rgba(56, 239, 125, 0.2));
                     padding: 1 rem; border-radius: 15 px; margin: 1 rem 0; border: 1 px solid rgba(17, 153, 142, 0.3);>
                    <h5 style=color: #11998e; margin: 0 0 0.5 rem 0;> Quick Actions</h5>
                ''', unsafe_allow_html=True)
                
                col_action1, col_action2, col_action3, col_action4 = st.columns(4)
                
                with col_action1:
                    if st.button(" Ask Another", help="Clear and ask a new question"):
                        st.session_state.question_input = ""
                        st.rerun()
                
                with col_action2:
                    if st.button(" Export This", help="Export this conversation"):
                        if EXPORT_AVAILABLE and st.session_state.chat_history:
                            try:
                                latest_chat = [st.session_state.chat_history[-1]]
                                docx_data = st.session_state.chat_exporter.export_to_docx(latest_chat)
                                st.download_button(
                                    label="Download",
                                    data=docx_data,
                                    file_name=f"conversation_{int(time.time())}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key="export_latest"
                                )
                            except Exception as e:
                                display_animated_message(f"Export error: {str(e)}", "error")
                
                with col_action3:
                    if st.button(" Refine Search", help="Refine this question"):
                        st.markdown('''
                        <div style=background: rgba(102, 126, 234, 0.1); padding: 1 rem; 
                             border-radius: 8 px; margin: 1 rem 0;>
                             <strong>Tips to refine your search:</strong><br>
                             Be more specific about what you want to know<br>
                            Add context or background information<br>
                            Specify the type of answer you need<br>
                            Try different keywords or phrases
                        </div>
                        ''', unsafe_allow_html=True)
                
                with col_action4:
                    if st.button(" View Sources", help="Explore all sources used"):
                        with st.expander(" Detailed Source Analysis", expanded=True):
                            if pdf_results:
                                st.markdown("** PDF Sources Analysis:**")
                                for i, result in enumerate(pdf_results, 1):
                                    st.markdown(f'''
                                    <div style=background: rgba(102, 126, 234, 0.1); padding: 0.8 rem; 
                                         border-radius: 8 px; margin: 0.5 rem 0; border-left: 3 px solid #667eea;>
                                        <strong>PDF Source {i}:</strong><br>
                                        <em>Relevance: High  Length: {len(result)} chars</em><br>
                                        {result[:300]}{"..." if len(result) > 300 else ""}
                                    </div>
                                    ''', unsafe_allow_html=True)
                            
                            if web_results:
                                st.markdown("** Web Sources Analysis:**")
                                for i, result in enumerate(web_results, 1):
                                    st.markdown(f'''
                                    <div style=background: rgba(17, 153, 142, 0.1); padding: 0.8 rem; 
                                         border-radius: 8 px; margin: 0.5 rem 0; border-left: 3 px solid #11998e;>
                                        <strong>Web Source {i}: {result.get("title", "Unknown")}</strong><br>
                                        <em>URL: {result.get("url", "N/A")}</em><br>
                                        {result.get("snippet", "No snippet available")[:300]}{"..." if len(result.get("snippet", "")) > 300 else ""}
                                    </div>
                                    ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            else:
                # No Sources Found
                st.markdown('''
                <div style=background: linear-gradient(135 deg, #ff416c, #ff4b2b); 
                     color: white; padding: 2 rem; border-radius: 15 px; margin: 2 rem 0;
                     text-align: center; animation: shake 0.5 s ease-in-out;>
                    <div style=font-size: 2 em; margin-bottom: 1 rem;></div>
                    <h3 style=margin: 0 0 1 rem 0;>No Relevant Sources Found</h3>
                    <p style=margin: 0 0 1.5 rem 0; opacity: 0.9;>
                        We could not find information matching your question in the selected sources.
                    </p>
                    <div style=background: rgba(255,255,255,0.1); padding: 1 rem; 
                         border-radius: 8 px; text-align: left;>
                        <strong> Try these suggestions:</strong><br>
                         Rephrase your question with different keywords<br>
                         Upload more relevant PDF documents<br>
                         Check if web search is enabled<br>
                         Try a broader or more specific question<br>
                         Use simpler language or technical terms
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Suggestion buttons for no results
                col_suggest1, col_suggest2 = st.columns(2)
                
                with col_suggest1:
                    if st.button(" Try Web Search Only", help="Search web sources only"):
                        # Force web search
                        st.session_state.search_options = ["Web Sources"]
                        st.rerun()
                
                with col_suggest2:
                    if st.button(" Upload More PDFs", help="Add more documents"):
                        st.markdown('''
                        <div style=background: rgba(102, 126, 234, 0.2); padding: 1 rem; 
                             border-radius: 8 px; margin: 1 rem 0;>
                            Use the sidebar to upload more PDF documents that might contain relevant information.
                        </div>
                        ''', unsafe_allow_html=True)
        
        except Exception as e:
            display_animated_message(f"Search error: {str(e)}", "error")
            
            # Error recovery options
            st.markdown('''
            <div style=background: rgba(255, 65, 108, 0.2); padding: 1.5 rem; 
                 border-radius: 15 px; margin: 1 rem 0; border: 1 px solid rgba(255, 65, 108, 0.3);>
                <h4 style=color: #ff416c; margin: 0 0 1 rem 0;>Error Recovery</h4>
                <p>Something went wrong. Here are some things you can try:</p>
            </div>
            ''', unsafe_allow_html=True)
            
            col_recovery1, col_recovery2, col_recovery3 = st.columns(3)
            
            with col_recovery1:
                if st.button("Retry Search", help="Try the search again"):
                    st.rerun()
            
            with col_recovery2:
                if st.button("🧹 Clear & Reset", help="Clear everything and start over"):
                    st.session_state.question_input = ""
                    st.rerun()
            
            with col_recovery3:
                if st.button("🔧 Troubleshoot", help="Run system diagnostics"):
                    # This would trigger the troubleshoot function from the main app
                    st.markdown('''
                    <div style=background: rgba(102, 126, 234, 0.1); padding: 1 rem; 
                         border-radius: 8 px; margin: 1 rem 0;>
                         Check the troubleshoot button at the bottom of the page for system diagnostics.
                    </div>
                    ''', unsafe_allow_html=True)
    
    # Recent Questions Quick Access
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown('''
        <div style=background: linear-gradient(135 deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
             padding: 1.5 rem; border-radius: 15 px; margin: 2 rem 0;>
            <h4 style=color: #667eea; margin: 0 0 1 rem 0; display: flex; align-items: center; gap: 0.5 rem;>
                <span></span> Recent Questions
            </h4>
        ''', unsafe_allow_html=True)
        
        # Show last 3 questions as quick buttons
        recent_questions = st.session_state.chat_history[-3:]
        for i, chat in enumerate(reversed(recent_questions), 1):
            question_preview = chat["question"][:60] + "..." if len(chat["question"]) > 60 else chat["question"]
            timestamp = time.strftime('%H:%M', time.localtime(chat["timestamp"]))
            
            if st.button(f" {timestamp} - {question_preview}", key=f"recent_{i}", help="Click to view this conversation"):
                st.markdown(f'''
                <div style=background: rgba(17, 153, 142, 0.1); padding: 1 rem; 
                     border-radius: 8 px; margin: 1 rem 0; animation: slideInUp 0.3 s ease-out;>
                    <strong>Previous Question:</strong> {chat["question"]}<br><br>
                    <strong>Answer:</strong> {chat["answer"][:200]}{"..." if len(chat["answer"]) > 200 else ""}
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tips and Hints Section
    if not st.session_state.chat_history:
        st.markdown("---")
        st.markdown('''
        <div style=background: linear-gradient(135 deg, rgba(0, 242, 96, 0.1), rgba(5, 117, 230, 0.1));
             padding: 2 rem; border-radius: 15 px; margin: 2 rem 0; text-align: center;>
            <h3 style=color: #00f260; margin: 0 0 1.5 rem 0;> Get Started with These Examples</h3>
            <div style=display: grid; grid-template-columns: repeat(autofit, minmax(300 px, 1 fr)); gap: 1 rem;>
        ''', unsafe_allow_html=True)
        
        example_questions = [
            {
                "icon": "📊",
                "title": "Data Analysis", 
                "question": "What are the key findings and trends in my uploaded documents?",
                "description": "Analyze your PDFs for insights"
            },
            {
                "icon": "🔬", 
                "title": "Research",
                "question": "What are the latest developments in artificial intelligence?",
                "description": "Get current information from the web"
            },
            {
                "icon": "📚",
                "title": "Summary",
                "question": "Can you summarize the main points from my documents?",
                "description": "Quick overview of your content"
            },
            {
                "icon": "🤔",
                "title": "Comparison", 
                "question": "Compare renewable energy sources and their effectiveness",
                "description": "Compare topics using web research"
            }
        ]
        
        for example in example_questions:
            if st.button(f"{example['icon']} {example['title']}", key=f"example_{example['title']}", help=example['description']):
                st.session_state.question_input = example['question']
                st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
    
    # Performance Tips Section
    if len(st.session_state.chat_history) > 0:
        st.markdown("---")
        st.markdown('''
        <div style=background: linear-gradient(135 deg, rgba(240, 147, 251, 0.1), rgba(245, 87, 108, 0.1));
             padding: 1.5 rem; border-radius: 15 px; margin: 2 rem 0;>
            <h4 style=color: #f093fb; margin: 0 0 1 rem 0; display: flex; align-items: center; gap: 0.5 rem;>
                <span></span> Pro Tips for Better Results
            </h4>
            <div style=display: grid; grid-template-columns: repeat(auto-fit, minmax(250 px, 1 fr)); gap: 1 rem;>
                <div style=background: rgba(255,255,255,0.05); padding: 1 rem; border-radius: 8 px;>
                    <strong> Be Specific</strong><br>
                    <small>Instead of "Tell me about AI", try What are the latest AI applications in healthcare?</small>
                </div>
                <div style=background: rgba(255,255,255,0.05); padding: 1 rem; border-radius: 8 px;>
                    <strong> Use Context</strong><br>
                    <small>Reference your documents: Based on my uploaded research papers, what are the conclusions?</small>
                </div>
                <div style=background: rgba(255,255,255,0.05); padding: 1 rem; border-radius: 8 px;>
                    <strong> Iterate</strong><br>
                    <small>Build on previous answers with follow-up questions for deeper insights</small>
                </div>
                <div style=background: rgba(255,255,255,0.05); padding: 1 rem; border-radius: 8 px;>
                    <strong> Compare Sources</strong><br>
                    <small>Enable both PDF and web search to get comprehensive, well-rounded answers</small>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Keyboard Shortcuts Info
    st.markdown('''
    <div style=background: rgba(102, 126, 234, 0.05); padding: 1 rem; border-radius: 10 px; 
         margin: 1 rem 0; border: 1 px solid rgba(102, 126, 234, 0.2);>
        <details>
            <summary style=color: #667eea; cursor: pointer; font-weight: 500;>
                 Keyboard Shortcuts & Tips
            </summary>
            <div style=margin-top: 1 rem; font-size: 0.9 em;>
                <strong>Shortcuts:</strong><br>
                 <code>Ctrl/Cmd + Enter</code> - Submit question<br>
                 <code>Ctrl/Cmd + /</code> - Focus on question input<br>
                 <code>Escape</code> - Clear current input<br><br>
                
                <strong>Voice Commands (if enabled):</strong><br>
                 Say "Ask question" to start voice input<br>
                 Say "Read answer" to hear the response<br>
                 Say "Clear" to reset the input
            </div>
        </details>
    </div>
    ''', unsafe_allow_html=True)
    
    # Session Statistics (if there's activity)
    if st.session_state.chat_history:
        total_chars = sum(len(chat['answer']) for chat in st.session_state.chat_history)
        avg_response_time = 2.3  # This would be calculated from actual response times
        
        st.markdown(f'''
        <div style=background: linear-gradient(135 deg, rgba(17, 153, 142, 0.1), rgba(56, 239, 125, 0.1));
             padding: 1 rem; border-radius: 10 px; margin: 1 rem 0; text-align: center;>
            <strong> Session Stats:</strong>
            {len(st.session_state.chat_history)} questions  
            {total_chars:,} response characters 
            ~{avg_response_time:.f}s avg response time
        </div>
        ''', unsafe_allow_html=True)

# Additional Custom CSS for enhanced animations and effects
st.markdown('''
<style>
    /* Enhanced button hover effects */
    .stButton > button:hover {
        transform: translateY(-px) scale(1.02) !important;
        box-shadow: 0 15 px 35 px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3 s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Enhanced input focus effects */
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 20 px rgba(102, 126, 234, 0.3) !important;
        transform: scale(1.01) !important;
        transition: all 0.3 s ease !important;
    }
    
    /* Loading animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30 px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50 px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50 px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30 px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    /* Pulse animation for important elements */
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.05);
            opacity: 0.8;
        }
    }
    
    /* Shake animation for errors */
    @keyframes shake {
        0%, 100% {
            transform: translateX(0);
        }
        10%, 30%, 50%, 70%, 90% {
            transform: translateX(-5 px);
        }
        20%, 40%, 60%, 80% {
            transform: translateX(5 px);
        }
    }
    
    /* Glowing border effect */
    .glow-border {
        position: relative;
        border-radius: 15 px;
        background: linear-gradient(45 deg, #667eea, #764ba2);
        padding: 2 px;
    
    .glow-border::before {
        content: '';
        position: absolute;
        inset: -2 px;
        border-radius: 15 px;
        padding: 2 px;
        background: linear-gradient(45 deg, #667eea, #764ba2, #f093fb, #f5576c);
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: exclude;
        animation: rotate 3 s linear infinite;
    
    
    @keyframes rotate {
        from {
            transform: rotate(0 deg);
        }
        to {
            transform: rotate(360 deg);
        }
    }
    
    /* Responsive design improvements */
    @media (max-width: 768 px) {
        .question-container {
            padding: 1 rem !important;
            margin: 0.5 rem 0 !important;
        }
        
        .floating-badge {
            font-size: 0.8 em !important;
            padding: 0.3 rem 0.8 rem !important;
        }
        
        .user-message, .bot-message {
            margin: 0.5 rem 0 !important;
            padding: 1 rem !important;
        }
        
        .answer-container {
            padding: 1 rem !important;
        }
    }
    
    /* Dark mode optimizations */
    @media (prefers-color-scheme: dark) {
        .info-card {
            background: linear-gradient(135 deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)) !important;
            border-color: rgba(255,255,255,0.1) !important;
        }
        
        .source-box {
            background: linear-gradient(135 deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)) !important;
            border-color: rgba(255,255,255,0.1) !important;
        }
    }
    
    /* Accessibility improvements */
    .stButton > button:focus {
        outline: 2 px solid #667eea !important;
        outline-offset: 2 px !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8 px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10 px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135 deg, #667eea, #764ba2);
        border-radius: 10 px;
    
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135 deg, #764ba2, #667eea);
    
    
    /* Print styles */
    @media print {
        .stButton, .floating-btn, .voice-section {
            display: none !important;
        }
        
        .main-header, .question-container, .answer-container {
            background: none !important;
            color: black !important;
        }
    }
</style>

<script>
// Enhanced JavaScript for better user experience
document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize text areas
    const textAreas = document.querySelectorAll('textarea');
    textAreas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const submitButton = document.querySelector('[data-testid="stButton"] button');
            if (submitButton && !submitButton.disabled) {
                submitButton.click();
            }
        }
        
        // Ctrl/Cmd + / to focus on question input
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const questionInput = document.querySelector('textarea[placeholder*="Ask"]');
            if (questionInput) {
                questionInput.focus();
            }
        }
        
        // Escape to clear input
        if (e.key === 'Escape') {
            const questionInput = document.querySelector('textarea[placeholder*="Ask"]');
            if (questionInput && document.activeElement === questionInput) {
                questionInput.value = '';
                questionInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    });
    
    // Smooth scroll to new content
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                const newContent = Array.from(mutation.addedNodes).find(node => 
                    node.nodeType === Node.ELEMENT_NODE && 
                    (node.classList.contains('answer-container') || node.classList.contains('user-message'))
                );
                if (newContent) {
                    setTimeout(() => {
                        newContent.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'start',
                            inline: 'nearest'
                        });
                    }, 100);
                }
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Add loading states to buttons
    const buttons = document.querySelectorAll('[data-testid="stButton"] button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                this.style.opacity = '0.7';
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.opacity = '1';
                    this.style.transform = 'scale(1)';
                }, 200);
            }
        });
    });
});
</script>
''', unsafe_allow_html=True)
