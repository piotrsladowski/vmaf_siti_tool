param(
    [Parameter(Mandatory=$true)]
    [string]$input_csv_dir,
    [Parameter(Mandatory=$true)]
    [string]$def_values_csv,
    [Parameter(Mandatory=$true)]
    [string]$input_video_metrics,
    [Parameter(Mandatory=$true)]
    [string]$experiment_number
)

$all_results_fname = "results_all_$experiment_number.csv"

Write-Host "Extracting results" -ForegroundColor Cyan
Get-ChildItem -Filter "*.csv" -Path $input_csv_dir | ForEach-Object { 
        $tested_var = $_.BaseName.Split('+')[1]; 
        $csv = Import-Csv -Path $_.FullName; 
        $vmaf_min = ($csv | Where-Object { $_.name -eq 'vmaf' }).min;
        if ($vmaf_min -is [System.Object[]]) {
            $vmaf_min = $vmaf_min[0]
        }
        if ([int]$vmaf_min -lt 1.0) {
            Write-Host "Omitting $($_.Name): $vmaf_min" -ForegroundColor Yellow
        }
        else {
            $vmaf_mean = ($csv | Where-Object { $_.name -eq 'vmaf' }).mean;
            $short_name = ($_.Name -split '\+' )[0]; 
            $bitrate = ($_.Basename -split '\+' )[2]; 
            Write-Output "$($short_name);$($tested_var);$($bitrate);$($vmaf_mean)"
        }
    } | Out-File -FilePath $all_results_fname -Encoding utf8


Write-Host "Merging video metrics. May take a while..." -ForegroundColor Cyan
$output_metrics_dir = "$($experiment_number)_video_metrics_full"
Get-ChildItem -Path $input_video_metrics -Filter "*.csv" | ForEach-Object { 
    Merge_video_metrics.ps1 -input_video_metric $_.FullName -log_csv_filename $all_results_fname -output_directory $output_metrics_dir -def_values_csv $def_values_csv
}

Write-Host "Creating train data" -ForegroundColor Cyan
# Concatenate all files from $output_metrics_dir into one file
Get-ChildItem -Path $output_metrics_dir | ForEach-Object { 
    Add-Content -Path "train_data_$($experiment_number).csv" -Value (Get-Content -Path $_.FullName)
}

$header = Get-Content -Path "train_data_$($experiment_number).csv" | Select-Object -First 1

# remove all lines from train_data_$experiment_number.csv equal to $header
Get-Content -Path "train_data_$($experiment_number).csv" | Where-Object { $_ -ne $header } | Out-File -FilePath "train_data_$($experiment_number)_tmp.csv" -Encoding utf8
Remove-Item "train_data_$($experiment_number).csv"
Add-Content -Path "train_data_$($experiment_number).csv" -Value $header
Add-Content -Path "train_data_$($experiment_number).csv" -Value (Get-Content -Path "train_data_$($experiment_number)_tmp.csv")

$csv_file = "train_data_$($experiment_number).csv"
(Get-Content $csv_file) -replace 'ultrafast', '0' | Set-Content $csv_file
(Get-Content $csv_file) -replace 'superfast', '1' | Set-Content $csv_file
(Get-Content $csv_file) -replace 'veryfast', '2' | Set-Content $csv_file
(Get-Content $csv_file) -replace 'faster', '3' | Set-Content $csv_file
(Get-Content $csv_file) -replace 'fast', '4' | Set-Content $csv_file
(Get-Content $csv_file) -replace 'medium', '5' | Set-Content $csv_file
(Get-Content $csv_file) -replace 'veryslow', '8' | Set-Content $csv_file
(Get-Content $csv_file) -replace 'slower', '7' | Set-Content $csv_file
(Get-Content $csv_file) -replace 'slow', '6' | Set-Content $csv_file

Write-Host "Removing temporary files" -ForegroundColor Cyan
Remove-Item "train_data_$($experiment_number)_tmp.csv"
Write-Host "Done" -ForegroundColor Green