
import streamlit as st
import os
from pdf_processor import PDFProcessor
from web_search import WebSearcher
from vector_store import VectorStore
from groq_handler import GroqHandler
from config import AVAILABLE_MODELS, GROQ_API_KEY
from typing import List, Dict
import time
import json

import streamlit as st
from streamlit_lottie import st_lottie
import requests

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
from streamlit_lottie import st_lottie
import requests

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Professional tabs
tab1, tab2, tab3, tab4 = st.tabs(["📄 Documents", "💬 Chat", "🔍 Search", "📊 Analytics"])

with tab1:
    st.markdown("### 📁 Document Management Hub")
    uploaded_files = st.file_uploader(
        "Drop your files here or click to browse",
        accept_multiple_files=True,
        type=['pdf'],
        help="Supported formats: PDF (up to 200MB each)"
    )

with tab2:
    st.markdown("### 💬 Intelligent Conversation")
    # Your chat interface here

with tab3:
    st.markdown("### 🔍 Advanced Search")
    # Search interface

with tab4:
    st.markdown("### 📊 Usage Analytics")
    # Analytics dashboard
# Professional header with icons
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 class="glow-text">🚀 DocuMind AI Pro</h1>
    <p style="font-size: 1.2rem; color: #8b949e;">
        Advanced Document Intelligence & Web Search Platform
    </p>
    <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;">
        <span class="status-good">⚡ Groq Powered</span>
        <span class="status-info">🧠 AI Enhanced</span>
        <span class="status-warning">🔒 Secure</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Professional sidebar
with st.sidebar:
    st.markdown('<h2 class="glow-text">⚙️ Control Panel</h2>', unsafe_allow_html=True)
    
    # Model selection with icons
    st.markdown("### 🤖 AI Configuration")
    model = st.selectbox(
        "Select Model:",
        options=["llama3-70b-8192", "mixtral-8x7b-32768", "llama3-8b-8192"],
        format_func=lambda x: f"🧠 {x.replace('-', ' ').title()}"
    )
    
    # Enhanced sliders
    st.markdown("### 🎛️ Parameters")
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider("🌡️ Creativity", 0.0, 1.0, 0.7)
    with col2:
        max_tokens = st.slider("📏 Response Length", 100, 2000, 1000)

# Professional metrics display
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📊 Status", "Active", delta="Online")
with col2:
    st.metric("🗂️ Documents", "0", delta="Ready")
with col3:
    st.metric("🧠 Model", "Llama3-70B", delta="Optimal")
with col4:
    st.metric("⚡ Speed", "Fast", delta="Real-time")

# Custom CSS for dark professional theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 50%, #0d1117 100%);
        color: #ffffff;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
        border-right: 2px solid #30363d;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff !important;
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.3);
    }
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        background: rgba(22, 27, 34, 0.8) !important;
        border: 2px solid #30363d !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.3) !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(45deg, #238636, #2ea043) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(46, 160, 67, 0.3) !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(45deg, #2ea043, #56d364) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(46, 160, 67, 0.4) !important;
    }
    
    /* Selectbox */
    .stSelectbox select {
        background: rgba(22, 27, 34, 0.8) !important;
        border: 2px solid #30363d !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    /* Sliders */
    .stSlider .css-1cpxqw2 {
        background: linear-gradient(90deg, #f85149, #ff7b72, #58a6ff) !important;
    }
    
    /* Cards/containers */
    .stContainer, .element-container {
        background: rgba(22, 27, 34, 0.6) !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Success messages */
    .stSuccess {
        background: rgba(35, 134, 54, 0.2) !important;
        border: 1px solid #238636 !important;
        border-radius: 8px !important;
        color: #56d364 !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background: rgba(22, 27, 34, 0.8) !important;
        border: 2px dashed #58a6ff !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        text-align: center !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        margin: 0.5rem 0 !important;
        padding: 1rem !important;
    }
    
    /* Metrics */
    .metric-container {
        background: linear-gradient(135deg, #161b22, #0d1117) !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Custom glow effects */
    .glow-text {
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.5);
        color: #58a6ff;
    }
    
    /* Status indicators */
    .status-good { color: #56d364; }
    .status-warning { color: #f85149; }
    .status-info { color: #58a6ff; }
    
    /* Animations */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)


# Now your line 14 should work
lottie_ai = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_x62chJ.json")
# Lottie animation: AI robot (change URL for other animations)
lottie_ai = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_x62chJ.json")



st.markdown("""
<style>
    .main-header {
        border-radius: 16px;
        background: rgba(102,126,234,0.82);
        box-shadow: 0 8px 32px 0 rgba(31,38,135,0.13);
        backdrop-filter: blur(4px);
        color: white;
        padding: 2rem 0 1rem 0;
        margin-bottom: 2rem;
        font-size: 2.3rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeInDown 1s;
    }
    .chat-message {
        background: rgba(255,255,255,0.75);
        box-shadow: 0 2px 8px 0 rgba(102,126,234,0.09);
        border-left: 5px solid #764ba2;
        margin: 1rem 0;
        padding: 1.2rem;
        border-radius: 14px;
        transition: box-shadow 0.3s;
    }
    .chat-message:hover {
        box-shadow: 0 4px 16px 0 rgba(102,126,234,0.16);
    }
    .source-box {
        background: rgba(231,243,255,0.8);
        border: 1.5px solid #b3d9ff;
        margin-top: 0.5rem;
        border-radius: 8px;
        padding: 0.7rem;
        font-size: 0.95rem;
        transition: background 0.2s;
    }
    .source-box:hover {
        background: #e0e7ff;
    }
    @keyframes fadeInDown {
      0% { opacity: 0; transform: translateY(-24px);}
      100% { opacity: 1; transform: translateY(0);}
    }
</style>
""", unsafe_allow_html=True)
# Animated RGB header with Lottie
st.markdown('<div class="rgb-header">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 6])
with col1:
    st_lottie(lottie_ai, height=70, key="ai-robot")
with col2:
    st.markdown('<div class="rgb-title">DocuMind AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="rgb-subtitle">Made by Vineet; Talk to documents and search the web for intelligent answers</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)




st.markdown("""
<style>
    .main-header {
        border-radius: 16px;
        background: rgba(102,126,234,0.82);
        box-shadow: 0 8px 32px 0 rgba(31,38,135,0.13);
        backdrop-filter: blur(4px);
        color: white;
        padding: 2rem 0 1rem 0;
        margin-bottom: 2rem;
        font-size: 2.3rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeInDown 1s;
    }
    .chat-message {
        background: rgba(255,255,255,0.75);
        box-shadow: 0 2px 8px 0 rgba(102,126,234,0.09);
        border-left: 5px solid #764ba2;
        margin: 1rem 0;
        padding: 1.2rem;
        border-radius: 14px;
        transition: box-shadow 0.3s;
    }
    .chat-message:hover {
        box-shadow: 0 4px 16px 0 rgba(102,126,234,0.16);
    }
    .source-box {
        background: rgba(231,243,255,0.8);
        border: 1.5px solid #b3d9ff;
        margin-top: 0.5rem;
        border-radius: 8px;
        padding: 0.7rem;
        font-size: 0.95rem;
        transition: background 0.2s;
    }
    .source-box:hover {
        background: #e0e7ff;
    }
    @keyframes fadeInDown {
      0% { opacity: 0; transform: translateY(-24px);}
      100% { opacity: 1; transform: translateY(0);}
    }
</style>
""", unsafe_allow_html=True)
# Page configuration
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
    }
    .source-box {
        background-color: #e7f3ff;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border: 1px solid #b3d9ff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
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

initialize_session_state()

def process_pdfs(uploaded_files):
    """Process uploaded PDF files"""
    with st.spinner("🔄 Processing PDFs..."):
        all_chunks = []
        processed_files = []
        
        progress_bar = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))
            
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
                
                st.success(f"✅ Processed: {uploaded_file.name} ({len(chunks)} chunks)")
            else:
                st.error(f"❌ Failed to process: {uploaded_file.name}")
        
        progress_bar.empty()
        
        # Add to vector store
        if all_chunks:
            st.session_state.vector_store.add_texts(all_chunks)
            st.session_state.pdf_processed = True
            st.session_state.pdf_files_info = processed_files
            st.success(f"🎉 Successfully processed {len(uploaded_files)} PDFs with {len(all_chunks)} text chunks!")

def search_sources(question: str, search_options: List[str]):
    """Search both PDF and web sources"""
    pdf_results = []
    web_results = []
    
    # Search PDF content
    if st.session_state.pdf_processed and "PDF Content" in search_options:
        pdf_search_results = st.session_state.vector_store.search(question, k=3)
        pdf_results = [text for text, score in pdf_search_results if score > 0.3]
    
    # Search web
    if "Web Sources" in search_options:
        web_results = st.session_state.web_searcher.search_multiple_sources(question, max_results=3)
    
    return pdf_results, web_results

def display_sources(pdf_results: List[str], web_results: List[Dict]):
    """Display the sources used for the answer"""
    if pdf_results or web_results:
        with st.expander("📚 Sources Used", expanded=False):
            if pdf_results:
                st.markdown("**PDF Sources:**")
                for i, text in enumerate(pdf_results, 1):
                    st.markdown(f'<div class="source-box">📄 PDF Source {i}: {text[:200]}...</div>', unsafe_allow_html=True)
            
            if web_results:
                st.markdown("**Web Sources:**")
                for i, result in enumerate(web_results, 1):
                    url_display = f" - [Link]({result['url']})" if result.get('url') else ""
                    st.markdown(f'<div class="source-box">🌐 {result["title"]}: {result["snippet"][:150]}...{url_display}</div>', unsafe_allow_html=True)

# Main UI
st.markdown('<div class="main-header"><h1>🤖 Hybrid AI Bot with Groq</h1><p>Powered by Groq API - Extract data from PDFs and search the web for intelligent answers</p></div>', unsafe_allow_html=True)

# Sidebar for PDF upload and settings
with st.sidebar:
    st.header("📚 Document Management")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type="pdf",
        accept_multiple_files=True,
        help="Upload PDF documents to create a knowledge base"
    )
    
    if uploaded_files:
        if st.button("🔄 Process PDFs", type="primary"):
            process_pdfs(uploaded_files)
        
        # Show file details
        if uploaded_files:
            st.markdown("**Files selected:**")
            for file in uploaded_files:
                st.write(f"📄 {file.name} ({file.size} bytes)")
    
    st.markdown("---")
    
    # Groq Model Settings
    st.header("🧠 AI Settings")
    
    # Model selection
    selected_model_name = st.selectbox(
        "Choose Groq Model:",
        list(AVAILABLE_MODELS.keys()),
        help="Different models have different capabilities and speeds"
    )
    selected_model = AVAILABLE_MODELS[selected_model_name]
    
    # Response settings
    temperature = st.slider(
        "Temperature (Creativity):", 
        0.0, 1.0, 0.7, 0.1,
        help="Higher values make responses more creative but less focused"
    )
    max_tokens = st.slider(
        "Max Response Length:", 
        100, 2000, 1000, 100,
        help="Maximum number of tokens in the response"
    )
    
    # Update Groq settings
    st.session_state.groq_handler.update_settings(
        model=selected_model,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    st.markdown("---")
    
    # Status section
    st.header("📊 Status")
    if st.session_state.pdf_processed:
        st.success("✅ PDFs processed")
        vector_stats = st.session_state.vector_store.get_stats()
        st.info(f"📄 {vector_stats['total_texts']} text chunks available")
        
        # Show processed files
        if st.session_state.pdf_files_info:
            with st.expander("📁 Processed Files"):
                for file_info in st.session_state.pdf_files_info:
                    st.write(f"**{file_info['name']}**")
                    st.write(f"- Chunks: {file_info['chunks']}")
                    st.write(f"- Size: {file_info['size']} characters")
                    st.write(f"- Preview: {file_info['preview']}")
                    st.write("---")
    else:
        st.warning("⏳ No PDFs processed yet")
    
    # API Status
    if st.button("🔍 Test Groq Connection"):
        if st.session_state.groq_handler.test_connection():
            st.success("✅ Groq API connected!")
        else:
            st.error("❌ Groq API connection failed")
    
    st.markdown("---")
    
    # Clear data option
    if st.button("🗑️ Clear All Data", help="Clear processed PDFs and chat history"):
        st.session_state.vector_store = VectorStore()
        st.session_state.pdf_processed = False
        st.session_state.chat_history = []
        st.session_state.pdf_files_info = []
        st.success("✅ All data cleared!")
        st.rerun()

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.header("💬 Ask Questions")
    
    # Question input
    question = st.text_input(
        "What would you like to know?",
        placeholder="Ask anything about your PDFs or general knowledge...",
        key="question_input",
        help="Type your question here. The AI will search both your PDFs and the web for answers."
    )
    
    # Search and response options
    col_a, col_b = st.columns(2)
    with col_a:
        search_options = st.multiselect(
            "Search in:",
            ["PDF Content", "Web Sources"],
            default=["PDF Content", "Web Sources"] if st.session_state.pdf_processed else ["Web Sources"],
            help="Choose where to search for information"
        )
    
    with col_b:
        response_mode = st.radio(
            "Response Mode:",
            ["Complete", "Streaming"],
            horizontal=True,
            help="Complete: Get full response at once. Streaming: See response as it's generated"
        )
    
    # Ask button
    if st.button("🔍 Get Answer", type="primary", use_container_width=True) and question:
        if not search_options:
            st.warning("⚠️ Please select at least one search option!")
        else:
            # Search for sources
            with st.spinner("🔍 Searching sources..."):
                pdf_results, web_results = search_sources(question, search_options)
            
            # Show search results summary
            results_summary = []
            if pdf_results:
                results_summary.append(f"📄 {len(pdf_results)} PDF sources")
            if web_results:
                results_summary.append(f"🌐 {len(web_results)} web sources")
            
            if results_summary:
                st.info(f"Found: {', '.join(results_summary)}")
            
            # Generate answer with Groq
            if pdf_results or web_results or "Web Sources" in search_options:
                st.markdown("### 🤖 AI Answer")
                
                if response_mode == "Streaming":
                    # Streaming response
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
                                    response_placeholder.markdown(full_response + "▌")
                            
                            response_placeholder.markdown(full_response)
                            
                            # Add to chat history
                            st.session_state.chat_history.append({
                                "question": question,
                                "answer": full_response,
                                "sources": {"pdf": pdf_results, "web": web_results},
                                "timestamp": time.time()
                            })
                            
                        except Exception as e:
                            st.error(f"Streaming error: {str(e)}")
                else:
                    # Complete response
                    with st.spinner("🧠 Generating answer with Groq..."):
                        answer = st.session_state.groq_handler.generate_answer(
                            question, pdf_results, web_results
                        )
                        st.markdown(answer)
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": answer,
                            "sources": {"pdf": pdf_results, "web": web_results},
                            "timestamp": time.time()
                        })
                
                # Display sources
                display_sources(pdf_results, web_results)
                
            else:
                st.warning("⚠️ No relevant sources found. Try different search terms or upload relevant PDFs.")

with col2:
    st.header("ℹ️ How to Use")
    st.markdown("""
    ### 📋 Quick Guide:
    1. **Upload PDFs** in the sidebar
    2. **Click "Process PDFs"** to extract text
    3. **Choose AI model** and settings
    4. **Ask questions** in the main area
    5. **Select search sources** (PDF/Web)
    6. **Get intelligent answers**!
    
    ### ✨ Features:
    - 📄 **PDF text extraction**
    - 🔍 **OCR for scanned documents**  
    - 🌐 **Web search integration**
    - 🧠 **Semantic search**
    - 💬 **Natural language Q&A**
    - ⚡ **Groq-powered responses**
    - 🎯 **Source citations**
    
    ### 🎛️ Models Available:
    - **Mixtral 8x7B** (Recommended)
    - **Llama3 70B** (Most powerful)
    - **Llama3 8B** (Fast)
    - **Gemma 7B** (Efficient)
    """)
    
    # Model info
    current_model = st.session_state.groq_handler.model
    st.info(f"🤖 Current Model: {current_model}")

# Chat History Section
if st.session_state.chat_history:
    st.markdown("---")
    st.header("📜 Chat History")
    
    # Show recent conversations
    for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
        with st.expander(f"Q: {chat['question'][:50]}..." if len(chat['question']) > 50 else f"Q: {chat['question']}"):
            st.markdown(f"**Question:** {chat['question']}")
            st.markdown(f"**Answer:** {chat['answer']}")
            
            # Show sources if available
            sources = chat.get('sources', {})
            if sources.get('pdf') or sources.get('web'):
                st.markdown("**Sources:**")
                if sources.get('pdf'):
                    st.write(f"📄 PDF sources: {len(sources['pdf'])}")
                if sources.get('web'):
                    st.write(f"🌐 Web sources: {len(sources['web'])}")
            
            # Timestamp
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(chat['timestamp']))
            st.caption(f"🕒 {timestamp}")
    
    # Export chat history
    if st.button("💾 Export Chat History"):
        chat_json = json.dumps(st.session_state.chat_history, indent=2, default=str)
        st.download_button(
            label="📥 Download JSON",
            data=chat_json,
            file_name=f"chat_history_{int(time.time())}.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 <strong>Hybrid AI Bot</strong> - Built with ❤️ using Streamlit, Groq API, FAISS, and open-source AI tools</p>
    <p>🔧 <strong>Tech Stack:</strong> Streamlit • Groq • FAISS • Sentence Transformers • PyPDF2 • Tesseract OCR</p>
</div>
""", unsafe_allow_html=True)
