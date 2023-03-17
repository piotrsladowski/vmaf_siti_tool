param ([switch]$fullmode, [string]$input_video_fname, [string]$test_single_param, [string]$output_directory, [switch]$twopass)


$bitrate_low_threshold = 400
$bitrate_upper_threshold = 6000

$num_of_threads = 4
if ($IsWindows){
    $processor = Get-ComputerInfo -Property CsProcessors
    $num_of_threads = $processor.CsProcessors.NumberOfLogicalProcessors
}

if ([string]::IsNullOrEmpty($test_single_param)){
    Write-Host "Testing all parameters"
}
else {
    Write-Host "Testing single parameter $test_single_param"
}

if ([string]::IsNullOrEmpty($output_directory)){
    $output_directory = "encoded_results"
}

New-Item -Name $output_directory -ItemType Directory -Force
$output_directory = Resolve-Path $output_directory

$input_video_fname_base_name = (Get-Item $input_video_fname).BaseName
$input_video_fname_extension = (Get-Item $input_video_fname).Extension

$output_video_fname = $null


function Start-Conversion {

    foreach ($preset in $presets){

        $width = $(Get-Host).UI.RawUI.WindowSize.Width
        $preset_len = [int]($preset.Length/2)
        Write-Host (("=" * ($width/2 - $preset_len - 9)) -join "") -NoNewline -ForegroundColor Cyan
        Write-Host "Testing preset $preset" -ForegroundColor Cyan  -NoNewline
        Write-Host (("=" * ($width/2 - $preset_len - 9)) -join "") -ForegroundColor Cyan
            
            # Test params per different bitrate
            for ($i = 0; $i -lt 5; $i++) {
                $bitrate = Get-Random -Minimum $bitrate_low_threshold -Maximum $bitrate_upper_threshold
                Write-Host "Testing bitrate $bitrate" -ForegroundColor Cyan

                $output_fname = $input_video_fname_base_name + "+" + $var_name + "=" + $val + "+" + $bitrate
                $output_path = Join-Path -Path $output_directory -ChildPath $output_fname
                $output_video_fname = $output_path + $input_video_fname_extension

                if ($twopass)
                {
                    if ($IsWindows)
                    {
                        ffmpeg -y -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -preset $preset -b:v "$($bitrate)k" -pass 1 -an -f null NUL && ` ffmpeg -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -preset $preset -b:v "$($bitrate)k" -pass 2 $output_video_fname
                    }
                    else {
                        ffmpeg -y -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -preset $preset -b:v "$($bitrate)k" -pass 1 -an -f null /dev/null && \ ffmpeg -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -preset $preset -b:v "$($bitrate)k" -pass 2  $output_video_fname

                    }
                }
                else {
                    ffmpeg -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -preset $preset -b:v "$($bitrate)k" -c:a copy $output_video_fname
                }

                # Log VMAF path is supplied in param string delimited by colon, so there might be problems in providing full path
                $output_vmaf_xml_fname = $output_fname + ".xml"
                ffmpeg -hide_banner -loglevel warning -i $output_video_fname -i $input_video_fname -lavfi libvmaf=log_path=$($output_vmaf_xml_fname):n_threads=$($num_of_threads):feature=name=psnr -f null -

                $output_vmaf_csv_fname = $output_path + ".csv"
                #Select-Xml -Path $output_vmaf_fname -XPath "/VMAF/pooledmetrics" | Select-Object -ExpandProperty Node | Select-Object -ExpandProperty InnerText | Add-Content -Path $output_vmaf_fname -Encoding UTF8 -NoNewline
                Select-Xml -Path $output_vmaf_xml_fname -XPath "/VMAF/pooled_metrics" | ForEach-Object { $_.Node.metric} | ConvertTo-Csv | Add-Content -Path $output_vmaf_csv_fname -Encoding UTF8
                
                # Move VMAF log to output directory
                Move-Item -Path $output_vmaf_xml_fname -Destination $output_directory
            }
        }
    }



$width = $(Get-Host).UI.RawUI.WindowSize.Width
Write-Host (("=" * ($width/2 - 6)) -join "") -NoNewline -ForegroundColor Cyan
Write-Host "STARTING" -ForegroundColor Magenta  -NoNewline
Write-Host (("=" * ($width/2 - 6)) -join "") -ForegroundColor Cyan


################################# Presets ###########################################

$presets = @("ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow")

############################# Rate control type #######################################



Start-Conversion $fullmode
