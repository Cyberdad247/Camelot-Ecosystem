"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
/**
 * Camelot-OS VS Code Extension
 * ==============================
 *
 * Thin shell-out to bin/camelot_portable.py. NO logic reproduction, NO
 * widening of capability.
 *
 * Iron-Gate posture:
 *  - All subprocess calls use child_process.spawn with argv-list (shell=false).
 *  - NO_RICH=1 forced for clean stdout capture in prompt UI.
 *  - PYTHONUTF8=1 forced for Windows console parity.
 *  - The --target flag on camelot.cartridge emit is forwarded; the MCP
 *    server (bin/camelot_ide_mcp.py) is the path-traversal jail, so MCP
 *    clients are safe. Extension users running this command directly accept
 *    the same risk as running `bin/camelot_portable.py cartridge --emit`.
 */
const vscode = __importStar(require("vscode"));
const node_child_process_1 = require("node:child_process");
const node_fs_1 = require("node:fs");
const path = __importStar(require("node:path"));
const REPO = path.resolve(__dirname, '..', '..', '..');
const PORTABLE = path.join(REPO, 'bin', 'camelot_portable.py');
const MCP_SERVER = path.join(REPO, 'bin', 'camelot_ide_mcp.py');
function pythonPath() {
    return vscode.workspace.getConfiguration('camelot').get('pythonPath') ?? 'python';
}
function runPortable(args) {
    return new Promise((resolve, reject) => {
        const env = { ...process.env, NO_RICH: '1', PYTHONUTF8: '1' };
        const proc = (0, node_child_process_1.spawn)(pythonPath(), [PORTABLE, ...args], {
            cwd: REPO,
            env,
            stdio: ['ignore', 'pipe', 'pipe'],
            shell: false,
            windowsHide: true,
        });
        let stdout = '';
        let stderr = '';
        proc.stdout.setEncoding('utf8');
        proc.stderr.setEncoding('utf8');
        proc.stdout.on('data', (d) => { stdout += d; });
        proc.stderr.on('data', (d) => { stderr += d; });
        proc.on('close', (code) => resolve({ stdout, stderr, code: code ?? 0 }));
        proc.on('error', reject);
    });
}
/**
 * Thin wrapper over ``runPortable`` for the ``cartridge --emit`` flow. The
 * portable CLI's preflight guard (see ``bin/camelot_portable.py ::
 * _preflight_emit_overwrite``) returns rc=1 + ``refusing without --force`` in
 * stdout when the existing trio is non-trivial; the camelot.cartridge command
 * catches that and offers a "Overwrite (--force)" QuickPick to re-invoke with
 * the flag set.
 */
function runCartridgeEmit(stage, target, force) {
    const argv = ['cartridge', '--emit', stage, '--target', target];
    if (force) {
        argv.push('--force');
    }
    return runPortable(argv);
}
async function showOutput(name, content) {
    const out = vscode.window.createOutputChannel(name);
    out.clear();
    out.append(content);
    out.show();
}
// ── McpServerDefinitionProvider ─────────────────────────────────────────────────
// Self-registers `bin/camelot_ide_mcp.py` as the `camelot-ide` MCP server so
// VS Code's MCP client (1.96+), Cursor, and Claude Dev discover it without
// requiring the user to hand-edit `.vscode/mcp.json`.
class CamelotMcpProvider {
    _onDidChange = new vscode.EventEmitter();
    onDidChangeMcpServerDefinitions = this._onDidChange.event;
    /**
     * Public refresh hook — fires ``onDidChangeMcpServerDefinitions`` so the MCP
     * client re-queries ``provideMcpServerDefinitions`` (e.g. after a
     * ``camelot.pythonPath`` setting change). Promotes configuration edits to
     * live MCP client state without an extension reload.
     */
    refresh() {
        this._onDidChange.fire(undefined);
    }
    provideMcpServerDefinitions(_token) {
        // Workspace Trust gate — a malicious repo could put a hostile path in
        // `.vscode/settings.json` for `camelot.pythonPath`, so we refuse to expose
        // the MCP server until the user has explicitly trusted the workspace.
        if (!vscode.workspace.isTrusted) {
            return [];
        }
        // Gracefully no-op if the MCP server script is missing (e.g., extension
        // installed without the full Camelot-OS repo on disk).
        if (!(0, node_fs_1.existsSync)(MCP_SERVER)) {
            return [];
        }
        // Read python interpreter fresh so changing settings propagates without an
        // extension reload (paired with onDidChangeConfiguration below). Reuses the
        // module-top ``pythonPath()`` helper to avoid duplicated config-read code.
        const pythonExec = pythonPath();
        // Constructor positional args per @types/vscode 1.125.0 (line 20469 verbatim):
        //   constructor(label: string, command: string, args?: string[],
        //               env?: Record<string, string | number | null>, version?: string)
        // ``cwd`` is a *property* of type ``Uri``, NOT a constructor arg — set it
        // on the instance after construction.
        const def = new vscode.McpStdioServerDefinition('Camelot-OS IDE/CLI', pythonExec, [MCP_SERVER], { NO_RICH: '1', PYTHONUTF8: '1' });
        def.cwd = vscode.Uri.file(REPO);
        return [def];
    }
}
function activate(ctx) {
    // ── Register Camelot commands. Each delegates argv-list spawn to camelot_portable.py. ──
    ctx.subscriptions.push(vscode.commands.registerCommand('camelot.omniroute', async () => {
        const intent = await vscode.window.showInputBox({
            prompt: 'Camelot: enter intent text (use Phase-H style — keyword or phrase)',
            ignoreFocusOut: true,
        });
        if (!intent) {
            return;
        }
        const r = await runPortable(['omniroute', '--select', intent]);
        if (r.code === 0) {
            await showOutput('Camelot OmniRoute', r.stdout);
            vscode.window.showInformationMessage('LaneSignal emitted — see Camelot OmniRoute output.');
        }
        else {
            vscode.window.showErrorMessage(`Camelot omniroute exit ${r.code}: ${r.stderr.slice(0, 240)}`);
        }
    }));
    ctx.subscriptions.push(vscode.commands.registerCommand('camelot.knight', async () => {
        const kid = await vscode.window.showInputBox({
            prompt: 'Knight id (sir_codex, sir_boris, sir_helio, sir_alex, sir_mnemo, sir_forge, merlin_omega, ...)',
            ignoreFocusOut: true,
        });
        if (!kid) {
            return;
        }
        const prompt = await vscode.window.showInputBox({
            prompt: 'Prompt for the knight',
            ignoreFocusOut: true,
        });
        if (!prompt) {
            return;
        }
        const r = await runPortable(['knight', '--invoke', kid, '--prompt', prompt]);
        if (r.code === 0) {
            await showOutput(`Camelot Knight [${kid}]`, r.stdout);
        }
        else {
            vscode.window.showErrorMessage(`Camelot knight exit ${r.code}: ${r.stderr.slice(0, 240)}`);
        }
    }));
    ctx.subscriptions.push(vscode.commands.registerCommand('camelot.mcp', async () => {
        const r = await runPortable(['mcp']);
        if (r.code === 0) {
            await showOutput('Camelot MCP', r.stdout);
        }
        else {
            vscode.window.showErrorMessage(`Camelot mcp exit ${r.code}: ${r.stderr.slice(0, 240)}`);
        }
    }));
    ctx.subscriptions.push(vscode.commands.registerCommand('camelot.cartridge', async () => {
        const stage = await vscode.window.showInputBox({
            prompt: 'V4000 stage name (slug, lowercase snake_case)',
            ignoreFocusOut: true,
        });
        if (!stage) {
            return;
        }
        const defaultTarget = `projects/${stage}`;
        const target = await vscode.window.showInputBox({
            prompt: 'Target directory (default: projects/<stage>)',
            value: defaultTarget,
            ignoreFocusOut: true,
        });
        if (!target) {
            return;
        }
        // First attempt: portable CLI preflight guard refuses (rc=1) when the
        // existing trio is non-trivial; stdout includes the
        // "refusing without --force" sentinel. Surface a QuickPick so the
        // operator can confirm the rewrite intent without re-typing the
        // command + --force flag.
        const announceSuccess = async (rr) => {
            await showOutput(`Camelot Cartridge [${stage}]`, rr.stdout);
            await vscode.commands.executeCommand('workbench.files.action.refreshFilesExplorer');
            vscode.window.showInformationMessage(`Camelot: emitted ${stage} trio to ${target}`);
        };
        const r = await runCartridgeEmit(stage, target, false);
        if (r.code === 0) {
            await announceSuccess(r);
            return;
        }
        if (r.stdout.includes('refusing without --force')) {
            const choice = await vscode.window.showWarningMessage('Camelot: existing trio is non-trivial. Overwrite with --force?', { modal: false }, 'Overwrite (--force)', 'Cancel');
            if (choice === 'Overwrite (--force)') {
                const r2 = await runCartridgeEmit(stage, target, true);
                if (r2.code === 0) {
                    await announceSuccess(r2);
                    return;
                }
                vscode.window.showErrorMessage(`Camelot cartridge exit ${r2.code} (after --force): ${r2.stderr.slice(0, 240)}`);
                return;
            }
            // Operator picked Cancel — leave the existing trio untouched.
            await showOutput(`Camelot Cartridge [${stage}] — refused, no changes made`, r.stdout);
            return;
        }
        vscode.window.showErrorMessage(`Camelot cartridge exit ${r.code}: ${r.stderr.slice(0, 240)}`);
    }));
    // ── Status bar item ─────────────────────────────────────────────────────────
    const cfg = vscode.workspace.getConfiguration('camelot');
    const defaultKnight = cfg.get('defaultKnight') ?? 'sir_helio';
    const sb = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    sb.text = `$(zap) Camelot: ${defaultKnight}`;
    sb.tooltip = `Camelot-OS IDE bound to bin/camelot_portable.py.\nClick to invoke OmniRoute lane.`;
    sb.command = 'camelot.omniroute';
    sb.show();
    ctx.subscriptions.push(sb);
    // ── MCP server self-registration (replaces `.vscode/mcp.json` hand-edit) ───
    // The provider exposes bin/camelot_ide_mcp.py to VS Code's MCP client. The
    // Workspace Trust gate inside ``provideMcpServerDefinitions`` prevents a
    // malicious repo from overriding ``camelot.pythonPath`` to a hostile binary.
    // NOTE: in @types/vscode 1.125.0 (and 1.96+ runtime) the registration
    // function lives under the **language model** namespace as
    // ``vscode.lm.registerMcpServerDefinitionProvider`` — verified verbatim from
    // node_modules/@types/vscode/index.d.ts line 20843.
    const mcpProvider = new CamelotMcpProvider();
    ctx.subscriptions.push(vscode.lm.registerMcpServerDefinitionProvider('camelot-ide', mcpProvider));
    // Fire ``onDidChangeMcpServerDefinitions`` whenever the user tweaks
    // ``camelot.pythonPath`` so the MCP client picks up the new interpreter
    // without an extension reload. Also refreshes the status bar text on
    // ``camelot.defaultKnight`` changes.
    ctx.subscriptions.push(vscode.workspace.onDidChangeConfiguration((e) => {
        const cfg = vscode.workspace.getConfiguration('camelot');
        if (e.affectsConfiguration('camelot.pythonPath')) {
            mcpProvider.refresh();
        }
        if (e.affectsConfiguration('camelot.defaultKnight')) {
            sb.text = `$(zap) Camelot: ${cfg.get('defaultKnight') ?? 'sir_helio'}`;
        }
    }));
}
function deactivate() {
    // No persistent state to teardown — every cubcommand opens a fresh subprocess.
}
//# sourceMappingURL=extension.js.map