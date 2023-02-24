import pandas as pd
import matplotlib.pyplot as plt
import argparse

# Create an argument parser object
parser = argparse.ArgumentParser()
parser.add_argument("--file_path", help="Path to the CSV file", required=True)
args = parser.parse_args()
file_path = args.file_path


# Load the CSV file
df = pd.read_csv(file_path, delimiter=";", decimal=",", encoding="utf-8")

# Extract the "Mean" and "Param" columns
y_data = df["Mean"]
x_data = df["Param"]

tested_param = None

# Iterate over each row to extract parameter values
param_values = []
for index, row in df.iterrows():
    # Split the parameter column into individual values
    param_str = row["Param"]
    params = param_str.split(";")

    # Find the value for the selected parameter (e.g., A001)
    selected_param = "A001"
    for param in params:
        # Extract the value and convert to a float
        value_str = param.split("=")[1]
        tested_param = param.split("=")[0]
        value = None
        try:
            value = float(value_str.replace(",", "."))
        except ValueError:
            value = value_str
        param_values.append(value)

# Plot the scatter chart
plt.scatter(param_values, y_data)
plt.xlabel(tested_param)
plt.ylabel("Mean")

# Add labels to each dot
for x, y, label in zip(param_values, y_data, x_data):
    plt.text(x, y, round(y, 3))

# Save the scatter chart as a PNG file
plt.savefig("{0}.png".format(tested_param))