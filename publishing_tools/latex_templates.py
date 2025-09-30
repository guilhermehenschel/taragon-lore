"""
LaTeX template system using Jinja2 for converting Markdown to LaTeX.
"""
from pathlib import Path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from file_scanner import MarkdownFile
from markdown_processor import MarkdownProcessor
from config import TEMPLATES_DIR


class LaTeXTemplateSystem:
    """Manages Jinja2 templates for LaTeX generation."""
    
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(['html', 'xml']),
            block_start_string='{%',
            block_end_string='%}',
            variable_start_string='{{',
            variable_end_string='}}',
            comment_start_string='{#',
            comment_end_string='#}',
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['latex_escape'] = self._latex_escape_filter
        self.env.filters['section_title'] = self._section_title_filter
    
    def _latex_escape_filter(self, text: str) -> str:
        """Jinja2 filter to escape LaTeX special characters."""
        if not isinstance(text, str):
            return str(text)
        
        escapes = {
            '&': '\\&',
            '%': '\\%',  
            '$': '\\$',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '\\': '\\textbackslash{}'
        }
        
        for char, escape in escapes.items():
            text = text.replace(char, escape)
        
        return text
    
    def _section_title_filter(self, section_name: str) -> str:
        """Convert section name to a nice title."""
        # Handle special cases
        replacements = {
            'README.md': 'Introduction',
            'Geografia': 'Geography',
            'Religião': 'Religion', 
            'Pessoas': 'People',
            'Raças': 'Races',
            'HomebrewPF2e': 'Homebrew Rules',
            'Cronologia': 'Timeline'
        }
        
        if section_name in replacements:
            return replacements[section_name]
        
        # Default formatting
        return section_name.replace('_', ' ').replace('-', ' ').title()
    
    def generate_latex_document(self, files: List[MarkdownFile]) -> str:
        """Generate complete LaTeX document from markdown files."""
        # Process all markdown files
        processor = MarkdownProcessor(files)
        
        # Group files by section and process content
        sections = {}
        for file in files:
            if file.section not in sections:
                sections[file.section] = []
            
            # Process the file content
            processed_content = processor.process_file(file)
            
            # Create a new file object with processed content
            processed_file = MarkdownFile(
                path=file.path,
                relative_path=file.relative_path,
                section=file.section,
                title=file.title,
                content=processed_content
            )
            processed_file.processed_content = processed_content
            
            sections[file.section].append(processed_file)
        
        # Load and render the main template
        template = self.env.get_template('main_document.tex')
        latex_content = template.render(
            sections=sections,
            total_files=len(files),
            processed_images=processor.get_processed_images()
        )
        
        return latex_content
    
    def generate_section_template(self, section_name: str, files: List[MarkdownFile]) -> str:
        """Generate LaTeX for a specific section (useful for debugging)."""
        processor = MarkdownProcessor(files)
        
        processed_files = []
        for file in files:
            if file.section == section_name:
                processed_content = processor.process_file(file)
                processed_file = MarkdownFile(
                    path=file.path,
                    relative_path=file.relative_path,
                    section=file.section,
                    title=file.title,
                    content=processed_content
                )
                processed_file.processed_content = processed_content
                processed_files.append(processed_file)
        
        # Simple section template
        latex_content = f"\\chapter{{{self._section_title_filter(section_name)}}}\n\n"
        
        for file in processed_files:
            if file.title:
                latex_content += f"\\section{{{file.title}}}\n"
                latex_content += file.processed_content + "\n\n"
        
        return latex_content


if __name__ == "__main__":
    from file_scanner import FileScanner
    
    # Test the template system
    scanner = FileScanner()
    files = scanner.scan_files()
    
    template_system = LaTeXTemplateSystem()
    latex_content = template_system.generate_latex_document(files)
    
    print("Generated LaTeX document:")
    print(latex_content[:1000] + "..." if len(latex_content) > 1000 else latex_content)