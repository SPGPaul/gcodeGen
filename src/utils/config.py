"""
Configuration module for G-code generator.
Centralized settings for coordinates, feedrates, pen commands, and work area limits.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class PlotterConfig:
    """
    Configuration for pen plotter and G-code generation.
    
    Attributes:
        feedrate: Movement speed in mm/min (typically 200-500 for plotters)
        pen_up_z: Z-axis height for pen up (or M5 command if Z not used)
        pen_down_z: Z-axis height for pen down (or M3 S255 if Z not used)
        origin_x: X-axis offset from home position (mm)
        origin_y: Y-axis offset from home position (mm)
        work_area_x: Maximum X-axis travel (mm)
        work_area_y: Maximum Y-axis travel (mm)
        use_z_axis: If True, use Z moves for pen up/down; if False, use M3/M5 spindle commands
        acceleration: Acceleration rate in mm/s²
        corner_radius: Radius for corner smoothing (0 = no smoothing, in mm)
    """
    feedrate: float = 300.0
    pen_up_z: float = 5.0
    pen_down_z: float = 0.0
    origin_x: float = 0.0
    origin_y: float = 0.0
    work_area_x: float = 200.0
    work_area_y: float = 200.0
    use_z_axis: bool = True
    acceleration: float = 1000.0
    corner_radius: float = 0.0


@dataclass
class ImageProcessingConfig:
    """Configuration for image processing."""
    threshold_value: int = 127
    blur_kernel: int = 3
    edge_detection_method: str = "canny"  # "canny" or "sobel"
    min_line_width: float = 0.5
    simplify_tolerance: float = 1.0


# Default configurations
DEFAULT_PLOTTER_CONFIG = PlotterConfig()
DEFAULT_IMAGE_CONFIG = ImageProcessingConfig()
