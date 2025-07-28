#!/usr/bin/env python3
"""
PDF Outline Extraction System
Main entry point for processing PDFs and generating structured JSON outlines.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from pdf_processor import PDFProcessor
from json_generator import JSONGenerator
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OutlineExtractor:
    """Main class for PDF outline extraction system."""
    
    def __init__(self):
        self.config = Config()
        self.pdf_processor = PDFProcessor(self.config)
        self.json_generator = JSONGenerator()
        
    def process_pdfs(self) -> None:
        """Process all PDFs in the input directory."""
        input_dir = Path(self.config.INPUT_DIR)
        output_dir = Path(self.config.OUTPUT_DIR)
        
        # Ensure directories exist
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {input_dir}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Process each PDF
        for pdf_file in pdf_files:
            try:
                start_time = time.time()
                logger.info(f"Processing: {pdf_file.name}")
                
                # Extract outline
                result = self.pdf_processor.extract_outline(pdf_file)
                
                # Generate JSON output
                output_file = output_dir / f"{pdf_file.stem}.json"
                self.json_generator.save_outline(result, output_file)
                
                processing_time = time.time() - start_time
                logger.info(f"Completed {pdf_file.name} in {processing_time:.2f} seconds")
                
                # Check performance constraint
                if processing_time > self.config.MAX_PROCESSING_TIME:
                    logger.warning(
                        f"Processing time ({processing_time:.2f}s) exceeded "
                        f"limit ({self.config.MAX_PROCESSING_TIME}s)"
                    )
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {str(e)}")
                # Create error output
                error_result = {
                    "title": "Error: Could not process document",
                    "outline": [],
                    "error": str(e)
                }
                output_file = output_dir / f"{pdf_file.stem}.json"
                self.json_generator.save_outline(error_result, output_file)
    
    def run(self) -> None:
        """Run the outline extraction system."""
        logger.info("Starting PDF Outline Extraction System")
        logger.info(f"Input directory: {self.config.INPUT_DIR}")
        logger.info(f"Output directory: {self.config.OUTPUT_DIR}")
        
        try:
            self.process_pdfs()
            logger.info("PDF processing completed successfully")
        except Exception as e:
            logger.error(f"System error: {str(e)}")
            sys.exit(1)


def main():
    """Main entry point."""
    extractor = OutlineExtractor()
    extractor.run()


if __name__ == "__main__":
    main()
