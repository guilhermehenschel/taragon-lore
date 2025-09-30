"""
PDF generator module for compiling LaTeX documents to PDF.
"""
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List
import tempfile
import os
from config import OUTPUT_DIR, LATEX_ENGINE, MAX_COMPILE_ATTEMPTS


class PDFGenerator:
    """Handles LaTeX compilation to PDF."""
    
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.latex_engine = LATEX_ENGINE
        self.max_attempts = MAX_COMPILE_ATTEMPTS
    
    def check_latex_installation(self) -> bool:
        """Check if LaTeX is installed and available."""
        try:
            result = subprocess.run(
                [self.latex_engine, '--version'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_required_packages(self) -> List[str]:
        """Return list of LaTeX packages that should be installed."""
        return [
            'fontspec',
            'babel-portuguese', 
            'geometry',
            'fancyhdr',
            'microtype',
            'graphicx',
            'xcolor',
            'tikz',
            'array',
            'longtable',
            'booktabs',
            'enumitem',
            'listings',
            'hyperref',
            'titlesec'
        ]
    
    def compile_latex(self, latex_content: str, output_filename: str = "taragon_complete") -> Optional[Path]:
        """
        Compile LaTeX content to PDF.
        
        Args:
            latex_content: The LaTeX source code
            output_filename: Base name for output files (without extension)
            
        Returns:
            Path to generated PDF file, or None if compilation failed
        """
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Create temporary working directory (avoiding spaces in path)
        with tempfile.TemporaryDirectory(prefix="taragon_", dir=self.output_dir) as temp_dir:
            temp_path = Path(temp_dir)
            tex_file = temp_path / f"{output_filename}.tex"
            
            # Write LaTeX content to file
            tex_file.write_text(latex_content, encoding='utf-8')
            
            # Copy any image files that might be referenced
            self._copy_referenced_images(latex_content, temp_path)
            
            # Compile LaTeX (need multiple passes for references and TOC)
            pdf_path = None
            for attempt in range(self.max_attempts):
                success = self._run_latex_compilation(tex_file, temp_path, attempt + 1)
                if not success:
                    break
                
                # Always run at least 2 passes for proper cross-references and TOC
                # Check if PDF was generated after the first pass
                temp_pdf = temp_path / f"{output_filename}.pdf"
                if temp_pdf.exists() and attempt >= 1:  # Require at least 2 passes
                    # Copy PDF to output directory
                    final_pdf = self.output_dir / f"{output_filename}.pdf"
                    shutil.copy2(temp_pdf, final_pdf)
                    pdf_path = final_pdf
                    break
            
            # Copy log file for debugging
            log_file = temp_path / f"{output_filename}.log"
            if log_file.exists():
                shutil.copy2(log_file, self.output_dir / f"{output_filename}.log")
            
            return pdf_path
    
    def _run_latex_compilation(self, tex_file: Path, work_dir: Path, attempt: int) -> bool:
        """Run a single LaTeX compilation attempt."""
        try:
            cmd = [
                self.latex_engine,
                '-interaction=nonstopmode',
                '-halt-on-error',
                f'-output-directory={work_dir}',
                f'{tex_file.name}'  # Use just the filename since we're in the work_dir
            ]
            
            print(f"Compilation attempt {attempt}/{self.max_attempts}...")
            
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',  # Ignore encoding errors
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"LaTeX compilation failed (attempt {attempt}):")
                print("STDOUT:", result.stdout[-1000:])  # Last 1000 chars
                print("STDERR:", result.stderr[-1000:])
                return False
            
            print(f"Compilation attempt {attempt} successful")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"LaTeX compilation timed out (attempt {attempt})")
            return False
        except Exception as e:
            print(f"Error during LaTeX compilation (attempt {attempt}): {e}")
            return False
    
    def _copy_referenced_images(self, latex_content: str, temp_dir: Path):
        """Copy image files referenced in LaTeX to the temporary directory."""
        import re
        from config import TARAGON_ROOT
        
        # Find all includegraphics references
        image_pattern = r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}'
        images = re.findall(image_pattern, latex_content)
        
        for image_path in images:
            # Clean up the path
            image_path = image_path.strip()
            
            # Resolve relative to Taragon root
            source_path = TARAGON_ROOT / image_path
            
            if source_path.exists():
                # Create subdirectories in temp if needed
                dest_path = temp_dir / image_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(source_path, dest_path)
                    print(f"Copied image: {image_path}")
                except Exception as e:
                    print(f"Warning: Could not copy image {image_path}: {e}")
            else:
                print(f"Warning: Image not found: {source_path}")
    
    def clean_auxiliary_files(self, base_filename: str = "taragon_complete"):
        """Clean up auxiliary LaTeX files."""
        extensions = ['.aux', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk', '.synctex.gz']
        
        for ext in extensions:
            file_path = self.output_dir / f"{base_filename}{ext}"
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"Cleaned: {file_path.name}")
                except Exception as e:
                    print(f"Warning: Could not clean {file_path.name}: {e}")
    
    def get_compilation_info(self) -> dict:
        """Get information about the LaTeX installation."""
        info = {
            'latex_available': self.check_latex_installation(),
            'latex_engine': self.latex_engine,
            'output_directory': str(self.output_dir),
            'required_packages': self.get_required_packages()
        }
        
        if info['latex_available']:
            try:
                result = subprocess.run(
                    [self.latex_engine, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                # Extract version from first line
                first_line = result.stdout.split('\n')[0] if result.stdout else "Unknown version"
                info['latex_version'] = first_line
            except Exception:
                info['latex_version'] = "Unknown version"
        
        return info


if __name__ == "__main__":
    generator = PDFGenerator()
    info = generator.get_compilation_info()
    
    print("PDF Generator Information:")
    for key, value in info.items():
        if isinstance(value, list):
            print(f"{key}: {', '.join(value)}")
        else:
            print(f"{key}: {value}")
    
    if not info['latex_available']:
        print("\nWarning: LaTeX is not available. Please install a LaTeX distribution like:")
        print("- TeX Live (recommended)")
        print("- MiKTeX") 
        print("- MacTeX (on macOS)")
        print(f"\nMake sure '{generator.latex_engine}' is in your PATH.")