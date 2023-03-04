param ([string]$input_video_file, [string]$siti_output_dir, [string]$output_directory)

if ([string]::IsNullOrEmpty($output_directory)){
    $output_directory = "video_metrics_basic"
}
New-Item -Name $output_directory -ItemType Directory -Force

$video_basename = Split-Path $input_video_file -LeafBase
$output_file = Join-Path $output_directory "$($video_basename).csv"

$siti_log_file = Get-ChildItem -Path $siti_output_dir -Filter "$video_basename.json"
if ($siti_log_file -eq $null) {
    Write-Host "SITI log file not found for $video_basename"
    exit(1)
}
$siti = Get-Content $siti_log_file.FullName | Out-String | ConvertFrom-Json

$si = $siti.si | Measure-Object -Average | Select-Object -ExpandProperty Average
$ti = $siti.ti | Measure-Object -Average | Select-Object -ExpandProperty Average

$resolution_raw = (ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 $input_video_file)
$dims = $resolution_raw -split "x"
$resolution = [int](([float]$dims[0]) * ([float]$dims[1]))

$bitrate = ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -of csv=s=x:p=0 $input_video_file

Add-Content -Path $output_file -Value "video;si;ti;resolution;bitrate"
Add-Content -Path $output_file -Value "$($video_basename);$($si);$($ti);$($resolution);$($bitrate)"

