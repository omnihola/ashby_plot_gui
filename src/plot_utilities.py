# -*- coding: utf-8 -*-
"""
Plot utilities script.
Contains all the misc. functions to generate the ashby plot (not related to the actual ellipses).


@author: Walgren
"""
import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import colors

from src.plot_convex_hull import (
    draw_ellipses,
    draw_hull,
    )

from src.rotation_aware_annotation import RotationAwareAnnotation


def save_high_quality_figure(fig, filename, dpi=300, format='png', transparent=False):
    '''
    将图表以高分辨率保存到./figures目录下

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        要保存的图表对象
    filename : str
        文件名（不包含路径和扩展名）
    dpi : int, optional
        分辨率，默认300（出版质量），更高的值会产生更大的文件
    format : str, optional
        文件格式，可选：'png', 'pdf', 'svg', 'eps', 'jpg'等
    transparent : bool, optional
        是否使用透明背景，对于PNG等支持透明的格式有效
    
    Returns
    -------
    str
        保存的文件的完整路径
    '''
    # 确保figures目录存在
    figures_dir = os.path.join(os.getcwd(), 'figures')
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)
    
    # 构建完整文件路径
    full_filename = f"{filename}.{format}" if '.' not in filename else filename
    filepath = os.path.join(figures_dir, full_filename)
    
    # 保存图表
    fig.savefig(
        filepath, 
        dpi=dpi, 
        format=format, 
        bbox_inches='tight',  # 裁剪多余的空白区域
        transparent=transparent
    )
    
    print(f"高清图表已保存至: {filepath}")
    return filepath


def plotting_presets(figure_type='publication'):
    """
    设置绘图样式的函数。控制图表的整体外观和风格。
    
    参数:
    ------
    figure_type : str
        'publication' - 为出版物优化的样式（小字体，紧凑）
        'presentation' - 为演示优化的样式（大字体，宽松）
    """
    # 禁用LaTeX渲染，防止因系统没有安装LaTeX导致的错误
    plt.rcParams['text.usetex'] = False
    
    # 设置字体系列
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # 设置SVG输出选项
    plt.rcParams['svg.fonttype'] = 'none'
    
    # 根据图表类型配置样式
    if figure_type == 'publication':
        # 小字体适合出版物
        plt.rcParams['font.size'] = 12  # 基本字体大小
        plt.rcParams['axes.labelsize'] = 12  # 轴标签字体大小
        plt.rcParams['xtick.labelsize'] = 10  # x轴刻度标签字体大小
        plt.rcParams['ytick.labelsize'] = 10  # y轴刻度标签字体大小
        plt.rcParams['legend.fontsize'] = 8  # 图例字体大小
        plt.rcParams['figure.titlesize'] = 14  # 图表标题字体大小
        
        # 标记和线条的大小
        plt.rcParams['lines.markersize'] = 5  # 标记大小
        plt.rcParams['lines.linewidth'] = 1.0  # 线条宽度
        
    elif figure_type == 'presentation':
        # 大字体适合演示
        plt.rcParams['font.size'] = 16  # 基本字体大小
        plt.rcParams['axes.labelsize'] = 18  # 轴标签字体大小
        plt.rcParams['xtick.labelsize'] = 14  # x轴刻度标签字体大小
        plt.rcParams['ytick.labelsize'] = 14  # y轴刻度标签字体大小
        plt.rcParams['legend.fontsize'] = 14  # 图例字体大小
        plt.rcParams['figure.titlesize'] = 20  # 图表标题字体大小
        
        # 标记和线条的大小
        plt.rcParams['lines.markersize'] = 8  # 标记大小
        plt.rcParams['lines.linewidth'] = 2.0  # 线条宽度


def draw_plot(
    data, x_quantity, y_quantity, ax, material_colors, data_type="mix"
):
    """
    Draws the Ashby plot. Handles different data types:
    - 'mix': Automatically determines whether to plot ellipses, lines, or points for each entry.
    - 'ranges': Plots ellipses for all entries, requires 'low' and 'high' columns.
    - 'values': Plots points for all entries, requires direct value columns.
    """
    for category, group in data.groupby("Category"):
        color = material_colors.get(category, "gray")

        for _, row in group.iterrows():
            x_low_col, x_high_col = f"{x_quantity} low", f"{x_quantity} high"
            y_low_col, y_high_col = f"{y_quantity} low", f"{y_quantity} high"

            # --- Determine X and Y coordinates based on data_type ---
            if data_type == "ranges":
                x_vals = [row.get(x_low_col), row.get(x_high_col)]
                y_vals = [row.get(y_low_col), row.get(y_high_col)]
            elif data_type == "values":
                x_vals = [row.get(x_quantity), row.get(x_quantity)]
                y_vals = [row.get(y_quantity), row.get(y_quantity)]
            else:  # 'mix' mode
                x_low, x_high = row.get(x_low_col), row.get(x_high_col)
                y_low, y_high = row.get(y_low_col), row.get(y_high_col)
                x_val, y_val = row.get(x_quantity), row.get(y_quantity)

                # Consolidate values for X
                if pd.notna(x_low) or pd.notna(x_high):
                    x_vals = [x_low, x_high]
                else:
                    x_vals = [x_val, x_val]

                # Consolidate values for Y
                if pd.notna(y_low) or pd.notna(y_high):
                    y_vals = [y_low, y_high]
                else:
                    y_vals = [y_val, y_val]

            # --- Clean up None/NaN and determine plot type ---
            x_points = [p for p in x_vals if pd.notna(p)]
            y_points = [p for p in y_vals if pd.notna(p)]

            if not x_points or not y_points:
                continue

            x_center = sum(x_points) / len(x_points)
            y_center = sum(y_points) / len(y_points)
            x_width = max(x_points) - min(x_points) if len(x_points) > 1 else 0
            y_height = max(y_points) - min(y_points) if len(y_points) > 1 else 0

            # --- Draw based on determined shape ---
            if x_width > 0 and y_height > 0:  # Ellipse
                ellipse = patches.Ellipse(
                    (x_center, y_center),
                    width=x_width,
                    height=y_height,
                    facecolor=color,
                    alpha=0.3,
                    zorder=1,
                )
                ax.add_patch(ellipse)
            elif x_width > 0:  # Horizontal Line
                ax.plot([min(x_points), max(x_points)], [y_center, y_center], color=color, solid_capstyle='round', lw=2, zorder=1)
            elif y_height > 0:  # Vertical Line
                ax.plot([x_center, x_center], [min(y_points), max(y_points)], color=color, solid_capstyle='round', lw=2, zorder=1)
            else:  # Point
                ax.scatter(x_center, y_center, facecolor=color, edgecolor='k', s=50, zorder=2)


def create_legend(ax, material_classes, material_colors, ncol, fontsize):
    """Create a custom legend for the plot on a specific axis."""
    legend_elements = []
    for mc in material_classes:
        if mc in material_colors:
            patch = patches.Patch(facecolor=material_colors.get(mc), label=mc)
            legend_elements.append(patch)

    if not legend_elements:
        return  # Do not create an empty legend

    ax.legend(
        handles=legend_elements,
        loc='lower center',
        bbox_to_anchor=(0.5, 1.05),
        ncol=ncol,
        fontsize=fontsize,
        frameon=False,
    )


def draw_guideline(
        guideline,
        ax,
        log_flag = True,
        ):
    '''
    绘制材料指数参考线。
    可以修改本函数内的参数来调整参考线的样式和注释。

    Parameters
    ----------
    guideline : dict
        包含参考线设置的字典：
        power : 参考线的幂次
        x_lim : X轴范围
        y_intercept : Y轴截距
        string : 显示的公式文本
        string_position : 文本位置
    ax : matplotlib坐标轴对象
    log_flag : 是否使用对数坐标系
    '''
    power = guideline['power']
    x_lim = guideline['x_lim']
    y_intercept = guideline['y_intercept']
    string = guideline['string']
    string_position = guideline['string_position']

    # 创建X轴点
    num_points = 5  # 参考线上的点数，增加此值可使线条更平滑
    x_values = np.linspace(x_lim[0], x_lim[1], num_points)
    y_values = np.zeros(shape = num_points)

    # 创建参考线
    for i in range(len(x_values)):
        if log_flag:
            # 对数坐标系下的幂函数
            y_values[i] = y_intercept * x_values[i]**power
        else:
            # 线性坐标系下的线性函数
            y_values[i] = power * x_values[i] + y_intercept

    # 绘制参考线
    ax.plot(
        x_values,
        y_values,
        'k--',  # 黑色虚线，可以修改为其他样式，如'r-'红色实线
        )

    # 添加参考线的注释
    RotationAwareAnnotation(
        string,  # 显示的文本
        xy=string_position,  # 文本位置
        p=(x_values[3], y_values[3]),  # 参考点
        pa=(x_values[0], y_values[0]),  # 另一参考点，用于计算旋转
        ax=ax,
        xytext=(0,0),  # 文本偏移
        textcoords="offset points",
        va="top"  # 垂直对齐方式
        )


def common_definitions():
    '''
    定义常用的单位和材料颜色。
    可以在此函数中添加新的单位或修改材料颜色。

    Returns
    -------
    units : dict
        各物理量及其对应单位的字典
    material_colors : dict
        材料类别及其对应颜色的字典
    '''
    # ===== 常用单位定义 =====
    # 为添加新物理量，请在此字典中添加对应的单位
    units = {
        'Density': 'kg/m$^3$',
        'Tensile Strength': 'MPa',
        "Young Modulus": 'GPa',
        "Fracture Toughness": r"MPa$\sqrt{\text{m}}$",
        "Thermal Conductivity": r"W/m$\cdot$K",
        "Thermal expansion": "1$^-6$/m",
        "Resistivity": r"$\Omega \cdot$m",
        "Poisson": "-",
        "Poisson difference": "-",
        }

    # ===== 材料类别颜色定义 =====
    # 可以修改颜色值来改变不同材料类别的显示颜色
    # 支持的颜色名称：'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'white'等
    # 也可以使用十六进制颜色代码如'#FF5733'
    material_colors = {
        'Foams': 'blue',
        'Elastomers': 'orange',
        'Natural materials': 'green',
        'Polymers': 'red',
        'Nontechnical ceramics': 'purple',
        'Composites': 'Brown',
        'Technical ceramics': 'pink',
        'Metals': 'grey',
        }

    return units, material_colors
