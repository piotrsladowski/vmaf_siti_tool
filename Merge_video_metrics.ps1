param ([string]$input_video_metric, [string]$log_csv_filename, [string]$output_directory, [string]$def_values_csv)

if ([string]::IsNullOrEmpty($output_directory)){
    $output_directory = "video_metrics_full"
}
[void](New-Item -Name $output_directory -ItemType Directory -Force)

$video_metrics = Import-Csv -Delimiter ';' -Path $input_video_metric 

$video = $video_metrics.video
$si_avg = $video_metrics.si_avg
$si_std = $video_metrics.si_std
$si_min = $video_metrics.si_min
$si_max = $video_metrics.si_max

$ti_avg = $video_metrics.ti_avg
$ti_std = $video_metrics.ti_std
$ti_min = $video_metrics.ti_min
$ti_max = $video_metrics.ti_max

$criticality = $video_metrics.criticality

$resolution = $video_metrics.resolution
$width = $video_metrics.width
$height = $video_metrics.height
$input_bitrate = $video_metrics.input_bitrate
$duration_original = $video_metrics.duration_original

$output_file = Join-Path $output_directory "$($video).csv"
$data = Import-Csv -Delimiter ';' -Path $log_csv_filename -Header "Filename", "Param", "Output_bitrate", "Value"
$headers = $data.Param | Select-Object -Unique
$tested_params = $headers -replace "=.*" | Select-Object -Unique

$def_values = Import-Csv -Delimiter ';' -Path $def_values_csv -Header "Param", "Value"

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
    "duration_original",
    "vmaf",
    "output_bitrate"
)

$header_line = $header_values -join ";"

foreach ($t_param in $tested_params) {
    $header_line += ";$t_param"
}
Add-Content -Path $output_file -Value $header_line

foreach ($row in $data) {
    $log_csv_fname = $row.Filename
    if($log_csv_fname -ne $video) {
        continue
    }
    $vmaf = $row.Value
    $param = $row.Param
    $output_bitrate = $row.Output_bitrate
    $param_name = $param -replace "=.*"
    $param_value = $param -replace ".*="
    $row_values = @(
        $video,
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
        $duration_original,
        $vmaf,
        $output_bitrate
    )
    $line = $row_values -join ";"
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