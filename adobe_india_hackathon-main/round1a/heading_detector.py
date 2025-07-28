"""
Heading Detection Module
Implements multi-criteria heading detection and hierarchy assignment.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
import logging

from config import Config

logger = logging.getLogger(__name__)


class HeadingDetector:
    """Detects and classifies headings using multiple criteria."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def detect_headings(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect headings across all pages and assign hierarchy levels.
        
        Args:
            pages: List of page dictionaries containing text blocks
            
        Returns:
            List of heading dictionaries with level, text, and page number
        """
        all_candidates = []
        
        # Collect heading candidates from all pages
        for page in pages:
            page_candidates = self._find_heading_candidates(page)
            all_candidates.extend(page_candidates)
        
        if not all_candidates:
            return []
        
        # Analyze font size distribution
        font_analysis = self._analyze_font_sizes(all_candidates)
        
        # Classify headings by level
        classified_headings = self._classify_headings(all_candidates, font_analysis)
        
        # Sort by page number and position
        classified_headings.sort(key=lambda x: (x['page'], x.get('position', 0)))
        
        return classified_headings
    
    def _find_heading_candidates(self, page: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find potential heading candidates on a single page."""
        text_blocks = page.get('text_blocks', [])
        page_number = page.get('page_number', 1)
        
        candidates = []
        
        for block in text_blocks:
            text = block.get('text', '').strip()
            if not text or len(text) < 2:
                continue
            
            # Skip very long text (likely body text)
            if len(text) > self.config.MAX_HEADING_LENGTH:
                continue
            
            score = 0
            features = {}
            
            # Font size analysis
            font_size = block.get('size', 0)
            features['font_size'] = font_size
            
            # Style analysis
            flags = block.get('flags', 0)
            is_bold = (flags & 16) != 0
            is_italic = (flags & 2) != 0
            features['is_bold'] = is_bold
            features['is_italic'] = is_italic
            
            # Position analysis
            bbox = block.get('bbox', [0, 0, 0, 0])
            features['left_margin'] = bbox[0]
            features['top_position'] = bbox[1]
            features['position'] = bbox[1]
            
            # Pattern matching
            patterns_matched = self._check_text_patterns(text)
            features['patterns'] = patterns_matched
            
            # Calculate initial score
            if is_bold:
                score += 2
            if font_size > 12:
                score += 1
            if patterns_matched:
                score += len(patterns_matched)
            
            # Position scoring (left-aligned headings)
            if bbox[0] < 100:  # Near left margin
                score += 1
            
            # Length scoring (reasonable heading length)
            if 5 <= len(text) <= 80:
                score += 1
            
            if score >= self.config.MIN_HEADING_SCORE:
                candidate = {
                    'text': text,
                    'page': page_number,
                    'score': score,
                    'features': features
                }
                candidates.append(candidate)
        
        return candidates
    
    def _check_text_patterns(self, text: str) -> List[str]:
        """Check text for heading patterns."""
        patterns = []
        
        # Numbered patterns
        if re.match(r'^\d+\.?\s+', text):
            patterns.append('numbered')
        if re.match(r'^\d+\.\d+\.?\s+', text):
            patterns.append('sub_numbered')
        if re.match(r'^\d+\.\d+\.\d+\.?\s+', text):
            patterns.append('sub_sub_numbered')
        
        # Lettered patterns
        if re.match(r'^[A-Z]\.?\s+', text):
            patterns.append('lettered')
        if re.match(r'^[a-z][\)\.]?\s+', text):
            patterns.append('lower_lettered')
        
        # Formatting patterns
        if text.isupper() and len(text.split()) <= 8:
            patterns.append('all_caps')
        if text.istitle():
            patterns.append('title_case')
        
        # Roman numerals
        if re.match(r'^[IVX]+\.?\s+', text):
            patterns.append('roman')
        
        # Special markers
        if re.match(r'^(Chapter|Section|Part|Appendix)\s+', text, re.IGNORECASE):
            patterns.append('section_marker')
        
        return patterns
    
    def _analyze_font_sizes(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze font size distribution to establish hierarchy thresholds."""
        font_sizes = [c['features']['font_size'] for c in candidates if c['features']['font_size'] > 0]
        
        if not font_sizes:
            return {'h1_threshold': 16, 'h2_threshold': 14, 'h3_threshold': 12}
        
        font_sizes.sort(reverse=True)
        unique_sizes = sorted(list(set(font_sizes)), reverse=True)
        
        analysis = {
            'all_sizes': font_sizes,
            'unique_sizes': unique_sizes,
            'max_size': max(font_sizes),
            'min_size': min(font_sizes),
            'median_size': font_sizes[len(font_sizes) // 2]
        }
        
        # Establish thresholds based on distribution
        if len(unique_sizes) >= 3:
            analysis['h1_threshold'] = unique_sizes[0]
            analysis['h2_threshold'] = unique_sizes[1]
            analysis['h3_threshold'] = unique_sizes[2]
        elif len(unique_sizes) == 2:
            analysis['h1_threshold'] = unique_sizes[0]
            analysis['h2_threshold'] = unique_sizes[1]
            analysis['h3_threshold'] = unique_sizes[1] - 1
        else:
            # Single font size or very limited variety
            base_size = unique_sizes[0] if unique_sizes else 12
            analysis['h1_threshold'] = base_size
            analysis['h2_threshold'] = max(base_size - 2, 10)
            analysis['h3_threshold'] = max(base_size - 4, 8)
        
        return analysis
    
    def _classify_headings(self, candidates: List[Dict[str, Any]], font_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Classify headings into H1, H2, H3 levels."""
        classified = []
        
        h1_threshold = font_analysis.get('h1_threshold', 16)
        h2_threshold = font_analysis.get('h2_threshold', 14)
        h3_threshold = font_analysis.get('h3_threshold', 12)
        
        for candidate in candidates:
            features = candidate['features']
            font_size = features['font_size']
            patterns = features['patterns']
            
            # Determine level based on multiple criteria
            level = self._determine_heading_level(
                font_size, patterns, features, 
                h1_threshold, h2_threshold, h3_threshold
            )
            
            if level:
                heading = {
                    'level': level,
                    'text': candidate['text'],
                    'page': candidate['page'],
                    'position': features.get('position', 0)
                }
                classified.append(heading)
        
        return classified
    
    def _determine_heading_level(self, font_size: float, patterns: List[str], 
                                features: Dict[str, Any], h1_thresh: float, 
                                h2_thresh: float, h3_thresh: float) -> Optional[str]:
        """Determine the heading level using multiple criteria."""
        
        # Pattern-based classification (highest priority)
        if 'numbered' in patterns:
            if re.match(r'^\d+\.?\s+', features.get('text', '')):
                return 'H1'
        if 'sub_numbered' in patterns:
            return 'H2'
        if 'sub_sub_numbered' in patterns:
            return 'H3'
        
        # Section markers
        if 'section_marker' in patterns:
            return 'H1'
        
        # Font size-based classification
        if font_size >= h1_thresh:
            base_level = 'H1'
        elif font_size >= h2_thresh:
            base_level = 'H2'
        elif font_size >= h3_thresh:
            base_level = 'H3'
        else:
            return None  # Too small to be a heading
        
        # Adjust based on styling
        if features.get('is_bold', False):
            # Bold text gets priority
            pass
        else:
            # Non-bold text gets demoted one level
            if base_level == 'H1':
                base_level = 'H2'
            elif base_level == 'H2':
                base_level = 'H3'
            elif base_level == 'H3':
                return None
        
        # Special pattern adjustments
        if 'all_caps' in patterns and len(features.get('text', '')) < 50:
            # All caps likely H1 or H2
            if base_level == 'H3':
                base_level = 'H2'
        
        return base_level
