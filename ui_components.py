
import streamlit as st
import time
from typing import List, Dict

def load_custom_css():
    """Load all custom CSS styles and animations"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        .main { font-family: 'Poppins', sans-serif; }
        
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
        
        /* Question Container */
        .question-container {
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            animation: pulseGlow 2s infinite alternate;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
            position: relative;
        }
        
        @keyframes pulseGlow {
            0% { box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3); }
            100% { box-shadow: 0 8px 32px rgba(102, 126, 234, 0.6), 0 0 20px rgba(102, 126, 234, 0.4); }
        }
        
        /* Status Messages */
        .status-success {
            background: linear-gradient(135deg, #00f260, #0575e6);
            color: white;
            padding: 0.8rem 1rem;
            border-radius: 10px;
            display: inline-block;
            margin: 0.5rem 0;
            animation: slideInUp 0.5s ease-out;
        }
        
        .status-warning {
            background: linear-gradient(135deg, #f093fb, #f5576c);
            color: white;
            padding: 0.8rem 1rem;
            border-radius: 10px;
            display: inline-block;
            margin: 0.5rem 0;
            animation: slideInUp 0.5s ease-out;
        }
        
        .status-error {
            background: linear-gradient(135deg, #ff416c, #ff4b2b);
            color: white;
            padding: 0.8rem 1rem;
            border-radius: 10px;
            display: inline-block;
            margin: 0.5rem 0;
            animation: shake 0.5s ease-in-out;
        }
        
        /* Animations */
        @keyframes slideInUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        /* Chat Messages */
        .user-message {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-left: 5px solid #ff6b6b;
            margin-left: 2rem;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            animation: fadeInUp 0.6s ease-out;
        }
        
        .bot-message {
            background: linear-gradient(135deg, #11998e, #38ef7d);
            color: white;
            border-left: 5px solid #feca57;
            margin-right: 2rem;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            animation: fadeInUp 0.6s ease-out;
        }
        
        @keyframes fadeInUp {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        /* Source Boxes */
        .source-box {
            background: linear-gradient(135deg, #e7f3ff, #f8fdff);
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border: 2px solid #b3d9ff;
            transition: all 0.3s ease;
            animation: slideInRight 0.5s ease-out;
        }
        
        .source-box:hover {
            transform: scale(1.02);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
        }
        
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        /* Floating Badges */
        .floating-badge {
            background: linear-gradient(45deg, rgba(255,255,255,0.2), rgba(255,255,255,0.1));
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.3);
            animation: floatBadge 3s ease-in-out infinite alternate;
            backdrop-filter: blur(10px);
            display: inline-block;
            margin: 0.25rem;
        }
        
        @keyframes floatBadge {
            0% { transform: translateY(0px); }
            100% { transform: translateY(-5px); }
        }
        
        /* Loading Spinner */
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Glow Text */
        .glow-text {
            color: white;
            text-shadow: 0 0 10px #667eea, 0 0 20px #667eea, 0 0 30px #667eea;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 10px #667eea, 0 0 20px #667eea, 0 0 30px #667eea; }
            to { text-shadow: 0 0 20px #667eea, 0 0 30px #667eea, 0 0 40px #667eea; }
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 0.5rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
            background: linear-gradient(135deg, #764ba2, #667eea) !important;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .question-container, .user-message, .bot-message {
                margin-left: 0.5rem !important;
                margin-right: 0.5rem !important;
                padding: 1rem !important;
            }
            
            .floating-badge {
                font-size: 0.8em !important;
                padding: 0.3rem 0.8rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def display_animated_message(message: str, message_type: str = "info"):
    """Display animated status messages"""
    if message_type == "success":
        st.markdown(f'<div class="status-success">✅ {message}</div>', unsafe_allow_html=True)
    elif message_type == "error":
        st.markdown(f'<div class="status-error">❌ {message}</div>', unsafe_allow_html=True)
    elif message_type == "warning":
        st.markdown(f'<div class="status-warning">⚠️ {message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-success">ℹ️ {message}</div>', unsafe_allow_html=True)

def render_main_header():
    """Render the animated main header"""
    st.markdown('''
    <div class="main-header">
        <h1 class="glow-text">🤖 HybridBot Pro - AI Assistant</h1>
        <p>🚀 Powered by Groq API - Extract data from PDFs and search the web for intelligent answers</p>
        <div style="margin-top: 1rem;">
            <span class="floating-badge">⚡ Ultra Fast</span>
            <span class="floating-badge">🧠 AI Powered</span>
            <span class="floating-badge">🔍 Smart Search</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_question_section():
    """Render the question input section"""
    st.markdown('''
    <div class="question-container">
        <div style="text-align: center;">
            <h1 class="glow-text" style="font-size: 2.5em; margin-bottom: 0.5rem;">💬 Ask Anything</h1>
            <p style="color: white; font-size: 1.2em; opacity: 0.9; margin-bottom: 1rem;">
                🚀 Get intelligent answers from your documents and the web
            </p>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <span class="floating-badge">📄 PDF Analysis</span>
                <span class="floating-badge">🌐 Web Search</span>
                <span class="floating-badge">🧠 AI Powered</span>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_voice_section(voice_question: str = ""):
    """Render voice input section if available"""
    if voice_question:
        st.markdown(f'''
        <div style="background: linear-gradient(135deg, #00f260, #0575e6);
             color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;
             animation: slideInRight 0.5s ease-out;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5em;">🎤</span>
                <strong>Voice Detected:</strong>
            </div>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1em;">{voice_question}</p>
        </div>
        ''', unsafe_allow_html=True)

def render_input_validation(question: str):
    """Render input validation feedback"""
    if question:
        char_count = len(question)
        word_count = len(question.split())
        
        if char_count < 10:
            feedback_type = "warning"
            feedback_msg = f"⚠️ Very short question ({char_count} chars, {word_count} words) - Consider adding more details"
        elif char_count < 30:
            feedback_type = "info"
            feedback_msg = f"💡 Short question ({char_count} chars, {word_count} words) - More context could help"
        elif char_count > 500:
            feedback_type = "warning"
            feedback_msg = f"📝 Long question ({char_count} chars, {word_count} words) - Consider breaking it down"
        else:
            feedback_type = "success"
            feedback_msg = f"✅ Great question length ({char_count} chars, {word_count} words)"
        
        display_animated_message(feedback_msg, feedback_type)
        
        # Show keywords for longer questions
        if char_count > 20:
            question_keywords = question.lower().split()[:5]
            st.markdown(f'''
            <div style="background: rgba(102, 126, 234, 0.1); padding: 0.8rem; 
                 border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #667eea;">
                <small><strong>🔍 Detected keywords:</strong> {", ".join([f"#{word}" for word in question_keywords if len(word) > 3])}</small>
            </div>
            ''', unsafe_allow_html=True)

def render_search_progress(step: int, total: int, message: str):
    """Render search progress with animation"""
    progress = (step / total) * 100
    st.markdown(f'''
    <div style="background: rgba(102, 126, 234, 0.2); padding: 0.8rem; 
         border-radius: 8px; border-left: 3px solid #667eea; animation: pulse 1s infinite;">
        <span class="loading-spinner" style="margin-right: 0.5rem;"></span>
        <strong>{message}</strong>
    </div>
    
    ''', unsafe_allow_html=True)

def render_user_question(question: str):
    """Render user question with animation"""
    st.markdown(f'''
    <div class="user-message" style="animation: slideInLeft 0.5s ease-out;">
        <div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem;">
            <div style="background: linear-gradient(45deg, #667eea, #764ba2); 
                 padding: 8px; border-radius: 50%; color: white; font-size: 1.2em;">❓</div>
            <h3 style="margin: 0; color: white;">Your Question</h3>
        </div>
        <div style="font-size: 1.1em; line-height: 1.6; color: white; 
             background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
            {question}
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_ai_response_header(total_sources: int):
    """Render AI response header"""
    st.markdown(f'''
    <div class="answer-container" style="animation: slideInLeft 0.5s ease-out;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
            <div style="background: linear-gradient(45deg, #11998e, #38ef7d); 
                 padding: 12px; border-radius: 50%; color: white; font-size: 1.5em;">🤖</div>
            <div>
                <h2 style="margin: 0; color: white;">AI Assistant</h2>
                <p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 0.9em;">
                    Powered by Groq • Processing {total_sources} sources
                </p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

def render_streaming_response(text: str, is_complete: bool = False):
    """Render streaming response with typing animation"""
    if is_complete:
        st.markdown(f'''
        <div style="color: white; line-height: 1.8; font-size: 1.05em; 
             padding: 1rem; background: rgba(255,255,255,0.05); 
             border-radius: 8px; animation: fadeIn 0.5s ease-out;">
            {text}
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div style="color: white; line-height: 1.8; font-size: 1.05em; padding: 1rem;">
            {text}<span style="animation: blink 1s infinite; color: #667eea;">▌</span>
        </div>
        <style>
            @keyframes blink {{
                0%, 50% {{ opacity: 1; }}
                51%, 100% {{ opacity: 0; }}
            }}
        </style>
        ''', unsafe_allow_html=True)

def render_search_results_summary(pdf_count: int, web_count: int):
    """Render search results summary"""
    total_sources = pdf_count + web_count
    if total_sources > 0:
        st.markdown(f'''
        <div style="background: linear-gradient(135deg, #00f260, #0575e6); 
             color: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;
             text-align: center; animation: slideInUp 0.5s ease-out;">
            <div style="font-size: 1.3em; margin-bottom: 0.5rem;">
                🎯 <strong>Search Complete!</strong>
            </div>
            <div style="font-size: 1.1em;">
                Found <strong>{total_sources} relevant sources</strong>
                {f" • {pdf_count} from PDFs" if pdf_count else ""}
                {f" • {web_count} from web" if web_count else ""}
            </div>
        </div>
        ''', unsafe_allow_html=True)

def render_no_results_message():
    """Render no results found message"""
    st.markdown('''
    <div style="background: linear-gradient(135deg, #ff416c, #ff4b2b); 
         color: white; padding: 2rem; border-radius: 15px; margin: 2rem 0;
         text-align: center; animation: shake 0.5s ease-in-out;">
        <div style="font-size: 2em; margin-bottom: 1rem;">🔍</div>
        <h3 style="margin: 0 0 1rem 0;">No Relevant Sources Found</h3>
        <p style="margin: 0 0 1.5rem 0; opacity: 0.9;">
            We couldn't find information matching your question in the selected sources.
        </p>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; 
             border-radius: 8px; text-align: left;">
            <strong>💡 Try these suggestions:</strong><br>
            • Rephrase your question with different keywords<br>
            • Upload more relevant PDF documents<br>
            • Check if web search is enabled<br>
            • Try a broader or more specific question<br>
            • Use simpler language or technical terms
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_follow_up_questions(base_question: str):
    """Render follow-up question suggestions"""
    st.markdown('''
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
         padding: 1.5rem; border-radius: 15px; margin: 2rem 0; border: 1px solid rgba(102, 126, 234, 0.3);">
        <h4 style="color: #667eea; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            <span>💡</span> Suggested Follow-up Questions
        </h4>
    ''', unsafe_allow_html=True)
    
    # Generate smart follow-up questions
    base_words = base_question.split()[:3]
    followup_questions = [
        f"Can you provide more details about {' '.join(base_words)}?",
        f"What are the implications of {' '.join(base_words)}?",
        "What are the pros and cons?",
        "Can you give me some examples?",
        "How does this relate to current trends?"
    ]
    
    return followup_questions[:3]  # Return first 3 suggestions

def render_quick_actions():
    """Render quick action buttons"""
    st.markdown('''
    <div style="background: linear-gradient(135deg, rgba(17, 153, 142, 0.2), rgba(56, 239, 125, 0.2));
         padding: 1rem; border-radius: 15px; margin: 1rem 0; border: 1px solid rgba(17, 153, 142, 0.3);">
        <h5 style="color: #11998e; margin: 0 0 0.5rem 0;">⚡ Quick Actions</h5>
    </div>
    ''', unsafe_allow_html=True)

def render_example_questions():
    """Render example questions for new users"""
    st.markdown('''
    <div style="background: linear-gradient(135deg, rgba(0, 242, 96, 0.1), rgba(5, 117, 230, 0.1));
         padding: 2rem; border-radius: 15px; margin: 2rem 0; text-align: center;">
        <h3 style="color: #00f260; margin: 0 0 1.5rem 0;">🌟 Get Started with These Examples</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
    </div>
    ''', unsafe_allow_html=True)
    
    return [
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

def render_pro_tips():
    """Render pro tips section"""
    st.markdown('''
    <div style="background: linear-gradient(135deg, rgba(240, 147, 251, 0.1), rgba(245, 87, 108, 0.1));
         padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h4 style="color: #f093fb; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            <span>💡</span> Pro Tips for Better Results
        </h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
                <strong>🎯 Be Specific</strong><br>
                <small>Instead of "Tell me about AI", try "What are the latest AI applications in healthcare?"</small>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
                <strong>📖 Use Context</strong><br>
                <small>Reference your documents: "Based on my uploaded research papers, what are the conclusions?"</small>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
                <strong>🔄 Iterate</strong><br>
                <small>Build on previous answers with follow-up questions for deeper insights</small>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
                <strong>⚖️ Compare Sources</strong><br>
                <small>Enable both PDF and web search to get comprehensive, well-rounded answers</small>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_session_stats(chat_count: int, total_chars: int, avg_response_time: float = 2.3):
    """Render session statistics"""
    st.markdown(f'''
    <div style="background: linear-gradient(135deg, rgba(17, 153, 142, 0.1), rgba(56, 239, 125, 0.1));
         padding: 1rem; border-radius: 10px; margin: 1rem 0; text-align: center;">
        <strong>📊 Session Stats:</strong>
        {chat_count} questions • 
        {total_chars:,} response characters • 
        ~{avg_response_time:.1f}s avg response time
    </div>
    ''', unsafe_allow_html=True)

def render_recent_questions_section():
    """Render recent questions section header"""
    st.markdown('''
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
         padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h4 style="color: #667eea; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            <span>⏱️</span> Recent Questions
        </h4>
    </div>
    ''', unsafe_allow_html=True)

def render_recent_question_preview(question: str, answer: str, timestamp: float):
    """Render a preview of a recent question"""
    time_str = time.strftime('%H:%M', time.localtime(timestamp))
    question_preview = question[:60] + "..." if len(question) > 60 else question
    answer_preview = answer[:200] + "..." if len(answer) > 200 else answer
    
    return time_str, question_preview, answer_preview

def render_conversation_preview(question: str, answer: str):
    """Render conversation preview when clicked"""
    st.markdown(f'''
    <div style="background: rgba(17, 153, 142, 0.1); padding: 1rem; 
         border-radius: 8px; margin: 1rem 0; animation: slideInUp 0.3s ease-out;">
        <strong>Previous Question:</strong> {question}<br><br>
        <strong>Answer:</strong> {answer}
    </div>
    ''', unsafe_allow_html=True)

def close_ui_container():
    """Close UI container divs"""
    st.markdown('</div>', unsafe_allow_html=True)
