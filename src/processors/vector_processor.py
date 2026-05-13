"""
Vector processor for SVG files.
Extracts and normalizes paths from SVG documents.
"""

from typing import List, Tuple, Optional
import xml.etree.ElementTree as ET
from svgpathtools import svg2paths, parse_path
import os
import re


class VectorProcessor:
    """Process SVG files and extract toolpaths."""
    
    def __init__(self, svg_path: str):
        """
        Initialize with an SVG file.
        
        Args:
            svg_path: Path to SVG file
        
        Raises:
            FileNotFoundError: If SVG file doesn't exist.
            ValueError: If SVG cannot be parsed.
        """
        if not os.path.exists(svg_path):
            raise FileNotFoundError(f"SVG file not found: {svg_path}")
        
        self.svg_path = svg_path
        
        try:
            self.paths, self.attributes = svg2paths(svg_path)
        except Exception as e:
            raise ValueError(f"Failed to parse SVG: {e}")
        
        # Try to extract viewBox and dimensions
        self._parse_svg_dimensions()
    
    def _parse_svg_dimensions(self) -> None:
        """Parse SVG dimensions from XML."""
        try:
            tree = ET.parse(self.svg_path)
            root = tree.getroot()
            
            # Remove namespace if present
            if '}' in root.tag:
                namespace = root.tag.split('}')[0] + '}'
            else:
                namespace = ''
            
            # Extract viewBox
            viewbox = root.get('viewBox')
            if viewbox:
                parts = viewbox.split()
                self.viewbox = tuple(float(p) for p in parts)
            else:
                self.viewbox = None
            
            # Extract width and height
            width = root.get('width')
            height = root.get('height')
            
            self.svg_width = float(width.rstrip('pxemcmmin')) if width else None
            self.svg_height = float(height.rstrip('pxemcmmin')) if height else None
            
        except Exception:
            self.viewbox = None
            self.svg_width = None
            self.svg_height = None
    
    def extract_paths(self, simplify: bool = True) -> List[List[Tuple[float, float]]]:
        """
        Extract all paths from SVG as lists of points.
        
        Args:
            simplify: Whether to simplify paths
        
        Returns:
            List of paths, each path is a list of (x, y) points
        """
        all_paths = []
        
        for path in self.paths:
            points = []
            # Sample points along the path
            for i in np.linspace(0, 1, max(2, int(path.length() / 1.0))):
                try:
                    point = path.point(i)
                    points.append((point.real, point.imag))
                except Exception:
                    continue
            
            if len(points) >= 2:
                all_paths.append(points)
        
        return all_paths
    
    def normalize_paths(
        self,
        paths: List[List[Tuple[float, float]]],
        target_width: float = 100.0,
        target_height: Optional[float] = None,
        maintain_aspect: bool = True
    ) -> List[List[Tuple[float, float]]]:
        """
        Normalize SVG paths to target dimensions.
        
        Args:
            paths: List of paths in SVG coordinates
            target_width: Target width in mm
            target_height: Target height in mm (if None, derived from aspect ratio)
            maintain_aspect: Whether to maintain aspect ratio
        
        Returns:
            Normalized paths in real-world coordinates
        """
        if not paths:
            return []
        
        # Calculate bounding box
        all_points = []
        for path in paths:
            all_points.extend(path)
        
        if not all_points:
            return []
        
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        svg_width = max_x - min_x
        svg_height = max_y - min_y
        
        if svg_width == 0 or svg_height == 0:
            return paths
        
        # Calculate scaling
        if maintain_aspect:
            if target_height is None:
                target_height = target_width * (svg_height / svg_width)
            
            scale_x = target_width / svg_width
            scale_y = target_height / svg_height
            scale = min(scale_x, scale_y)
        else:
            scale_x = target_width / svg_width
            scale_y = (target_height or target_width) / svg_height
            scale = scale_x
        
        # Apply normalization
        normalized = []
        for path in paths:
            norm_path = []
            for x, y in path:
                nx = (x - min_x) * scale
                ny = (y - min_y) * scale
                norm_path.append((nx, ny))
            normalized.append(norm_path)
        
        return normalized
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Get bounding box of all paths.
        
        Returns:
            (min_x, min_y, max_x, max_y)
        """
        paths = self.extract_paths(simplify=False)
        if not paths:
            return (0, 0, 0, 0)
        
        all_points = []
        for path in paths:
            all_points.extend(path)
        
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        
        return (min(xs), min(ys), max(xs), max(ys))


# Import numpy for path sampling
import numpy as np
