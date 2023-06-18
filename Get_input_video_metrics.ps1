param ([string]$input_video_file, [string]$siti_output_dir, [string]$output_directory)

if ([string]::IsNullOrEmpty($output_directory)){
    $output_directory = "video_metrics_basic"
}
[void](New-Item -Name $output_directory -ItemType Directory -Force)

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

# metrics are extracted separately because ffprobe is not adding separator between null values
$resolution_raw = (ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 $input_video_file)
$dims = $resolution_raw -split "x"
$width = [int]([float]$dims[0])
$height = [int]([float]$dims[1])
$resolution = [int]($width * $height)

$bitrate = ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -of csv=s=x:p=0 $input_video_file
# Remove all characters except digits
$input_bitrate = $bitrate -replace "[^0-9]",""
$input_bitrate = [float](($input_bitrate -as [int]) / 1000)

$duration_original = [float](ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=s=x:p=0 $input_video_file)

$header_values = @(
    "video",
    "si_avg",
    "si_std",
    "si_min",
    "si_max",
    "ti_avg",
    "ti_std",
    "ti_min",
    "ti_max",
    "criticality",
    "resolution",
    "width",
    "height",
    "input_bitrate",
    "duration_original"
)

$header = $header_values -join ";"
$row_values = @(
    $video_basename,
    $si_avg,
    $si_std,
    $si_min,
    $si_max,
    $ti_avg,
    $ti_std,
    $ti_min,
    $ti_max,
    $criticality,
    $resolution,
    $width,
    $height,
    $input_bitrate,
    $duration_original
)
$row = $row_values -join ";"

Add-Content -Path $output_file -Value $header
Add-Content -Path $output_file -Value $row

