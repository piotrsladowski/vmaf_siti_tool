param ([string]$input_result_file)

$file = Split-Path $input_result_file -Leaf

$output_result_file = "excel_$($file)"

# Read the input CSV file
$data = Import-Csv -Delimiter ';' -Path $input_result_file -Header "Filename", "Param", "Value"

# Extract the unique headers from the input data
$headers = $data.Filename | Select-Object -Unique

# Create a hashtable to hold the output data
$output = @{}

# Loop through the input data and populate the hashtable
foreach ($row in $data) {
    $key = $row.Param
    $value = $row.Value
    $filename = $row.Filename
    if ($output.ContainsKey($key)) {
        $output[$key][$filename] = $value
    } else {
        $output[$key] = @{}
        $output[$key][$filename] = $value
    }
}

#$output.Keys
$h_line = "Param"
$headers | ForEach-Object{
    $h_line += ";$_"
}
$h_line += ";Mean"

Write-Host "Writing new file"
$h_line | Out-File -FilePath $output_result_file -Encoding utf8


# Output the data in the desired format
$output.Keys | Sort-Object | ForEach-Object {
    $key = $_
    $line = "$key"
    $sum = 0.0
    foreach ($header in $headers) {
        $value = $output[$key][$header]
        if ($value) {
            $sum += [float]$value
            # Round the value to 2 decimal places
            $value = [math]::Round($value, 3)
            $line += ";$value"
        } else {
            $line += ";"
        }
    }
    $mean = $sum / $headers.Count
    $mean = [math]::Round($mean, 3)
    $line += ";$mean"
    $line = $line -replace '\.', ','
    $line
} | Out-File -FilePath $output_result_file -Encoding utf8 -Append