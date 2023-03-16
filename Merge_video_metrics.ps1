param ([string]$input_video_metric, [string]$log_csv_filename, [string]$output_directory, [string]$def_values_csv)

if ([string]::IsNullOrEmpty($output_directory)){
    $output_directory = "video_metrics_full"
}
New-Item -Name $output_directory -ItemType Directory -Force

$video_metrics = Import-Csv -Delimiter ';' -Path $input_video_metric 

$video_metrics
$video = $video_metrics.video
$si = $video_metrics.si
$ti = $video_metrics.ti
$resolution = $video_metrics.resolution
$input_bitrate = $video_metrics.bitrate

$output_file = Join-Path $output_directory "$($video).csv"
$data = Import-Csv -Delimiter ';' -Path $log_csv_filename -Header "Filename", "Param", "Output_bitrate", "Value"
$headers = $data.Param | Select-Object -Unique
$tested_params = $headers -replace "=.*" | Select-Object -Unique

$def_values = Import-Csv -Delimiter ';' -Path $def_values_csv -Header "Param", "Value"

$header_line = "video;si;ti;resolution;input_bitrate;vmaf;output_bitrate"
foreach ($t_param in $tested_params) {
    $header_line += ";$t_param"
}
Add-Content -Path $output_file -Value $header_line

foreach ($row in $data) {
    $vmaf = $row.Value
    $param = $row.Param
    $output_bitrate = $row.Output_bitrate
    $param_name = $param -replace "=.*"
    $param_value = $param -replace ".*="
    $line = "$video;$si;$ti;$resolution;$input_bitrate;$vmaf;$output_bitrate"
    foreach ($t_param in $tested_params) {
        if ($t_param -eq $param_name) {
            $line += ";$param_value"
        } else {
            $line += ";$($($def_values | Where-Object {$_.Param -eq $t_param}).Value)"
        }
        #$def_values | Where-Object {$_.Param -eq $param}
    }
    Add-Content -Path $output_file -Value $line
}