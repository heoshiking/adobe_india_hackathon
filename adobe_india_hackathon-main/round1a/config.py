"""
Configuration Module
Contains all configuration parameters and settings for the PDF outline extraction system.
"""

import os
from pathlib import Path


class Config:
    """Configuration class containing all system parameters."""
    
    # Directory paths - use local directories in development
    INPUT_DIR = os.getenv('INPUT_DIR', './input')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
    
    # Performance constraints
    MAX_PROCESSING_TIME = int(os.getenv('MAX_PROCESSING_TIME', '10'))  # seconds
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '50')) * 1024 * 1024  # 50MB in bytes
    
    # PDF processing parameters
    MAX_PAGES = int(os.getenv('MAX_PAGES', '50'))
    MIN_TEXT_LENGTH = int(os.getenv('MIN_TEXT_LENGTH', '100'))  # Minimum text for native extraction
    MIN_TEXT_BLOCKS = int(os.getenv('MIN_TEXT_BLOCKS', '10'))   # Minimum blocks for native extraction
    
    # Title extraction parameters
    MAX_TITLE_LENGTH = int(os.getenv('MAX_TITLE_LENGTH', '200'))
    
    # Heading detection parameters
    MIN_HEADING_SCORE = int(os.getenv('MIN_HEADING_SCORE', '2'))
    MAX_HEADING_LENGTH = int(os.getenv('MAX_HEADING_LENGTH', '200'))
    
    # Font size thresholds (can be overridden by document analysis)
    DEFAULT_H1_FONT_SIZE = float(os.getenv('DEFAULT_H1_FONT_SIZE', '16.0'))
    DEFAULT_H2_FONT_SIZE = float(os.getenv('DEFAULT_H2_FONT_SIZE', '14.0'))
    DEFAULT_H3_FONT_SIZE = float(os.getenv('DEFAULT_H3_FONT_SIZE', '12.0'))
    
    # OCR parameters
    OCR_CONFIDENCE_THRESHOLD = int(os.getenv('OCR_CONFIDENCE_THRESHOLD', '30'))
    OCR_DPI = int(os.getenv('OCR_DPI', '200'))
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Language support
    SUPPORTED_LANGUAGES = os.getenv('SUPPORTED_LANGUAGES', 'eng').split(',')
    
    @classmethod
    def validate_directories(cls) -> bool:
        """Validate that required directories exist or can be created."""
        try:
            Path(cls.INPUT_DIR).mkdir(parents=True, exist_ok=True)
            Path(cls.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    @classmethod
    def get_tesseract_config(cls) -> str:
        """Get Tesseract configuration string."""
        languages = '+'.join(cls.SUPPORTED_LANGUAGES)
        return f'-l {languages} --psm 6 --oem 3'
    
    @classmethod
    def print_config(cls) -> None:
        """Print current configuration for debugging."""
        print("PDF Outline Extraction Configuration:")
        print(f"  Input Directory: {cls.INPUT_DIR}")
        print(f"  Output Directory: {cls.OUTPUT_DIR}")
        print(f"  Max Processing Time: {cls.MAX_PROCESSING_TIME}s")
        print(f"  Max Pages: {cls.MAX_PAGES}")
        print(f"  OCR Confidence Threshold: {cls.OCR_CONFIDENCE_THRESHOLD}")
        print(f"  Supported Languages: {cls.SUPPORTED_LANGUAGES}")
        print(f"  Log Level: {cls.LOG_LEVEL}")
