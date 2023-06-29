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

# Extract the "Mean", "Param", "Bitrate", and "std_dev" columns
y_data = df["Mean"]
std_dev_data = df["std_dev"]
x_data = df["Param"]
bitrate_data = df["Bitrate"]

tested_param = None
# Iterate over each row to extract parameter values
param_values = []
for index, row in df.iterrows():
    # Split the parameter column into individual values
    param_str = row["Param"]
    params = param_str.split(";")
    bitrate = row["Bitrate"]

    for param in params:
        # Extract the value and convert to a float
        value_str = param.split("=")[1]
        tested_param = param.split("=")[0]
        value = None
        try:
            value = float(value_str.replace(",", "."))
        except ValueError:
            value = value_str
        param_values.append((value, tested_param, bitrate))

# Create a dictionary to store the data for each bitrate
bitrate_data_dict = {}

# Iterate over each unique bitrate value
unique_bitrates = bitrate_data.unique()
for bitrate in unique_bitrates:
    bitrate_data_dict[bitrate] = {"x": [], "y": [], "yerr": []}

# Iterate over the parameter values and assign them to the corresponding bitrate
for param_value, tested_param, bitrate in param_values:
    index = param_values.index((param_value, tested_param, bitrate))
    bitrate_data_dict[bitrate]["x"].append(param_value)
    bitrate_data_dict[bitrate]["y"].append(y_data.iloc[index])
    bitrate_data_dict[bitrate]["yerr"].append(std_dev_data.iloc[index])


if tested_param == "keyint":
    # Create a figure and two subplots
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    colors = ['red', 'green', 'blue'] 

    # Plot the first subplot
    axs[0].set_xlabel(tested_param)
    axs[0].set_ylabel("VMAF mean")
    axs[0].set_title("All values")

    # Offset for x values to avoid overlap
    x_offset = 0

    # Plot three separate lines for each x-axis value
    for i, (bitrate, data) in enumerate(bitrate_data_dict.items()):
        # Calculate new x values with a slight offset
        x_values = [x + x_offset * i for x in data["x"]]
        axs[0].errorbar(x_values, data["y"], yerr=data["yerr"], fmt='o', label=f"Bitrate: {bitrate}", color=colors[i], capsize=5)

    # Add a legend to the first subplot
    axs[0].legend(loc="lower right")

    # Plot the second subplot
    axs[1].set_xlabel(tested_param)
    axs[1].set_ylabel("VMAF mean")
    axs[1].set_title("Zoomed in")

    # Plot three separate lines for each x-axis value
    for i, (bitrate, data) in enumerate(bitrate_data_dict.items()):
        # Calculate new x values with a slight offset
        x_values = [x + x_offset * i for x in data["x"]]
        axs[1].errorbar(x_values, data["y"], yerr=data["yerr"], fmt='o', label=f"Bitrate: {bitrate}", color=colors[i], capsize=5)

    # Add a legend to the second subplot on the upper left corner
    axs[1].legend(loc="lower right")

    # Set the limits for the second subplot
    axs[1].set_xlim(50, 320)
    axs[1].set_ylim(0.97, 1.01)

    # Save the figure as a PNG file
    plt.savefig("keyint.png")
    plt.savefig("keyint.svg", format="svg")

    # Display the figure
    plt.show()
else:
    # Create a figure and one subplot
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['red', 'green', 'blue'] 

    # Set the label and title of the subplot
    ax.set_xlabel(tested_param)
    ax.set_ylabel("VMAF mean")
    ax.set_title("All values")

    # Offset for x values to avoid overlap
    x_offset = 0

    # Plot three separate lines for each x-axis value
    for i, (bitrate, data) in enumerate(bitrate_data_dict.items()):
        # Calculate new x values with a slight offset
        x_values = [x + x_offset * i for x in data["x"]]
        ax.errorbar(x_values, data["y"], yerr=data["yerr"], fmt='o', label=f"Bitrate: {bitrate}", color=colors[i], capsize=5)

    # Add a legend to the subplot
    ax.legend(loc="lower right")

    # Save the figure as a PNG file
    plt.savefig(tested_param + ".png")
    plt.savefig(tested_param + ".svg", format="svg")

    # Display the figure
    plt.show()

