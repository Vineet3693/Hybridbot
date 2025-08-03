
import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import re
from typing import List
import streamlit as st
import io

class PDFProcessor:
    def __init__(self):
        self.text_chunks = []
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            # Reset file pointer
            pdf_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
            
            # If text is mostly empty, try OCR
            if len(text.strip()) < 100:
                st.info("PDF appears to be scanned. Using OCR...")
                text = self.extract_text_with_ocr(pdf_file)
            
            return text.strip()
        except Exception as e:
            st.error(f"Error extracting text: {str(e)}")
            return ""
    
    def extract_text_with_ocr(self, pdf_file) -> str:
        """Extract text using OCR for scanned PDFs"""
        try:
            pdf_file.seek(0)
            # Convert PDF to images
            images = convert_from_bytes(pdf_file.read(), dpi=200)
            text = ""
            
            progress_bar = st.progress(0)
            for i, image in enumerate(images):
                # Update progress
                progress_bar.progress((i + 1) / len(images))
                
                # Extract text from each page image
                page_text = pytesseract.image_to_string(image, lang='eng')
                text += page_text + "\n"
            
            progress_bar.empty()
            return text.strip()
        except Exception as e:
            st.error(f"OCR extraction failed: {str(e)}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks for better processing"""
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        if not text:
            return []
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk + sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_text_preview(self, text: str, max_length: int = 200) -> str:
        """Get a preview of the extracted text"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
