# History Clock: helper for testing the watch face on the Galaxy Watch over Wi-Fi.
# Usage (or double-click the .bat files next to this script):
#   hc.ps1 install     download the latest watch face build from GitHub and install it on the watch
#   hc.ps1 shot        take a screenshot of the watch, saved to Downloads
#   hc.ps1 pair        pair the PC with the watch (needed once; asks for the numbers)
param([string]$Action = "install")

$ErrorActionPreference = "Continue"   # adb writes progress to stderr; do not treat it as fatal
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
$apkUrl = "https://github.com/ottsme/time_machine/releases/download/watchface-latest/history-clock-watchface.apk"
$downloads = Join-Path $env:USERPROFILE "Downloads"

function Test-Watch($d) {
    # a connection adb still lists may be stale (old network, old port): check it really answers
    $r = & $adb -s $d shell echo ok 2>$null
    return ($r -match "ok")
}

function Get-Watch {
    & $adb start-server | Out-Null
    # 1. already connected and answering?
    $listed = & $adb devices | Select-String "`tdevice$" | ForEach-Object { ($_ -split "`t")[0] }
    foreach ($d in $listed) {
        if (Test-Watch $d) { return $d }
        & $adb disconnect $d | Out-Null          # stale: drop it
    }
    # 2. find the watch on the network by itself (works once paired, while Wireless debugging is on)
    Write-Host "Looking for the watch on the network..."
    for ($i = 0; $i -lt 5; $i++) {
        $addrs = & $adb mdns services | Select-String "_adb-tls-connect" | ForEach-Object { (($_.ToString().Trim()) -split "\s+")[-1] } | Select-Object -Unique
        foreach ($addr in $addrs) {
            & $adb connect $addr | Out-Host
            Start-Sleep -Seconds 1
            if (Test-Watch $addr) { return $addr }
            & $adb disconnect $addr | Out-Null
        }
        Start-Sleep -Seconds 2
    }
    # 3. ask for the address shown on the watch
    Write-Host ""
    Write-Host "Could not find the watch by itself. On the watch: Settings > Developer options > Wireless debugging."
    Write-Host "(If the PC or the watch changed network, run 'Pair with the watch' first.)"
    $addr = Read-Host "Type the IP address and port shown there (for example 192.168.18.118:33311)"
    & $adb connect $addr | Out-Host
    Start-Sleep -Seconds 1
    if (Test-Watch $addr) { return $addr }
    throw "The watch is not connected. Is Wireless debugging on, and the watch on the same Wi-Fi as the PC?"
}

switch ($Action) {
    "pair" {
        Write-Host "On the watch: Wireless debugging > Pair new device. Keep that screen open."
        $addr = Read-Host "Type the IP address and port shown under the pairing code"
        $code = Read-Host "Type the 6-digit pairing code"
        & $adb start-server | Out-Null
        & $adb pair $addr $code | Out-Host
    }
    "install" {
        $dev = Get-Watch
        $apk = Join-Path $env:TEMP "history-clock-watchface.apk"
        Write-Host "Downloading the latest watch face build..."
        Invoke-WebRequest -Uri $apkUrl -OutFile $apk -UseBasicParsing
        Write-Host "Installing on $dev ..."
        $out = (& $adb -s $dev install -r $apk 2>&1 | Out-String)
        Write-Host $out
        if ($out -match "UPDATE_INCOMPATIBLE|signatures do not match") {
            # an older build signed with a different key: remove it once, then install fresh
            Write-Host "Replacing the older build (different signing key)..."
            & $adb -s $dev uninstall com.timetravelco.historyclock.watchface | Out-Host
            & $adb -s $dev install $apk | Out-Host
            Write-Host "Now select History Clock again on the watch (long-press the face)."
        }
    }
    "shot" {
        $dev = Get-Watch
        $name = "hc-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".png"
        & $adb -s $dev shell screencap -p /sdcard/hc.png | Out-Null
        & $adb -s $dev pull /sdcard/hc.png (Join-Path $downloads $name) | Out-Null
        & $adb -s $dev shell rm /sdcard/hc.png | Out-Null
        Write-Host "Screenshot saved: Downloads\$name"
    }
    default { Write-Host "Use: install, shot or pair" }
}
