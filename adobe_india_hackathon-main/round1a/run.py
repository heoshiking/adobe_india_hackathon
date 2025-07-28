#!/usr/bin/env python3
"""
Run script for the PDF Outline Extraction System
This script provides a simple interface to run the system with different options.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import OutlineExtractor
from config import Config
from json_generator import JSONGenerator


def setup_logging(level: str = 'INFO'):
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point for the run script."""
    parser = argparse.ArgumentParser(
        description='PDF Outline Extraction System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                          # Run with default settings
  python run.py --input ./pdfs --output ./results
  python run.py --verbose               # Enable verbose logging
  python run.py --config               # Show current configuration
  python run.py --summary              # Generate summary report only
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Input directory containing PDF files (default: /app/input)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory for JSON files (default: /app/output)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode - minimal output'
    )
    
    parser.add_argument(
        '--config', '-c',
        action='store_true',
        help='Show current configuration and exit'
    )
    
    parser.add_argument(
        '--summary', '-s',
        action='store_true',
        help='Generate summary report only (requires existing output files)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level'
    )
    
    args = parser.parse_args()
    
    # Override config with command line arguments
    if args.input:
        Config.INPUT_DIR = args.input
    if args.output:
        Config.OUTPUT_DIR = args.output
    
    # Setup logging
    if args.verbose:
        log_level = 'DEBUG'
    elif args.quiet:
        log_level = 'WARNING'
    else:
        log_level = args.log_level
    
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    # Show configuration if requested
    if args.config:
        Config.print_config()
        return
    
    # Validate directories
    if not Config.validate_directories():
        logger.error("Failed to create or access required directories")
        sys.exit(1)
    
    # Generate summary report only
    if args.summary:
        try:
            json_generator = JSONGenerator()
            json_generator.generate_summary_report(Path(Config.OUTPUT_DIR))
            logger.info("Summary report generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate summary report: {e}")
            sys.exit(1)
        return
    
    # Run the main extraction system
    try:
        logger.info("Starting PDF Outline Extraction System")
        extractor = OutlineExtractor()
        extractor.run()
        
        # Generate summary report after processing
        try:
            json_generator = JSONGenerator()
            json_generator.generate_summary_report(Path(Config.OUTPUT_DIR))
        except Exception as e:
            logger.warning(f"Failed to generate summary report: {e}")
        
        logger.info("Processing completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
