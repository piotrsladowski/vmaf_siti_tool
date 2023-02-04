param ([switch]$fullmode, [string]$input_video_fname)

$output_directory = "output"

New-Item -Name $output_directory -ItemType Directory -Force

$input_video_fname_base_name = (Get-Item $input_video_fname).BaseName
$input_video_fname_extension = (Get-Item $input_video_fname).Extension

$output_video_fname = $null


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
        if($null -eq (Get-Variable $var_name -ErrorAction SilentlyContinue).Value){
            write-host "Variable $var_name is not defined"
        }
        elseif ($False -eq $var_value.value) {
            Write-Host "Option $var_name is not used" -ForegroundColor Yellow
        }
        else{
            $correct_var_name = $var_name.Substring(1).Replace("_","-")
            $x_params += $correct_var_name + "=" + (Get-Variable $var_name -ErrorAction SilentlyContinue).Value.value + ":"
        }
    }
    $x_params = $x_params.Substring(0,$x_params.Length-1)

    return $x_params
}

function Start-Conversion {
    <#
    .DESCRIPTION
    Start conversion.
    #>
    param ([switch]$fullmode)

    foreach ($var_name in $var_names) {
        $var_value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value

        # Set values of all others variables to default
        foreach ($other_var_name in $var_names){
            if ($other_var_name -eq $var_name){
                continue
            }
            if (!($null -eq (Get-Variable $var_name -ErrorAction SilentlyContinue).Value)){
                (Get-Variable $var_name -ErrorAction SilentlyContinue).Value.value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value.default
            }
        }

        # Iterate over all available values of current variable

        $i = 1

        foreach ($val in $var_value.available_values){
            $exclusion = $var_name
            $x_params = Merge-xparams-String $exclusion

            (Get-Variable $var_name -ErrorAction SilentlyContinue).Value.value = $val
            
            $_min_keyint.value = [int]([int]$val/10)
            Write-Host "min-keyint: $_min_keyint" -ForegroundColor Red
            $correct_var_name = $var_name.Substring(1).Replace("_","-")
            $x_params += ":" + $correct_var_name + "=" + $val

            $output_fname = $input_video_fname_base_name + "+" + $var_name + "+" + $i
            $output_fname = Join-Path -Path $output_directory -ChildPath $output_fname
            $output_video_fname = $output_fname + $input_video_fname_extension

            Write-Host "x264-params: $x_params" -ForegroundColor Red
            ffmpeg -hide_banner -i $input_video_fname -c:v libx264 -b:v 1000k -x264-params $x_params -c:a copy $output_video_fname

            $output_log_fname = $output_fname + ".log"
            Merge-Output-Params-Variable | Out-File -FilePath $output_log_fname -Encoding UTF8 -NoNewline

            $output_vmaf_xml_fname = $output_fname + ".xml"

            ffmpeg -hide_banner -i $output_video_fname -i $input_video_fname -lavfi libvmaf=log_path=$($output_vmaf_xml_fname):n_threads=2:feature=name=psnr -f null -

            $output_vmaf_csv_fname = $output_fname + ".csv"
            #Select-Xml -Path $output_vmaf_fname -XPath "/VMAF/pooledmetrics" | Select-Object -ExpandProperty Node | Select-Object -ExpandProperty InnerText | Add-Content -Path $output_vmaf_fname -Encoding UTF8 -NoNewline
            Select-Xml -Path $output_vmaf_xml_fname -XPath "/VMAF/pooled_metrics" | ForEach-Object { $_.Node.metric} | ConvertTo-Csv | Add-Content -Path $output_vmaf_csv_fname -Encoding UTF8

            $i++
        }
    }

    if ($fullmode){
        Write-Host "fsdfsdfsd" -ForegroundColor Magenta
    }
}



Write-Host "=============STARTING==============" -ForegroundColor Magenta
enum var_types {int = 1; float = 2; string = 3; bool = 4}

$_keyint= @{
    default=250
    type=[var_types]::int
    available_values=10,30,50,100,150,200,300,400,500,600,700,800,900
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
    available_values = 0,2,3#,4,6,8,10,12,14,16
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


##########################
# Initialize variables
Set-Variable -Option AllScope -Name "var_names" -Value "_keyint", "_min_keyint", "_no_scenecut", "_scenecut", "_intra_refresh", "_bframes", "_b_adapt", "_b_bias", "_b_pyramid", "_open_gop", "_no_cabac", "_ref", "_no_deblock", "_deblock", "_slices", "_slice_max_size", "_slice_max_mbs", "_tff", "_bff", "_constrained_intra", "_pulldown", "_fake_interlaced"

$x_params = [string]::Empty
$num_of_combinations_full_mesh = 1
$num_of_combinations = 1

foreach ($var_name in $var_names) {
    if (!($null -eq (Get-Variable $var_name -ErrorAction SilentlyContinue).Value)){
        (Get-Variable $var_name -ErrorAction SilentlyContinue).Value.value = (Get-Variable $var_name -ErrorAction SilentlyContinue).Value.default
    }
}

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

$command = "-hide_banner -i ./B232.mp4 -c:v libx264 -b:v 1000k -x264-params $x_params -c:a copy -o output.mp4"

#$x_params | ConvertTo-Json

#ffmpeg -hide_banner -i "B232.mp4" -c:v libx264 -b:v 1000k -x264-params $x_params -c:a copy output.mp4

Write-Host $command
#Write-Host $x_params

