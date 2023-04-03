param ([string]$input_video_file, [string]$siti_output_dir, [string]$output_directory)

if ([string]::IsNullOrEmpty($output_directory)){
    $output_directory = "video_metrics_basic"
}
New-Item -Name $output_directory -ItemType Directory -Force

$video_basename = Split-Path $input_video_file -LeafBase
$output_file = Join-Path $output_directory "$($video_basename).csv"

$siti_log_file = Get-ChildItem -Path $siti_output_dir -Filter "$video_basename.json"
if ($null -eq $siti_log_file) {
    Write-Host "SITI log file not found for $video_basename"
    exit(1)
}
$siti = Get-Content $siti_log_file.FullName | Out-String | ConvertFrom-Json

$si = $siti.si | Measure-Object -AllStats
$ti = $siti.ti | Measure-Object -AllStats

$si_avg = [math]::Round($si.Average, 2)
$si_std = [math]::Round($si.StandardDeviation, 2)
$si_min = [math]::Round($si.Minimum, 2)
$si_max = [math]::Round($si.Maximum, 2)

$ti_avg = [math]::Round($ti.Average, 2)
$ti_std = [math]::Round($ti.StandardDeviation, 2)
$ti_min = [math]::Round($ti.Minimum, 2)
$ti_max = [math]::Round($ti.Maximum, 2)

$criticality = [math]::Log($si_avg * $ti_avg, 2)
$criticality = [math]::Round($criticality, 2)

$resolution_raw = (ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 $input_video_file)
$dims = $resolution_raw -split "x"
$resolution = [int](([float]$dims[0]) * ([float]$dims[1]))

$bitrate = ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -of csv=s=x:p=0 $input_video_file
# Remove all characters except digits
$bitrate = $bitrate -replace "[^0-9]",""

Add-Content -Path $output_file -Value "video;si_avg;si_std;si_min;si_max;ti_avg;ti_std;ti_min;ti_max;criticality;resolution;bitrate"
Add-Content -Path $output_file -Value "$($video_basename);$($si_avg);$($si_std);$($si_min);$($si_max);$($ti_avg);$($ti_std);$($ti_min);$($ti_max);$($criticality);$($resolution);$($bitrate)"

