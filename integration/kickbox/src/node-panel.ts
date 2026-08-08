// Node Status panel (Phase 4A). Renders what the gateway says about the
// mesh: which nodes exist, their trust band, their health, and where the
// last job actually ran. It never shows a dispatch address, key fingerprint,
// or any credential — the gateway does not even send those.

import { nodeStandingLabel, routeExplanation } from '@camelot/contracts';
import type { NodeRouteDecision, NodeView } from '@camelot/contracts';

export interface NodePanelState {
  nodes: NodeView[];
  lastRoute: NodeRouteDecision | null;
  reachable: boolean;
}

export function initialNodePanelState(): NodePanelState {
  return { nodes: [], lastRoute: null, reachable: false };
}

/** Summary line for the panel header / degraded indicator. */
export function meshSummary(state: NodePanelState): string {
  if (!state.reachable) return 'mesh: gateway unreachable — local operation only';
  const total = state.nodes.length;
  if (total === 0) return 'mesh: no nodes registered';
  const serviceable = state.nodes.filter(
    (n) => (n.trust === 'trusted' || n.trust === 'limited') && n.health === 'healthy',
  ).length;
  const remote = state.nodes.filter((n) => !n.local).length;
  const degraded = total - serviceable;
  const parts = [`${serviceable}/${total} ready`, `${remote} remote`];
  if (degraded > 0) parts.push(`${degraded} unavailable`);
  return `mesh: ${parts.join(' · ')}`;
}

export function bandClass(node: NodeView): string {
  return `band-${node.trust}`;
}

/** Render into a container. Pure DOM, no framework. */
export function renderNodePanel(
  listEl: HTMLElement,
  routeEl: HTMLElement,
  state: NodePanelState,
): void {
  listEl.innerHTML = '';

  if (state.nodes.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'node-caps';
    empty.textContent = state.reachable
      ? 'No nodes registered. Start the agent with ENABLE_TAILSCALE_MESH=true to enrol one.'
      : 'Gateway unreachable.';
    listEl.appendChild(empty);
  }

  for (const node of state.nodes) {
    const row = document.createElement('div');
    row.className = 'node-row';
    row.dataset['node'] = node.nodeId;

    const name = document.createElement('span');
    name.className = 'node-name';
    name.textContent = node.displayName || node.nodeId;
    const scope = document.createElement('span');
    scope.className = 'scope';
    scope.textContent = ` ${node.local ? 'local' : 'remote'} · ${node.addressHash}`;
    name.appendChild(scope);

    const caps = document.createElement('span');
    caps.className = 'node-caps';
    caps.textContent = node.capabilities.map((c) => c.name.replace(/^compute:/, '')).join(', ');

    const standing = document.createElement('span');
    standing.className = `node-standing ${bandClass(node)}`;
    standing.textContent = nodeStandingLabel(node);

    row.append(name, caps, standing);
    listEl.appendChild(row);
  }

  routeEl.textContent = state.lastRoute
    ? `last route → ${routeExplanation(state.lastRoute)}`
    : meshSummary(state);
}
