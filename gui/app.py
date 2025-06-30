import tkinter as tk
from tkinter import ttk

from gui.panels import (
    FilePanel, 
    AxisPanel, 
    GuidelinePanel,
    MaterialsPanel, 
    UnitCellPanel,
    ColorPanel
)
from gui.plot_handler import PlotHandler

class AshbyPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ashby Plot Generator")
        self.root.geometry("1200x800")
        
        # Create shared variables
        self.variables = self.create_variables()
        
        # Create main layout
        self.create_layout()
        
        # Initialize plot handler
        self.plot_handler = PlotHandler(self.plot_frame, self.variables)
        
    def create_variables(self):
        """Create and return dictionary of all shared variables"""
        variables = {
            # File variables
            'file_path': tk.StringVar(),
            'data_type': tk.StringVar(value="mix"),
            'figure_type': tk.StringVar(value="presentation"),
            'log_flag': tk.BooleanVar(value=True),
            
            # Axis variables
            'x_axis_quantity': tk.StringVar(),
            'y_axis_quantity': tk.StringVar(),
            'x_min': tk.StringVar(value="10"),
            'x_max': tk.StringVar(value="30000"),
            'y_min': tk.StringVar(value="1E-4"),
            'y_max': tk.StringVar(value="1E3"),
            'x_axis_unit': tk.StringVar(),
            'y_axis_unit': tk.StringVar(),
            'axis_linewidth': tk.StringVar(value="1.0"),
            'show_top_spine': tk.BooleanVar(value=True),
            'show_right_spine': tk.BooleanVar(value=True),
            
            # Guideline variables
            'guideline_flag': tk.BooleanVar(value=True),
            'guideline_power': tk.StringVar(value="2"),
            'guideline_x_min': tk.StringVar(value="1E1"),
            'guideline_x_max': tk.StringVar(value="1E5"),
            'guideline_string': tk.StringVar(value=r"$\frac{E^{1/2}}{\rho} \equiv k$"),
            'guideline_y_intercept': tk.StringVar(value="1E-4"),
            'guideline_string_pos_x': tk.StringVar(value="65"),
            'guideline_string_pos_y': tk.StringVar(value="3"),
            
            # Material variables
            'individual_material_flag': tk.BooleanVar(value=False),
            'unique_categories': [],
            'custom_colors': {},
            
            # Unit cell variables
            'unit_cell_flag': tk.BooleanVar(value=False),
            'unit_cell_material': tk.StringVar(value="foamed elastomer"),
            
            # Standard properties list
            'standard_properties': [
                "Density", "Young Modulus", "Tensile Strength", "Fracture Toughness", 
                "Thermal Conductivity", "Thermal expansion", "Resistivity", 
                "Poisson", "Poisson difference"
            ]
        }
        return variables
    
    def create_layout(self):
        """Create the main application layout"""
        # Main paned window - left for controls, right for plot
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        control_frame = ttk.Frame(main_paned)
        main_paned.add(control_frame, weight=1)
        
        # Right panel - Plot
        self.plot_frame = ttk.Frame(main_paned)
        main_paned.add(self.plot_frame, weight=3)
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Add tabs
        file_panel = FilePanel(notebook, self.variables, self.update_ui_after_file_load)
        self.axis_panel = AxisPanel(notebook, self.variables)
        guideline_panel = GuidelinePanel(notebook, self.variables)
        materials_panel = MaterialsPanel(notebook, self.variables)
        unit_cell_panel = UnitCellPanel(notebook, self.variables)
        self.color_panel = ColorPanel(notebook, self.variables)
        
        notebook.add(file_panel, text="File")
        notebook.add(self.axis_panel, text="Axis Settings")
        notebook.add(guideline_panel, text="Guidelines")
        notebook.add(materials_panel, text="Materials")
        notebook.add(unit_cell_panel, text="Unit Cells")
        notebook.add(self.color_panel, text="Colors")
        
        # Bottom buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Button(button_frame, text="Generate Plot", command=self.refresh_plot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Plot", command=self.save_plot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
    
    def update_ui_after_file_load(self):
        """Callback to refresh UI elements after a file is loaded."""
        if hasattr(self, 'axis_panel'):
            self.axis_panel.update_axis_options()
        if hasattr(self, 'color_panel'):
            self.color_panel.update_color_options()

    def refresh_plot(self):
        """Refresh the plot with current settings"""
        self.plot_handler.generate_plot()
    
    def save_plot(self):
        """Save the current plot to a file"""
        self.plot_handler.save_plot() 