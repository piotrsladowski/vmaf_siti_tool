import argparse
import pandas as pd
import csv


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
    if (column != "Mean") and (column != "Param"):
        tested_files.append(column)

params = df["Param"]

def_value_row = None

for param in params:
    params_s = param.split("=")
    if (params_s[1] == def_values[params_s[0]]):
        def_value_row = param

vmaf_score_def_value = df[df['Param'] == def_value_row]
vmaf_score_def_value.set_index('Param', inplace=True)

output_df = pd.DataFrame()

for param in params:
    if param != def_value_row:
        vmaf_score_param = df[df['Param'] == param]
        vmaf_score_param.set_index('Param', inplace=True)
        divided = vmaf_score_param.iloc[0] / vmaf_score_def_value.iloc[0]
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

output_df.to_csv(out_csv_filename, sep=';', decimal=',', encoding='utf-8')