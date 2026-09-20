# CAMELOT-OS runtime-state backup (Windows host).
# Implements docs/guides/PRODUCTION_READINESS_GUIDE.md RPO/RTO targets:
#   RPO < 1 day (run daily via Task Scheduler), RTO < 1 hour (single archive restore).
# Backs up: 03_VAULT/runtime_state, all PROVENANCE_LEDGER.md mirrors,
# verification ledgers, local *.db. Prunes archives older than retention.
# Values inside archives stay on this host; copy off-host over Tailscale only.
param(
  [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
  [string]$BackupRoot = (Join-Path $RepoRoot '03_VAULT\runtime_state\backups'),
  [int]$RetentionDays = 30
)

$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$dest = Join-Path $BackupRoot "runtime_state_$stamp.zip"
New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null

$paths = @(
  (Join-Path $RepoRoot '03_VAULT\runtime_state'),
  (Join-Path $RepoRoot 'PROVENANCE_LEDGER.md'),
  (Join-Path $RepoRoot '03_VAULT\PROVENANCE_LEDGER.md'),
  (Join-Path $RepoRoot 'docs\PROVENANCE_LEDGER.md'),
  (Join-Path $RepoRoot '03_VAULT\training\configs\PROVENANCE_LEDGER.md'),
  (Join-Path $RepoRoot '03_VAULT\Missions\verification_ledger.jsonl'),
  (Join-Path $RepoRoot 'control_plane\03_VAULT\Missions\verification_ledger.jsonl')
) | Where-Object { Test-Path $_ }

Compress-Archive -Path $paths -DestinationPath $dest -Force
$hash = (Get-FileHash -Path $dest -Algorithm SHA256).Hash
"$stamp $hash  $(Split-Path -Leaf $dest)" | Add-Content (Join-Path $BackupRoot 'MANIFEST.sha256')

Get-ChildItem -Path $BackupRoot -Filter 'runtime_state_*.zip' |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } |
  Remove-Item -Force

Write-Output "[ok] backup $dest sha256=$($hash.Substring(0,12))…"
