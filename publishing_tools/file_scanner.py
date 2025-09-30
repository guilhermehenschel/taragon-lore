"""
File scanner module for discovering and organizing Markdown files.
"""
import os
from pathlib import Path
from typing import List, Dict, Tuple
import fnmatch
from dataclasses import dataclass
from config import TARAGON_ROOT, MD_PATTERN, EXCLUDE_PATTERNS, SECTION_ORDER


@dataclass
class MarkdownFile:
    """Represents a Markdown file with metadata."""
    path: Path
    relative_path: Path
    section: str
    title: str
    content: str = ""
    
    @property
    def basename(self) -> str:
        return self.path.stem
    
    @property
    def section_path(self) -> str:
        """Returns the path relative to the section directory."""
        parts = self.relative_path.parts
        if len(parts) > 1 and parts[0] in SECTION_ORDER:
            return str(Path(*parts[1:]))
        return str(self.relative_path)


class FileScanner:
    """Discovers and organizes Markdown files from the Taragon directory."""
    
    def __init__(self, root_path: Path = TARAGON_ROOT):
        self.root_path = root_path
        self.files: List[MarkdownFile] = []
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded based on exclude patterns."""
        path_str = str(path.relative_to(self.root_path))
        for pattern in EXCLUDE_PATTERNS:
            if fnmatch.fnmatch(path_str, pattern):
                return True
        return False
    
    def _extract_title(self, content: str) -> str:
        """Extract title from Markdown content (first # header)."""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return ""
    
    def _determine_section(self, relative_path: Path) -> str:
        """Determine which section a file belongs to."""
        if relative_path.name == "README.md" and len(relative_path.parts) == 1:
            return "README.md"
        
        if len(relative_path.parts) > 0:
            first_part = relative_path.parts[0]
            if first_part in SECTION_ORDER:
                return first_part
        
        return "Other"
    
    def scan_files(self) -> List[MarkdownFile]:
        """Scan for all Markdown files and return organized list."""
        self.files = []
        
        # Find all markdown files
        for md_file in self.root_path.rglob("*.md"):
            if self._should_exclude(md_file):
                continue
            
            relative_path = md_file.relative_to(self.root_path)
            section = self._determine_section(relative_path)
            
            # Read content and extract title
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                title = self._extract_title(content) or md_file.stem.replace('-', ' ').replace('_', ' ')
            except Exception as e:
                print(f"Warning: Could not read {md_file}: {e}")
                content = ""
                title = md_file.stem.replace('-', ' ').replace('_', ' ')
            
            markdown_file = MarkdownFile(
                path=md_file,
                relative_path=relative_path,
                section=section,
                title=title,
                content=content
            )
            
            self.files.append(markdown_file)
        
        # Sort files by section order and then by title
        section_priority = {section: i for i, section in enumerate(SECTION_ORDER)}
        
        def sort_key(file: MarkdownFile) -> Tuple[int, str, str]:
            section_idx = section_priority.get(file.section, len(SECTION_ORDER))
            return (section_idx, file.section, file.title.lower())
        
        self.files.sort(key=sort_key)
        return self.files
    
    def get_files_by_section(self) -> Dict[str, List[MarkdownFile]]:
        """Group files by section."""
        sections = {}
        for file in self.files:
            if file.section not in sections:
                sections[file.section] = []
            sections[file.section].append(file)
        return sections
    
    def print_structure(self):
        """Print the discovered file structure for debugging."""
        sections = self.get_files_by_section()
        
        print(f"Found {len(self.files)} Markdown files in {len(sections)} sections:")
        print()
        
        for section_name in SECTION_ORDER:
            if section_name in sections:
                files = sections[section_name]
                print(f"📁 {section_name} ({len(files)} files)")
                for file in files:
                    print(f"  📄 {file.title} ({file.section_path})")
                print()
        
        # Print any "Other" files that don't fit the standard structure
        if "Other" in sections:
            files = sections["Other"]
            print(f"📁 Other ({len(files)} files)")
            for file in files:
                print(f"  📄 {file.title} ({file.relative_path})")


if __name__ == "__main__":
    scanner = FileScanner()
    files = scanner.scan_files()
    scanner.print_structure()