import pandas as pd

# Read the Excel file
df = pd.read_excel('attached_assets/Wohnungskalkulationen_RAW.xlsx')

# Display basic information about the structure
print("Excel File Structure:")
print(df.info())

# Display the first few rows
print("\nFirst few rows:")
print(df.head())

# Display column names
print("\nColumns:")
print(df.columns.tolist())
