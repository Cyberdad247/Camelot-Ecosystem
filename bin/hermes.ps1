# Camelot-OS — Hermes Agent CLI Proxy (PowerShell)
# Connects directly to the NousResearch Hermes Agent running on VPS Hub KVM563
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$HermesArgs
)

if ($HermesArgs.Count -eq 0) {
    ssh -t root@162.35.107.134 "docker exec -it hermes hermes"
} else {
    $joined = $HermesArgs -join " "
    ssh root@162.35.107.134 "docker exec -i hermes hermes $joined"
}
