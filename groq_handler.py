
from groq import Groq
import streamlit as st
from typing import List, Dict, Optional
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS, TEMPERATURE

class GroqHandler:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        if not self.api_key:
            st.error("⚠️ Groq API key not found!")
            st.stop()
        
        try:
            self.client = Groq(api_key=self.api_key)
            self.model = GROQ_MODEL
            self.max_tokens = MAX_TOKENS
            self.temperature = TEMPERATURE
        except Exception as e:
            st.error(f"Error initializing Groq client: {str(e)}")
            st.stop()
    
    def test_connection(self) -> bool:
        """Test if Groq API is working"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model=self.model,
                max_tokens=10
            )
            return True
        except Exception as e:
            st.error(f"Groq API connection failed: {str(e)}")
            return False
    
    # ADD THESE NEW METHODS HERE ⬇️
    def validate_model(self, model: str) -> bool:
        """Validate if the model is available and working"""
        try:
            # Test with a simple query
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "Test"}],
                model=model,
                max_tokens=5
            )
            return True
        except Exception as e:
            # Don't show error in UI, just return False
            return False
    
    def get_available_models(self) -> dict:
        """Get list of actually working models"""
        working_models = {}
        
        # Test only the Llama3 models that should be working
        test_models = {
            "Llama3 8B (Fast & Efficient)": "llama3-8b-8192",
            "Llama3 70B (Most Powerful)": "llama3-70b-8192"
        }
        
        progress_bar = st.progress(0)
        st.info("🔍 Testing model availability...")
        
        for i, (name, model_id) in enumerate(test_models.items()):
            progress_bar.progress((i + 1) / len(test_models))
            
            if self.validate_model(model_id):
                working_models[name] = model_id
                st.success(f"✅ {name} - Available")
            else:
                st.warning(f"❌ {name} - Not available")
        
        progress_bar.empty()
        return working_models
    
    def auto_select_working_model(self) -> str:
        """Automatically select a working model"""
        test_models = ["llama3-8b-8192", "llama3-70b-8192"]
        
        for model in test_models:
            if self.validate_model(model):
                st.success(f"✅ Auto-selected working model: {model}")
                return model
        
        st.error("❌ No working models found!")
        return "llama3-8b-8192"  # Fallback
    # ADD THESE NEW METHODS HERE ⬆️
    
    def generate_answer(self, question: str, pdf_context: List[str] = None, web_context: List[Dict] = None) -> str:
        """Generate comprehensive answer using Groq API"""
        
        # Build context from PDF and web sources
        context_parts = []
        
        if pdf_context:
            context_parts.append("=== INFORMATION FROM PDF DOCUMENTS ===")
            for i, text in enumerate(pdf_context, 1):
                context_parts.append(f"PDF Source {i}: {text}")
        
        if web_context:
            context_parts.append("\n=== INFORMATION FROM WEB SOURCES ===")
            for i, result in enumerate(web_context, 1):
                context_parts.append(f"Web Source {i} - {result['title']}: {result['snippet']}")
                if result.get('url'):
                    context_parts.append(f"URL: {result['url']}")
        
        context = "\n".join(context_parts)
        
        # Create system prompt
        system_prompt = """You are a helpful AI assistant that answers questions based on provided context from PDF documents and web sources. 

Instructions:
1. Use the provided context to answer the question accurately
2. If information comes from PDFs, mention "According to the PDF documents..."
3. If information comes from web sources, mention "According to web sources..."
4. If you use both sources, clearly distinguish between them
5. If the context doesn't contain enough information, say so and provide what you can
6. Be concise but comprehensive
7. Always cite your sources when possible
8. Format your response clearly with proper sections if needed"""

        # Create user prompt
        if context:
            user_prompt = f"""Context Information:
{context}

Question: {question}

Please provide a comprehensive answer based on the available context."""
        else:
            user_prompt = f"""Question: {question}

Please provide a helpful answer to this question. Since no specific context is provided, use your general knowledge but mention that the answer is based on general knowledge."""

        try:
            # Make API call to Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=False
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            # If current model fails, try to auto-select working model
            if "model" in str(e).lower() or "not found" in str(e).lower():
                st.warning(f"Model {self.model} failed, trying to find working model...")
                working_model = self.auto_select_working_model()
                if working_model != self.model:
                    self.model = working_model
                    return self.generate_answer(question, pdf_context, web_context)
            
            st.error(f"Groq API Error: {str(e)}")
            return "Sorry, I encountered an error while generating the response. The model might be temporarily unavailable. Please try again or switch to a different model."
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize long text using Groq"""
        if len(text) <= max_length:
            return text
        
        prompt = f"""Please summarize the following text in about {max_length} characters while keeping the key information:

{text}

Summary:"""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=100,
                temperature=0.3,
                stream=False
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            return text[:max_length] + "..."
    
    def stream_response(self, question: str, pdf_context: List[str] = None, web_context: List[Dict] = None):
        """Stream response from Groq API for real-time display"""
        
        # Build context (same as generate_answer)
        context_parts = []
        
        if pdf_context:
            context_parts.append("=== INFORMATION FROM PDF DOCUMENTS ===")
            for i, text in enumerate(pdf_context, 1):
                context_parts.append(f"PDF Source {i}: {text}")
        
        if web_context:
            context_parts.append("\n=== INFORMATION FROM WEB SOURCES ===")
            for i, result in enumerate(web_context, 1):
                context_parts.append(f"Web Source {i} - {result['title']}: {result['snippet']}")
                if result.get('url'):
                    context_parts.append(f"URL: {result['url']}")
        
        context = "\n".join(context_parts)
        
        system_prompt = """You are a helpful AI assistant that answers questions based on provided context from PDF documents and web sources. 

Instructions:
1. Use the provided context to answer the question accurately
2. If information comes from PDFs, mention "According to the PDF documents..."
3. If information comes from web sources, mention "According to web sources..."
4. If you use both sources, clearly distinguish between them
5. If the context doesn't contain enough information, say so and provide what you can
6. Be concise but comprehensive
7. Always cite your sources when possible
8. Format your response clearly with proper sections if needed"""

        if context:
            user_prompt = f"""Context Information:
{context}

Question: {question}

Please provide a comprehensive answer based on the available context."""
        else:
            user_prompt = f"""Question: {question}

Please provide a helpful answer to this question. Since no specific context is provided, use your general knowledge but mention that the answer is based on general knowledge."""

        try:
            # Stream response
            stream = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            return stream
            
        except Exception as e:
            # If current model fails, try to auto-select working model
            if "model" in str(e).lower() or "not found" in str(e).lower():
                st.warning(f"Model {self.model} failed, trying to find working model...")
                working_model = self.auto_select_working_model()
                if working_model != self.model:
                    self.model = working_model
                    return self.stream_response(question, pdf_context, web_context)
            
            st.error(f"Groq API Error: {str(e)}")
            return None
    
    def update_settings(self, model: str = None, temperature: float = None, max_tokens: int = None):
        """Update Groq settings"""
        if model:
            # Validate model before setting it
            if self.validate_model(model):
                self.model = model
                st.success(f"✅ Model updated to: {model}")
            else:
                st.error(f"❌ Model {model} is not available. Keeping current model: {self.model}")
        
        if temperature is not None:
            self.temperature = temperature
        if max_tokens:
            self.max_tokens = max_tokens
