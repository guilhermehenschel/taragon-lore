"""
Configuration settings for the Taragon PDF publisher.
"""
import os
from pathlib import Path

# Base paths
TARAGON_ROOT = Path(__file__).parent.parent
PUBLISHING_TOOLS_DIR = Path(__file__).parent
OUTPUT_DIR = PUBLISHING_TOOLS_DIR / "output"
TEMPLATES_DIR = PUBLISHING_TOOLS_DIR / "templates"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# File patterns and exclusions
MD_PATTERN = "**/*.md"
EXCLUDE_PATTERNS = [
    "**/.*",  # Hidden files/folders
    "**/node_modules/**",
    "**/output/**",
    "**/templates/**"
]

# LaTeX settings
LATEX_ENGINE = "xelatex"  # Better Unicode support
MAX_COMPILE_ATTEMPTS = 3

# Document structure ordering
SECTION_ORDER = [
    "README.md",
    "Geografia",
    "Religião", 
    "Pessoas",
    "Raças",
    "HomebrewPF2e",
    "Cronologia"
]

# Output filenames
LATEX_FILENAME = "taragon_complete.tex"
PDF_FILENAME = "taragon_complete.pdf"