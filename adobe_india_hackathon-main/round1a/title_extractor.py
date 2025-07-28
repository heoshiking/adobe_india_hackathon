"""
Title Extraction Module
Implements heuristics for detecting document titles from the first page.
"""

import re
from typing import Dict, List, Any, Optional
import logging

from config import Config

logger = logging.getLogger(__name__)


class TitleExtractor:
    """Extracts document titles using font size and positioning heuristics."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def extract_title(self, first_page: Dict[str, Any]) -> str:
        """
        Extract title from first page using multiple heuristics.
        
        Args:
            first_page: Dictionary containing first page information
            
        Returns:
            Extracted title string
        """
        text_blocks = first_page.get('text_blocks', [])
        
        if not text_blocks:
            return "Untitled Document"
        
        # Apply multiple extraction strategies
        candidates = []
        
        # Strategy 1: Largest font size
        largest_font_candidate = self._find_by_font_size(text_blocks)
        if largest_font_candidate:
            candidates.append(('font_size', largest_font_candidate))
        
        # Strategy 2: Central positioning
        centered_candidate = self._find_by_position(text_blocks)
        if centered_candidate:
            candidates.append(('position', centered_candidate))
        
        # Strategy 3: Bold text
        bold_candidate = self._find_by_style(text_blocks)
        if bold_candidate:
            candidates.append(('style', bold_candidate))
        
        # Strategy 4: Top positioning
        top_candidate = self._find_by_top_position(text_blocks)
        if top_candidate:
            candidates.append(('top', top_candidate))
        
        # Score and select best candidate
        best_title = self._select_best_candidate(candidates, text_blocks)
        
        return self._clean_title(best_title) if best_title else "Untitled Document"
    
    def _find_by_font_size(self, text_blocks: List[Dict[str, Any]]) -> Optional[str]:
        """Find title by largest font size."""
        if not text_blocks:
            return None
        
        # Get font sizes and find the largest
        font_sizes = [block['size'] for block in text_blocks if block.get('size', 0) > 0]
        if not font_sizes:
            return None
        
        max_font_size = max(font_sizes)
        
        # Find blocks with the largest font size
        largest_blocks = [
            block for block in text_blocks 
            if abs(block.get('size', 0) - max_font_size) < 0.1
        ]
        
        # Prefer blocks in the upper portion of the page
        largest_blocks.sort(key=lambda x: x.get('bbox', [0, 0, 0, 0])[1])
        
        if largest_blocks:
            return largest_blocks[0]['text']
        
        return None
    
    def _find_by_position(self, text_blocks: List[Dict[str, Any]]) -> Optional[str]:
        """Find title by central horizontal positioning."""
        if not text_blocks:
            return None
        
        # Calculate page width (approximate)
        if text_blocks:
            page_width = max(
                block.get('bbox', [0, 0, 0, 0])[2] 
                for block in text_blocks
            )
        else:
            return None
        
        centered_blocks = []
        
        for block in text_blocks:
            bbox = block.get('bbox', [0, 0, 0, 0])
            text_width = bbox[2] - bbox[0]
            center_x = bbox[0] + text_width / 2
            page_center = page_width / 2
            
            # Check if text is reasonably centered
            center_tolerance = page_width * 0.2  # 20% tolerance
            if abs(center_x - page_center) < center_tolerance:
                # Prefer blocks in upper portion
                if bbox[1] < page_width * 0.3:  # Upper 30% of page
                    centered_blocks.append((bbox[1], block))
        
        if centered_blocks:
            # Sort by vertical position (top first)
            centered_blocks.sort(key=lambda x: x[0])
            return centered_blocks[0][1]['text']
        
        return None
    
    def _find_by_style(self, text_blocks: List[Dict[str, Any]]) -> Optional[str]:
        """Find title by bold or special styling."""
        # Look for bold text (flag bit 4 in PyMuPDF)
        bold_blocks = []
        
        for block in text_blocks:
            flags = block.get('flags', 0)
            
            # Check for bold flag (16 in PyMuPDF flags)
            is_bold = (flags & 16) != 0
            
            # Also check font name for bold indicators
            font_name = block.get('font', '').lower()
            font_bold = any(
                indicator in font_name 
                for indicator in ['bold', 'black', 'heavy', 'semibold']
            )
            
            if is_bold or font_bold:
                bbox = block.get('bbox', [0, 0, 0, 0])
                # Prefer blocks in upper portion
                if bbox[1] < 200:  # Arbitrary upper threshold
                    bold_blocks.append((bbox[1], block))
        
        if bold_blocks:
            # Sort by vertical position
            bold_blocks.sort(key=lambda x: x[0])
            return bold_blocks[0][1]['text']
        
        return None
    
    def _find_by_top_position(self, text_blocks: List[Dict[str, Any]]) -> Optional[str]:
        """Find title by topmost position with reasonable font size."""
        if not text_blocks:
            return None
        
        # Filter blocks in top portion with decent font size
        font_sizes = [block.get('size', 0) for block in text_blocks]
        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
        
        top_blocks = []
        for block in text_blocks:
            bbox = block.get('bbox', [0, 0, 0, 0])
            font_size = block.get('size', 0)
            
            # Must be in top 20% and have above-average font size
            if bbox[1] < 100 and font_size >= avg_font_size:
                top_blocks.append((bbox[1], block))
        
        if top_blocks:
            top_blocks.sort(key=lambda x: x[0])
            return top_blocks[0][1]['text']
        
        return None
    
    def _select_best_candidate(self, candidates: List[tuple], text_blocks: List[Dict[str, Any]]) -> Optional[str]:
        """Select the best title candidate using scoring."""
        if not candidates:
            return None
        
        scores = {}
        
        for strategy, text in candidates:
            if text not in scores:
                scores[text] = 0
            
            # Score based on strategy type
            if strategy == 'font_size':
                scores[text] += 3
            elif strategy == 'position':
                scores[text] += 2
            elif strategy == 'style':
                scores[text] += 2
            elif strategy == 'top':
                scores[text] += 1
        
        # Additional scoring based on text characteristics
        for text in scores:
            # Penalize very short or very long text
            text_length = len(text.strip())
            if 5 <= text_length <= 100:
                scores[text] += 1
            elif text_length > 200:
                scores[text] -= 2
            
            # Bonus for title-like patterns
            if self._looks_like_title(text):
                scores[text] += 2
        
        # Return highest scoring candidate
        if scores:
            best_candidate = max(scores.items(), key=lambda x: x[1])
            return best_candidate[0]
        
        return None
    
    def _looks_like_title(self, text: str) -> bool:
        """Check if text looks like a title based on patterns."""
        text = text.strip()
        
        # Check for title patterns
        patterns = [
            r'^[A-Z][a-z\s]+$',  # Starts with capital, contains words
            r'^[A-Z\s]+$',       # All caps with spaces
            r'^\w+(\s+\w+)*$'    # Multiple words
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        
        # Avoid common non-title patterns
        avoid_patterns = [
            r'^\d+$',            # Just numbers
            r'^page\s+\d+',      # Page numbers
            r'^chapter\s+\d+',   # Chapter numbers only
            r'^www\.',           # URLs
            r'@'                 # Email addresses
        ]
        
        for pattern in avoid_patterns:
            if re.search(pattern, text.lower()):
                return False
        
        return True
    
    def _clean_title(self, title: str) -> str:
        """Clean and format the extracted title."""
        if not title:
            return "Untitled Document"
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['title:', 'subject:', 'document:']
        for prefix in prefixes_to_remove:
            if title.lower().startswith(prefix):
                title = title[len(prefix):].strip()
        
        # Limit length
        if len(title) > self.config.MAX_TITLE_LENGTH:
            title = title[:self.config.MAX_TITLE_LENGTH].strip()
            if not title.endswith('...'):
                title += '...'
        
        return title if title else "Untitled Document"
