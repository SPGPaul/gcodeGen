# Quick Start Guide

## Installation (5 minutes)

### 1. Check Python Version
```bash
python --version
```
Requires Python 3.8 or higher

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

That's it! The following packages will be installed:
- **Pillow**: Image processing
- **opencv-python**: Computer vision operations
- **numpy**: Numerical computing
- **svgpathtools**: SVG handling

## Usage

### Option A: GUI (Easiest)
```bash
python main.py
```

Steps:
1. Click "Browse" → Select your image (JPG, PNG) or SVG file
2. Adjust **Width** slider to desired size (mm)
3. Adjust **Height** if needed (or keep auto-scale)
4. Adjust **Rotation** if needed (degrees)
5. Click "Preview" to see the paths
6. Click "Generate" → Choose output filename
7. Done! G-code saved to your file

### Option B: Command Line (For Scripts/Automation)

**Basic usage:**
```bash
python -m src.cli --input myimage.jpg --output output.gcode
```

**With options:**
```bash
python -m src.cli \
  --input myimage.png \
  --output output.gcode \
  --width 100 \
  --feedrate 300 \
  --origin-x 10 \
  --origin-y 10
```

**Get help:**
```bash
python -m src.cli --help
```

## Common Tasks

### Process a JPG Image
```bash
python -m src.cli --input drawing.jpg --output drawing.gcode --width 150
```

### Process a PNG with Edge Detection
```bash
python -m src.cli --input photo.png --output photo.gcode --edge-method canny --threshold 150
```

### Process an SVG File
```bash
python -m src.cli --input drawing.svg --output drawing.gcode --width 100
```

### Adjust for Your Plotter
```bash
python -m src.cli \
  --input image.jpg \
  --output output.gcode \
  --width 200 \
  --feedrate 400 \
  --work-area-x 250 \
  --work-area-y 250 \
  --origin-x 50 \
  --origin-y 50
```

## Output

The generated G-code file contains:
- ✓ Absolute coordinates (G90)
- ✓ Move commands (G0, G1)
- ✓ Pen up/down commands (Z moves or M3/M5)
- ✓ Feedrate setting (F)
- ✓ Comments with source info
- ✓ Clean termination (M30)

Example first few lines:
```gcode
; G-code for Pen Plotter
; Generated: 2025-05-09 10:21:48
; Source: image.jpg
G90 ; Absolute positioning
G0 X0 Y0 ; Move to origin
G0 Z5 ; Pen up
F300 ; Set feedrate
```

## Tips

1. **Start with small images** to test your plotter
2. **Use high-contrast images** for best edge detection
3. **Adjust threshold** (0-255) if paths don't look right
   - Higher = emphasizes lighter areas
   - Lower = emphasizes darker areas
4. **Test the preview** before generating
5. **Check work area limits** to avoid out-of-bounds moves
6. **Save generated G-code** before modifying

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No paths detected | Try different edge detection method or threshold value |
| Paths look wrong | Adjust threshold, try other edge detection method |
| Coordinates seem off | Check origin offset and work area settings |
| File not found | Use full path or relative path to your input file |
| GUI won't start | Make sure Tkinter is available (usually included with Python) |

## Project Structure

```
gcodeGen/
├── main.py              # Run this for GUI
├── src/
│   ├── cli.py          # Command-line interface
│   ├── processors/     # Image and SVG processing
│   ├── gcode/          # G-code generation
│   ├── gui/            # GUI application
│   └── utils/          # Helpers and config
├── output/             # Where G-code files are saved
├── README.md           # Full documentation
└── requirements.txt    # Python dependencies
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [.github/copilot-instructions.md](.github/copilot-instructions.md) for architecture
- Experiment with different images and settings
- Look at generated G-code to understand the format

## Need Help?

1. Check README.md for detailed documentation
2. Run `python -m src.cli --help` for CLI options
3. Use `--edge-method` canny or `--threshold` to fine-tune image processing
4. Try smaller images first to debug issues

---

**Happy plotting!** 🎨
