// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
// CAMELOT_OS GenKit Logic Layer
// Refined Heuristic Dispatcher

const input = process.argv[2] || '';
const lowerInput = input.toLowerCase();

let knight = 'Sir Bedivere'; // The Wise (Default)
let plan = 'Analyzing request...';

// Heuristic Routing
if (
  lowerInput.includes('plan') ||
  lowerInput.includes('design') ||
  lowerInput.includes('architect') ||
  lowerInput.includes('tutorial')
) {
  knight = 'Sir Lancelot'; // The Architect
  plan = `Drafting documentation and blueprints for: '${input.substring(0, 50)}...'`;
} else if (
  lowerInput.includes('code') ||
  lowerInput.includes('function') ||
  lowerInput.includes('dev') ||
  lowerInput.includes('implement')
) {
  knight = 'Sir Galahad'; // The Pure (Coder)
  plan = `Forging code artifacts for request. Initiating syntax generation...`;
} else if (
  lowerInput.includes('test') ||
  lowerInput.includes('verify') ||
  lowerInput.includes('audit') ||
  lowerInput.includes('check')
) {
  knight = 'Sir Percival'; // The Seeker (QA)
  plan = `Running verification protocols. Scanning for anomalies...`;
} else if (
  lowerInput.includes('delete') ||
  lowerInput.includes('remove') ||
  lowerInput.includes('destroy') ||
  lowerInput.includes('kill')
) {
  knight = 'Sir Mordred'; // The Executioner
  plan = `Preparing for destructive kinetic action. Safety interlocks engaged.`;
} else {
  plan = `Processing intent: '${input.substring(0, 50)}...' via Standard Protocol.`;
}

// Output formatted for Merlin_Omega
console.log('RESULT_START');
console.log(
  JSON.stringify({
    knight_assigned: knight,
    action_plan: plan,
  }),
);
console.log('RESULT_END');
