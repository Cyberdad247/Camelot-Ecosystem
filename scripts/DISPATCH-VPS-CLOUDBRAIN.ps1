# CAMELOT-OS: Edge-to-CloudBrain Asymmetric Compute Dispatcher
# Run from Cybertronia Edge Node to offload heavy tasks to VPS CloudBrain
param(
    [string]$TaskType = "RUST_COMPILATION",
    [string]$Payload = "cargo build --release",
    [string]$VpsHost = "100.110.180.18:8091"
)

Write-Host "⚔️ [CYBERTRONIA EDGE] Initiating Asymmetric Compute Dispatch..." -ForegroundColor Cyan
Write-Host "🎯 Target VPS CloudBrain Node: $VpsHost" -ForegroundColor DarkCyan

$taskId = "task-" + [System.Guid]::NewGuid().ToString().Substring(0, 8)
$body = @{
    task_id   = $taskId
    task_type = $TaskType
    payload   = $Payload
    requester = "cybertronia"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://$VpsHost/cloudbrain/execute" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 15
    Write-Host "✅ [Z3 RECEIPT RECEIVED]: Task $taskId successfully offloaded to CloudBrain!" -ForegroundColor Green
    $response | Format-List
} catch {
    Write-Warning "⚠️ Unable to reach VPS CloudBrain on $VpsHost. Ensure FORGE-VPS-CLOUDBRAIN.sh is running on the VPS."
    Write-Host "Error details: $_" -ForegroundColor Red
}
