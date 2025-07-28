"""
OCR Handler Module
Handles OCR processing for scanned PDFs using Tesseract.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

try:
    import pytesseract
    from PIL import Image
    import fitz  # PyMuPDF for image extraction
    OCR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"OCR dependencies not available: {e}")
    OCR_AVAILABLE = False

from config import Config

logger = logging.getLogger(__name__)


class OCRHandler:
    """Handles OCR processing for scanned PDFs."""
    
    def __init__(self, config: Config):
        self.config = config
        self.ocr_available = OCR_AVAILABLE
        
        if self.ocr_available:
            # Configure Tesseract
            tesseract_cmd = os.getenv('TESSERACT_CMD', 'tesseract')
            if tesseract_cmd != 'tesseract':
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract_text(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract text from scanned PDF using OCR.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Document information similar to native extraction
        """
        if not self.ocr_available:
            logger.error("OCR dependencies not available")
            return None
        
        try:
            doc = fitz.open(str(pdf_path))
            doc_info = {
                'pages': [],
                'total_pages': len(doc)
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
                pix = page.get_pixmap(matrix=mat)
                
                # Save to temporary image file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    pix.save(temp_file.name)
                    temp_image_path = temp_file.name
                
                try:
                    # Perform OCR
                    page_info = self._ocr_image(temp_image_path, page_num + 1)
                    doc_info['pages'].append(page_info)
                    
                finally:
                    # Clean up temporary file
                    os.unlink(temp_image_path)
            
            doc.close()
            return doc_info
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return None
    
    def _ocr_image(self, image_path: str, page_number: int) -> Dict[str, Any]:
        """Perform OCR on a single image and structure the results."""
        try:
            # Open image
            image = Image.open(image_path)
            
            # Get detailed OCR data with bounding boxes
            ocr_data = pytesseract.image_to_data(
                image, 
                output_type=pytesseract.Output.DICT,
                config='--psm 6'  # Uniform block of text
            )
            
            # Extract plain text as fallback
            raw_text = pytesseract.image_to_string(image)
            
            page_info = {
                'page_number': page_number,
                'text_blocks': [],
                'raw_text': raw_text
            }
            
            # Process OCR data to create text blocks
            current_block = None
            
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                conf = int(ocr_data['conf'][i])
                
                # Skip low confidence text
                if conf < self.config.OCR_CONFIDENCE_THRESHOLD or not text:
                    continue
                
                # Create text block
                left = ocr_data['left'][i]
                top = ocr_data['top'][i]
                width = ocr_data['width'][i]
                height = ocr_data['height'][i]
                
                # Estimate font size based on height
                estimated_font_size = max(height * 0.7, 8)
                
                text_block = {
                    'text': text,
                    'font': 'ocr-detected',
                    'size': estimated_font_size,
                    'flags': 0,  # Can't detect bold/italic from OCR easily
                    'bbox': [left, top, left + width, top + height],
                    'color': 0,
                    'confidence': conf
                }
                
                page_info['text_blocks'].append(text_block)
            
            # Post-process to merge nearby text blocks
            page_info['text_blocks'] = self._merge_nearby_blocks(page_info['text_blocks'])
            
            return page_info
            
        except Exception as e:
            logger.error(f"OCR processing failed for image: {str(e)}")
            return {
                'page_number': page_number,
                'text_blocks': [],
                'raw_text': ""
            }
    
    def _merge_nearby_blocks(self, text_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge nearby text blocks that likely belong together."""
        if not text_blocks:
            return text_blocks
        
        merged = []
        sorted_blocks = sorted(text_blocks, key=lambda x: (x['bbox'][1], x['bbox'][0]))
        
        current_line = []
        current_y = None
        
        for block in sorted_blocks:
            bbox = block['bbox']
            block_y = bbox[1]
            
            # If this block is on the same line (similar Y coordinate)
            if current_y is None or abs(block_y - current_y) < 10:
                current_line.append(block)
                current_y = block_y if current_y is None else current_y
            else:
                # Process current line
                if current_line:
                    merged.extend(self._merge_line_blocks(current_line))
                
                # Start new line
                current_line = [block]
                current_y = block_y
        
        # Process final line
        if current_line:
            merged.extend(self._merge_line_blocks(current_line))
        
        return merged
    
    def _merge_line_blocks(self, line_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge blocks on the same line that are close together."""
        if len(line_blocks) <= 1:
            return line_blocks
        
        # Sort by X coordinate
        line_blocks.sort(key=lambda x: x['bbox'][0])
        
        merged = []
        current_block = line_blocks[0].copy()
        
        for i in range(1, len(line_blocks)):
            next_block = line_blocks[i]
            
            # Check if blocks are close enough to merge
            current_right = current_block['bbox'][2]
            next_left = next_block['bbox'][0]
            
            # Merge if gap is small (less than average character width)
            avg_char_width = (current_block['bbox'][2] - current_block['bbox'][0]) / max(len(current_block['text']), 1)
            
            if next_left - current_right < avg_char_width * 2:
                # Merge blocks
                current_block['text'] += ' ' + next_block['text']
                current_block['bbox'][2] = next_block['bbox'][2]  # Extend right boundary
                current_block['size'] = max(current_block['size'], next_block['size'])
            else:
                # Blocks are too far apart, finalize current and start new
                merged.append(current_block)
                current_block = next_block.copy()
        
        merged.append(current_block)
        return merged
