# Pen Plotter G-code Generator

A Python-based G-code generator that converts images and vector files into toolpaths suitable for pen plotters. Supports JPG, PNG, SVG input formats with raster and vector processing capabilities.

## Features

✓ **Image Processing**
  - Support for JPG, PNG formats
  - Automatic edge detection (Canny or Sobel algorithms)
  - Binary thresholding for high-contrast images
  - Contour extraction for path generation

✓ **Vector Processing**
  - Direct SVG path extraction
  - Automatic path normalization
  - Support for complex vector graphics

✓ **G-code Generation**
  - Standard G-code with absolute positioning (G90)
  - Configurable feedrate (F parameter)
  - Flexible pen control: Z-axis moves or spindle commands (M3/M5)
  - Origin offset configuration
  - Work area constraints
  - Automatic path optimization (nearest-neighbor ordering)

✓ **User Interface**
  - Tkinter-based GUI with preview
  - Real-time scaling and rotation controls
  - Path visualization canvas
  - File browser integration
  - Configuration of plotter settings

✓ **Command-Line Interface**
  - Full CLI support for automation
  - Scriptable processing pipeline
  - Batch conversion capabilities

## Project Structure

```
gcodeGen/
├── src/
│   ├── processors/          # File processing modules
│   │   ├── image_processor.py    # Raster image handling
│   │   └── vector_processor.py   # SVG/vector handling
│   ├── gcode/               # G-code generation
│   │   └── generator.py          # G-code engine
│   ├── gui/                 # GUI application
│   │   └── app.py                # Tkinter interface
│   ├── utils/               # Utilities
│   │   ├── config.py             # Configuration dataclasses
│   │   └── transforms.py         # Coordinate transformations
│   └── cli.py               # Command-line interface
├── main.py                  # GUI entry point
├── requirements.txt         # Python dependencies
└── output/                  # Generated G-code files
```

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the repository:**
   ```bash
   cd gcodeGen
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode (Recommended for Interactive Use)

Launch the graphical interface:

```bash
python main.py
```

**Steps:**
1. Click "Browse" to select an input file (JPG, PNG, or SVG)
2. Adjust scaling:
   - **Width (mm):** Set the desired output width
   - **Height (mm):** Set the desired output height (auto-scales if maintaining aspect ratio)
3. Set rotation angle if needed (0-360°)
4. Configure plotter settings:
   - **Feedrate:** Movement speed (typically 200-500 mm/min)
   - **Origin X/Y:** Start coordinates offset from home position
5. Click "Preview" to visualize paths
6. Click "Generate" to create G-code file
7. Select output location and save

### CLI Mode (For Automation/Batch Processing)

**Basic usage:**
```bash
python src/cli.py --input image.jpg --output output.gcode
```

**Full example with all options:**
```bash
python src/cli.py \
  --input drawing.png \
  --output my_drawing.gcode \
  --width 150 \
  --height 100 \
  --feedrate 400 \
  --origin-x 50 \
  --origin-y 50 \
  --work-area-x 200 \
  --work-area-y 200 \
  --edge-method canny \
  --threshold 127
```

**CLI Arguments:**
```
--input, -i           Input file (JPG, PNG, SVG) [REQUIRED]
--output, -o          Output G-code file (default: output.gcode)
--width, -w           Target width in mm (default: 100)
--height, -h          Target height in mm (auto-calculated if omitted)
--feedrate, -f        Feedrate in mm/min (default: 300)
--origin-x            X origin offset in mm (default: 0)
--origin-y            Y origin offset in mm (default: 0)
--work-area-x         Work area X limit in mm (default: 200)
--work-area-y         Work area Y limit in mm (default: 200)
--threshold           Threshold for image processing 0-255 (default: 127)
--edge-method         Edge detection: 'canny' or 'sobel' (default: canny)
--no-z-axis           Use M3/M5 spindle commands instead of Z-axis moves
```

## G-Code Output Format

The generator produces standard G-code with:

**Coordinate System:**
- Absolute positioning (G90)
- Origin configurable via offset parameters
- Work area boundaries enforced

**Pen Control Options:**

*Option 1: Z-axis moves (default for compatible machines)*
```gcode
G0 Z5    ; Pen up
G0 Z0    ; Pen down
```

*Option 2: Spindle commands (with --no-z-axis flag)*
```gcode
M5       ; Pen up (spindle off)
M3 S255  ; Pen down (spindle on, full power)
```

**Example G-code output:**
```gcode
; G-code for Pen Plotter
; Generated: 2025-05-09 14:30:45
; Source: image.jpg
; Work area: X[0-200] Y[0-200]
; Feedrate: 300 mm/min

G90                    ; Absolute positioning
G0 X0 Y0               ; Move to origin
G0 Z5                  ; Pen up
F300                   ; Set feedrate

; Path 1
G0 X10.000 Y10.000    ; Move to start (pen up)
G0 Z0                  ; Pen down
G1 X10.100 Y10.200    ; Draw line
G1 X10.200 Y10.400    ; Draw line
... (more lines)
G0 Z5                  ; Pen up at end of path

; Return to origin and end
G0 Z5
G0 X0 Y0
M30                    ; End program
```

## Configuration

### Plotter Configuration (config.py)

Edit `src/utils/config.py` to customize default settings:

```python
@dataclass
class PlotterConfig:
    feedrate: float = 300.0              # Movement speed (mm/min)
    pen_up_z: float = 5.0                # Z height for pen up
    pen_down_z: float = 0.0              # Z height for pen down
    origin_x: float = 0.0                # X start offset (mm)
    origin_y: float = 0.0                # Y start offset (mm)
    work_area_x: float = 200.0           # Max X travel (mm)
    work_area_y: float = 200.0           # Max Y travel (mm)
    use_z_axis: bool = True              # Z moves vs spindle commands
```

### Image Processing Configuration

For images, customize edge detection and thresholding in `config.py`:

```python
@dataclass
class ImageProcessingConfig:
    threshold_value: int = 127           # Binary threshold (0-255)
    blur_kernel: int = 3                 # Gaussian blur size
    edge_detection_method: str = "canny" # "canny" or "sobel"
    min_line_width: float = 0.5          # Minimum contour size (mm)
```

## API Usage (Python)

Use the modules directly in your own Python code:

```python
from src.processors.image_processor import ImageProcessor
from src.processors.vector_processor import VectorProcessor
from src.gcode.generator import GCodeGenerator
from src.utils.config import PlotterConfig

# Process an image
processor = ImageProcessor("image.jpg")
processor.edge_detection(method="canny", blur_kernel=3)
contours = processor.extract_contours(min_area=10.0)
paths = processor.normalize_contours(contours, target_width=100.0)

# Or process SVG
svg_processor = VectorProcessor("drawing.svg")
svg_paths = svg_processor.extract_paths()
paths = svg_processor.normalize_paths(svg_paths, target_width=100.0)

# Generate G-code
config = PlotterConfig(feedrate=400, origin_x=50, origin_y=50)
generator = GCodeGenerator(config)
gcode = generator.generate_from_paths(paths, source_filename="image.jpg")
generator.save_to_file(gcode, "output.gcode")
```

## Tips & Best Practices

### Image Processing
- **Thresholding:** Higher values emphasize lighter areas; lower values emphasize darker areas
- **Edge Detection:** 
  - Canny: Better for clear edge detection
  - Sobel: Better for gradient-based detection
- **Clean Input:** Use high-contrast images for best results

### Vector Files (SVG)
- Ensure paths are properly defined in your SVG editor
- Test with simple geometric shapes first
- Remove unnecessary metadata or transforms

### Plotter Setup
- **Feedrate:** Start conservative (200-300 mm/min) and increase gradually
- **Pen Pressure:** Adjust pen holder height for consistent line weight
- **Origin Offset:** Configure based on your plotter's home position
- **Work Area:** Set limits to prevent collisions

### Optimization
- Use "Preview" before generating to catch issues
- Check path count in status bar
- Consider simplifying complex SVG files
- Test on paper scraps first

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No paths detected from image | Increase threshold value, try different edge detection method |
| Paths extend beyond work area | Reduce scale width/height, adjust origin offset |
| G-code coordinates seem wrong | Verify origin offset and work area settings |
| SVG not processing | Ensure SVG is valid, try simplifying in editor |
| GUI won't start | Check Python version (3.8+), reinstall Tkinter if needed |

## Development & Extension

### Adding New File Format Support

1. Create processor in `src/processors/new_format_processor.py`
2. Implement methods:
   - `extract_paths()` → returns list of paths
   - `normalize_paths()` → scales to target dimensions
3. Integrate into GUI (`src/gui/app.py`) and CLI (`src/cli.py`)

### Customizing G-code Output

Modify `src/gcode/generator.py`:
- `generate_header()` - Add initialization commands
- `pen_up_command()` / `pen_down_command()` - Custom pen control
- `move_command()` - Add acceleration/jerk parameters

### Path Optimization

Enhance path ordering in `optimize_paths()` method or implement your own algorithm (TSP solver, etc.)

## License

This project is provided as-is for educational and personal use.

## Contributing

Contributions, bug reports, and feature requests welcome!

## Support

For issues or questions, please refer to the inline code documentation or open an issue in the repository.

---

**Happy plotting!** 🎨
