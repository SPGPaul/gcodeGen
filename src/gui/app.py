"""
Tkinter-based GUI for G-code generator.
Provides file selection, scaling/rotation controls, path preview, and export functionality.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Canvas
import os
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageTk
import threading

from src.processors.image_processor import ImageProcessor
from src.processors.vector_processor import VectorProcessor
from src.gcode.generator import GCodeGenerator
from src.utils.config import PlotterConfig, DEFAULT_PLOTTER_CONFIG
from src.utils.transforms import transform_points


class PlotterGUI:
    """Tkinter GUI for pen plotter G-code generator."""
    
    def __init__(self, root: tk.Tk):
        """Initialize GUI."""
        self.root = root
        self.root.title("Pen Plotter G-code Generator")
        self.root.geometry("1000x700")
        
        self.config = PlotterConfig()
        self.input_file: Optional[str] = None
        self.paths: List[List[Tuple[float, float]]] = []
        self.preview_image: Optional[ImageTk.PhotoImage] = None
        
        self._create_widgets()
        self._update_config_from_gui()
    
    def _create_widgets(self) -> None:
        """Create GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: Controls
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
        
        # File selection
        ttk.Label(left_panel, text="Input File", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        file_frame = ttk.Frame(left_panel)
        file_frame.pack(fill=tk.X, pady=5)
        
        self.file_label = ttk.Label(file_frame, text="No file selected", width=30)
        self.file_label.pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Browse", command=self._select_file).pack(side=tk.LEFT, padx=5)
        
        # Scaling
        ttk.Label(left_panel, text="Scaling", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        
        ttk.Label(left_panel, text="Width (mm):").pack(anchor=tk.W)
        self.width_var = tk.DoubleVar(value=100.0)
        ttk.Scale(left_panel, from_=10, to=500, orient=tk.HORIZONTAL, variable=self.width_var).pack(fill=tk.X)
        self.width_label = ttk.Label(left_panel, text="100.0 mm")
        self.width_label.pack(anchor=tk.W)
        self.width_var.trace_add("write", lambda *args: self.width_label.config(text=f"{self.width_var.get():.1f} mm"))
        
        ttk.Label(left_panel, text="Height (mm):").pack(anchor=tk.W, pady=(10, 0))
        self.height_var = tk.DoubleVar(value=100.0)
        ttk.Scale(left_panel, from_=10, to=500, orient=tk.HORIZONTAL, variable=self.height_var).pack(fill=tk.X)
        self.height_label = ttk.Label(left_panel, text="100.0 mm")
        self.height_label.pack(anchor=tk.W)
        self.height_var.trace_add("write", lambda *args: self.height_label.config(text=f"{self.height_var.get():.1f} mm"))
        
        # Rotation
        ttk.Label(left_panel, text="Rotation", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        self.rotation_var = tk.DoubleVar(value=0.0)
        ttk.Scale(left_panel, from_=0, to=360, orient=tk.HORIZONTAL, variable=self.rotation_var).pack(fill=tk.X)
        self.rotation_label = ttk.Label(left_panel, text="0.0°")
        self.rotation_label.pack(anchor=tk.W)
        self.rotation_var.trace_add("write", lambda *args: self.rotation_label.config(text=f"{self.rotation_var.get():.1f}°"))
        
        # Path Simplification (reduces wavy paths from edge detection)
        ttk.Label(left_panel, text="Path Simplification", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        ttk.Label(left_panel, text="Simplify Tolerance (mm):", wraplength=150).pack(anchor=tk.W)
        self.simplify_var = tk.DoubleVar(value=1.0)
        ttk.Scale(left_panel, from_=0, to=10, orient=tk.HORIZONTAL, variable=self.simplify_var).pack(fill=tk.X)
        self.simplify_label = ttk.Label(left_panel, text="1.0 mm (higher = smoother)")
        self.simplify_label.pack(anchor=tk.W)
        self.simplify_var.trace_add("write", lambda *args: self.simplify_label.config(text=f"{self.simplify_var.get():.2f} mm (higher = smoother)"))
        
        # Plotter settings
        ttk.Label(left_panel, text="Plotter Settings", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        
        ttk.Label(left_panel, text="Feedrate (mm/min):").pack(anchor=tk.W)
        self.feedrate_var = tk.DoubleVar(value=300.0)
        ttk.Entry(left_panel, textvariable=self.feedrate_var, width=10).pack(anchor=tk.W)
        
        ttk.Label(left_panel, text="Origin X (mm):").pack(anchor=tk.W, pady=(5, 0))
        self.origin_x_var = tk.DoubleVar(value=0.0)
        ttk.Entry(left_panel, textvariable=self.origin_x_var, width=10).pack(anchor=tk.W)
        
        ttk.Label(left_panel, text="Origin Y (mm):").pack(anchor=tk.W, pady=(5, 0))
        self.origin_y_var = tk.DoubleVar(value=0.0)
        ttk.Entry(left_panel, textvariable=self.origin_y_var, width=10).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Preview", command=self._preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Generate", command=self._generate).pack(side=tk.LEFT, padx=2)
        
        # Right panel: Preview
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(right_panel, text="Path Preview", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.canvas = Canvas(right_panel, bg="white", width=400, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _select_file(self) -> None:
        """Select input file."""
        filetypes = (
            ("Image Files", "*.jpg *.jpeg *.png"),
            ("Vector Files", "*.svg"),
            ("All Files", "*.*")
        )
        filename = filedialog.askopenfilename(filetypes=filetypes)
        
        if filename:
            self.input_file = filename
            self.file_label.config(text=os.path.basename(filename))
            self.status_var.set(f"Loaded: {os.path.basename(filename)}")
    
    def _preview(self) -> None:
        """Generate and preview paths."""
        if not self.input_file:
            messagebox.showwarning("Warning", "Please select an input file first")
            return
        
        self.status_var.set("Processing...")
        self.root.update()
        
        try:
            self._process_file()
            self._draw_preview()
            self.status_var.set(f"Preview ready ({len(self.paths)} paths)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {str(e)}")
            self.status_var.set("Error processing file")
    
    def _process_file(self) -> None:
        """Process input file and extract paths."""
        if not self.input_file:
            return
        
        _, ext = os.path.splitext(self.input_file)
        ext = ext.lower()
        
        # Update config from GUI
        self._update_config_from_gui()
        
        width = self.width_var.get()
        height = self.height_var.get()
        rotation = self.rotation_var.get()
        simplify = self.simplify_var.get()
        
        try:
            if ext in [".jpg", ".jpeg", ".png"]:
                processor = ImageProcessor(self.input_file)
                processor.edge_detection(method="canny", blur_kernel=3)
                contours = processor.extract_contours(min_area=10.0)
                self.paths = processor.normalize_contours(contours, target_width=width, target_height=height, simplify_tolerance=simplify)
            elif ext == ".svg":
                processor = VectorProcessor(self.input_file)
                paths = processor.extract_paths()
                self.paths = processor.normalize_paths(paths, target_width=width, target_height=height)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
            
            # Apply rotation if needed
            if rotation != 0:
                center = (width / 2, height / 2)
                self.paths = [
                    transform_points(path, rotation=rotation, rotation_center=center)
                    for path in self.paths
                ]
        
        except Exception as e:
            raise e
    
    def _draw_preview(self) -> None:
        """Draw paths on canvas."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 400
            canvas_height = 400
        
        self.canvas.delete("all")
        
        if not self.paths:
            self.canvas.create_text(canvas_width // 2, canvas_height // 2, text="No paths to display")
            return
        
        # Calculate scale to fit canvas
        all_points = []
        for path in self.paths:
            all_points.extend(path)
        
        if not all_points:
            return
        
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        width = max_x - min_x
        height = max_y - min_y
        
        if width == 0:
            width = 1
        if height == 0:
            height = 1
        
        scale_x = (canvas_width - 20) / width
        scale_y = (canvas_height - 20) / height
        scale = min(scale_x, scale_y)
        
        # Draw paths
        for path in self.paths:
            points_scaled = []
            for x, y in path:
                px = 10 + (x - min_x) * scale
                py = 10 + (y - min_y) * scale
                points_scaled.append((px, py))
            
            if len(points_scaled) > 1:
                for i in range(len(points_scaled) - 1):
                    x1, y1 = points_scaled[i]
                    x2, y2 = points_scaled[i + 1]
                    self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)
    
    def _generate(self) -> None:
        """Generate G-code and save to file."""
        if not self.paths:
            messagebox.showwarning("Warning", "Please preview a file first")
            return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".gcode",
            filetypes=(("G-code Files", "*.gcode"), ("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        
        if not output_file:
            return
        
        try:
            self._update_config_from_gui()
            generator = GCodeGenerator(self.config)
            gcode = generator.generate_from_paths(self.paths, os.path.basename(self.input_file))
            generator.save_to_file(gcode, output_file)
            messagebox.showinfo("Success", f"G-code saved to:\n{output_file}")
            self.status_var.set(f"Saved: {os.path.basename(output_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate G-code: {str(e)}")
    
    def _update_config_from_gui(self) -> None:
        """Update plotter config from GUI values."""
        self.config.feedrate = self.feedrate_var.get()
        self.config.origin_x = self.origin_x_var.get()
        self.config.origin_y = self.origin_y_var.get()


def run_gui() -> None:
    """Launch GUI application."""
    root = tk.Tk()
    app = PlotterGUI(root)
    root.mainloop()
