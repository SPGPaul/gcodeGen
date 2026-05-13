"""
Image processor for raster files (JPG, PNG).
Supports edge detection, thresholding, and path extraction from binary images.
"""

from typing import List, Tuple, Optional
import cv2
import numpy as np
from PIL import Image
import os
from src.utils.transforms import simplify_path


class ImageProcessor:
    """Process raster images and extract toolpaths."""
    
    def __init__(self, image_path: str):
        """
        Initialize with an image file.
        
        Args:
            image_path: Path to image file (JPG, PNG, etc.)
        
        Raises:
            FileNotFoundError: If image file doesn't exist.
            ValueError: If image cannot be loaded.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        self.image_path = image_path
        self.original_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        if self.original_image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        self.processed_image = self.original_image.copy()
        self.height, self.width = self.original_image.shape
    
    def threshold(self, threshold_value: int = 127) -> np.ndarray:
        """
        Apply binary threshold to image.
        
        Args:
            threshold_value: Threshold value (0-255)
        
        Returns:
            Binary image array
        """
        _, binary = cv2.threshold(self.original_image, threshold_value, 255, cv2.THRESH_BINARY)
        self.processed_image = binary
        return binary
    
    def edge_detection(self, method: str = "canny", blur_kernel: int = 3) -> np.ndarray:
        """
        Detect edges in image using Canny or Sobel.
        
        Args:
            method: "canny" or "sobel"
            blur_kernel: Kernel size for Gaussian blur (must be odd)
        
        Returns:
            Edge-detected image
        """
        # Ensure blur kernel is odd
        if blur_kernel % 2 == 0:
            blur_kernel += 1
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(self.original_image, (blur_kernel, blur_kernel), 0)
        
        if method.lower() == "canny":
            # Canny edge detection
            edges = cv2.Canny(blurred, 100, 200)
        elif method.lower() == "sobel":
            # Sobel edge detection
            sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
            edges = np.sqrt(sobelx**2 + sobely**2).astype(np.uint8)
            _, edges = cv2.threshold(edges, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            raise ValueError(f"Unknown edge detection method: {method}")
        
        self.processed_image = edges
        return edges
    
    def invert(self) -> np.ndarray:
        """Invert the processed image (black <-> white)."""
        self.processed_image = cv2.bitwise_not(self.processed_image)
        return self.processed_image
    
    def extract_contours(self, min_area: float = 10.0) -> List[List[Tuple[int, int]]]:
        """
        Extract contours from binary image.
        
        Args:
            min_area: Minimum contour area to include (in pixels)
        
        Returns:
            List of contours, each contour is a list of (x, y) points
        """
        contours, _ = cv2.findContours(self.processed_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter by area and convert to list format
        filtered_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                # Convert contour format (N x 1 x 2) to list of points (N x 2)
                points = contour.squeeze().tolist()
                # Ensure points is a list of tuples
                if isinstance(points[0], list):
                    points = [(int(p[0]), int(p[1])) for p in points]
                else:
                    points = [(int(points[0]), int(points[1]))]
                filtered_contours.append(points)
        
        return filtered_contours
    
    def normalize_contours(
        self,
        contours: List[List[Tuple[int, int]]],
        target_width: float = 100.0,
        target_height: Optional[float] = None,
        maintain_aspect: bool = True,
        simplify_tolerance: float = 1.0
    ) -> List[List[Tuple[float, float]]]:
        """
        Normalize contours to target dimensions with optional path simplification.
        
        Args:
            contours: List of contours in image coordinates
            target_width: Target width in mm
            target_height: Target height in mm (if None, derived from aspect ratio)
            maintain_aspect: Whether to maintain aspect ratio
            simplify_tolerance: Tolerance for path simplification (0 = no simplification).
                               Using Ramer-Douglas-Peucker algorithm to remove wavy artifacts.
        
        Returns:
            Normalized contours in real-world coordinates with simplified paths
        """
        if not contours:
            return []
        
        # Calculate bounding box
        all_points = []
        for contour in contours:
            all_points.extend(contour)
        
        if not all_points:
            return []
        
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        image_width = max_x - min_x
        image_height = max_y - min_y
        
        if image_width == 0 or image_height == 0:
            return contours
        
        # Calculate scaling
        if maintain_aspect:
            if target_height is None:
                target_height = target_width * (image_height / image_width)
            
            scale_x = target_width / image_width
            scale_y = target_height / image_height
            scale = min(scale_x, scale_y)
        else:
            scale_x = target_width / image_width
            scale_y = (target_height or target_width) / image_height
            scale = scale_x
        
        # Apply normalization and simplification
        normalized = []
        for contour in contours:
            norm_contour = []
            for x, y in contour:
                nx = (x - min_x) * scale
                ny = (y - min_y) * scale
                norm_contour.append((nx, ny))
            
            # Apply path simplification to remove wavy artifacts from pixel-based edge detection
            if simplify_tolerance > 0:
                norm_contour = simplify_path(norm_contour, tolerance=simplify_tolerance)
            
            normalized.append(norm_contour)
        
        return normalized
    
    def get_dimensions(self) -> Tuple[int, int]:
        """Get original image dimensions (width, height)."""
        return (self.width, self.height)
    
    def save_processed(self, output_path: str) -> None:
        """Save processed image for debugging."""
        cv2.imwrite(output_path, self.processed_image)
