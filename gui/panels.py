import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import pandas as pd

class BasePanel(ttk.Frame):
    """Base panel class with common functionality"""
    def __init__(self, parent, variables):
        super().__init__(parent)
        self.variables = variables

class FilePanel(BasePanel):
    """Panel for file selection and basic settings"""
    def __init__(self, parent, variables, refresh_callback=None):
        super().__init__(parent, variables)
        self.refresh_callback = refresh_callback
        self.create_widgets()
        
    def create_widgets(self):
        # File selection
        ttk.Label(self, text="Material Properties File:").pack(anchor=tk.W, padx=5, pady=5)
        file_frame = ttk.Frame(self)
        file_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Entry(file_frame, textvariable=self.variables['file_path']).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.RIGHT)
        
        # Data type selection
        ttk.Label(self, text="Data Type:").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Radiobutton(self, text="Mix (Default)", variable=self.variables['data_type'], 
                       value="mix").pack(anchor=tk.W, padx=25)
        ttk.Radiobutton(self, text="Ranges Only", variable=self.variables['data_type'], 
                       value="ranges").pack(anchor=tk.W, padx=25)
        ttk.Radiobutton(self, text="Values Only", variable=self.variables['data_type'], 
                       value="values").pack(anchor=tk.W, padx=25)
        
        # Figure type selection
        ttk.Label(self, text="Figure Type:").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Radiobutton(self, text="Presentation", variable=self.variables['figure_type'], 
                       value="presentation").pack(anchor=tk.W, padx=25)
        ttk.Radiobutton(self, text="Publication", variable=self.variables['figure_type'], 
                       value="publication").pack(anchor=tk.W, padx=25)
        
        # Log-log plot option
        ttk.Checkbutton(self, text="Log-Log Plot", variable=self.variables['log_flag']).pack(anchor=tk.W, padx=5, pady=5)
    
    def browse_file(self):
        """Browse for material properties file"""
        filename = filedialog.askopenfilename(
            title="Select Material Properties File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.variables['file_path'].set(filename)
            self.load_file_columns()
    
    def load_file_columns(self):
        """Load column names from the selected Excel file for the axis combo boxes"""
        try:
            data = pd.read_excel(self.variables['file_path'].get())
            columns = data.columns.tolist()
            
            # Store the raw column names for auto-detection logic
            self.variables['excel_columns'] = columns
            
            # Remove 'Category' from the list if it exists
            if 'Category' in columns:
                columns.remove('Category')
            
            # --- Enhanced and more robust column filtering ---
            property_columns = []
            processed_bases = set()

            for col in columns:
                base_prop = col
                if ' low' in col:
                    base_prop = col.replace(' low', '')
                elif ' high' in col:
                    base_prop = col.replace(' high', '')

                if base_prop not in processed_bases:
                    # Try to convert column to numeric, coercing errors.
                    # This is robust against columns with mixed types.
                    numeric_series = pd.to_numeric(data[col], errors='coerce')
                    
                    # If the column contains at least one valid number, add its base property.
                    if not numeric_series.isnull().all():
                        property_columns.append(base_prop)
                        processed_bases.add(base_prop)

            # --- Calculate and store unique categories for the ColorPanel ---
            if 'Category' in data.columns:
                data['Category'] = data['Category'].astype(str).str.strip()
                self.variables['unique_categories'] = sorted(data['Category'].unique())
            else:
                self.variables['unique_categories'] = [] # Clear if no category column

            # Update the standard properties list
            if property_columns:
                self.variables['standard_properties'] = sorted(list(set(property_columns)))
                
                # If the refresh callback exists, call it to update the UI
                if self.refresh_callback:
                    self.refresh_callback()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")


class AxisPanel(BasePanel):
    """Panel for axis settings"""
    def __init__(self, parent, variables):
        super().__init__(parent, variables)
        self.create_widgets()
        self._add_traces()

    def _add_traces(self):
        """Add traces to variables to auto-update settings."""
        self.variables['x_axis_quantity'].trace_add('write', self._auto_update_data_type)
        self.variables['y_axis_quantity'].trace_add('write', self._auto_update_data_type)

    def _auto_update_data_type(self, *args):
        """Automatically select 'ranges' or 'values' based on available columns."""
        if not self.variables.get('excel_columns'):
            return

        columns = self.variables['excel_columns']
        x_quantity = self.variables['x_axis_quantity'].get()
        y_quantity = self.variables['y_axis_quantity'].get()

        # Prefer 'ranges' if either axis has a 'low' or 'high' column
        x_has_range_cols = f"{x_quantity} low" in columns or f"{x_quantity} high" in columns
        y_has_range_cols = f"{y_quantity} low" in columns or f"{y_quantity} high" in columns

        if x_has_range_cols or y_has_range_cols:
            self.variables['data_type'].set("ranges")
        else:
            self.variables['data_type'].set("values")

    def create_widgets(self):
        # X-Axis settings
        ttk.Label(self, text="X-Axis Quantity:").pack(anchor=tk.W, padx=5, pady=5)
        x_axis_frame = ttk.Frame(self)
        x_axis_frame.pack(fill=tk.X, padx=5, pady=2)
        self.x_axis_combo = ttk.Combobox(x_axis_frame, textvariable=self.variables['x_axis_quantity'])
        self.x_axis_combo['values'] = self.variables['standard_properties']
        self.x_axis_combo.pack(fill=tk.X)
        
        # X-Axis unit
        ttk.Label(self, text="X-Axis Unit:").pack(anchor=tk.W, padx=5, pady=5)
        x_unit_entry = ttk.Entry(self, textvariable=self.variables['x_axis_unit'])
        x_unit_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # Set default value if not already set
        if not self.variables['x_axis_quantity'].get() and self.variables['standard_properties']:
            self.variables['x_axis_quantity'].set(self.variables['standard_properties'][0])
        
        # Y-Axis settings
        ttk.Label(self, text="Y-Axis Quantity:").pack(anchor=tk.W, padx=5, pady=5)
        y_axis_frame = ttk.Frame(self)
        y_axis_frame.pack(fill=tk.X, padx=5, pady=2)
        self.y_axis_combo = ttk.Combobox(y_axis_frame, textvariable=self.variables['y_axis_quantity'])
        self.y_axis_combo['values'] = self.variables['standard_properties']
        self.y_axis_combo.pack(fill=tk.X)
        
        # Y-Axis unit
        ttk.Label(self, text="Y-Axis Unit:").pack(anchor=tk.W, padx=5, pady=5)
        y_unit_entry = ttk.Entry(self, textvariable=self.variables['y_axis_unit'])
        y_unit_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # Set default value if not already set
        if not self.variables['y_axis_quantity'].get() and self.variables['standard_properties']:
            self.variables['y_axis_quantity'].set(self.variables['standard_properties'][0])
        
        # X-Axis limits
        ttk.Label(self, text="X-Axis Limits:").pack(anchor=tk.W, padx=5, pady=5)
        x_limit_frame = ttk.Frame(self)
        x_limit_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(x_limit_frame, text="Min:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(x_limit_frame, textvariable=self.variables['x_min'], width=10).pack(side=tk.LEFT)
        ttk.Label(x_limit_frame, text="Max:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(x_limit_frame, textvariable=self.variables['x_max'], width=10).pack(side=tk.LEFT)
        
        # Y-Axis limits
        ttk.Label(self, text="Y-Axis Limits:").pack(anchor=tk.W, padx=5, pady=5)
        y_limit_frame = ttk.Frame(self)
        y_limit_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(y_limit_frame, text="Min:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(y_limit_frame, textvariable=self.variables['y_min'], width=10).pack(side=tk.LEFT)
        ttk.Label(y_limit_frame, text="Max:").pack(side=tk.LEFT, padx=5)
        y_max_entry = ttk.Entry(y_limit_frame, textvariable=self.variables['y_max'])
        y_max_entry.pack(side=tk.LEFT, padx=2)

        # --- New Axis Style Controls ---
        style_frame = ttk.LabelFrame(self, text="Axis Style", padding=(5, 5))
        style_frame.pack(fill=tk.X, padx=5, pady=10)

        # Axis Line Width
        width_frame = ttk.Frame(style_frame)
        width_frame.pack(fill=tk.X, pady=2)
        ttk.Label(width_frame, text="Line Width:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(width_frame, textvariable=self.variables['axis_linewidth'], width=8).pack(side=tk.LEFT)

        # Spine Visibility
        ttk.Checkbutton(style_frame, text="Show Top Axis Spine", variable=self.variables['show_top_spine']).pack(anchor=tk.W, padx=5)
        ttk.Checkbutton(style_frame, text="Show Right Axis Spine", variable=self.variables['show_right_spine']).pack(anchor=tk.W, padx=5)

    def update_axis_options(self):
        """Update the values in the axis comboboxes based on the loaded file."""
        new_options = self.variables['standard_properties']
        
        current_x = self.variables['x_axis_quantity'].get()
        current_y = self.variables['y_axis_quantity'].get()

        self.x_axis_combo['values'] = new_options
        self.y_axis_combo['values'] = new_options
        
        if current_x not in new_options:
            self.variables['x_axis_quantity'].set(new_options[0] if new_options else "")
            
        if current_y not in new_options or current_x == self.variables['x_axis_quantity'].get():
            self.variables['y_axis_quantity'].set(new_options[1] if len(new_options) > 1 else (new_options[0] if new_options else ""))


class GuidelinePanel(BasePanel):
    """Panel for guideline settings"""
    def __init__(self, parent, variables):
        super().__init__(parent, variables)
        self.create_widgets()
        
    def create_widgets(self):
        # Enable/disable guideline
        ttk.Checkbutton(self, text="Show Guideline", 
                       variable=self.variables['guideline_flag']).pack(anchor=tk.W, padx=5, pady=5)
        
        # Guideline settings
        guideline_frame = ttk.LabelFrame(self, text="Guideline Settings")
        guideline_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Power
        ttk.Label(guideline_frame, text="Power:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(guideline_frame, textvariable=self.variables['guideline_power'], 
                 width=10).grid(row=0, column=1, padx=5, pady=5)
        
        # X Limits
        ttk.Label(guideline_frame, text="X Limits:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        x_limit_guideline_frame = ttk.Frame(guideline_frame)
        x_limit_guideline_frame.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(x_limit_guideline_frame, text="Min:").pack(side=tk.LEFT)
        ttk.Entry(x_limit_guideline_frame, textvariable=self.variables['guideline_x_min'], 
                 width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(x_limit_guideline_frame, text="Max:").pack(side=tk.LEFT)
        ttk.Entry(x_limit_guideline_frame, textvariable=self.variables['guideline_x_max'], 
                 width=10).pack(side=tk.LEFT)
        
        # String
        ttk.Label(guideline_frame, text="String:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(guideline_frame, textvariable=self.variables['guideline_string']).grid(
            row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Y-Intercept
        ttk.Label(guideline_frame, text="Y-Intercept:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(guideline_frame, textvariable=self.variables['guideline_y_intercept'], 
                 width=10).grid(row=3, column=1, padx=5, pady=5)
        
        # String Position
        ttk.Label(guideline_frame, text="String Position:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        string_pos_frame = ttk.Frame(guideline_frame)
        string_pos_frame.grid(row=4, column=1, padx=5, pady=5)
        ttk.Label(string_pos_frame, text="X:").pack(side=tk.LEFT)
        ttk.Entry(string_pos_frame, textvariable=self.variables['guideline_string_pos_x'], 
                 width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(string_pos_frame, text="Y:").pack(side=tk.LEFT)
        ttk.Entry(string_pos_frame, textvariable=self.variables['guideline_string_pos_y'], 
                 width=10).pack(side=tk.LEFT)


class MaterialsPanel(BasePanel):
    """Panel for individual materials settings"""
    def __init__(self, parent, variables):
        super().__init__(parent, variables)
        self.create_widgets()
        
    def create_widgets(self):
        # Enable/disable individual materials
        ttk.Checkbutton(self, text="Show Individual Materials", 
                       variable=self.variables['individual_material_flag']).pack(anchor=tk.W, padx=5, pady=5)
        
        # Material settings
        materials_frame = ttk.LabelFrame(self, text="Individual Materials")
        materials_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(materials_frame, text="Individual materials can be defined in the code.").pack(padx=5, pady=5)
        ttk.Label(materials_frame, text="Examples:").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(materials_frame, text="• Foam (E=0.124E-3 GPa, ν=0.45, ρ=400 kg/m³)").pack(anchor=tk.W, padx=15, pady=2)
        ttk.Label(materials_frame, text="• PLA (E=2.009 GPa, ν=0.3, ρ=1300 kg/m³)").pack(anchor=tk.W, padx=15, pady=2)


class UnitCellPanel(BasePanel):
    """Panel for unit cell settings"""
    def __init__(self, parent, variables):
        super().__init__(parent, variables)
        self.create_widgets()
        
    def create_widgets(self):
        # Enable/disable unit cell
        ttk.Checkbutton(self, text="Show Unit Cell Data", 
                       variable=self.variables['unit_cell_flag']).pack(anchor=tk.W, padx=5, pady=5)
        
        # Unit cell settings
        unit_cell_frame = ttk.LabelFrame(self, text="Unit Cell Settings")
        unit_cell_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Infill Material selection
        ttk.Label(unit_cell_frame, text="Infill Material:").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Radiobutton(self, text="Foamed Elastomer", variable=self.variables['unit_cell_material'], 
                       value="foamed elastomer").pack(anchor=tk.W, padx=25)
        ttk.Radiobutton(self, text="Dense Elastomer", variable=self.variables['unit_cell_material'], 
                       value="dense elastomer").pack(anchor=tk.W, padx=25)
        ttk.Radiobutton(self, text="None", variable=self.variables['unit_cell_material'], 
                       value="none").pack(anchor=tk.W, padx=25)
        
        # File path information
        ttk.Label(unit_cell_frame, text="Note: Unit cell data must be in folders:").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Chiral_All_inputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Chiral_All_outputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Lattice_All_inputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Lattice_All_outputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Re-entrant_All_inputs.csv").pack(anchor=tk.W, padx=25, pady=2)
        ttk.Label(unit_cell_frame, text="- unit_cell_data/Re-entrant_All_outputs.csv").pack(anchor=tk.W, padx=25, pady=2)


class ColorPanel(BasePanel):
    """Panel for customizing material category colors."""
    def __init__(self, parent, variables):
        super().__init__(parent, variables)
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.color_widgets = {}

    def update_color_options(self):
        """Dynamically create widgets for color customization."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        categories = self.variables.get('unique_categories', [])
        
        for i, category in enumerate(categories):
            self._create_color_widget(category, i)

    def _create_color_widget(self, category, row):
        """Create a single row of widgets for a category."""
        # Get the default color
        custom_color = self.variables['custom_colors'].get(category)
        if custom_color:
            color = custom_color
        else:
            # Fallback to the default color generation logic
            DISTINCT_COLORS = [
                '#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', 
                '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#469990', '#dcbeff', 
                '#9A6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', 
                '#000075', '#a9a9a9'
            ]
            color = DISTINCT_COLORS[row % len(DISTINCT_COLORS)]

        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(fill='x', expand=True, padx=5, pady=2)

        label = ttk.Label(row_frame, text=category, width=25)
        label.pack(side='left', fill='x')

        color_swatch = tk.Frame(row_frame, width=50, height=20, bg=color, relief='sunken', borderwidth=1)
        color_swatch.pack(side='left', padx=10)

        change_button = ttk.Button(row_frame, text="Change Color", 
                                  command=lambda cat=category, swatch=color_swatch: self._change_color(cat, swatch))
        change_button.pack(side='left')
        
    def _change_color(self, category, swatch):
        """Open color chooser and update the color for a category."""
        initial_color = swatch.cget("bg")
        color_code = colorchooser.askcolor(title=f"Choose color for {category}", initialcolor=initial_color)
        
        if color_code and color_code[1]:
            new_color = color_code[1]
            swatch.config(bg=new_color)
            self.variables['custom_colors'][category] = new_color 