"""
JSON Generation Module
Handles structured JSON output generation for extracted outlines.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class JSONGenerator:
    """Generates structured JSON output for PDF outlines."""
    
    def __init__(self):
        pass
    
    def save_outline(self, outline_data: Dict[str, Any], output_path: Path) -> None:
        """
        Save extracted outline data to JSON file.
        
        Args:
            outline_data: Dictionary containing title and outline
            output_path: Path where JSON file should be saved
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Validate and clean data
            cleaned_data = self._validate_and_clean(outline_data)
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Outline saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving outline to {output_path}: {str(e)}")
            raise
    
    def _validate_and_clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean outline data before JSON serialization."""
        
        # Ensure required fields exist
        cleaned = {
            'title': self._clean_title(data.get('title', 'Untitled Document')),
            'outline': self._clean_outline(data.get('outline', []))
        }
        
        # Add metadata if error occurred
        if 'error' in data:
            cleaned['error'] = str(data['error'])
        
        return cleaned
    
    def _clean_title(self, title: Any) -> str:
        """Clean and validate title field."""
        if not isinstance(title, str):
            return 'Untitled Document'
        
        # Clean whitespace and normalize
        title = ' '.join(str(title).split())
        
        # Ensure reasonable length
        if len(title) > 200:
            title = title[:197] + '...'
        
        return title if title else 'Untitled Document'
    
    def _clean_outline(self, outline: Any) -> List[Dict[str, Any]]:
        """Clean and validate outline entries."""
        if not isinstance(outline, list):
            return []
        
        cleaned_outline = []
        
        for entry in outline:
            if not isinstance(entry, dict):
                continue
            
            # Validate required fields
            level = entry.get('level')
            text = entry.get('text')
            page = entry.get('page')
            
            if not all([level, text, page]):
                continue
            
            # Validate level
            if level not in ['H1', 'H2', 'H3']:
                continue
            
            # Validate page number
            try:
                page_num = int(page)
                if page_num < 1:
                    continue
            except (ValueError, TypeError):
                continue
            
            # Clean text
            clean_text = ' '.join(str(text).split())
            if not clean_text:
                continue
            
            # Ensure reasonable text length
            if len(clean_text) > 500:
                clean_text = clean_text[:497] + '...'
            
            cleaned_entry = {
                'level': level,
                'text': clean_text,
                'page': page_num
            }
            
            cleaned_outline.append(cleaned_entry)
        
        return cleaned_outline
    
    def generate_summary_report(self, output_dir: Path) -> None:
        """Generate a summary report of all processed files."""
        try:
            json_files = list(output_dir.glob("*.json"))
            
            summary = {
                'total_files_processed': len(json_files),
                'files': [],
                'statistics': {
                    'total_headings': 0,
                    'avg_headings_per_file': 0,
                    'heading_levels': {'H1': 0, 'H2': 0, 'H3': 0}
                }
            }
            
            total_headings = 0
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    outline = data.get('outline', [])
                    file_headings = len(outline)
                    total_headings += file_headings
                    
                    # Count heading levels
                    level_counts = {'H1': 0, 'H2': 0, 'H3': 0}
                    for heading in outline:
                        level = heading.get('level')
                        if level in level_counts:
                            level_counts[level] += 1
                            summary['statistics']['heading_levels'][level] += 1
                    
                    file_info = {
                        'filename': json_file.name,
                        'title': data.get('title', 'Unknown'),
                        'total_headings': file_headings,
                        'heading_levels': level_counts,
                        'has_error': 'error' in data
                    }
                    
                    summary['files'].append(file_info)
                    
                except Exception as e:
                    logger.warning(f"Error reading {json_file}: {str(e)}")
                    summary['files'].append({
                        'filename': json_file.name,
                        'error': str(e)
                    })
            
            # Calculate averages
            if summary['total_files_processed'] > 0:
                summary['statistics']['total_headings'] = total_headings
                summary['statistics']['avg_headings_per_file'] = round(
                    total_headings / summary['total_files_processed'], 2
                )
            
            # Save summary report
            summary_path = output_dir / 'processing_summary.json'
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Summary report saved to {summary_path}")
            
        except Exception as e:
            logger.error(f"Error generating summary report: {str(e)}")
