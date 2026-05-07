import os
import pandas as pd
import string
import matplotlib.pyplot as plt

def load_file(file_path):

    plates_sizes = {
    6 : {'rows': 2, 'cols': 3},
    12 : {'rows': 3, 'cols': 4},
    24 : {'rows': 4, 'cols': 6},
    96 : {'rows': 8, 'cols': 12},
    384 : {'rows': 16, 'cols': 24}
    }
    
    df = pd.read_csv(file_path, skiprows = 9)
    print(df.head())
    num_cols = len(df.columns) - 2

    detected_plate = None
    for row, col in plates_sizes.items():
        if col['cols'] == num_cols:
            detected_plate = row
            break
    if detected_plate:
        read_this = plates_sizes[detected_plate]['rows']
        print(f'✓ Detected: {detected_plate} well plate — reading {read_this} rows')
        df = pd.read_csv(file_path, skiprows=9, nrows= read_this)
    else:
        print(f'✗ Unknown plate size — {num_cols} columns not in list')
    table_data = df.iloc[0:read_this, 1:num_cols + 1]
    row_labels = [string.ascii_uppercase[i] for i in range(len(table_data))]
    table_data.insert(0, 'Row_Label', row_labels)
    return table_data

def variable_application(table_data, blank_well, sample_well, sample_concentration):
    def get_well_value(df, well):
        row_label = well[0]
        col_number = int(well[1:])
        row = df[df['Row_Label'] == row_label]
        return row.iloc[0, col_number]
    
    zero_point_value = get_well_value(table_data, blank_well)
    zero_point_concentration = 0

    print(f"0ng/ul standard: Measured Value = {zero_point_value}, Concentration = {zero_point_concentration}ng/ul")

    point_value = get_well_value(table_data, sample_well)
    point_concentration = sample_concentration

    print(f"{sample_concentration}ng/ul standard: Measured Value = {point_value}, Concentration = {point_concentration}ng/ul")
    return zero_point_value, point_value

def concentration_calculation(zero_point_value, point_value, zero_point_concentration, point_concentration):
    m = (point_value - zero_point_value) / (point_concentration - zero_point_concentration)
    b = zero_point_value - (m * zero_point_concentration)

    print(f"Calculated slope (m): {m:.2f}")
    print(f"Calculated y-intercept (b): {b:.2f}")

    def calculate_concentration(measured_value):
        concentration = (2 * ((measured_value - b)/ m))
        return concentration.round(2)
    return calculate_concentration

def calculation_application(table_data, calculate_concentration, zero_point_value, point_value, zero_point_concentration, point_concentration):
    for col in [col for col in table_data.columns if col != 'Row_Label']:
        table_data[col] = table_data[col].apply(calculate_concentration)

    print("Here is the data with calculated concentrations:")
    print(table_data)

    x_values = [zero_point_concentration, point_concentration]
    y_values = [zero_point_value, point_value]

    plt.figure(figsize=(8, 5))
    plt.plot(x_values, y_values, color='blue', linestyle='-', marker='o')
    plt.xlim(0, max(x_values) * 1.1)
    plt.ylim(0, max(y_values) * 1.1)
    plt.title('Calibration Curve')
    plt.ylabel('Measured Fluorescence Value')
    plt.xlabel('Concentration (ng/ul)')
    plt.grid(True)
    plt.show()

    table_data1 = table_data.where(table_data.select_dtypes(include='number') >= 0)
    new_table = table_data1[table_data1 >= 0].fillna('')
    new_table['Row_Label'] = table_data['Row_Label']
    return new_table

def excel_export(new_table, file_name):
    if not os.path.exists('result'):
        os.mkdir('result')
    data_table = new_table.copy()
    data_table['Row_Label'] = new_table['Row_Label']
    data_table.to_excel(f'result/{file_name}_data_table.xlsx', index=False)

def csv_list(new_table, file_name):
    rows = []
    for i, row in new_table.iterrows():
        row_label = row['Row_Label']
        for col in [col for col in new_table.columns if col != 'Row_Label']:
            value = row[col]
            if pd.notna(value) and value != '':
                rows.append({'Well': f"{row_label}{col}", 'Concentration_ng_ul': value})
    csv_df = pd.DataFrame(rows)
    csv_df.to_csv(f'result/{file_name}_well_concentrations.csv', index=False)
    print(f"Saved {len(csv_df)} wells to CSV!")
    print(csv_df)

def main():

    blank_well = input("Enter the blank well (e.g. A1): ").strip().upper()
    sample_well = input("Enter the sample well (e.g. B2): ").strip().upper()
    sample_concentration = float(input("Enter the sample concentration (ng/ul): ").strip())

    file_path = input("Enter the path to your CSV file: ")#.strip()

    while True:
        if not os.path.exists(file_path):
            print(f"✗ File not found: '{file_path}'")
        elif os.path.isdir(file_path):
            print(f"✗ That's a folder, not a file. Please include the filename (e.g. /Users/you/Desktop/data.csv)")
        elif not file_path.lower().endswith('.csv'):
            print(f"✗ File must be a .csv file")
        else:
            break
        file_path = input("Enter the path to your CSV file: ")#.strip()
    file_name = os.path.basename(file_path).replace('.csv', '')
    
    table_data = load_file(file_path)
    zero_point_value, point_value = variable_application(table_data, blank_well, sample_well, sample_concentration)
    calculate_concentration = concentration_calculation(zero_point_value, point_value, 0, sample_concentration)
    new_table = calculation_application(table_data, calculate_concentration, zero_point_value, point_value, 0, sample_concentration)
    excel_export(new_table, file_name)
    csv_list(new_table, file_name)
if __name__ == "__main__":
    main()
