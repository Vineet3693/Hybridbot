
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
# Page configuration
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
