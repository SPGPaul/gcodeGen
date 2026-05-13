"""
Command-line interface for G-code generator.
"""

import argparse
import os
from src.processors.image_processor import ImageProcessor
from src.processors.vector_processor import VectorProcessor
from src.gcode.generator import GCodeGenerator
from src.utils.config import PlotterConfig


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert images and vector files to G-code for pen plotters"
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input file (JPG, PNG, SVG, PDF)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="output.gcode",
        help="Output G-code file (default: output.gcode)"
    )
    
    parser.add_argument(
        "--width", "-w",
        type=float,
        default=100.0,
        help="Target width in mm (default: 100)"
    )
    
    parser.add_argument(
        "--height",
        type=float,
        default=None,
        help="Target height in mm (default: auto-calculated from aspect ratio)"
    )
    
    parser.add_argument(
        "--feedrate", "-f",
        type=float,
        default=300.0,
        help="Feedrate in mm/min (default: 300)"
    )
    
    parser.add_argument(
        "--origin-x",
        type=float,
        default=0.0,
        help="X origin offset in mm (default: 0)"
    )
    
    parser.add_argument(
        "--origin-y",
        type=float,
        default=0.0,
        help="Y origin offset in mm (default: 0)"
    )
    
    parser.add_argument(
        "--work-area-x",
        type=float,
        default=200.0,
        help="Work area X limit in mm (default: 200)"
    )
    
    parser.add_argument(
        "--work-area-y",
        type=float,
        default=200.0,
        help="Work area Y limit in mm (default: 200)"
    )
    
    parser.add_argument(
        "--threshold",
        type=int,
        default=127,
        help="Threshold for image processing (0-255, default: 127)"
    )
    
    parser.add_argument(
        "--edge-method",
        choices=["canny", "sobel"],
        default="canny",
        help="Edge detection method for images (default: canny)"
    )
    
    parser.add_argument(
        "--simplify-tolerance",
        type=float,
        default=1.0,
        help="Path simplification tolerance in mm to reduce wavy artifacts from edge detection (default: 1.0, 0 = no simplification)"
    )
    
    parser.add_argument(
        "--no-z-axis",
        action="store_true",
        help="Use M3/M5 spindle commands instead of Z-axis moves"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    _, ext = os.path.splitext(args.input)
    ext = ext.lower()
    
    print(f"Processing {os.path.basename(args.input)}...")
    
    # Create config
    config = PlotterConfig(
        feedrate=args.feedrate,
        origin_x=args.origin_x,
        origin_y=args.origin_y,
        work_area_x=args.work_area_x,
        work_area_y=args.work_area_y,
        use_z_axis=not args.no_z_axis
    )
    
    try:
        # Process input file
        if ext in [".jpg", ".jpeg", ".png"]:
            print("  Detected image format")
            processor = ImageProcessor(args.input)
            processor.edge_detection(method=args.edge_method, blur_kernel=3)
            contours = processor.extract_contours(min_area=10.0)
            height = args.height or (args.width * processor.height / processor.width)
            paths = processor.normalize_contours(contours, target_width=args.width, target_height=height, simplify_tolerance=args.simplify_tolerance)
            
        elif ext == ".svg":
            print("  Detected SVG format")
            processor = VectorProcessor(args.input)
            svg_paths = processor.extract_paths()
            height = args.height or args.width
            paths = processor.normalize_paths(svg_paths, target_width=args.width, target_height=height)
            
        else:
            print(f"Error: Unsupported file format: {ext}")
            return 1
        
        print(f"  Extracted {len(paths)} paths")
        
        # Generate G-code
        print("Generating G-code...")
        generator = GCodeGenerator(config)
        gcode = generator.generate_from_paths(paths, os.path.basename(args.input))
        
        # Save output
        generator.save_to_file(gcode, args.output)
        print(f"✓ G-code saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
