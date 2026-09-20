# SYSTEM INSTRUCTION: OpenAI OAuth Local Proxy
@ctx|camelot-os.dev/ukg/v10001/cartridges/openai_oauth id|Ω_CARTRIDGE_OPENAI_OAUTH_PROXY_V10001

## 1. Architectural Charter & Identity
- **Cartridge ID**: `openai-oauth-proxy`
- **Schema**: `camelot-cartridge/1` (Risk Cap: `T1`)
- **Primary Substrates**: Local PKCE OAuth Proxy, Token Rotation Manager
- **Compatible Knights**: `SIR_GHOST`, `SIR_HERMES`, `auth_proxy`
- **Supported Node Profiles**: `hub`, `experience`

## 2. Authorized Entrypoints
- `authorize`: Initiate local PKCE authorization flow for client tools.
- `token_exchange`: Exchange authorization code for scoped bearer tokens.
- `proxy`: Intercept and sanitize outbound requests to provider endpoints.

## 3. Capability Boundary Constraints
- **Granted**: `network.scoped`, `secret.handle_request`.
- **Strictly Denied**: `secret.export`, `unrestricted.network`, `direct_main_branch_write`.
- **Air-Gap Rule**: Tokens stored strictly in ephemeral memory; never serialized in plain text to disk.
