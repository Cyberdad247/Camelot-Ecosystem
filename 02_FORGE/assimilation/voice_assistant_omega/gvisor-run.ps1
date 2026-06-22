$ErrorActionPreference = "Stop"

$image = "camelot/voice-assistant-omega:latest"
docker build -t $image .
docker run --rm `
  --runtime=runsc `
  --read-only `
  --cap-drop=ALL `
  --security-opt=no-new-privileges `
  --pids-limit=256 `
  --memory=1024m `
  --tmpfs /tmp:rw,noexec,nosuid,size=128m `
  -e OMEGA_WS_TOKEN="${env:OMEGA_WS_TOKEN}" `
  -e OMEGA_MODEL_PROVIDER="${env:OMEGA_MODEL_PROVIDER}" `
  -e OMEGA_STT_PROVIDER="${env:OMEGA_STT_PROVIDER}" `
  -e OMEGA_TTS_PROVIDER="${env:OMEGA_TTS_PROVIDER}" `
  -p 8088:8088 `
  $image

