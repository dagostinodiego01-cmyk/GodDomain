param([string]$In, [string]$Out, [int]$Width = 900)
# Downscale an editor capture to a JPEG small enough to inspect (no ImageMagick here).
Add-Type -AssemblyName System.Drawing
$src = [System.Drawing.Image]::FromFile($In)
$h = [int]($src.Height * $Width / $src.Width)
$bmp = New-Object System.Drawing.Bitmap($Width, $h)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = 'HighQualityBicubic'
$g.DrawImage($src, 0, 0, $Width, $h)
$enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$prm = New-Object System.Drawing.Imaging.EncoderParameters(1)
$prm.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, 85L)
$bmp.Save($Out, $enc, $prm)
$g.Dispose(); $bmp.Dispose(); $src.Dispose()
Write-Output "$Out ${Width}x$h"
