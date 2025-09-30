#!/usr/bin/env python3
"""
Setup script for Taragon PDF Publisher.
Installs required dependencies and checks system requirements.
"""

import sys
import subprocess
from pathlib import Path

def install_python_dependencies():
    """Install required Python packages."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        print("📦 Installing Python dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def check_latex_installation():
    """Check if LaTeX is available."""
    engines = ['xelatex', 'pdflatex', 'lualatex']
    
    print("🔍 Checking LaTeX installation...")
    
    for engine in engines:
        try:
            result = subprocess.run(
                [engine, '--version'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ Found {engine}: {version_line}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    print("❌ No LaTeX engine found")
    print("\n📋 Please install a LaTeX distribution:")
    print("   • Windows: https://miktex.org/ or https://tug.org/texlive/")
    print("   • macOS: https://tug.org/mactex/")
    print("   • Linux: sudo apt-get install texlive-full (Ubuntu/Debian)")
    print("           sudo yum install texlive-scheme-full (RHEL/CentOS)")
    
    return False

def create_output_directory():
    """Create output directory if it doesn't exist."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory ready: {output_dir}")

def test_system():
    """Run a quick system test."""
    print("\n🧪 Running system test...")
    
    try:
        # Import our modules
        sys.path.insert(0, str(Path(__file__).parent))
        
        from file_scanner import FileScanner
        from pdf_generator import PDFGenerator
        
        # Test file scanner
        scanner = FileScanner()
        files = scanner.scan_files()
        print(f"✅ File scanner found {len(files)} Markdown files")
        
        # Test PDF generator
        generator = PDFGenerator()
        if generator.check_latex_installation():
            print("✅ PDF generator ready")
        else:
            print("❌ PDF generator not ready (LaTeX issues)")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main setup routine."""
    print("🚀 Taragon PDF Publisher Setup")
    print("=" * 40)
    
    success = True
    
    # Install Python dependencies
    if not install_python_dependencies():
        success = False
    
    # Check LaTeX
    if not check_latex_installation():
        success = False
    
    # Create directories
    create_output_directory()
    
    # Test system
    if success and not test_system():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Setup completed successfully!")
        print("\n📖 Usage:")
        print("   python run_pdf_publisher.py")
        print("   python run_pdf_publisher.py --help")
    else:
        print("❌ Setup completed with errors")
        print("   Please resolve the issues above before using the publisher")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)