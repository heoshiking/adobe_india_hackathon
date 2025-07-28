"""
Utility Module
Contains helper functions and utilities used across the application.
"""

import re
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from functools import wraps

logger = logging.getLogger(__name__)


def timing_decorator(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"{func.__name__} executed in {end_time - start_time:.3f} seconds")
        return result
    return wrapper


def safe_file_operation(func):
    """Decorator for safe file operations with error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return None
        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            return None
        except Exception as e:
            logger.error(f"File operation failed: {e}")
            return None
    return wrapper


class TextProcessor:
    """Utility class for text processing operations."""
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text."""
        return ' '.join(text.split())
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text content."""
        if not isinstance(text, str):
            return ""
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
        
        # Normalize whitespace
        text = TextProcessor.normalize_whitespace(text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[-]{3,}', '---', text)
        
        return text.strip()
    
    @staticmethod
    def extract_numbers(text: str) -> List[int]:
        """Extract all numbers from text."""
        return [int(match) for match in re.findall(r'\d+', text)]
    
    @staticmethod
    def is_likely_heading(text: str, max_length: int = 200) -> bool:
        """Determine if text is likely a heading based on characteristics."""
        if not text or len(text) > max_length:
            return False
        
        # Count words
        words = text.split()
        if len(words) > 15:  # Too many words for a heading
            return False
        
        # Check for heading-like patterns
        patterns = [
            r'^\d+\.?\s+\w+',           # Numbered headings
            r'^[A-Z][A-Z\s]+$',         # All caps
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$',  # Title case
            r'^(Chapter|Section|Part|Appendix)\s+',  # Section markers
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Simple language detection based on character patterns."""
        if not text:
            return 'unknown'
        
        # Count different script types
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF]', text))
        
        if latin_chars / max(len(text.replace(' ', '')), 1) > 0.7:
            return 'eng'
        elif total_chars / max(len(text.replace(' ', '')), 1) > 0.5:
            return 'extended_latin'
        else:
            return 'unknown'


class FontAnalyzer:
    """Utility class for font analysis operations."""
    
    @staticmethod
    def extract_font_info(font_name: str) -> Dict[str, bool]:
        """Extract font style information from font name."""
        font_lower = font_name.lower()
        
        return {
            'is_bold': any(keyword in font_lower for keyword in ['bold', 'black', 'heavy', 'semibold']),
            'is_italic': any(keyword in font_lower for keyword in ['italic', 'oblique']),
            'is_condensed': any(keyword in font_lower for keyword in ['condensed', 'narrow']),
            'is_extended': any(keyword in font_lower for keyword in ['extended', 'wide'])
        }
    
    @staticmethod
    def calculate_font_prominence(size: float, is_bold: bool, is_italic: bool) -> float:
        """Calculate font prominence score."""
        score = size
        if is_bold:
            score *= 1.3
        if is_italic:
            score *= 1.1
        return score
    
    @staticmethod
    def group_similar_fonts(font_sizes: List[float], tolerance: float = 1.0) -> Dict[float, List[float]]:
        """Group similar font sizes together."""
        if not font_sizes:
            return {}
        
        sorted_sizes = sorted(set(font_sizes))
        groups = {}
        
        for size in sorted_sizes:
            grouped = False
            for group_key in groups:
                if abs(size - group_key) <= tolerance:
                    groups[group_key].append(size)
                    grouped = True
                    break
            
            if not grouped:
                groups[size] = [size]
        
        return groups


class GeometryUtils:
    """Utility class for geometric calculations."""
    
    @staticmethod
    def bbox_area(bbox: List[float]) -> float:
        """Calculate area of bounding box."""
        if len(bbox) < 4:
            return 0
        return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    
    @staticmethod
    def bbox_center(bbox: List[float]) -> tuple:
        """Calculate center point of bounding box."""
        if len(bbox) < 4:
            return (0, 0)
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
    
    @staticmethod
    def bbox_overlap(bbox1: List[float], bbox2: List[float]) -> float:
        """Calculate overlap ratio between two bounding boxes."""
        if len(bbox1) < 4 or len(bbox2) < 4:
            return 0
        
        # Calculate intersection
        left = max(bbox1[0], bbox2[0])
        top = max(bbox1[1], bbox2[1])
        right = min(bbox1[2], bbox2[2])
        bottom = min(bbox1[3], bbox2[3])
        
        if left >= right or top >= bottom:
            return 0
        
        intersection_area = (right - left) * (bottom - top)
        area1 = GeometryUtils.bbox_area(bbox1)
        area2 = GeometryUtils.bbox_area(bbox2)
        
        return intersection_area / min(area1, area2) if min(area1, area2) > 0 else 0
    
    @staticmethod
    def is_approximately_centered(bbox: List[float], page_width: float, tolerance: float = 0.2) -> bool:
        """Check if text is approximately centered on the page."""
        if len(bbox) < 4:
            return False
        
        text_center = (bbox[0] + bbox[2]) / 2
        page_center = page_width / 2
        tolerance_pixels = page_width * tolerance
        
        return abs(text_center - page_center) <= tolerance_pixels


@safe_file_operation
def read_file_safely(file_path: Union[str, Path]) -> Optional[str]:
    """Safely read text file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


@safe_file_operation
def write_file_safely(file_path: Union[str, Path], content: str) -> bool:
    """Safely write content to text file."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


def validate_pdf_file(file_path: Path) -> bool:
    """Validate if file is a proper PDF."""
    if not file_path.exists():
        return False
    
    if not file_path.suffix.lower() == '.pdf':
        return False
    
    # Check file size
    try:
        file_size = file_path.stat().st_size
        if file_size == 0:
            return False
        
        # Basic PDF header check
        with open(file_path, 'rb') as f:
            header = f.read(5)
            if not header.startswith(b'%PDF-'):
                return False
        
        return True
        
    except Exception:
        return False


def format_processing_stats(stats: Dict[str, Any]) -> str:
    """Format processing statistics for logging."""
    return (
        f"Processing Stats - "
        f"Files: {stats.get('files_processed', 0)}, "
        f"Total Time: {stats.get('total_time', 0):.2f}s, "
        f"Avg Time: {stats.get('avg_time', 0):.2f}s, "
        f"Headings: {stats.get('total_headings', 0)}"
    )
