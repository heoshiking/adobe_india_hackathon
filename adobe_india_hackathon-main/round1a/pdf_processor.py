"""
PDF Processing Module
Handles PDF parsing, text extraction, and coordinate with other components.
"""

import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

from title_extractor import TitleExtractor
from heading_detector import HeadingDetector
from ocr_handler import OCRHandler
from config import Config

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Main PDF processing class that orchestrates text extraction and analysis."""
    
    def __init__(self, config: Config):
        self.config = config
        self.title_extractor = TitleExtractor(config)
        self.heading_detector = HeadingDetector(config)
        self.ocr_handler = OCRHandler(config)
        
    def extract_outline(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract complete outline from PDF including title and headings.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing title and outline structure
        """
        try:
            # Try native PDF extraction first
            doc_info = self._extract_native_pdf(pdf_path)
            
            # If native extraction fails or yields poor results, try OCR
            if self._needs_ocr(doc_info):
                logger.info(f"Attempting OCR extraction for {pdf_path.name}")
                ocr_info = self._extract_with_ocr(pdf_path)
                if ocr_info:
                    doc_info = ocr_info
            
            # Extract title from first page
            title = self.title_extractor.extract_title(doc_info['pages'][0])
            
            # Detect headings across all pages
            headings = self.heading_detector.detect_headings(doc_info['pages'])
            
            return {
                "title": title,
                "outline": headings
            }
            
        except Exception as e:
            logger.error(f"Error extracting outline from {pdf_path}: {str(e)}")
            raise
    
    def _extract_native_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text and layout information from native PDF."""
        doc_info = {
            'pages': [],
            'total_pages': 0
        }
        
        # Use PyMuPDF for primary extraction
        try:
            doc = fitz.open(str(pdf_path))
            doc_info['total_pages'] = len(doc)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text blocks with detailed formatting
                blocks = page.get_text("dict")
                
                page_info = {
                    'page_number': page_num + 1,
                    'text_blocks': [],
                    'raw_text': page.get_text()
                }
                
                # Process text blocks
                for block in blocks.get('blocks', []):
                    if 'lines' in block:
                        for line in block['lines']:
                            for span in line['spans']:
                                text_block = {
                                    'text': span['text'].strip(),
                                    'font': span['font'],
                                    'size': span['size'],
                                    'flags': span['flags'],  # Bold, italic flags
                                    'bbox': span['bbox'],    # Bounding box
                                    'color': span.get('color', 0)
                                }
                                
                                if text_block['text']:
                                    page_info['text_blocks'].append(text_block)
                
                doc_info['pages'].append(page_info)
            
            doc.close()
            return doc_info
            
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {str(e)}")
            
        # Fallback to pdfplumber
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                doc_info['total_pages'] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    chars = page.chars
                    
                    page_info = {
                        'page_number': page_num + 1,
                        'text_blocks': [],
                        'raw_text': page.extract_text() or ""
                    }
                    
                    # Group characters into text blocks
                    current_block = None
                    for char in chars:
                        if char['text'].strip():
                            if (current_block is None or 
                                abs(char['size'] - current_block['size']) > 0.1 or
                                abs(char['top'] - current_block['bbox'][1]) > 2):
                                
                                if current_block:
                                    page_info['text_blocks'].append(current_block)
                                
                                current_block = {
                                    'text': char['text'],
                                    'font': char.get('fontname', 'unknown'),
                                    'size': char['size'],
                                    'flags': 0,  # pdfplumber doesn't provide flags directly
                                    'bbox': [char['x0'], char['top'], char['x1'], char['bottom']],
                                    'color': 0
                                }
                            else:
                                current_block['text'] += char['text']
                                # Extend bounding box
                                current_block['bbox'][2] = char['x1']
                    
                    if current_block:
                        page_info['text_blocks'].append(current_block)
                    
                    doc_info['pages'].append(page_info)
                
                return doc_info
                
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            raise
    
    def _extract_with_ocr(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """Extract text using OCR for scanned PDFs."""
        try:
            return self.ocr_handler.extract_text(pdf_path)
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return None
    
    def _needs_ocr(self, doc_info: Dict[str, Any]) -> bool:
        """Determine if OCR is needed based on extraction quality."""
        if not doc_info or not doc_info.get('pages'):
            return True
        
        # Check if we have sufficient text content
        total_text = sum(
            len(page.get('raw_text', '').strip()) 
            for page in doc_info['pages']
        )
        
        # If very little text was extracted, likely a scanned PDF
        if total_text < self.config.MIN_TEXT_LENGTH:
            return True
        
        # Check for low-quality text blocks
        total_blocks = sum(
            len(page.get('text_blocks', [])) 
            for page in doc_info['pages']
        )
        
        if total_blocks < self.config.MIN_TEXT_BLOCKS:
            return True
        
        return False
