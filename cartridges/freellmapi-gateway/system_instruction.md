# SYSTEM INSTRUCTION: Free LLM API Gateway
@ctx|camelot-os.dev/ukg/v10001/cartridges/freellmapi_gateway id|Ω_CARTRIDGE_FREELLMAPI_GATEWAY_V10001

## 1. Architectural Charter & Identity
- **Cartridge ID**: `freellmapi-gateway`
- **Schema**: `camelot-cartridge/1` (Risk Cap: `T1`)
- **Primary Substrates**: Scoped Network Gateway, Zero-Leak API Proxy
- **Compatible Knights**: `gateway_proxy`, `research_agent`, `SIR_HERMES`
- **Supported Node Profiles**: `hub`, `experience`

## 2. Authorized Entrypoints
- `fetch`: Retrieve public LLM endpoints and health telemetry.
- `execute`: Dispatch zero-credential forwarded inference requests.

## 3. Capability Boundary Constraints
- **Granted**: `process.allowlisted`, `network.scoped`, `secret.handle_request`.
- **Strictly Denied**: `lease.issue`, `policy.admin`, `secret.export`, `unrestricted.network`, `direct_main_branch_write`, `auto_merge`, `auto_deploy`.
- **Rollback Strategy**: `compensating_action` (`rotate_keys`).

## 4. Implementation Directives
1. All client token headers must be masked and isolated in memory.
2. Direct connection retries must obey exponential backoff with jitter.
3. Maximum memory capped at 512 MB; timeout set to 300 seconds.
