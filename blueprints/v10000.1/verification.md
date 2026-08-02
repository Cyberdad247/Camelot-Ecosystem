# Forge Law Verification Gates v10000.1

1. A source bundle without a matching successful ledger event cannot
   crystallize.
2. Editing any source file after verification invalidates the evidence match.
3. Cartridge digest tampering prevents inspection and execution.
4. Traversal, symlink escape, protected ledgers, secret-like values, unknown
   operation types, dependency cycles, and shell-style commands are rejected.
5. `//EXECUTE_PROMPT` does not enter the harness queue without a v2 approval
   grant bound to the cartridge digest and target root.
6. A failed check restores all earlier file mutations and ends in
   `rolled_back` state.
7. The PWA APIs require operator authentication and never expose write routes.
8. Python tests, PWA architecture tests, strict TypeScript, and the production
   Next.js build pass.

