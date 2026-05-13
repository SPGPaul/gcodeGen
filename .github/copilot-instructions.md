# G-Code Generator for Pen Plotter

## Project Overview
A Python-based G-code generator that converts images and vector files into toolpaths suitable for pen plotters. Supports JPG, PNG, SVG input formats with raster and vector processing capabilities.

## Architecture
- **src/processors**: Image and vector file processing modules
  - `image_processor.py`: Raster image handling (JPG, PNG)
  - `vector_processor.py`: SVG/vector file handling
- **src/gcode**: G-code generation engine
  - `generator.py`: G-code generation with absolute coordinates (G90)
- **src/gui**: Tkinter-based GUI application
  - `app.py`: Interactive GUI with preview and export
- **src/utils**: Configuration, coordinate transforms, and utilities
  - `config.py`: PlotterConfig and ImageProcessingConfig dataclasses
  - `transforms.py`: Coordinate transformation utilities (scale, rotate, translate)
- **src/cli.py**: Command-line interface for automation
- **main.py**: GUI entry point
- **output**: Generated G-code files directory

## Key Features
✓ Image processing (edge detection - Canny/Sobel, thresholding)
✓ SVG path extraction and normalization
✓ Configurable feedrate and pen commands
✓ Origin offset and work area constraints
✓ GUI with scaling, rotation, path preview
✓ CLI support for automation/batch processing
✓ G-code with absolute positioning (G90)
✓ Flexible pen control (Z-axis or M3/M5 spindle commands)
✓ Path optimization (nearest-neighbor ordering)
✓ Well-structured, extensible codebase

## Setup Instructions
1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Run GUI: `python main.py`
4. Or use CLI: `python -m src.cli --input image.jpg --output output.gcode`

## Usage

### GUI Mode
```bash
python main.py
```
Then:
1. Select input file (JPG, PNG, SVG)
2. Adjust scaling and rotation
3. Configure plotter settings
4. Click Preview to visualize
5. Click Generate to save G-code

### CLI Mode
```bash
python -m src.cli --input image.jpg --output output.gcode --width 100 --feedrate 300
```

## G-Code Output Format
- Absolute positioning (G90)
- Configurable feedrate (F parameter)
- Pen control: Z-axis moves OR M3/M5 spindle commands
- Origin offset support
- Work area boundaries enforced

Example:
```gcode
G90 ; Absolute positioning
G0 X0 Y0 ; Move to origin
G0 Z5 ; Pen up
F300 ; Feedrate
; ... paths ...
M30 ; End program
```

## Development Status
- ✅ Project structure created
- ✅ Core modules implemented (image, vector, gcode)
- ✅ GUI with Tkinter developed
- ✅ CLI interface implemented
- ✅ Testing and validation complete
- ✅ Documentation complete
- ✅ Ready for production use

## Installation Instructions

### Prerequisites
- Python 3.8 or higher
- pip (comes with Python)

### Install Steps
1. Navigate to project directory
2. Install dependencies: `pip install -r requirements.txt`
3. All packages installed:
   - Pillow 11.0.0 (image processing)
   - opencv-python 4.10.0.84 (CV operations)
   - numpy 1.24.3 (numerical computing)
   - svgpathtools 1.4.4 (SVG handling)

## Quick Test
```bash
# Generate test image and process it
python -m src.cli --input test_image.png --output output/test.gcode

# View generated G-code
type output/test.gcode
```

## Key Files
- [README.md](../README.md) - Full documentation
- [requirements.txt](../requirements.txt) - Python dependencies
- [main.py](../main.py) - GUI entry point
- [src/cli.py](../src/cli.py) - CLI entry point

## Extension Points
- Add new image formats: Extend `ImageProcessor`
- Add new vector formats: Create new processor class
- Customize G-code output: Modify `GCodeGenerator`
- Add new pen behaviors: Extend `pen_up_command()` / `pen_down_command()`
- Implement advanced path optimization: Enhance `optimize_paths()` method

## Troubleshooting
- **No paths detected**: Try adjusting threshold or edge detection method
- **Paths exceed work area**: Reduce scale or adjust origin offset
- **GUI won't start**: Ensure Tkinter is installed (usually included with Python)
- **SVG not processing**: Verify SVG file is valid, try simplifying

