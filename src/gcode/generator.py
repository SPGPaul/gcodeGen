"""
G-code generator for pen plotter.
Converts toolpaths to standard G-code with configurable feedrate, pen commands, and work area limits.
"""

from typing import List, Tuple, Optional
from datetime import datetime
from src.utils.config import PlotterConfig


class GCodeGenerator:
    """Generate G-code from toolpaths."""
    
    def __init__(self, config: PlotterConfig):
        """
        Initialize G-code generator.
        
        Args:
            config: PlotterConfig with feedrate, pen commands, work area, etc.
        """
        self.config = config
        self.gcode_lines: List[str] = []
    
    def generate_header(self, filename: Optional[str] = None) -> str:
        """
        Generate G-code header with initialization commands.
        
        Args:
            filename: Optional source filename to include in comments
        
        Returns:
            Header string with comments and initial commands
        """
        header = []
        header.append("; G-code for Pen Plotter")
        header.append(f"; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if filename:
            header.append(f"; Source: {filename}")
        header.append(f"; Work area: X[0-{self.config.work_area_x}] Y[0-{self.config.work_area_y}]")
        header.append(f"; Feedrate: {self.config.feedrate} mm/min")
        header.append("; ")

        # IMPORTANT FIXES
        header.append("G21 ; Set units to millimeters")
        header.append("G90 ; Absolute positioning")
        header.append("M5 ; Pen up (start state)")
        header.append(f"G0 X{self.config.origin_x} Y{self.config.origin_y} ; Move to origin")
        header.append(f"F{self.config.feedrate} ; Set feedrate")

        return "\n".join(header)
    
    def generate_footer(self) -> str:
        """Generate G-code footer with cleanup commands."""
        footer = []
        footer.append("; ")
        footer.append("; Return to origin and end")
        footer.append("M5 ; Pen up")
        footer.append(f"G0 X{self.config.origin_x} Y{self.config.origin_y} ; Return to origin")
        footer.append("M30 ; End program")
        return "\n".join(footer)
    
    def pen_up_command(self) -> str:
        """Generate pen up command (always M5)."""
        return "M5"
    
    def pen_down_command(self) -> str:
        """Generate pen down command (always M3 S255)."""
        return "M3 S255"
    
    def move_command(self, x: float, y: float, feed: Optional[float] = None, is_cut: bool = False) -> str:
        """
        Generate movement command.
        
        Args:
            x: X coordinate
            y: Y coordinate
            feed: Optional custom feedrate
            is_cut: If True, use G1 (cut/draw); if False, use G0 (rapid)
        
        Returns:
            G-code movement command
        """
        # Clamp to work area
        x = max(self.config.origin_x, min(self.config.origin_x + self.config.work_area_x, x))
        y = max(self.config.origin_y, min(self.config.origin_y + self.config.work_area_y, y))

        # FIX: Always enforce pen state before movement
        if is_cut:
            cmd = f"{self.pen_down_command()}\nG1 X{x:.3f} Y{y:.3f}"
        else:
            cmd = f"{self.pen_up_command()}\nG0 X{x:.3f} Y{y:.3f}"

        if feed:
            cmd += f" F{feed:.1f}"

        return cmd
    
    def generate_from_paths(
        self,
        paths: List[List[Tuple[float, float]]],
        source_filename: Optional[str] = None,
        tool_offset: Tuple[float, float] = (0.0, 0.0)
    ) -> str:
        """
        Generate complete G-code from toolpaths.
        
        Args:
            paths: List of paths, each path is a list of (x, y) tuples
            source_filename: Optional source filename for header comments
            tool_offset: Apply offset to all coordinates
        
        Returns:
            Complete G-code as string
        """
        self.gcode_lines = []
        
        # Header
        self.gcode_lines.append(self.generate_header(source_filename))
        self.gcode_lines.append("")
        
        # Process each path
        for path_idx, path in enumerate(paths):
            if not path:
                continue
            
            self.gcode_lines.append(f"; Path {path_idx + 1}")
            
            # Move to start of path (pen up enforced in move_command)
            start_x = path[0][0] + tool_offset[0] + self.config.origin_x
            start_y = path[0][1] + tool_offset[1] + self.config.origin_y
            self.gcode_lines.append(self.move_command(start_x, start_y, is_cut=False))
            
            # Draw path
            for x, y in path[1:]:
                x = x + tool_offset[0] + self.config.origin_x
                y = y + tool_offset[1] + self.config.origin_y
                self.gcode_lines.append(self.move_command(x, y, is_cut=True))
            
            # Pen up at end of path
            self.gcode_lines.append(self.pen_up_command())
            self.gcode_lines.append("")
        
        # Footer
        self.gcode_lines.append(self.generate_footer())
        
        return "\n".join(self.gcode_lines)
    
    def save_to_file(self, gcode: str, filepath: str) -> None:
        """
        Save G-code to file.
        
        Args:
            gcode: G-code string
            filepath: Output file path
        """
        with open(filepath, 'w') as f:
            f.write(gcode)
    
    def optimize_paths(self, paths: List[List[Tuple[float, float]]]) -> List[List[Tuple[float, float]]]:
        """
        Optimize paths by ordering them to minimize pen-up travel distance.
        Uses nearest-neighbor heuristic.
        
        Args:
            paths: List of paths
        
        Returns:
            Reordered paths
        """
        if len(paths) <= 1:
            return paths
        
        import math
        
        def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
            return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        optimized = []
        remaining = list(range(len(paths)))
        current_idx = 0
        optimized.append(paths[current_idx])
        remaining.remove(current_idx)
        
        while remaining:
            # Find closest path endpoint
            current_end = optimized[-1][-1]
            nearest_idx = min(remaining, key=lambda i: min(
                distance(current_end, paths[i][0]),
                distance(current_end, paths[i][-1])
            ))
            
            # Check if we need to reverse the path
            if distance(current_end, paths[nearest_idx][-1]) < distance(current_end, paths[nearest_idx][0]):
                optimized.append(list(reversed(paths[nearest_idx])))
            else:
                optimized.append(paths[nearest_idx])
            
            remaining.remove(nearest_idx)
        
        return optimized
