// SPDX-License-Identifier: MIT

'use client';

import { OperatorConsole } from '../../components/operator_console';

export default function OperatorConsolePage() {
  // Fixture task id for slice #2; the harness drives real task ids later.
  return <OperatorConsole taskId="task_01J" />;
}
