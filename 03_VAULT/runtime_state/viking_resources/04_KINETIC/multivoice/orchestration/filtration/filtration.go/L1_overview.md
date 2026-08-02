# [L1_OVERVIEW: filtration.go]
# [PROTOCOL: OPENVIKING_ORIENT]

## 1. Description
ModelFingerprint represents Stage 1 output DeploymentPlan represents Stage 4 output

## 2. Dependencies / Imports
- `import (`
- `"errors"`
- `"fmt"`

## 3. Structural Signatures
- `type ModelFingerprint struct {`
- `type DeploymentPlan struct {`
- `func ExecuteFiltrationDAG(modelURI string, availableVRAM int) (DeploymentPlan, error) {`
- `func fingerprintModel(uri string) ModelFingerprint {`
- `func routePolicy(fp ModelFingerprint) string {`
- `func validateHardware(fp ModelFingerprint, vram int) error {`
