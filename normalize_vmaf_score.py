import argparse
import pandas as pd
import csv
import os
import traceback


parser = argparse.ArgumentParser()
parser.add_argument("--file_path", help="Path to the CSV file", required=True)
parser.add_argument("--file_basename", help="Basename of the CSV file", required=True)
parser.add_argument("--file_path_def", help="Path to the def values CSV file", required=True)
args = parser.parse_args()
file_path = args.file_path
basename = args.file_basename
file_path_def = args.file_path_def

out_csv_filename = "normalized_" + basename + ".csv"

def_values = dict()


# Extract bitrate to the last column
input_file = file_path
output_file = "tmp_extract_bitrate.csv"

try:
    bitrate_column_exists = False
    with open(input_file, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        headers = next(reader)  # Read the header row

        # Check if bitrate column already exists
        if headers[-1] == 'Bitrate':
            bitrate_column_exists = True

        if not bitrate_column_exists:
            # Find the index of the first column
            first_column_index = 0

            # Append 'bitrate' to the headers
            headers.append('Bitrate')

            with open(output_file, 'w', newline='') as output:
                writer = csv.writer(output, delimiter=';')
                writer.writerow(headers)  # Write the header row to the output file

                for row in reader:
                    # Split the first column by '+'
                    parts = row[first_column_index].split('+')
                    # Create a new row with the additional column
                    new_row = [parts[0]]  + row[first_column_index+1:] + [parts[1]]

                    writer.writerow(new_row)  # Write the updated row to the output file
    if not bitrate_column_exists:
        # Replace the original file with the new one
        os.remove(input_file)
        os.rename(output_file, input_file)
except:
    print("Error while extracting bitrate")
    traceback.print_exc()
    exit(1)


# read the csv file line by line
with open(file_path_def, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    # skip the header
    next(csv_reader)
    for row in csv_reader:
        param = row[0]
        value = row[1]
        def_values[param] = value


# Load the CSV file
cols = list(pd.read_csv(file_path, nrows=1, delimiter=";", encoding="utf-8"))
df = pd.read_csv(file_path, delimiter=";", decimal=",", usecols =[i for i in cols if i != 'Mean'], encoding="utf-8")
tested_files = []
# get columns from dataframe
for column in df.columns:
    if (column != "Mean") and (column != "Param") and (column != "Bitrate"):
        tested_files.append(column)

# Extract "Param" and "Bitrate" columns and combine them into one dataframe
params = df["Param"]
bitrates = df["Bitrate"]
params_bitrates = pd.concat([params, bitrates], axis=1)

def_value_row = dict()

for param_bitrate in params_bitrates.values:
    param = param_bitrate[0]
    params_s = param.split("=")
    bitrate = param_bitrate[1]
    #if "," in params_s[1]:
    #    params_s[1] = float(params_s[1].replace(",", "."))
    #    try:
    #        def_values[params_s[0]] = float(def_values[params_s[0]].replace(",", "."))
    #    except AttributeError:
    #        pass
    if (params_s[1] == def_values[params_s[0]]):
        def_value_row[bitrate] = param


vmaf_score_def_value = dict()
for key in def_value_row.keys():
    vmaf_score_def_value[key] = df[(df['Param'] == def_value_row[key]) & (df['Bitrate'] == key)]

# Drop the bitrate column
for key in def_value_row.keys():
    vmaf_score_def_value[key] = vmaf_score_def_value[key].drop(columns=['Bitrate'])
    vmaf_score_def_value[key].set_index('Param', inplace=True)


output_dataframes = dict()
merged_output_df = pd.DataFrame()
# Create single dataframe for each bitrate. Key is the bitrate value
for key in def_value_row.keys():
    print(key)
    output_dataframes[key] = pd.DataFrame()
    # Create subdataframe where bitrate is equal to key
    subdataframe = df[df['Bitrate'] == key]
    #Drop the bitrate column
    subdataframe = subdataframe.drop(columns=['Bitrate'])
    output_df = pd.DataFrame()
    for param in params:
        if param != def_value_row[key]:
            vmaf_score_param = subdataframe[subdataframe['Param'] == param]
            vmaf_score_param.set_index('Param', inplace=True)
            divided = vmaf_score_param.iloc[0] / (vmaf_score_def_value[key]).iloc[0]
            # calculate the mean of the row and append it to the dataframe
            mean = divided.mean()
            divided = pd.concat([divided, pd.Series(mean, index=['Mean'])])
            divided = divided.round(3)
            output_df[param] = divided
        else:
            # Set row values to 1.0. But first generate dataframe, because default one can be the first one in the list
            columns = [i for i in cols if (i != 'Mean' and i != 'Param')]
            columns.append('Mean')
            row = pd.DataFrame(data=[[1.0 for i in range(len(cols)-1)]], columns=columns, index=[param])
            row = row.transpose()
            output_df[param] = row
    output_df = output_df.transpose()
    output_df.index.name = 'Param'
    # Add the bitrate column
    output_df['Bitrate'] = key
    # Add dataframe to merged dataframe using concat
    merged_output_df = pd.concat([merged_output_df, output_df], axis=0)


exclude_columns = ['Param', 'Mean', 'Bitrate']

# Get the list of dynamic FileX headers
file_columns = [col for col in merged_output_df.columns if col not in exclude_columns]

# Calculate standard deviation for each row and store it in a new column 'std_dev'
merged_output_df['std_dev'] = merged_output_df[file_columns].std(axis=1)

# Print the updated DataFrame
print(merged_output_df)

merged_output_df.to_csv(out_csv_filename, sep=';', decimal=',', encoding='utf-8')