param ([string]$results_dir, [string]$source_video_dir, [string]$correct_results_output_dir)

Write-Host "Looking for invalid vmaf value in XML files" -ForegroundColor Yellow
$invalid_vmaf = Get-ChildItem -Path $results_dir -Filter *.xml | ForEach-Object {
    $file = $_.FullName
    $vmaf_values = Select-Xml -Path $file -XPath "/VMAF/frames" | ForEach-Object { $_.Node.frame.vmaf }
    $low_vmaf_found = $false
    foreach ($value in $vmaf_values) {
        if ([int]$value -lt 2.0) {
            $low_vmaf_found = $true
            break
        }
    }
    if ($low_vmaf_found) {
        Write-Output $file
    }
}


# Define an array to store the extracted file names
$fileNames = @()

foreach ($filePath in $invalid_vmaf) {
    # Extract the file name from the file path
    $fileName = $filePath.Substring($filePath.LastIndexOf("\") + 1)
    $fileName = $fileName.Substring(0, $fileName.IndexOf("+"))
    $fileName = $fileName + ".mp4"

    if ($fileName -notin $fileNames) {
        $fileNames += $fileName
    }
}

#$fileNames

if (!([string]::IsNullOrEmpty($correct_results_output_dir))){
    Write-Host "Copying correct vmaf files to $correct_results_output_dir"
    New-Item -Name $correct_results_output_dir -ItemType Directory -Force
    Get-ChildItem -Path $results_dir -Filter *.csv | ForEach-Object {
        $fileName = $_.Name.Substring($_.Name.LastIndexOf("\") + 1)
        $fileName = $fileName.Substring(0, $fileName.IndexOf("+"))
        $fileName = $fileName + ".mp4"
        if ($fileName -notin $fileNames) {
            Copy-Item -Path $_.FullName -Destination $correct_results_output_dir
        }
    }
}

$num_of_invalid = 0
$num_of_valid = 0

Get-ChildItem -Path $source_video_dir -Filter "*.mp4" | foreach {
    $output = (ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=avg_frame_rate $_.FullName)
    $numerator, $denominator = $output.Trim().Split('/')
    $numerator = [int]$numerator
    $denominator = [int]$denominator
    $result = $numerator / $denominator
    if ($_.Name -in $fileNames) {
        $num_of_invalid += 1
        Write-Host "$($_.Name): $($result) - $(ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate $_.Fullname)" -ForegroundColor Red
    }
    else {
        $num_of_valid += 1
        Write-Host "$($_.Name): $($result) - $(ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate $_.Fullname)" -ForegroundColor Green
    }
    
}

Write-Host "Number of invalid videos: $num_of_invalid" -ForegroundColor Red
Write-Host "Number of valid videos: $num_of_valid" -ForegroundColor Green
Write-Host "Number of total videos: $($num_of_invalid + $num_of_valid)" -ForegroundColor Yellow