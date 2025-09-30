#!/usr/bin/env python3
"""
Main script for generating Taragon PDF from Markdown files.

This script orchestrates the entire process:
1. Scans for Markdown files in the Taragon directory
2. Processes the content and converts to LaTeX
3. Compiles the LaTeX to PDF

Usage:
    python run_pdf_publisher.py [options]

Options:
    --output-name NAME    Set output filename (default: taragon_complete)
    --section SECTION     Process only specific section 
    --debug              Enable debug output
    --clean-only         Only clean auxiliary files
    --check-deps         Check dependencies and exit
"""

import argparse
import sys
from pathlib import Path
import time

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from file_scanner import FileScanner
from latex_templates import LaTeXTemplateSystem
from pdf_generator import PDFGenerator
from config import OUTPUT_DIR, LATEX_FILENAME, PDF_FILENAME


class TaragonPDFPublisher:
    """Main publisher class that coordinates all components."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.scanner = FileScanner()
        self.template_system = LaTeXTemplateSystem()
        self.pdf_generator = PDFGenerator()
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
        if self.debug and level == "DEBUG":
            print(f"[{timestamp}] DEBUG: {message}")
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        self.log("Checking dependencies...")
        
        # Check LaTeX installation
        if not self.pdf_generator.check_latex_installation():
            self.log("ERROR: LaTeX not found. Please install TeX Live, MiKTeX, or MacTeX.", "ERROR")
            return False
        
        # Check if Jinja2 is available
        try:
            import jinja2
            self.log(f"Jinja2 version: {jinja2.__version__}")
        except ImportError:
            self.log("ERROR: Jinja2 not found. Install with: pip install jinja2", "ERROR")
            return False
        
        # Print LaTeX info
        latex_info = self.pdf_generator.get_compilation_info()
        self.log(f"LaTeX engine: {latex_info['latex_engine']}")
        self.log(f"LaTeX version: {latex_info.get('latex_version', 'Unknown')}")
        
        return True
    
    def scan_files(self, section_filter: str = None) -> list:
        """Scan for Markdown files."""
        self.log("Scanning for Markdown files...")
        
        files = self.scanner.scan_files()
        
        if section_filter:
            files = [f for f in files if f.section == section_filter]
            self.log(f"Filtered to section '{section_filter}': {len(files)} files")
        
        self.log(f"Found {len(files)} Markdown files")
        
        if self.debug:
            self.scanner.print_structure()
        
        return files
    
    def generate_latex(self, files: list) -> str:
        """Generate LaTeX content from Markdown files."""
        self.log("Converting Markdown to LaTeX...")
        
        latex_content = self.template_system.generate_latex_document(files)
        
        # Save LaTeX file for debugging
        latex_file = OUTPUT_DIR / LATEX_FILENAME
        latex_file.write_text(latex_content, encoding='utf-8')
        self.log(f"LaTeX saved to: {latex_file}")
        
        return latex_content
    
    def compile_pdf(self, latex_content: str, output_name: str = "taragon_complete") -> Path:
        """Compile LaTeX to PDF."""
        self.log("Compiling LaTeX to PDF...")
        
        pdf_path = self.pdf_generator.compile_latex(latex_content, output_name)
        
        if pdf_path and pdf_path.exists():
            self.log(f"PDF generated successfully: {pdf_path}")
            self.log(f"PDF size: {pdf_path.stat().st_size / 1024:.1f} KB")
        else:
            self.log("ERROR: PDF generation failed", "ERROR")
            # Try to show log content for debugging
            log_file = OUTPUT_DIR / f"{output_name}.log"
            if log_file.exists():
                self.log("LaTeX compilation log (last 20 lines):", "ERROR")
                log_content = log_file.read_text(encoding='utf-8', errors='ignore')
                log_lines = log_content.split('\n')[-20:]
                for line in log_lines:
                    if line.strip():
                        print(f"  {line}")
        
        return pdf_path
    
    def clean_auxiliary_files(self, output_name: str = "taragon_complete"):
        """Clean up auxiliary LaTeX files."""
        self.log("Cleaning auxiliary files...")
        self.pdf_generator.clean_auxiliary_files(output_name)
    
    def publish(self, output_name: str = "taragon_complete", section_filter: str = None) -> bool:
        """Main publishing workflow."""
        start_time = time.time()
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                return False
            
            # Scan files
            files = self.scan_files(section_filter)
            if not files:
                self.log("No Markdown files found to process", "ERROR")
                return False
            
            # Generate LaTeX
            latex_content = self.generate_latex(files)
            
            # Compile PDF
            pdf_path = self.compile_pdf(latex_content, output_name)
            
            if pdf_path and pdf_path.exists():
                elapsed = time.time() - start_time
                self.log(f"Publishing completed successfully in {elapsed:.1f} seconds")
                self.log(f"Output: {pdf_path}")
                return True
            else:
                self.log("Publishing failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Unexpected error during publishing: {e}", "ERROR")
            if self.debug:
                import traceback
                traceback.print_exc()
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Taragon campaign setting PDF from Markdown files"
    )
    
    parser.add_argument(
        '--output-name',
        default='taragon_complete',
        help='Output filename base (default: taragon_complete)'
    )
    
    parser.add_argument(
        '--section',
        help='Process only specific section (e.g., Geografia, Religião)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    
    parser.add_argument(
        '--clean-only',
        action='store_true',
        help='Only clean auxiliary files and exit'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check dependencies and exit'
    )
    
    args = parser.parse_args()
    
    # Create publisher
    publisher = TaragonPDFPublisher(debug=args.debug)
    
    # Handle special modes
    if args.check_deps:
        success = publisher.check_dependencies()
        sys.exit(0 if success else 1)
    
    if args.clean_only:
        publisher.clean_auxiliary_files(args.output_name)
        sys.exit(0)
    
    # Run main publishing workflow
    success = publisher.publish(args.output_name, args.section)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()