import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import filedialog, messagebox
import matplotlib
import tkinter as tk
from tkinter import ttk
import matplotlib.patches as patches
import io
from PIL import Image, ImageTk

from src.plot_utilities import (
    create_legend,
    draw_plot,
    plotting_presets,
    draw_guideline,
    common_definitions,
    save_high_quality_figure
)
from src.plot_convex_hull import draw_hull
from gui.unit_cell_handler import UnitCellHandler

class PlotHandler:
    """Handler for plot operations"""
    
    def __init__(self, plot_frame, variables):
        self.plot_frame = plot_frame
        self.variables = variables
        
        # Initialize figure
        self.fig, self.ax = plt.subplots(figsize=(8, 7))
        
        # Make sure the figure has enough DPI for good display
        self.fig.set_dpi(100)
        
        # Create a label to hold the plot image
        self.plot_label = tk.Label(self.plot_frame)
        self.plot_label.pack(fill='both', expand=True)
        
        # Keep a reference to the PhotoImage to prevent garbage collection
        self.plot_photo = None
    
    def generate_plot(self):
        """Generate the Ashby plot based on user inputs"""
        try:
            # Clear the current plot
            self.ax.clear()
            
            # Validate inputs for standard plot
            if not self.variables['unit_cell_flag'].get() and not self.variables['file_path'].get():
                messagebox.showwarning("Warning", "Please select a material properties file.")
                return
                
            if not self.variables['x_axis_quantity'].get() or not self.variables['y_axis_quantity'].get():
                messagebox.showwarning("Warning", "Please select X and Y axis quantities.")
                return
            
            # Get common definitions
            units, material_colors = common_definitions()
            
            # Set up plot formatting
            plotting_presets(self.variables['figure_type'].get())
            
            # Set x and y labels
            try:
                x_quantity = self.variables['x_axis_quantity'].get()
                y_quantity = self.variables['y_axis_quantity'].get()
                x_unit = self.variables['x_axis_unit'].get()
                y_unit = self.variables['y_axis_unit'].get()
                
                if x_quantity == 'Poisson difference':
                    x_label = 'Hyperbolic Poisson Ratio 1/(1+v)'
                else:
                    x_label = x_quantity
                if x_unit:
                    x_label += f", {x_unit}"

                if y_quantity == 'Poisson difference':
                    y_label = 'Hyperbolic Poisson Ratio 1/(1+v)'
                else:
                    y_label = y_quantity
                if y_unit:
                    y_label += f", {y_unit}"

                self.ax.set_xlabel(x_label)
                self.ax.set_ylabel(y_label)
            except:
                messagebox.showerror("Error", "Could not set correct x- and y-labels. Make sure your axis quantities have units defined.")
                return
            
            # Set axes limits
            try:
                x_lim = [float(self.variables['x_min'].get()), float(self.variables['x_max'].get())]
                y_lim = [float(self.variables['y_min'].get()), float(self.variables['y_max'].get())]
                self.ax.set(xlim=x_lim, ylim=y_lim)
            except ValueError:
                messagebox.showerror("Error", "Invalid axis limits. Please enter numeric values.")
                return
            
            # Set log scale if needed
            if self.variables['log_flag'].get():
                self.ax.loglog()
            
            # Add grid lines
            self.ax.grid(which='major', axis='both', linestyle='-.', zorder=0.5)
            
            # Draw guideline if enabled
            if self.variables['guideline_flag'].get():
                try:
                    guideline = {
                        'power': float(self.variables['guideline_power'].get()),
                        'x_lim': [float(self.variables['guideline_x_min'].get()), float(self.variables['guideline_x_max'].get())],
                        'string': self.variables['guideline_string'].get(),
                        'y_intercept': float(self.variables['guideline_y_intercept'].get()),
                        'string_position': (float(self.variables['guideline_string_pos_x'].get()), 
                                           float(self.variables['guideline_string_pos_y'].get())),
                    }
                    draw_guideline(guideline, ax=self.ax, log_flag=self.variables['log_flag'].get())
                except ValueError:
                    messagebox.showerror("Error", "Invalid guideline parameters. Please enter numeric values.")
                    return
            
            # Draw standard material data if file is provided
            if self.variables['file_path'].get():
                self._plot_material_data(x_quantity, y_quantity, material_colors)
            
            # Plot individual materials if enabled
            if self.variables['individual_material_flag'].get():
                self._plot_individual_materials(x_quantity, y_quantity)
            
            # Plot unit cell data if enabled
            if self.variables['unit_cell_flag'].get():
                self._plot_unit_cell_data(x_quantity, y_quantity)
            
            # --- Final Legend Creation ---
            # Create the legend at the very end to ensure all artists are included.
            if self.variables['file_path'].get():
                try:
                    data = pd.read_excel(self.variables['file_path'].get())
                    data['Category'] = data['Category'].astype(str).str.strip()

                    # 2. Pre-process and convert all other columns to numeric.
                    for col in data.columns:
                        if col != 'Category':
                            # First, convert to string to use string methods.
                            # Then, remove the '~' character for approximate values.
                            # Finally, convert to numeric, coercing any remaining non-numeric values to NaN.
                            data[col] = pd.to_numeric(
                                data[col].astype(str).str.replace('~', ''), 
                                errors='coerce'
                            )
                    
                    unique_categories = sorted(data['Category'].unique())
                    cmap = plt.get_cmap('tab20')
                    colors = cmap(np.linspace(0, 1, len(unique_categories)))
                    dynamic_material_colors = dict(zip(unique_categories, colors))
                    
                    figure_type = self.variables['figure_type'].get()
                    fontsize = 8 if figure_type == 'publication' else 14
                    
                    create_legend(
                        ax=self.ax,
                        material_classes=unique_categories,
                        material_colors=dynamic_material_colors,
                        ncol=2,
                        fontsize=fontsize
                    )
                except Exception as e:
                    print(f"Failed to create legend: {e}") # Log error instead of messagebox

            # Render the figure to an image and display it
            self._update_plot_image()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot: {str(e)}")
    
    def _update_plot_image(self):
        """Renders the Matplotlib figure to a static image and displays it."""
        buf = io.BytesIO()
        self.fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        img = Image.open(buf)
        self.plot_photo = ImageTk.PhotoImage(image=img)
        
        self.plot_label.config(image=self.plot_photo)
        
        buf.close()
    
    def _plot_material_data(self, x_quantity, y_quantity, material_colors):
        """Plot standard material data from file"""
        try:
            data = pd.read_excel(self.variables['file_path'].get())
            
            # --- Comprehensive Data Cleaning ---
            # 1. Force 'Category' to be a string and strip whitespace.
            if 'Category' not in data.columns:
                messagebox.showwarning("Warning", "The Excel file must contain a 'Category' column for coloring and legend.")
                return
            data['Category'] = data['Category'].astype(str).str.strip()

            # 2. Pre-process and convert all other columns to numeric.
            for col in data.columns:
                if col != 'Category':
                    # First, convert to string to use string methods.
                    # Then, remove the '~' character for approximate values.
                    # Finally, convert to numeric, coercing any remaining non-numeric values to NaN.
                    data[col] = pd.to_numeric(
                        data[col].astype(str).str.replace('~', ''), 
                        errors='coerce'
                    )
            
            unique_categories = sorted(data['Category'].unique())
            cmap = plt.get_cmap('tab20')
            colors = cmap(np.linspace(0, 1, len(unique_categories)))
            dynamic_material_colors = dict(zip(unique_categories, colors))

            # Handle Poisson difference calculation if needed
            if (x_quantity == 'Poisson difference') or (y_quantity == 'Poisson difference'):
                data['Poisson difference high'] = 1/(1+data['Poisson low'])
                data['Poisson difference low'] = 1/(1+data['Poisson high'])
            
            # Draw the plot
            draw_plot(
                data,
                x_quantity,
                y_quantity,
                self.ax,
                dynamic_material_colors,
                data_type=self.variables['data_type'].get(),
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot material data: {str(e)}")
    
    def _plot_individual_materials(self, x_quantity, y_quantity):
        """Plot individual materials as stars"""
        marker_size = 500
        
        # Example materials - these could be made configurable in the future
        foam = {
            'Young Modulus': 0.124E-3,
            'Poisson': 0.45,
            'Density': 400,
            'name': 'Foam',
            'color': 'b'
        }
        
        pla = {
            'Young Modulus': 2.009,
            'Poisson': 0.3,
            'Density': 1300,
            'name': 'PLA',
            'color': 'r'
        }
        
        materials = [foam, pla]
        
        for material in materials:
            x_value = material[x_quantity] if x_quantity in material else (
                1/(1+material['Poisson']) if x_quantity == 'Poisson difference' else None
            )
            y_value = material[y_quantity] if y_quantity in material else (
                1/(1+material['Poisson']) if y_quantity == 'Poisson difference' else None
            )
            
            if x_value is not None and y_value is not None:
                self.ax.scatter(
                    x_value,
                    y_value,
                    c=material['color'],
                    edgecolors='k',
                    marker='*',
                    s=marker_size,
                    label=material['name']
                )
    
    def _plot_unit_cell_data(self, x_quantity, y_quantity):
        """Plot unit cell data"""
        unit_cell_data = UnitCellHandler.load_unit_cell_data(self.variables['unit_cell_material'].get())
        
        if unit_cell_data is not None and len(unit_cell_data) > 0:
            # Map property names for unit cell data
            if x_quantity == 'Young Modulus':
                x_field = 'E1'
            elif x_quantity == 'Poisson':
                x_field = 'Nu12'
            elif x_quantity == 'Poisson difference':
                x_field = 'Poisson difference'
            else:
                x_field = x_quantity
                
            if y_quantity == 'Young Modulus':
                y_field = 'E1'
            elif y_quantity == 'Poisson':
                y_field = 'Nu12'
            elif y_quantity == 'Poisson difference':
                y_field = 'Poisson difference'
            else:
                y_field = y_quantity
            
            if x_field in unit_cell_data.columns and y_field in unit_cell_data.columns:
                # Create array for hull drawing
                X = np.zeros(shape=(len(unit_cell_data), 2))
                X[:, 0] = unit_cell_data[x_field]
                X[:, 1] = unit_cell_data[y_field]
                
                # Draw hull for all unit cell data
                draw_hull(
                    X,
                    scale=1.1,
                    padding='scale',
                    n_interpolate=1000,
                    interpolation='cubic',
                    ax=self.ax,
                    plot_kwargs={
                        'color': 'b',
                        'alpha': 0.75,
                        'hatch': '+'
                    }
                )
                
                # 为单元格数据准备图例项
                handles = []
                labels = []
                
                # 定义单元格类型的颜色和标签
                unit_cell_colors = {'Chiral': 'r', 'Lattice': 'b', 'Re-entrant': 'g'}
                
                # 添加图例项
                for unit_cell_type, group_data in unit_cell_data.groupby('Unit Cell'):
                    if len(group_data) > 2:  # Need at least 3 points for a hull
                        color = unit_cell_colors.get(unit_cell_type, 'k')
                        label = f"{unit_cell_type} ({self.variables['unit_cell_material'].get()})"
                        
                        # 创建图例项
                        patch = patches.Patch(color=color, alpha=0.75, hatch='+', label=label)
                        handles.append(patch)
                        labels.append(label)
                
                # 添加图例，如果有图例项且没有显示材料数据图例
                if handles and not self.variables['file_path'].get():
                    # 获取图表类型，用于确定字体大小
                    figure_type = self.variables['figure_type'].get()
                    fontsize = 8 if figure_type == 'publication' else 14
                    
                    # 创建图例
                    self.ax.legend(
                        handles=handles,
                        loc='upper center',
                        bbox_to_anchor=(0.5, 1.08),
                        ncol=1,  # 单列显示单元格类型
                        fontsize=fontsize
                    )
            else:
                messagebox.showwarning("Warning", f"Selected properties not available in unit cell data: {x_field} or {y_field}")
    
    def save_plot(self):
        """Save the current plot to a file"""
        options = {
            "defaultextension": ".png",
            "filetypes": [
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("EPS files", "*.eps"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*"),
            ]
        }
        
        # 保存位置选项
        save_option = messagebox.askyesnocancel(
            "保存选项", 
            "是否保存到 ./figures 目录？\n\n选择'是'：保存到./figures\n选择'否'：选择保存位置\n选择'取消'：取消保存"
        )
        
        if save_option is None:  # 用户选择了取消
            return
        
        if save_option:  # 用户选择了是，保存到./figures
            # 打开简化的对话框，只需要输入文件名
            filename = filedialog.asksaveasfilename(
                title="输入文件名（不含扩展名）",
                initialdir="./figures",
            )
            
            if filename:
                try:
                    # 获取文件格式
                    format_dialog = FormatDialog(self.plot_frame)
                    format_info = format_dialog.result
                    
                    if format_info:  # 用户没有取消对话框
                        format, dpi, transparent = format_info
                        
                        # 使用高质量保存函数
                        filepath = save_high_quality_figure(
                            self.fig, 
                            os.path.basename(filename),  # 只使用文件名部分
                            dpi=dpi, 
                            format=format,
                            transparent=transparent
                        )
                        
                        messagebox.showinfo("成功", f"高清图表已保存至:\n{filepath}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")
        else:  # 用户选择了否，选择保存位置
            file_path = filedialog.asksaveasfilename(**options)
            if file_path:
                try:
                    self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                    messagebox.showinfo("成功", f"图表已保存至: {file_path}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")


class FormatDialog(tk.Toplevel):
    """图表格式设置对话框"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("设置保存格式")
        self.geometry("300x200")
        self.resizable(False, False)
        
        # 结果变量，返回 (format, dpi, transparent)
        self.result = None
        
        # 创建变量
        self.format_var = tk.StringVar(value="png")
        self.dpi_var = tk.StringVar(value="300")
        self.transparent_var = tk.BooleanVar(value=False)
        
        # 创建控件
        self.create_widgets()
        
        # 设置模态对话框
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # 等待用户操作
        self.wait_window(self)
    
    def create_widgets(self):
        # 格式选择
        ttk.Label(self, text="文件格式:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        format_combo = ttk.Combobox(self, textvariable=self.format_var, 
                              values=["png", "pdf", "svg", "eps", "jpg"], 
                              width=10, state="readonly")
        format_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # DPI设置
        ttk.Label(self, text="分辨率(DPI):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        dpi_combo = ttk.Combobox(self, textvariable=self.dpi_var, 
                           values=["100", "200", "300", "600"], 
                           width=10)
        dpi_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # 透明背景选择
        ttk.Checkbutton(self, text="透明背景", variable=self.transparent_var).grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
    
    def on_ok(self):
        # 验证DPI输入
        try:
            dpi = int(self.dpi_var.get())
            if dpi <= 0:
                raise ValueError("DPI必须是正整数")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的DPI值（正整数）")
            return
        
        self.result = (self.format_var.get(), dpi, self.transparent_var.get())
        self.destroy()
    
    def on_cancel(self):
        self.result = None
        self.destroy() 