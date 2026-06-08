# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import subprocess


def notify(title, message):
    """
    HERMES NOTIFICATION SYSTEM: Windows Native Toast via PowerShell
    """
    ps_command = f"""
    [void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms');
    $objNotification = New-Object System.Windows.Forms.NotifyIcon;
    $objNotification.Icon = [System.Drawing.SystemIcons]::Information;
    $objNotification.BalloonTipIcon = 'Info';
    $objNotification.BalloonTipTitle = '{title}';
    $objNotification.BalloonTipText = '{message}';
    $objNotification.Visible = $True;
    $objNotification.ShowBalloonTip(10000);
    """
    try:
        subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return True
    except Exception as e:
        print(f"❌ [HERMES] Delivery Failure: {e}")
        return False


# Example:
# notify("⚔️ Camelot OS", "Audit Complete. No threats detected.")