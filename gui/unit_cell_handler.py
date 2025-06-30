import os
import pandas as pd
from tkinter import messagebox

class UnitCellHandler:
    """Handler for unit cell data operations"""
    
    @staticmethod
    def load_unit_cell_data(unit_cell_material):
        """Load unit cell data from CSV files"""
        try:
            # Define file paths
            OV_file_names = ['Chiral_All_outputs.csv', 'Lattice_All_outputs.csv', 'Re-entrant_All_outputs.csv']
            DV_file_names = ['Chiral_All_inputs.csv', 'Lattice_All_inputs.csv', 'Re-entrant_All_inputs.csv']
            
            # Concatenate all data
            counter = 0
            for OV_file_name, DV_file_name in zip(OV_file_names, DV_file_names):
                OV_file = os.path.join(os.getcwd(), 'unit_cell_data', OV_file_name)
                DV_file = os.path.join(os.getcwd(), 'unit_cell_data', DV_file_name)
                
                if not os.path.exists(OV_file) or not os.path.exists(DV_file):
                    messagebox.showerror("Error", f"Unit cell data file not found: {OV_file_name} or {DV_file_name}")
                    return None
                
                if counter == 0:
                    OV_data_frame = pd.read_csv(OV_file)
                    DV_data_frame = pd.read_csv(DV_file)
                else:
                    OV_data_frame = pd.concat([OV_data_frame, pd.read_csv(OV_file)])
                    DV_data_frame = pd.concat([DV_data_frame, pd.read_csv(DV_file)])
                counter += 1
            
            # Merge data
            merged_data = OV_data_frame.merge(DV_data_frame, on=['ID', 'Unit Cell'])
            
            # Apply orthonormal rotation - simplified implementation
            data_to_plot = merged_data.copy()
            data_to_plot = data_to_plot[data_to_plot['Infill material'] == unit_cell_material]
            data_to_plot = data_to_plot.reset_index(drop=True)
            
            # Create baseline materials
            material_properties = UnitCellHandler.create_baseline_materials()
            
            # Set compliant material based on selection
            if unit_cell_material == 'foamed elastomer':
                compliant_material = material_properties['compliant_foam']
            elif unit_cell_material == 'dense elastomer':
                compliant_material = material_properties['compliant_dense']
            else:  # 'none'
                compliant_material = material_properties['null_material']
            
            stiff = material_properties['stiff']
            
            # Create density field
            data_to_plot['Density'] = 1E6 * (
                data_to_plot['Stiff volume'] * stiff['rho'] + 
                (data_to_plot['Total volume'] - data_to_plot['Stiff volume']) * compliant_material['rho']
            ) / data_to_plot['Total volume']
            
            # Create Poisson difference field
            data_to_plot['Poisson difference'] = 1 / (1 + data_to_plot['Nu12'])
            
            # Filter out invalid data points
            data_to_plot = data_to_plot[
                (data_to_plot['E1'] > compliant_material['E']) & 
                (data_to_plot['E2'] > compliant_material['E'])
            ]
            
            return data_to_plot
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load unit cell data: {str(e)}")
            return None
    
    @staticmethod
    def create_baseline_materials():
        """Create baseline material properties dictionary"""
        materials = {
            'stiff': {
                'E': 200,  # GPa
                'nu': 0.3,
                'rho': 7800,  # kg/m^3
                'name': 'stiff'
            },
            'compliant_dense': {
                'E': 0.1,  # GPa
                'nu': 0.48,
                'rho': 1000,  # kg/m^3
                'name': 'dense elastomer'
            },
            'compliant_foam': {
                'E': 0.001,  # GPa
                'nu': 0.3,
                'rho': 100,  # kg/m^3
                'name': 'foamed elastomer'
            },
            'null_material': {
                'E': 0,
                'nu': 0,
                'rho': 0,
                'name': 'none'
            }
        }
        return materials 