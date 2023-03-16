param ([switch]$fullmode, [string]$input_video_fname, [string]$test_single_param, [string]$output_directory)


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

function Set-VariableValueToDefault {
    <#
    .DESCRIPTION
    Set all variables values to default. Default value is defined in variable dictionary.
    #>
    foreach ($var_name in $var_names) {
        if (!($null -eq (Get-Variable $var_name -ErrorAction SilentlyContinue).Value)){
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
        if ($var_name -eq $exclusion){
            continue
        }

        $var_value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value
        if($null -eq $var_value){
            write-host "Variable $var_name is not defined"
        }
        else{
            if (($False -eq $var_value.value -and ($var_value.value -is [System.Boolean]))) {
                Write-Host "Option $var_name is not used" -ForegroundColor Yellow
            }
            elseif (($True -eq $var_value.value) -and ($var_value.value -is [System.Boolean])){
                Write-Host $var_value.value -ForegroundColor DarkBlue
                $correct_var_name = $var_name.Substring(1).Replace("_","-")
                $x_params += $correct_var_name + "=1" + ":"
            }
            else{
                $correct_var_name = $var_name.Substring(1).Replace("_","-")
                $x_params += $correct_var_name + "=" + (Get-Variable $var_name).Value.value + ":"
            }
        }

    }
    # Remove last unnecesary colon
    $x_params = $x_params.Substring(0,$x_params.Length-1)

    return $x_params
}

function Start-Conversion {
    <#
    .DESCRIPTION
    Start conversion.
    #>
    param ([switch]$fullmode)
    Set-VariableValueToDefault
    foreach ($var_name in $var_names) {
        if (($var_name -ne $test_single_param) -and !([string]::IsNullOrEmpty($test_single_param))){
            Write-Host "Skipping variable $var_name" -ForegroundColor DarkYellow
            continue
        }
        Set-VariableValueToDefault
        $width = $(Get-Host).UI.RawUI.WindowSize.Width
        $var_name_len = [int]($var_name.Length/2)
        Write-Host (("=" * ($width/2 - $var_name_len - 9)) -join "") -NoNewline -ForegroundColor Cyan
        Write-Host "Testing variable $var_name" -ForegroundColor Cyan  -NoNewline
        Write-Host (("=" * ($width/2 - $var_name_len - 9)) -join "") -ForegroundColor Cyan
        $var_value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value

        # Iterate over all available values of current variable


        foreach ($val in $var_value.available_values){

            # Checking dependency variables
            if ($var_name -eq "_aq_strength"){
                if ((Get-Variable -Name "_aq_mode" -ErrorAction SilentlyContinue).Value.value -eq 0){
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
            elseif (($True -eq $val) -and ($val -is [System.Boolean])){
                (Get-Variable -Name $var_name -ErrorAction SilentlyContinue).Value.value = $True
                Write-Host $var_value.value -ForegroundColor DarkBlue
                $correct_var_name = $var_name.Substring(1).Replace("_","-")
                $x_params_current_variable += ":" + $correct_var_name + "=1"
            }
            else{
                (Get-Variable -Name $var_name -ErrorAction SilentlyContinue).Value.value = $val
                $correct_var_name = $var_name.Substring(1).Replace("_","-")
                $x_params_current_variable += ":" + $correct_var_name + "=" + $val #(Get-Variable $var_name).Value.value
            }

            if ($var_name -eq "_keyint"){
                $key_int_val = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value.value
                $min_key_int = [int]([int]$key_int_val/10)
                if ($min_key_int -lt 1){
                    $min_key_int = 1
                }
                (Get-Variable -Name "_min_keyint" -ErrorAction SilentlyContinue).Value.value = $min_key_int
                Write-Host "min_keyint set to $((Get-Variable -Name "_min_keyint" -ErrorAction SilentlyContinue).Value.value)" -ForegroundColor Blue
            }
            # Create x264-params string without current variable
            $exclusion = $var_name
            $x_params = Merge-xparams-String $exclusion

            $x_params += $x_params_current_variable
            
            # Test params per different bitrate
            for ($i = 0; $i -lt 5; $i++) {
                $bitrate = Get-Random -Minimum $bitrate_low_threshold -Maximum $bitrate_upper_threshold
                Write-Host "Testing bitrate $bitrate" -ForegroundColor Cyan

                $output_fname = $input_video_fname_base_name + "+" + $var_name + "=" + $val + "+" + $bitrate
                $output_path = Join-Path -Path $output_directory -ChildPath $output_fname
                $output_video_fname = $output_path + $input_video_fname_extension

                Write-Host "---------x264-params: $x_params ----------------" -ForegroundColor Red
                if ($IsWindows)
                {
                    ffmpeg -y -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -b:v "$($bitrate)k" -pass 1 -an -f null NUL && ` ffmpeg -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -b:v "$($bitrate)k" -pass 2 -b:a 128k $output_video_fname
                }
                else {
                    ffmpeg -y -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -b:v "$($bitrate)k" -pass 1 -an -f null /dev/null && \ ffmpeg -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -b:v "$($bitrate)k" -pass 2 -b:a 128k $output_video_fname

                }
                #ffmpeg -hide_banner -loglevel warning -i $input_video_fname -c:v libx264 -b:v "$($bitrate)k" -x264-params $x_params -c:a copy $output_video_fname

                $output_log_fname = $output_path + ".log"
                Merge-Output-Params-Variable | Out-File -FilePath $output_log_fname -Encoding UTF8 -NoNewline

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

    if ($fullmode){
        Write-Host "Not yet implemented" -ForegroundColor Magenta
    }
}


$width = $(Get-Host).UI.RawUI.WindowSize.Width
Write-Host (("=" * ($width/2 - 6)) -join "") -NoNewline -ForegroundColor Cyan
Write-Host "STARTING" -ForegroundColor Magenta  -NoNewline
Write-Host (("=" * ($width/2 - 6)) -join "") -ForegroundColor Cyan

enum var_types {int = 1; float = 2; string = 3; bool = 4}

############################# Rate control type #######################################

# Bitrate in kbps. Bitrate is not present in "var_names" variable
$_bitrates = @{
    default=2000
    type=[var_types]::int
    available_values=2000,3000,4000
    value=$null
}

########################### Frame-type options ########################################


$_keyint= @{
    default=250
    type=[var_types]::int
    available_values=3,5,10,15,30,45,60,75,100,125,150,200,250,300
    value=$null
}
$_min_keyint = @{
    default = [int]$_keyint.default / 10
    type=[var_types]::int
    available_values = [int]$_keyint.default / 10
    value=$null
}
$_no_scenecut = @{default=$False; type=[var_types]::bool; available_values=$False, $True; value=$null}
$_scenecut = @{default=40; type=[var_types]::int; available_values=10,20,30,40,50,60; value=$null}
$_intra_refresh = @{default=$False; type=[var_types]::bool; available_values=$False, $True; value=$null}
$_bframes = @{default=3; type=[var_types]::int; available_values=1,2,3,4; value=$null}
$_b_adapt = @{default=1; type=[var_types]::int; available_values=0,1,2; value=$null}
$_b_bias = @{default=0; type=[var_types]::int; available_values=-100,-50,0,50,100; value=$null}
$_b_pyramid = @{
    default = "normal"
    type=[var_types]::string
    available_values = "none", "strict", "normal"
    value=$null
}
# $_open_gop = 1
# $_no_cabac = $null
# this option won't be used
# Disables CABAC (Context Adaptive Binary Arithmetic Coder) stream compression and falls back to the less efficient CAVLC (Context Adaptive Variable Length Coder) system. Significantly reduces both the compression efficiency (10-20% typically) and the decoding requirements.

$_ref = @{
    default = 3
    type=[var_types]::int
    available_values = 0,2,3,4,6,8,10,12,14,16
    value=$null
}
$_no_deblock = @{default=$False; type=[var_types]::bool; available_values=$False, $True; value=$null}
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


$_constrained_intra = @{default=$False; type=[var_types]::bool; available_values=$False, $True; value=$null}
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
    default = 1.4
    type=[var_types]::float
    available_values = 1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0
    value=$null
}

$_pbratio = @{
    default = 1.3
    type=[var_types]::float
    available_values = 1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0
    value=$null
}

$_chroma_qp_offset = @{
    default = 0
    type=[var_types]::int
    available_values = -6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6
    value=$null
}

$_aq_mode = @{
    default = 1
    type=[var_types]::int
    available_values = 0,1,2
    value=$null
}

# use this option if aq_mode != 0
$_aq_strength = @{
    default = 1.0
    type=[var_types]::float
    available_values = 0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5
    value=$null
}

#$_pass = @{
#    default = $null
#    type=[var_types]::int
#    available_values = 1,2,3
#    value=$null
#}

$_no_mbtree = @{default=$False; type=[var_types]::bool; available_values=$False, $True; value=$null}

$_qcomp = @{
    default = 0.6
    type=[var_types]::float
    available_values = 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0
    value=$null
}

$_cplxblur = @{
    default = 20.0
    type=[var_types]::float
    available_values = 5.0,10.0,15.0,20.0,25.0,30.0,35.0,40.0,45.0,50.0
    value=$null
}

$_qblur = @{
    default = 0.5
    type=[var_types]::float
    available_values = 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0
    value=$null
}

##########################
# Initialize variables
Set-Variable -Option AllScope -Name "var_names" -Value "_keyint", "_min_keyint", "_no_scenecut", "_scenecut", "_intra_refresh", "_bframes", "_b_adapt", "_b_bias", "_b_pyramid", "_open_gop", "_no_cabac", "_ref", "_no_deblock", "_deblock", "_slices", "_slice_max_size", "_slice_max_mbs", "_tff", "_bff", "_constrained_intra", "_pulldown", "_fake_interlaced", "_crf", "_ipratio", "_pbratio", "_chroma_qp_offset", "_aq_mode", "_aq_strength", "_pass", "_no_mbtree", "_qcomp", "_cplxblur", "_qblur"

$x_params = [string]::Empty
$num_of_combinations_full_mesh = 1
$num_of_combinations = 1

foreach ($var_name in $var_names) {
    $var_value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value
    if ($var_value.available_values.Length -gt 0){
        $num_of_combinations_full_mesh *= $var_value.available_values.Length
        $num_of_combinations += $var_value.available_values.Length
    }
}
##########################

if ($fullmode) {
    Write-Host "Number of combinations in full mode: $num_of_combinations_full_mesh" -foregroundcolor green
}
else{
    Write-Host "Number of combinations: $num_of_combinations" -foregroundcolor green
}

Start-Conversion $fullmode
