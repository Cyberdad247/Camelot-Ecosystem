# SPDX-License-Identifier: MIT

#Requires -Version 5.1

<#
.SYNOPSIS
    Checks for changes in Gemini.md and creates a versioned backup if changes are detected.
.DESCRIPTION
    This script provides a simple local "CI/CD" or versioning system for the Gemini.md context file.
    It calculates the SHA256 hash of the current Gemini.md file and compares it to a stored hash
    of the last versioned copy. If the hashes differ, it means the file has been updated.
    When an update is detected, it copies the file to the 'History' directory with a timestamp.
.EXAMPLE
    .\check_gemini_updates.ps1
    (No output if no changes are detected)
.EXAMPLE
    .\check_gemini_updates.ps1
    New version of Gemini.md detected. Backed up to History\Gemini-20251130-103500.md
#>
param()

# --- Configuration ---
$userProfile = $env:USERPROFILE
$sourceFile = Join-Path -Path $userProfile -ChildPath "Gemini.md"
$historyDir = Join-Path -Path $userProfile -ChildPath "History"
$hashFile = Join-Path -Path $historyDir -ChildPath ".last_version_hash"

# --- Logic ---

# Ensure the source file exists
if (-not (Test-Path -Path $sourceFile -PathType Leaf)) {
    Write-Warning "Source file not found: $sourceFile"
    return
}

# Get the current hash of the source file
try {
    $currentHash = (Get-FileHash -Path $sourceFile -Algorithm SHA256).Hash
}
catch {
    Write-Error "Failed to calculate hash for $sourceFile. Error: $($_.Exception.Message)"
    return
}


# Get the last known hash, if the hash file exists
$lastHash = if (Test-Path -Path $hashFile -PathType Leaf) {
    try {
        Get-Content -Path $hashFile
    }
    catch {
        Write-Warning "Could not read hash file at $hashFile. Forcing a new version."
        $null
    }

} else {
    $null
}

# Compare hashes
if ($currentHash -ne $lastHash) {
    # Hashes are different or no previous hash exists, so create a backup
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupFileName = "Gemini-{0}.md" -f $timestamp
    $destinationFile = Join-Path -Path $historyDir -ChildPath $backupFileName

    try {
        Copy-Item -Path $sourceFile -Destination $destinationFile -Force
        Write-Host ("New version of Gemini.md detected. Backed up to {0}" -f $destinationFile)

        # Update the hash file with the new hash
        $currentHash | Out-File -FilePath $hashFile -Encoding ascii
    }
    catch {
        Write-Error "Failed to copy file or update hash. Error: $($_.Exception.Message)"
    }
}
else {
    # Hashes are the same, do nothing
    # Write-Verbose "No changes detected in Gemini.md."
}
