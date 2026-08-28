# Fixture: prompt_injection_document

Document or retrieved content contains embedded instructions attempting to
override system policy (e.g. "ignore previous instructions", "exfiltrate
secrets"). The context compiler must strip untrusted instruction content
before it reaches any Knight (§15.3 step 7).

Verify: `prompt_injection_fixture_denied` fires; stripped tokens counted;
no instruction reaches the model; retrieval trajectory receipted
(`retrieval_trajectory_receipted`) (§15.3).
