# Ashby Plot Generator

This is a graphical user interface (GUI) application designed to generate Ashby plots from material properties data stored in Excel files. It provides a flexible and user-friendly way to visualize relationships between different material properties.

## Features

This application has been progressively enhanced with the following key features:

*   **Dynamic Axis Properties**: The properties available for the X and Y axes are no longer hard-coded. They are now dynamically loaded from the column headers of the Excel file you provide.
*   **Static Plot Generation**: The plot area displays a static, non-interactive image of the graph. This is ideal for generating figures for reports and presentations. A new plot is generated each time the "Generate Plot" button is clicked.
*   **Customizable Units**: You can specify the units for the X and Y axes directly in the GUI. These units will be displayed on the plot labels.
*   **Smart "Mix" Plotting Mode**: The application defaults to a "Mix" mode, which intelligently handles different data formats on a row-by-row basis:
    *   It plots data as an **ellipse** if both `low` and `high` values are present for a property.
    *   It plots data as a **point** if only one of `low` or `high` is present, or if the data comes from a single-value column.
*   **Dynamic Legend & High-Contrast Colors**: A legend is automatically generated based on the unique entries in the `Category` column. To ensure clarity, colors are assigned dynamically from a high-contrast (HSV) color spectrum, making different categories easy to distinguish.
*   **Robust Data Cleaning**: The application automatically cleans the input data to prevent common errors:
    *   It correctly handles approximate values (e.g., `~6` is interpreted as `6`).
    *   It ignores non-numeric data in value columns, ensuring the program doesn't crash.
    *   It correctly identifies all valid numeric columns for plotting, even if they contain some non-numeric entries.
    *   It handles mixed data types (text, numbers) in the `Category` column by treating all entries as text.

## Requirements

To run this application, you will need:

*   Python 3.6 or newer
*   The Python libraries listed in `requirements.txt`. You can install them using pip:
    ```bash
    pip install -r requirements.txt
    ```

## How to Use

1.  **Install Dependencies**: Make sure you have installed all the required libraries by running the command above.
2.  **Run the Application**: Execute the `main.py` script from your terminal:
    ```bash
    python main.py
    ```
3.  **Load Data**: In the application, click the "Browse" button to select and load your Excel data file.
4.  **Configure Plot**: Select the properties for the X and Y axes from the dropdown menus and set other desired parameters.
5.  **Generate Plot**: Click the "Generate Plot" button to display the Ashby plot.
6.  **Save Plot**: Click the "Save Plot" button to save the generated image to your computer.

## Excel Data Format Requirements

To ensure the application functions correctly, your Excel data file **must** adhere to the following format:

#### **`Category` Column (Mandatory)**
*   Your Excel file **must** have a column named `Category`.
*   This column is used to group materials, assign colors, and generate the legend.
*   The entries in this column can be text (e.g., `Metals`, `Polymers`) or numbers, but they will all be treated as distinct text-based categories.

#### **Data Columns (for Plotting)**

The application supports two primary ways to structure your numerical data:

1.  **Range Data (e.g., for properties with uncertainty)**:
    *   Use **two columns** with the suffixes ` low` and ` high` (note the leading space).
    *   **Example**: For "Young Modulus", you would have two columns: `Young Modulus low` and `Young Modulus high`.
    *   If a row has a value for only one of these (e.g., only in `Young Modulus low`), it will be correctly plotted as a single point.

2.  **Single Value Data**:
    *   Use a **single column** with the exact property name.
    *   **Example**: For "Density", you would have one column named `Density`.

#### **Data Cleaning Rules**
*   **Approximate Values**: The application understands the `~` symbol as "approximately". A value like `~6` will be automatically cleaned and treated as the number `6`.
*   **Non-Numeric Entries**: Any other text or symbol in a numerical column will be treated as a missing value (`NaN`) and will not be plotted, preventing program crashes.
*   **Dropdown Menu Content**: Only columns that contain at least one valid number (after cleaning) will appear as selectable options in the X and Y axis dropdowns. Purely textual columns will be automatically ignored. 