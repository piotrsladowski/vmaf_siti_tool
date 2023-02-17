# Read the input CSV file
$data = Import-Csv -Delimiter ';' -Path "wyniki2.csv" -Header "Filename", "Param", "Value"

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

$output.Keys
$h_line = "Param"
$headers | ForEach-Object{
    $h_line += ";$_"
}

$h_line | Out-File -FilePath "output.csv" -Encoding utf8


# Output the data in the desired format
$output.Keys | Sort-Object | ForEach-Object {
    $key = $_
    $line = "$key"
    foreach ($header in $headers) {
        $value = $output[$key][$header]
        if ($value) {
            $line += ";$value"
        } else {
            $line += ";"
        }
    }
    $line
} | Out-File -FilePath "output.csv" -Encoding utf8 -Append