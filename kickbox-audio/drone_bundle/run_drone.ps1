# Camelot-OS KBA Drone — lakesha launcher (run from the extracted bundle folder)
# Governed drone: signed cartridges -> trust -> RBAC -> real KBA executor -> audit,
# with Sir Heimdall on watch. Reachable over the tailnet at 100.100.155.55:9000.
$env:WEBHOOK_SECRET            = "0b962d3eabb1503941036b793e7ecce3a0e5b425e9893d83"
$env:CAMELOT_CARTRIDGE_HMAC_KEY = "8f9ba99fd8e48123784850efe1f4dba884dab896020c9be1"

python -m control_plane.drone_node --node-id kba-drone-lakesha --host 100.100.155.55 --port 9000
