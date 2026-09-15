# Fixture: malformed_symbolect_tree

Symbolect tree submitted with an unknown glyph, unmet required child,
prohibited capability, missing actor/runtime, or a self-authorizing node.
The compiler must reject the tree at registration and deny the effect.

Verify: `symbolect_validation_enforced` fires; tree rejected; registering
Knight receives a `symbolect.rejected` receipt; effect denied (§17.3).
