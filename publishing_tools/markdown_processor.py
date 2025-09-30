"""
Markdown processor module for handling content conversion and cross-references.
"""
import re
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import unquote
from file_scanner import MarkdownFile


class MarkdownProcessor:
    """Processes Markdown content for LaTeX conversion."""
    
    def __init__(self, files: List[MarkdownFile]):
        self.files = files
        self.file_map = self._build_file_map()
        self.processed_images: Set[str] = set()
    
    def _build_file_map(self) -> Dict[str, MarkdownFile]:
        """Build a mapping of file paths to MarkdownFile objects."""
        file_map = {}
        
        for file in self.files:
            # Map by relative path
            file_map[str(file.relative_path)] = file
            # Map by filename (for simple references)
            file_map[file.path.name] = file
            # Map by stem (filename without extension)
            file_map[file.path.stem] = file
            # Map by title (for reference resolution)
            file_map[file.title] = file
        
        return file_map
    
    def _resolve_link_target(self, link_path: str, current_file: MarkdownFile) -> str:
        """Resolve a markdown link to a LaTeX reference."""
        # Decode URL encoding
        link_path = unquote(link_path)
        
        # Handle relative paths
        if link_path.startswith('./'):
            link_path = link_path[2:]
        elif link_path.startswith('../'):
            # Resolve relative path from current file's directory
            current_dir = current_file.path.parent
            target_path = (current_dir / link_path).resolve()
            try:
                link_path = str(target_path.relative_to(current_file.path.parent.parent))
            except ValueError:
                # Path is outside the project, keep as is
                pass
        
        # Remove .md extension
        if link_path.endswith('.md'):
            link_path = link_path[:-3]
        
        # Try to find the target file
        target_file = None
        
        # Direct path match
        if link_path in self.file_map:
            target_file = self.file_map[link_path]
        else:
            # Try filename match
            filename = Path(link_path).name
            if filename in self.file_map:
                target_file = self.file_map[filename]
        
        if target_file:
            # Create safe LaTeX label from the file path
            label = re.sub(r'[^\w\-_]', '_', str(target_file.relative_path)).lower()
            label = re.sub(r'_+', '_', label)  # Replace multiple underscores with single
            label = label.strip('_')  # Remove leading/trailing underscores
            title = target_file.title.replace('{', '').replace('}', '')  # Remove braces
            return f"\\hyperref[{label}]{{{title}}}"  # Proper hyperref link
        else:
            # Couldn't resolve, return as plain text
            clean_path = re.sub(r'[^\w\s\-]', '', link_path)  # Remove problematic chars
            return clean_path
    
    def _process_images(self, content: str, current_file: MarkdownFile) -> str:
        """Process image references in markdown."""
        def replace_image(match):
            alt_text = match.group(1)
            image_path = match.group(2)
            
            # Decode URL encoding
            image_path = unquote(image_path)
            
            # Handle relative paths
            if image_path.startswith('./'):
                image_path = image_path[2:]
            elif image_path.startswith('../'):
                current_dir = current_file.path.parent
                full_path = (current_dir / image_path).resolve()
                try:
                    # Convert to path relative to Taragon root
                    from config import TARAGON_ROOT
                    image_path = str(full_path.relative_to(TARAGON_ROOT))
                except ValueError:
                    # Keep original path if can't resolve
                    pass
            
            # Track processed images
            self.processed_images.add(image_path)
            
            # Convert to LaTeX figure
            return f"""
\\begin{{figure}}[h]
\\centering
\\includegraphics[width=0.8\\textwidth]{{{image_path}}}
\\caption{{{alt_text}}}
\\end{{figure}}
"""
        
        # Pattern for ![alt text](image_path)
        return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, content)
    
    def _process_links(self, content: str, current_file: MarkdownFile) -> str:
        """Process markdown links and convert to LaTeX references."""
        def replace_link(match):
            link_text = match.group(1)
            link_target = match.group(2)
            
            # Skip external links (http/https)
            if link_target.startswith(('http://', 'https://')):
                return f"\\href{{{link_target}}}{{{link_text}}}"
            
            # Handle anchors within the same document
            if link_target.startswith('#'):
                # Create reference to header within same document
                anchor_name = link_target[1:]  # Remove the #
                clean_anchor = re.sub(r'[^\w\-_]', '_', anchor_name.lower())
                clean_anchor = re.sub(r'_+', '_', clean_anchor)  # Replace multiple underscores with single
                clean_anchor = clean_anchor.strip('_')  # Remove leading/trailing underscores
                return f"\\hyperref[sub:{clean_anchor}]{{{link_text}}}"
            
            return self._resolve_link_target(link_target, current_file)
        
        # Pattern for [link text](link_target)
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)
    
    def _escape_latex_special_chars(self, content: str) -> str:
        """Escape special LaTeX characters and handle Unicode."""
        # Replace problematic characters
        escapes = {
            '&': ' and ',
            '%': ' percent ',
            '$': ' dollar ',
            '#': ' ',
            '_': ' ',  # Replace underscores with spaces
            # Unicode characters that cause issues - replace with simple text
            '•': '* ',
            '►': '> ',
            '◄': '< ',
            '▪': '- ',
        }
        
        for char, escape in escapes.items():
            content = content.replace(char, escape)
        
        # Remove other problematic Unicode characters
        import unicodedata
        content = ''.join(char for char in content if ord(char) < 256 or char.isalnum())
        
        return content
    
    def _convert_headers(self, content: str) -> str:
        """Convert markdown headers to LaTeX sections."""
        lines = content.split('\n')
        result = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                # Count the number of # characters
                level = 0
                for char in stripped:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                # Extract header text
                header_text = stripped[level:].strip()
                
                # Convert to LaTeX section based on level - simplified
                # Create a label for this header
                header_label = re.sub(r'[^\w\-_]', '_', header_text.lower())
                header_label = re.sub(r'_+', '_', header_label)  # Replace multiple underscores with single
                header_label = header_label.strip('_')  # Remove leading/trailing underscores
                
                if level == 1:
                    result.append(f"\n\\subsubsection{{{header_text}}}\n\\label{{sub:{header_label}}}\n")
                elif level == 2:
                    result.append(f"\n\\paragraph{{{header_text}}}\n\\label{{par:{header_label}}}\n")
                else:
                    result.append(f"\n\\textbf{{{header_text}}}\n")
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _convert_emphasis(self, content: str) -> str:
        """Convert markdown emphasis to LaTeX."""
        # For now, let's avoid LaTeX emphasis and just remove the markdown
        # Bold: **text** or __text__
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'__([^_]+)__', r'\1', content)
        
        # Italic: *text* or _text_ (be careful not to match underscores in file paths)
        content = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'\1', content)
        content = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'\1', content)
        
        return content
    
    def _convert_code(self, content: str) -> str:
        """Convert markdown code blocks and inline code to LaTeX."""
        # Code blocks: ```language\ncode\n```
        def replace_code_block(match):
            language = match.group(1) if match.group(1) else ''
            code = match.group(2)
            
            # Escape LaTeX special characters in code
            code = code.replace('\\', '\\textbackslash{}')
            code = code.replace('{', '\\{').replace('}', '\\}')
            code = code.replace('^', '\\textasciicircum{}')
            code = code.replace('~', '\\textasciitilde{}')
            
            return f"""
\\begin{{lstlisting}}[language={language}]
{code}
\\end{{lstlisting}}
"""
        
        content = re.sub(r'```(\w*)\n(.*?)\n```', replace_code_block, content, flags=re.DOTALL)
        
        # Inline code: `code`
        content = re.sub(r'`([^`]+)`', r'\\texttt{\1}', content)
        
        return content
    
    def _convert_lists(self, content: str) -> str:
        """Convert markdown lists to LaTeX."""
        lines = content.split('\n')
        result = []
        in_list = False
        list_type = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Check if this is a list item
            is_unordered = stripped.startswith(('- ', '* ', '+ '))
            is_ordered = re.match(r'^\d+\.\s', stripped)
            
            if is_unordered or is_ordered:
                current_list_type = 'itemize' if is_unordered else 'enumerate'
                
                # Start new list if needed
                if not in_list or list_type != current_list_type:
                    if in_list:
                        result.append(f"\\end{{{list_type}}}")
                    result.append(f"\\begin{{{current_list_type}}}")
                    in_list = True
                    list_type = current_list_type
                
                # Extract item text
                if is_unordered:
                    item_text = stripped[2:].strip()
                else:
                    item_text = re.sub(r'^\d+\.\s', '', stripped)
                
                result.append(f"\\item {item_text}")
            else:
                # End list if we were in one
                if in_list and stripped == '':
                    # Empty line - might end list, but check next non-empty line
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == '':
                        j += 1
                    
                    if j >= len(lines) or not (lines[j].strip().startswith(('- ', '* ', '+ ')) or 
                                              re.match(r'^\d+\.\s', lines[j].strip())):
                        # End the list
                        result.append(f"\\end{{{list_type}}}")
                        in_list = False
                        list_type = None
                
                result.append(line)
            
            i += 1
        
        # Close any remaining list
        if in_list:
            result.append(f"\\end{{{list_type}}}")
        
        return '\n'.join(result)
    
    def process_file(self, file: MarkdownFile) -> str:
        """Process a single markdown file and return LaTeX content."""
        content = file.content
        
        # Create a label for this file
        label = re.sub(r'[^\w\-_]', '_', str(file.relative_path)).lower()
        label = re.sub(r'_+', '_', label)  # Replace multiple underscores with single
        label = label.strip('_')  # Remove leading/trailing underscores
        
        # Add label at the beginning
        result = f"\\label{{{label}}}\n\n"
        
        # Process content
        content = self._process_links(content, file)  # Process links first before converting to plain text
        content = self._convert_headers(content)
        content = self._convert_emphasis(content)
        
        # Remove problematic markdown that we can't easily convert
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'[Image: \1]', content)  # Images as text
        content = re.sub(r'`([^`]+)`', r'\1', content)  # Remove code markup
        
        # Clean up any remaining problematic characters
        content = self._escape_latex_special_chars(content)
        
        return result + content + "\n\n"
    
    def get_processed_images(self) -> List[str]:
        """Return list of all images that were referenced in the processed files."""
        return sorted(list(self.processed_images))