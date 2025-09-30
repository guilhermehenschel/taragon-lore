# Taragon PDF Publisher

A modular Python system for generating professional PDF documents from Markdown files in the Taragon campaign setting.

## Features

- **Modular Architecture**: Single-purpose Python files for maintainability
- **Jinja2 Templates**: Flexible LaTeX template system
- **Cross-References**: Automatic resolution of Markdown links between files
- **Image Support**: Automatic inclusion of referenced images
- **Professional Output**: Book-style PDF with proper typography
- **Hierarchical Organization**: Respects folder structure and section ordering

## File Structure

```
publishing_tools/
├── run_pdf_publisher.py    # Main script
├── config.py              # Configuration settings
├── file_scanner.py        # Markdown file discovery
├── markdown_processor.py  # Content processing and conversion
├── latex_templates.py     # Jinja2 template system
├── pdf_generator.py       # LaTeX compilation
├── setup.py              # Dependency installer
├── requirements.txt       # Python dependencies
├── templates/
│   └── main_document.tex  # LaTeX document template
└── output/               # Generated files
```

## Prerequisites

### Required Software

1. **Python 3.7+** with pip
2. **LaTeX Distribution** (one of):
   - [TeX Live](https://tug.org/texlive/) (recommended, cross-platform)
   - [MiKTeX](https://miktex.org/) (Windows)
   - [MacTeX](https://tug.org/mactex/) (macOS)

### Python Packages

- `jinja2` - Template engine

## Installation

1. **Quick Setup** (installs dependencies and checks system):
   ```bash
   python setup.py
   ```

2. **Manual Setup**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Generate complete PDF from all Markdown files:
```bash
python run_pdf_publisher.py
```

### Options

```bash
python run_pdf_publisher.py [options]

Options:
  --output-name NAME    Set output filename base (default: taragon_complete)
  --section SECTION     Process only specific section (Geografia, Religião, etc.)
  --debug              Enable detailed debug output
  --clean-only         Only clean auxiliary LaTeX files
  --check-deps         Check system dependencies
```

### Examples

```bash
# Generate complete guide
python run_pdf_publisher.py

# Generate only Geography section
python run_pdf_publisher.py --section Geografia

# Custom output name with debug info
python run_pdf_publisher.py --output-name taragon_geography --section Geografia --debug

# Check if system is properly configured
python run_pdf_publisher.py --check-deps

# Clean up auxiliary files
python run_pdf_publisher.py --clean-only
```

## Output

The system generates:
- **PDF File**: `output/taragon_complete.pdf` (or custom name)
- **LaTeX Source**: `output/taragon_complete.tex` (for debugging)
- **Log File**: `output/taragon_complete.log` (compilation details)

## Section Organization

Files are organized in the following order:
1. **README.md** - Introduction
2. **Geografia** - Geography and locations
3. **Religião** - Religion and deities  
4. **Pessoas** - People and characters
5. **Raças** - Races and species
6. **HomebrewPF2e** - Game mechanics
7. **Cronologia** - Timeline and history

## Customization

### Templates

Edit `templates/main_document.tex` to customize:
- Document layout and styling
- Font choices
- Color schemes
- Page formatting

### Configuration

Modify `config.py` to adjust:
- Section ordering
- File patterns
- LaTeX engine selection
- Output paths

### Processing

Extend `markdown_processor.py` to add:
- Custom Markdown syntax
- Special formatting rules
- Additional cross-reference types

## Troubleshooting

### Common Issues

1. **"LaTeX not found"**
   - Install TeX Live, MiKTeX, or MacTeX
   - Ensure LaTeX binaries are in your PATH

2. **"Jinja2 not found"**
   - Run: `pip install jinja2`

3. **Image not found warnings**
   - Check image file paths in Markdown
   - Verify images exist relative to Taragon root

4. **PDF compilation fails**
   - Check the `.log` file in the output directory
   - Ensure all referenced images exist
   - Try with `--debug` flag for more information

### Debug Information

Run with `--debug` flag to see:
- Detailed file discovery process
- Content processing steps
- LaTeX compilation output
- Image copying operations

### Log Files

LaTeX compilation logs are saved to `output/[filename].log` and contain:
- Package loading information
- Warning and error messages
- File processing details

## System Requirements

- **RAM**: 1GB+ (for large documents)
- **Disk**: 500MB+ (for LaTeX distribution)
- **OS**: Windows, macOS, or Linux

## Development

### Adding New Processors

1. Create new module in the publishing_tools directory
2. Follow single-responsibility principle
3. Add to imports in `run_pdf_publisher.py`
4. Update configuration as needed

### Template Development

1. Edit Jinja2 templates in `templates/`
2. Use `{{ variable }}` for content insertion
3. Use `{% block %}` for conditional logic
4. Test with `--debug` flag

## License

This tool is part of the Taragon campaign setting project.