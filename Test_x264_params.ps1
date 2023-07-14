param ([string]$input_video_fname, [String[]]$test_param_list, [string]$output_directory, [switch]$twopass, [switch]$remove_videos)


$num_of_threads = 4
if ($IsWindows) {
    $processor = Get-ComputerInfo -Property CsProcessors
    $num_of_threads = $processor.CsProcessors.NumberOfLogicalProcessors
}
if ($IsLinux) {
    $num_of_threads = $(nproc)
    if ($num_of_threads -gt 10) {
        $num_of_threads = $num_of_threads - 5
    }
}

if ([string]::IsNullOrEmpty($test_param_list)) {
    Write-Host "Testing all parameters"
}
else {
    foreach ($param in $test_param_list) {
        Write-Host "Testing param: $param"
    }
}

if ([string]::IsNullOrEmpty($output_directory)) {
    $output_directory = "encoded_results"
}

if ([string]::IsNullOrEmpty($global:processed_videos)) {
    $global:processed_videos = 0
}

# Remove slash at the end of the path if it exists
if ($output_directory.EndsWith("\") -or $output_directory.EndsWith("/")) {
    $output_directory = $output_directory.Substring(0, $output_directory.Length - 1)
}

New-Item -Name $output_directory -ItemType Directory -Force
New-Item -Name ("$($output_directory)_invalid") -ItemType Directory -Force
$output_directory = Resolve-Path $output_directory

$input_video_fname_base_name = (Get-Item $input_video_fname).BaseName
$input_video_fname_extension = (Get-Item $input_video_fname).Extension

$output_video_fname = $null

function Set-VariableValueToDefault {
    <#
    .DESCRIPTION
    Set all variables values to default. Default value is defined in variable dictionary.
    #>
    foreach ($var_name in $var_names) {
        if (!($null -eq (Get-Variable $var_name -ErrorAction SilentlyContinue).Value)) {
            Write-Host "Setting $var_name to default value" -ForegroundColor DarkYellow
            (Get-Variable $var_name -ErrorAction SilentlyContinue).Value.value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value.default
        }
    }
}

function Merge-Output-Params-Variable {
    <#
    .DESCRIPTION
    Dump all variables values to JSON in order to save it as a log file.
    #>
    $Out_wariable = @{}

    foreach ($var_name in $var_names) {
        $var_value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value
        $Out_wariable[$var_name] = $var_value.value
    }
    return $Out_wariable | ConvertTo-Json
}

function Merge-xparams-String {
    <#
    .DESCRIPTION
    Merge all variables without exclustion to x264-params string. Exclusion is for variable which is currently iterated over.
    #>
    param ($exclusion)

    $x_params = [string]::Empty
    foreach ($var_name in $var_names) {
        if ($var_name -eq $exclusion) {
            continue
        }

        $var_value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value
        if ($null -eq $var_value) {
            write-host "Variable $var_name is not defined"
        }
        else {
            if (($False -eq $var_value.value -and ($var_value.value -is [System.Boolean]))) {
                Write-Host "Option $var_name is not used" -ForegroundColor Yellow
            }
            elseif (($True -eq $var_value.value) -and ($var_value.value -is [System.Boolean])) {
                Write-Host $var_value.value -ForegroundColor DarkBlue
                $correct_var_name = $var_name.Substring(1).Replace("_", "-")
                $x_params += $correct_var_name + "=1" + ":"
            }
            else {
                $correct_var_name = $var_name.Substring(1).Replace("_", "-")
                $x_params += $correct_var_name + "=" + (Get-Variable $var_name).Value.value + ":"
            }
        }

    }
    # Remove last unnecesary colon
    $x_params = $x_params.Substring(0, $x_params.Length - 1)

    return $x_params
}

function Start-Conversion {
    <#
    .DESCRIPTION
    Start conversion.
    #>
    Set-VariableValueToDefault
    foreach ($var_name in $var_names) {
        if (($var_name -notin $test_param_list) -and !([string]::IsNullOrEmpty($test_param_list))) {
            Write-Host "Skipping variable $var_name" -ForegroundColor DarkYellow
            continue
        }
        Set-VariableValueToDefault
        $width = $(Get-Host).UI.RawUI.WindowSize.Width
        $var_name_len = [int]($var_name.Length / 2)
        Write-Host (("=" * ($width / 2 - $var_name_len - 9)) -join "") -NoNewline -ForegroundColor Cyan
        Write-Host "Testing variable $var_name" -ForegroundColor Cyan  -NoNewline
        Write-Host (("=" * ($width / 2 - $var_name_len - 9)) -join "") -ForegroundColor Cyan
        $var_value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value

        # Iterate over all available values of current variable


        foreach ($val in $var_value.available_values) {

            # Checking dependency variables
            if ($var_name -eq "_aq_strength") {
                if ((Get-Variable -Name "_aq_mode" -ErrorAction SilentlyContinue).Value.value -eq 0) {
                    Write-Host "AQ mode is disabled. Skipping variable $var_name" -ForegroundColor DarkYellow
                    continue
                }
            }

            $x_params_current_variable = [string]::Empty

            Write-Host "Appending last variable" -ForegroundColor DarkBlue
            $var_value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value
            if (($False -eq $val -and ($val -is [System.Boolean]))) {
                (Get-Variable -Name $var_name -ErrorAction SilentlyContinue).Value.value = $False
                Write-Host "Option $var_name is not used" -ForegroundColor Yellow
            }
            elseif (($True -eq $val) -and ($val -is [System.Boolean])) {
                (Get-Variable -Name $var_name -ErrorAction SilentlyContinue).Value.value = $True
                Write-Host $var_value.value -ForegroundColor DarkBlue
                $correct_var_name = $var_name.Substring(1).Replace("_", "-")
                $x_params_current_variable += ":" + $correct_var_name + "=1"
            }
            else {
                (Get-Variable -Name $var_name -ErrorAction SilentlyContinue).Value.value = $val
                $correct_var_name = $var_name.Substring(1).Replace("_", "-")
                $x_params_current_variable += ":" + $correct_var_name + "=" + $val #(Get-Variable $var_name).Value.value
            }

            if ($var_name -eq "_keyint") {
                $key_int_val = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value.value
                $min_key_int = [int]([int]$key_int_val / 10)
                if ($min_key_int -lt 1) {
                    $min_key_int = 1
                }
                (Get-Variable -Name "_min_keyint" -ErrorAction SilentlyContinue).Value.value = $min_key_int
                Write-Host "min_keyint set to $((Get-Variable -Name "_min_keyint" -ErrorAction SilentlyContinue).Value.value)" -ForegroundColor Blue
            }

            if ($var_name -eq "_pbratio") {
                (Get-Variable -Name "_no_mbtree" -ErrorAction SilentlyContinue).Value.value = $True
            }

            if ($var_name -eq "_intra_refresh") {
                (Get-Variable -Name "_ref" -ErrorAction SilentlyContinue).Value.value = 1
                (Get-Variable -Name "_b_pyramid" -ErrorAction SilentlyContinue).Value.value = "none"
            }

            # Create x264-params string without current variable
            $exclusion = $var_name
            $x_params = Merge-xparams-String $exclusion

            $x_params += $x_params_current_variable
            
            # Test params per different bitrate
            foreach ($bitrate in $_bitrates.available_values) {
                Write-Host "Testing bitrate $bitrate" -ForegroundColor Cyan

                $output_fname = $input_video_fname_base_name + "+" + $var_name + "=" + $val + "+" + $bitrate
                $output_path = Join-Path -Path $output_directory -ChildPath $output_fname
                $output_video_fname = $output_path + $input_video_fname_extension

                if ($twopass) {
                    if ($IsWindows) {
                        ffmpeg -y -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -preset $preset -b:v "$($bitrate)k" -pass 1 -an -f null NUL && ffmpeg -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -preset $preset -b:v "$($bitrate)k" -pass 2 $output_video_fname
                    }
                    else {
                        ffmpeg -y -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -preset $preset -b:v "$($bitrate)k" -pass 1 -an -f null /dev/null && \ ffmpeg -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -preset $preset -b:v "$($bitrate)k" -pass 2  $output_video_fname
                    }
                }
                else {
                    Write-Host $output_video_fname
                    ffmpeg -y -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -x264-params $x_params -b:v "$($bitrate)k" -c:a copy $output_video_fname
                }

                # Log VMAF path is supplied in param string delimited by colon, so there might be problems in providing full path
                $output_vmaf_xml_fname = $output_fname + ".xml"
                ffmpeg -hide_banner -loglevel warning -i $output_video_fname -i $input_video_fname -lavfi libvmaf=log_path=$($output_vmaf_xml_fname):n_threads=$($num_of_threads):feature=name=psnr -f null -

                $output_vmaf_csv_fname = $output_path + ".csv"
                Select-Xml -Path $output_vmaf_xml_fname -XPath "/VMAF/pooled_metrics" | ForEach-Object { $_.Node.metric } | ConvertTo-Csv | Add-Content -Path $output_vmaf_csv_fname -Encoding UTF8
    
                $vmaf_values = Select-Xml -Path $output_vmaf_xml_fname -XPath "/VMAF/frames" | ForEach-Object { $_.Node.frame.vmaf }
                $low_vmaf_found = $false
                foreach ($value in $vmaf_values) {
                    if ([int]$value -lt 3.0) {
                        $low_vmaf_found = $true
                        break
                    }
                }
                if ($low_vmaf_found) {
                    if ($remove_videos) {
                        Remove-Item -Path $output_video_fname
                    }
                    else {
                        Move-Item -Path $output_video_fname -Destination ("$($output_directory)_invalid")
                    }
                    Move-Item -Path $output_vmaf_xml_fname -Destination ("$($output_directory)_invalid")
                    Move-Item -Path $output_vmaf_csv_fname -Destination ("$($output_directory)_invalid")
                }
                else {
                    Move-Item -Path $output_vmaf_xml_fname -Destination $output_directory
                }

                if ($remove_videos) {
                    Remove-Item -Path $output_video_fname
                }

            }
        }
    }

}


$width = $(Get-Host).UI.RawUI.WindowSize.Width
Write-Host (("=" * ($width / 2 - 6)) -join "") -NoNewline -ForegroundColor Cyan
Write-Host "STARTING" -ForegroundColor Magenta  -NoNewline
Write-Host (("=" * ($width / 2 - 6)) -join "") -ForegroundColor Cyan

enum var_types { int = 1; float = 2; string = 3; bool = 4 }

############################# Rate control type #######################################

# Bitrate in kbps. Bitrate is not present in "var_names" variable
$_bitrates = @{
    default          = 1000
    type             = [var_types]::int
    available_values = 300, 1000, 2000
    value            = $null
}

########################### Frame-type options ########################################


$_keyint = @{
    default          = 250
    type             = [var_types]::int
    available_values = 3, 5, 10, 15, 30, 45, 60, 75, 100, 125, 150, 200, 250, 300
    value            = $null
}
$_min_keyint = @{
    default          = [int]$_keyint.default / 10
    type             = [var_types]::int
    available_values = [int]$_keyint.default / 10
    value            = $null
}
$_no_scenecut = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }
$_scenecut = @{default = 40; type = [var_types]::int; available_values = 10, 20, 30, 40, 50, 60; value = $null }
$_intra_refresh = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }
$_bframes = @{default = 3; type = [var_types]::int; available_values = 1, 2, 3, 4; value = $null }
$_b_adapt = @{default = 1; type = [var_types]::int; available_values = 0, 1, 2; value = $null }
$_b_bias = @{default = 0; type = [var_types]::int; available_values = -100, -50, 0, 50, 100; value = $null }
$_b_pyramid = @{
    default          = "normal"
    type             = [var_types]::string
    available_values = "none", "strict", "normal"
    value            = $null
}
# $_open_gop = 1
# $_no_cabac = $null
# this option won't be used
# Disables CABAC (Context Adaptive Binary Arithmetic Coder) stream compression and falls back to the less efficient CAVLC (Context Adaptive Variable Length Coder) system. Significantly reduces both the compression efficiency (10-20% typically) and the decoding requirements.

$_ref = @{
    default          = 3
    type             = [var_types]::int
    available_values = 0, 2, 3, 4, 6, 8, 10, 12, 14, 16
    value            = $null
}
$_no_deblock = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }
# $_deblock = "0,0"
# # deblock "0:0" is mapped to the "deblock=1:0:0" and "1:0" to the "deblock=1:1:0"

# Slices are used for faster encoding. I won't use this option
# $_slices = 0
# $_slice_max_size = 0
# $_slice_max_mbs = 0

# for both tff and bff
# Enable interlaced encoding and specify the top field is first. x264's interlaced encoding uses MBAFF, and is inherently less efficient than progressive encoding. For that reason, you should only encode interlaced if you intend to display the video on an interlaced display
# $_tff = $null 
# $_bff = $null


$_constrained_intra = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }
# $_pulldown = "none" # is used for telecine. I don't have telecine input
# Mark a stream as interlaced even when not encoding as interlaced. Allows encoding of 25p and 30p Blu-ray compliant videos. I won't use this option
# $_fake_interlaced = $null


########################### Ratecontrol ########################################

#$_crf = @{
#    default = 23
#    type=[var_types]::int
#    available_values = 18,19,20,21,22,23,24,25,26,27,28,29,30
#    value=$null
#}

$_ipratio = @{
    default          = 1.4
    type             = [var_types]::float
    available_values = 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0
    value            = $null
}

$_pbratio = @{
    default          = 1.3
    type             = [var_types]::float
    available_values = 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0
    value            = $null
}

$_chroma_qp_offset = @{
    default          = 0
    type             = [var_types]::int
    available_values = -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6
    value            = $null
}

$_aq_mode = @{
    default          = 1
    type             = [var_types]::int
    available_values = 0, 1, 2
    value            = $null
}

# use this option if aq_mode != 0
$_aq_strength = @{
    default          = 1.0
    type             = [var_types]::float
    available_values = 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5
    value            = $null
}

#$_pass = @{
#    default = $null
#    type=[var_types]::int
#    available_values = 1,2,3
#    value=$null
#}

$_no_mbtree = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }

$_qcomp = @{
    default          = 0.6
    type             = [var_types]::float
    available_values = 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0
    value            = $null
}

$_cplxblur = @{
    default          = 20.0
    type             = [var_types]::float
    available_values = 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0
    value            = $null
}

$_qblur = @{
    default          = 0.5
    type             = [var_types]::float
    available_values = 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0
    value            = $null
}


########################### Analysis ########################################

$_direct = @{
    default          = "spatial"
    type             = [var_types]::string
    available_values = "none", "spatial", "temporal", "auto"
    value            = $null
}

$_no_weightb = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }

$_weightp = @{
    default          = 2
    type             = [var_types]::int
    available_values = 0, 1, 2
    value            = $null
}

$_me = @{
    default          = "hex"
    type             = [var_types]::string
    available_values = "dia", "hex", "umh", "esa", "tesa"
    value            = $null
}

# $_merange = @{
#     default          = 16
#     type             = [var_types]::int
#     available_values = 16, 24, 32, 48, 64, 96, 128
#     value            = $null
# }
# merange controls the max range of the motion search in pixels. For hex and dia, the range is clamped to 4-16, with a default of 16. For umh and esa, it can be increased beyond the default 16 to allow for a wider-range motion search, which is useful on HD footage and for high-motion footage. Note that for umh, esa, and tesa, increasing merange will significantly slow down encoding.

#$_mvrange = TODO

$_subme = @{
    default          = 7
    type             = [var_types]::int
    available_values = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    value            = $null
}

#$_psy_rd = TODO

$_no_psy = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }

$_no_mixed_refs = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }

$_no_chroma_me = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }

$_no_8x8dct = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }

$_trellis = @{
    default          = 1
    type             = [var_types]::int
    available_values = 0, 1, 2
    value            = $null
}

$_no_fast_pskip = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }

$_no_dct_decimate = @{default = $False; type = [var_types]::bool; available_values = $False, $True; value = $null }

$_nr = @{
    default          = 100
    type             = [var_types]::int
    available_values = 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    value            = $null
}

# $_deadzone-inter/intra TODO

$_cqm = @{
    default          = "flat"
    type             = [var_types]::string
    available_values = "flat", "jvt"
    value            = $null
}

##########################
# Initialize variables
Set-Variable -Option AllScope -Name "var_names" -Value "_keyint", "_min_keyint", "_no_scenecut", "_scenecut", "_intra_refresh", "_bframes", "_b_adapt", "_b_bias", "_b_pyramid", "_open_gop", "_no_cabac", "_ref", "_no_deblock", "_deblock", "_slices", "_slice_max_size", "_slice_max_mbs", "_tff", "_bff", "_constrained_intra", "_pulldown", "_fake_interlaced", "_crf", "_ipratio", "_pbratio", "_chroma_qp_offset", "_aq_mode", "_aq_strength", "_pass", "_no_mbtree", "_qcomp", "_cplxblur", "_qblur", "_direct", "_no_weightb", "_weightp", "_me", "_merange", "_mvrange", "_subme", "_psy_rd", "_no_psy", "_no_mixed_refs", "_no_chroma_me", "_no_8x8dct", "_trellis", "_no_fast_pskip", "_no_dct_decimate", "_nr", "_deadzone-inter", "_deadzone-intra", "_cqm"

$x_params = [string]::Empty
$num_of_combinations = 1

foreach ($var_name in $var_names) {
    $var_value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value
    if ($var_value.available_values.Length -gt 0) {
        $num_of_combinations += $var_value.available_values.Length
    }
}
##########################

Write-Host "Number of combinations: $num_of_combinations" -foregroundcolor green

Start-Conversion 

$global:processed_videos += 1
Write-Host "Processed videos: $($global:processed_videos)" -ForegroundColor Cyan
