
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
    page_title="Hybrid AI Bot with Groq",
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
    .stAlert > div {
        padding: 0.5rem;
        margin: 0.25rem 0;
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
            st.warning(f"Voice features disabled: {e}")
    
    # Export utilities (conditional)
    if EXPORT_AVAILABLE and 'chat_exporter' not in st.session_state:
        try:
            st.session_state.chat_exporter = ChatExporter()
        except Exception as e:
            st.warning(f"Export features disabled: {e}")

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
                    
                    st.success(f"✅ Processed: {uploaded_file.name} ({len(chunks)} chunks)")
                else:
                    st.error(f"❌ Failed to process: {uploaded_file.name}")
            
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        
        progress_bar.empty()
        
        # Add to vector store
        if all_chunks:
            try:
                st.session_state.vector_store.add_texts(all_chunks)
                st.session_state.pdf_processed = True
                st.session_state.pdf_files_info = processed_files
                st.success(f"🎉 Successfully processed {len(uploaded_files)} PDFs with {len(all_chunks)} text chunks!")
            except Exception as e:
                st.error(f"Error adding to vector store: {str(e)}")

def search_sources(question: str, search_options: List[str]):
    """Search both PDF and web sources"""
    pdf_results = []
    web_results = []
    
    try:
        # Search PDF content
        if st.session_state.pdf_processed and "PDF Content" in search_options:
            pdf_search_results = st.session_state.vector_store.search(question, k=3)
            pdf_results = [text for text, score in pdf_search_results if score > 0.3]
        
        # Search web
        if "Web Sources" in search_options:
            web_results = st.session_state.web_searcher.search_multiple_sources(question, max_results=3)
    
    except Exception as e:
        st.error(f"Search error: {str(e)}")
    
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

def export_chat_history():
    """Handle chat history export in multiple formats"""
    if not EXPORT_AVAILABLE:
        st.warning("Export features require additional packages")
        return
    
    if not st.session_state.chat_history:
        st.warning("No chat history to export")
        return
    
    # Export options
    col_export1, col_export2, col_export3, col_export4 = st.columns(4)
    
    with col_export1:
        if st.button("📄 Export as DOCX"):
            try:
                docx_data = st.session_state.chat_exporter.export_to_docx(st.session_state.chat_history)
                st.download_button(
                    label="📥 Download DOCX",
                    data=docx_data,
                    file_name=f"chat_history_{int(time.time())}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                st.success("✅ DOCX file ready for download!")
            except Exception as e:
                st.error(f"Error creating DOCX: {str(e)}")
    
    with col_export2:
        if st.button("📕 Export as PDF"):
            try:
                pdf_data = st.session_state.chat_exporter.export_to_pdf_reportlab(st.session_state.chat_history)
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_data,
                    file_name=f"chat_history_{int(time.time())}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ PDF file ready for download!")
            except Exception as e:
                try:
                    pdf_data = st.session_state.chat_exporter.export_to_pdf_fpdf(st.session_state.chat_history)
                    st.download_button(
                        label="📥 Download Simple PDF",
                        data=pdf_data,
                        file_name=f"chat_history_simple_{int(time.time())}.pdf",
                        mime="application/pdf"
                    )
                    st.info("📋 Using simple PDF format")
                except Exception as e2:
                    st.error(f"PDF export failed: {str(e2)}")
    
    with col_export3:
        if st.button("📝 Export as Markdown"):
            try:
                md_data = st.session_state.chat_exporter.export_to_markdown(st.session_state.chat_history)
                st.download_button(
                    label="📥 Download MD",
                    data=md_data,
                    file_name=f"chat_history_{int(time.time())}.md",
                    mime="text/markdown"
                )
                st.success("✅ Markdown file ready for download!")
            except Exception as e:
                st.error(f"Error creating Markdown: {str(e)}")
    
    with col_export4:
        if st.button("🗂️ Export as JSON"):
            try:
                chat_json = json.dumps(st.session_state.chat_history, indent=2, default=str)
                st.download_button(
                    label="📥 Download JSON",
                    data=chat_json,
                    file_name=f"chat_history_{int(time.time())}.json",
                    mime="application/json"
                )
                st.success("✅ JSON file ready for download!")
            except Exception as e:
                st.error(f"Error creating JSON: {str(e)}")
    
    # Export all formats at once
    st.markdown("---")
    if st.button("📦 Export All Formats", type="secondary", use_container_width=True):
        try:
            timestamp = int(time.time())
            
            with st.spinner("📦 Preparing all export formats..."):
                progress = st.progress(0)
                
                # DOCX
                docx_data = st.session_state.chat_exporter.export_to_docx(st.session_state.chat_history)
                progress.progress(25)
                
                # PDF
                try:
                    pdf_data = st.session_state.chat_exporter.export_to_pdf_reportlab(st.session_state.chat_history)
                except:
                    pdf_data = st.session_state.chat_exporter.export_to_pdf_fpdf(st.session_state.chat_history)
                progress.progress(50)
                
                # Markdown
                md_data = st.session_state.chat_exporter.export_to_markdown(st.session_state.chat_history)
                progress.progress(75)
                
                # JSON
                json_data = json.dumps(st.session_state.chat_history, indent=2, default=str)
                progress.progress(100)
                
                progress.empty()
                
                # Show download buttons
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.download_button("📄 DOCX", docx_data, f"chat_history_{timestamp}.docx", 
                                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                
                with col2:
                    st.download_button("📕 PDF", pdf_data, f"chat_history_{timestamp}.pdf", "application/pdf")
                
                with col3:
                    st.download_button("📝 MD", md_data, f"chat_history_{timestamp}.md", "text/markdown")
                
                with col4:
                    st.download_button("🗂️ JSON", json_data, f"chat_history_{timestamp}.json", "application/json")
                
                st.success("🎉 All formats ready for download!")
                
        except Exception as e:
            st.error(f"Error preparing exports: {str(e)}")

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
        help="Choose between fast (8B) or powerful (70B) Llama3 models"
    )
    selected_model = AVAILABLE_MODELS[selected_model_name]
    
    # Show model info
    if "8b" in selected_model.lower():
        st.info("🚀 **Llama3 8B**: Fast responses, good for most tasks")
    else:
        st.info("💪 **Llama3 70B**: Most powerful, best for complex tasks")
    
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
    
    st.markdown("---")
    
    # Model Status Check
    col_status1, col_status2 = st.columns(2)
    
    with col_status1:
        if st.button("🔍 Check Models", help="Test which models are currently working"):
            try:
                working_models = st.session_state.groq_handler.get_available_models()
                if working_models:
                    st.session_state.working_models = working_models
                else:
                    st.error("❌ No models available")
            except Exception as e:
                st.error(f"Model check error: {str(e)}")
    
    with col_status2:
        if st.button("🔄 Auto-Select", help="Automatically select a working model"):
            try:
                working_model = st.session_state.groq_handler.auto_select_working_model()
                st.session_state.groq_handler.model = working_model
                st.rerun()
            except Exception as e:
                st.error(f"Auto-select error: {str(e)}")
    
    st.markdown("---")
    
    # Voice Controls Section (if available)
    if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
        try:
            st.session_state.voice_integration.render_voice_sidebar()
        except Exception as e:
            st.warning(f"Voice controls error: {str(e)}")
    elif not VOICE_AVAILABLE:
        st.header("🎤 Voice Features")
        st.info("Voice features require additional packages:")
        st.code("pip install speechrecognition pyttsx3 gtts pygame pyaudio")
        st.markdown("Install these packages to enable voice chat!")
    
    st.markdown("---")
    
    # Status section
    st.header("📊 Status")
    if st.session_state.pdf_processed:
        st.success("✅ PDFs processed")
        try:
            vector_stats = st.session_state.vector_store.get_stats()
            st.info(f"📄 {vector_stats['total_texts']} text chunks available")
        except Exception as e:
            st.warning(f"Stats error: {str(e)}")
        
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
        try:
            if st.session_state.groq_handler.test_connection():
                st.success("✅ Groq API connected!")
            else:
                st.error("❌ Groq API connection failed")
        except Exception as e:
            st.error(f"Connection test error: {str(e)}")
    
    st.markdown("---")
    
    # Clear data option
    if st.button("🗑️ Clear All Data", help="Clear processed PDFs and chat history"):
        try:
            st.session_state.vector_store = VectorStore()
            st.session_state.pdf_processed = False
            st.session_state.chat_history = []
            st.session_state.pdf_files_info = []
            st.success("✅ All data cleared!")
            st.rerun()
        except Exception as e:
            st.error(f"Clear data error: {str(e)}")

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.header("💬 Ask Questions")
    
    # Voice input section (if available)
    voice_question = ""
    if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
        try:
            voice_question = st.session_state.voice_integration.handle_voice_input()
        except Exception as e:
            st.warning(f"Voice input error: {str(e)}")
    
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
            try:
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
                                            response_placeholder.markdown(full_response + "▌")
                                    
                                    response_placeholder.markdown(full_response)
                                    
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
                                            st.warning(f"Voice output error: {str(e)}")
                                    
                                except Exception as e:
                                    st.error(f"Streaming error: {str(e)}")
                        except Exception as e:
                            st.error(f"Streaming initialization error: {str(e)}")
                    else:
                        # Complete response
                        with st.spinner("🧠 Generating answer with Groq..."):
                            try:
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
                                
                                # Voice output (if available)
                                if VOICE_AVAILABLE and hasattr(st.session_state, 'voice_integration'):
                                    try:
                                        st.session_state.voice_integration.handle_voice_output(answer)
                                    except Exception as e:
                                        st.warning(f"Voice output error: {str(e)}")
                                        
                            except Exception as e:
                                st.error(f"Answer generation error: {str(e)}")
                    
                    # Display sources
                    display_sources(pdf_results, web_results)
                    
                else:
                    st.warning("⚠️ No relevant sources found. Try different search terms or upload relevant PDFs.")
            
            except Exception as e:
                st.error(f"Search error: {str(e)}")

with col2:
    st.header("ℹ️ How to Use")
    st.markdown("""
    ### 📋 Quick Guide:
    1. **Upload PDFs** in the sidebar
    2. **Click "Process PDFs"** to extract text
    3. **Choose AI model** (8B for speed, 70B for power)
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
    - 📤 **Export chat history**
    """)
    
    if VOICE_AVAILABLE:
        st.markdown("- 🎤 **Voice input/output**")
    
    st.markdown("""
    ### 🤖 Available Models:
    - **Llama3 8B**: Fast responses (8192 tokens)
    - **Llama3 70B**: Most powerful (8192 tokens)
    
    ### 💡 Model Recommendations:
    - **For quick questions**: Use Llama3 8B
    - **For complex analysis**: Use Llama3 70B
    - **For long documents**: Use Llama3 70B
    """)
    
    # Model info
    try:
        current_model = st.session_state.groq_handler.model
        model_display = "Llama3 8B" if "8b" in current_model else "Llama3 70B"
        st.info(f"🤖 Current Model: {model_display}")
    except Exception as e:
        st.warning(f"Model info error: {str(e)}")

# Chat History Section
if st.session_state.chat_history:
    st.markdown("---")
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
    
    # Show conversations
    for i, chat in enumerate(display_chats):
        chat_index = len(st.session_state.chat_history) - i if reverse_order else i + 1
        
        with st.expander(f"💬 Conversation {chat_index}: {chat['question'][:50]}..." if len(chat['question']) > 50 else f"💬 Conversation {chat_index}: {chat['question']}"):
            # Question and Answer
            st.markdown(f"**❓ Question:** {chat['question']}")
            st.markdown(f"**🤖 Answer:** {chat['answer']}")
            
            # Show sources if enabled
            if show_sources:
                sources = chat.get('sources', {})
                if sources.get('pdf') or sources.get('web'):
                    st.markdown("**📚 Sources:**")
                    
                    if sources.get('pdf'):
                        st.write(f"📄 **PDF sources:** {len(sources['pdf'])} documents")
                        for j, pdf_source in enumerate(sources['pdf'][:2], 1):
                            st.write(f"  • PDF {j}: {pdf_source[:100]}...")
                    
                    if sources.get('web'):
                        st.write(f"🌐 **Web sources:** {len(sources['web'])} results")
                        for j, web_source in enumerate(sources['web'][:2], 1):
                            st.write(f"  • {web_source['title']}: {web_source['snippet'][:100]}...")
            
            # Timestamp and actions
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(chat['timestamp']))
            
            col_time, col_actions = st.columns([2, 1])
            with col_time:
                st.caption(f"🕒 {timestamp}")
            
            with col_actions:
                # Individual export for this conversation (if available)
                if EXPORT_AVAILABLE and hasattr(st.session_state, 'chat_exporter'):
                    if st.button(f"📤 Export", key=f"export_{chat_index}"):
                        try:
                            single_chat = [chat]
                            docx_data = st.session_state.chat_exporter.export_to_docx(single_chat)
                            
                            st.download_button(
                                label="📥 Download Conversation",
                                data=docx_data,
                                file_name=f"conversation_{chat_index}_{int(chat['timestamp'])}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"download_{chat_index}"
                            )
                        except Exception as e:
                            st.error(f"Export error: {str(e)}")

# Footer
st.markdown("---")

# Feature status indicator
feature_status = []
if st.session_state.pdf_processed:
    feature_status.append("📄 PDFs Loaded")
if st.session_state.chat_history:
    feature_status.append(f"💬 {len(st.session_state.chat_history)} Conversations")
if VOICE_AVAILABLE:
    feature_status.append("🎤 Voice Enabled")
if EXPORT_AVAILABLE:
    feature_status.append("📤 Export Enabled")

if feature_status:
    st.info(" • ".join(feature_status))

st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🤖 <strong>Hybrid AI Bot</strong> - Built with ❤️ using Streamlit, Groq API, FAISS, and open-source AI tools</p>
    <p>🔧 <strong>Tech Stack:</strong> Streamlit • Groq • FAISS • Sentence Transformers • PyPDF2 • Tesseract OCR</p>
    <p>🌟 <strong>Features:</strong> PDF Processing • Web Search • Voice Chat • Multi-format Export • Semantic Search</p>
</div>
""", unsafe_allow_html=True)

# Error handling and recovery
if st.button("🔧 Troubleshoot Issues", help="Reset components if something isn't working"):
    try:
        # Re-initialize components
        st.session_state.groq_handler = GroqHandler()
        st.session_state.vector_store = VectorStore()
        st.session_state.web_searcher = WebSearcher()
        st.session_state.pdf_processor = PDFProcessor()
        
        # Test connections
        connection_status = []
        
        try:
            if st.session_state.groq_handler.test_connection():
                connection_status.append("✅ Groq API")
            else:
                connection_status.append("❌ Groq API")
        except:
            connection_status.append("❌ Groq API")
        
        try:
            test_search = st.session_state.web_searcher.search_multiple_sources("test", max_results=1)
            if test_search:
                connection_status.append("✅ Web Search")
            else:
                connection_status.append("⚠️ Web Search")
        except:
            connection_status.append("❌ Web Search")
        
        if st.session_state.pdf_processed:
            connection_status.append("✅ PDF Processing")
        else:
            connection_status.append("⚠️ No PDFs loaded")
        
        st.success("🔧 Troubleshooting complete!")
        st.info("System Status: " + " • ".join(connection_status))
        
    except Exception as e:
        st.error(f"Troubleshooting error: {str(e)}")

# Debug information (only show if there are errors)
if st.checkbox("🐛 Show Debug Info", help="Show technical details for troubleshooting"):
    with st.expander("Debug Information"):
        st.write("**Session State Variables:**")
        debug_info = {
            "PDF Processed": st.session_state.pdf_processed,
            "Chat History Count": len(st.session_state.chat_history),
            "PDF Files Info": len(st.session_state.pdf_files_info),
            "Voice Available": VOICE_AVAILABLE,
            "Export Available": EXPORT_AVAILABLE,
            "Current Model": getattr(st.session_state.groq_handler, 'model', 'Not set')
        }
        
        for key, value in debug_info.items():
            st.write(f"- **{key}**: {value}")
        
        st.write("**Environment Info:**")
        st.write(f"- Python packages status:")
        
        packages_status = []
        
        # Check core packages
        try:
            import streamlit
            packages_status.append(f"✅ Streamlit: {streamlit.__version__}")
        except:
            packages_status.append("❌ Streamlit: Not available")
        
        try:
            import groq
            packages_status.append("✅ Groq: Available")
        except:
            packages_status.append("❌ Groq: Not available")
        
        try:
            import faiss
            packages_status.append("✅ FAISS: Available")
        except:
            packages_status.append("❌ FAISS: Not available")
        
        try:
            import sentence_transformers
            packages_status.append("✅ Sentence Transformers: Available")
        except:
            packages_status.append("❌ Sentence Transformers: Not available")
        
        # Voice packages
        try:
            import speech_recognition
            packages_status.append("✅ Speech Recognition: Available")
        except:
            packages_status.append("❌ Speech Recognition: Not available")
        
        try:
            import pyttsx3
            packages_status.append("✅ pyttsx3: Available")
        except:
            packages_status.append("❌ pyttsx3: Not available")
        
        # Export packages
        try:
            from docx import Document
            packages_status.append("✅ python-docx: Available")
        except:
            packages_status.append("❌ python-docx: Not available")
        
        try:
            from reportlab.platypus import SimpleDocTemplate
            packages_status.append("✅ ReportLab: Available")
        except:
            packages_status.append("❌ ReportLab: Not available")
        
        for status in packages_status:
            st.write(f"  {status}")

# Quick actions sidebar
with st.sidebar:
    st.markdown("---")
    st.header("⚡ Quick Actions")
    
    if st.button("🚀 Quick Start Guide"):
        st.info("""
        **Getting Started:**
        1. Upload a PDF file above
        2. Click 'Process PDFs'
        3. Ask a question in the main area
        4. Choose your preferred AI model
        5. Enable voice features if available
        
        **Pro Tips:**
        - Use Llama3 8B for fast responses
        - Use Llama3 70B for complex questions
        - Enable both PDF and Web search for best results
        - Export your conversations for later reference
        """)
    
    if st.session_state.chat_history:
        if st.button("📊 Chat Statistics"):
            total_questions = len(st.session_state.chat_history)
            total_chars = sum(len(chat['answer']) for chat in st.session_state.chat_history)
            avg_chars = total_chars // total_questions if total_questions > 0 else 0
            
            st.success(f"""
            **Chat Statistics:**
            - Total conversations: {total_questions}
            - Total response characters: {total_chars:,}
            - Average response length: {avg_chars} chars
            - Latest conversation: {time.strftime('%Y-%m-%d %H:%M', time.localtime(st.session_state.chat_history[-1]['timestamp']))}
            """)
    
    if st.button("💡 Feature Tips"):
        st.info("""
        **Advanced Features:**
        
        🎤 **Voice Chat:**
        - Click microphone button to speak
        - AI responses can be read aloud
        - Multiple language support
        
        📄 **PDF Processing:**
        - Supports text-based and scanned PDFs
        - Automatic text chunking for better search
        - OCR for image-based documents
        
        🌐 **Web Search:**
        - Real-time internet search
        - Multiple search engines
        - Source attribution
        
        📤 **Export Options:**
        - DOCX for professional documents
        - PDF for sharing
        - Markdown for documentation
        - JSON for data analysis
        """)

# Performance monitoring (optional)
if hasattr(st.session_state, 'performance_metrics'):
    with st.expander("📈 Performance Metrics"):
        metrics = st.session_state.performance_metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg Response Time", f"{metrics.get('avg_response_time', 0):.1f}s")
        with col2:
            st.metric("PDF Processing Time", f"{metrics.get('pdf_process_time', 0):.1f}s")
        with col3:
            st.metric("Search Accuracy", f"{metrics.get('search_accuracy', 95)}%")
        with col4:
            st.metric("Success Rate", f"{metrics.get('success_rate', 98)}%")

# Auto-save functionality (optional)
if st.session_state.chat_history and len(st.session_state.chat_history) % 5 == 0:
    # Auto-save every 5 conversations
    try:
        auto_save_data = {
            'chat_history': st.session_state.chat_history,
            'timestamp': time.time(),
            'session_id': st.session_state.get('session_id', 'unknown')
        }
        # This could be saved to a database or file in a real deployment
        st.session_state.last_auto_save = time.time()
    except Exception as e:
        pass  # Silent auto-save failure

# End of app.py
