"""
Coordinate transformation utilities for scaling, rotation, and translation.
"""

import math
from typing import List, Tuple


def scale_point(point: Tuple[float, float], scale_x: float, scale_y: float) -> Tuple[float, float]:
    """Scale a point by factors."""
    return (point[0] * scale_x, point[1] * scale_y)


def rotate_point(point: Tuple[float, float], angle_degrees: float, center: Tuple[float, float] = (0, 0)) -> Tuple[float, float]:
    """Rotate a point around a center point. Angle in degrees, counter-clockwise."""
    angle_rad = math.radians(angle_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # Translate to origin
    x, y = point[0] - center[0], point[1] - center[1]
    
    # Rotate
    rotated_x = x * cos_a - y * sin_a
    rotated_y = x * sin_a + y * cos_a
    
    # Translate back
    return (rotated_x + center[0], rotated_y + center[1])


def translate_point(point: Tuple[float, float], offset: Tuple[float, float]) -> Tuple[float, float]:
    """Translate a point by an offset."""
    return (point[0] + offset[0], point[1] + offset[1])


def transform_points(
    points: List[Tuple[float, float]],
    scale: Tuple[float, float] = (1.0, 1.0),
    rotation: float = 0.0,
    offset: Tuple[float, float] = (0.0, 0.0),
    rotation_center: Tuple[float, float] = (0, 0)
) -> List[Tuple[float, float]]:
    """Apply scale, rotation, and translation to a list of points."""
    transformed = []
    for point in points:
        # Apply scale
        point = scale_point(point, scale[0], scale[1])
        # Apply rotation
        if rotation != 0:
            point = rotate_point(point, rotation, rotation_center)
        # Apply offset
        point = translate_point(point, offset)
        transformed.append(point)
    return transformed


def clamp_point(point: Tuple[float, float], min_x: float, max_x: float, min_y: float, max_y: float) -> Tuple[float, float]:
    """Clamp a point to specified bounds."""
    return (
        max(min_x, min(max_x, point[0])),
        max(min_y, min(max_y, point[1]))
    )


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def simplify_path(path: List[Tuple[float, float]], tolerance: float = 1.0) -> List[Tuple[float, float]]:
    """
    Simplify a path using Ramer-Douglas-Peucker algorithm.
    Removes points that are within 'tolerance' distance from the line formed by their neighbors.
    """
    if len(path) < 3:
        return path
    
    # Find the point with maximum distance from line p1-p2
    dmax = 0.0
    index = 0
    start = path[0]
    end = path[-1]
    
    for i in range(1, len(path) - 1):
        d = point_to_line_distance(path[i], start, end)
        if d > dmax:
            dmax = d
            index = i
    
    # If max distance is greater than tolerance, recursively simplify
    if dmax > tolerance:
        rec1 = simplify_path(path[:index+1], tolerance)
        rec2 = simplify_path(path[index:], tolerance)
        resultlist = rec1[:-1] + rec2
    else:
        resultlist = [start, end]
    
    return resultlist


def point_to_line_distance(point: Tuple[float, float], line_start: Tuple[float, float], line_end: Tuple[float, float]) -> float:
    """Calculate perpendicular distance from point to line."""
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    den = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    
    if den == 0:
        return distance(point, line_start)
    
    return num / den
