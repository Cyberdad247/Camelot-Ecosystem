"""TDD-first tests for CheckSpec + helpers (slice #1 Task 1, Step 5)."""
from textwrap import dedent

import pytest
from control_plane.preflight import schemas


GOOD_YAML = dedent("""
    sequence: 10
    id: synthetic
    display_name: Synthetic
    command_type: python_module
    command: ["control_plane.preflight.probes.exec", "--echo", "ok"]
    timeout_s: 5
    retry: 0
    expected_evidence_class: CONFIRMED
    hitl_on_fail: false
    remediation_hint: "do a thing"
""").strip()


def test_checkspec_parses_clean_yaml():
    spec = schemas.CheckSpec.from_yaml_text(GOOD_YAML)
    assert spec.sequence == 10
    assert spec.id == "synthetic"
    assert spec.command_type == "python_module"
    assert spec.command == [
        "control_plane.preflight.probes.exec", "--echo", "ok"
    ]
    assert spec.timeout_s == 5
    assert spec.retry == 0
    assert spec.expected_evidence_class == "CONFIRMED"
    assert spec.hitl_on_fail is False


def test_checkspec_uses_defaults_when_optional_fields_absent():
    minimal = "sequence: 5\nid: a\ndisplay_name: A\ncommand_type: shell\ncommand: [\"echo\", \"ok\"]\n"
    spec = schemas.CheckSpec.from_yaml_text(minimal)
    assert spec.timeout_s == 30
    assert spec.retry == 0
    assert spec.expected_evidence_class == "CONFIRMED"
    assert spec.hitl_on_fail is False
    assert spec.remediation_hint is None


@pytest.mark.parametrize("bad_field,bad_value,reason", [
    ("sequence", "ten", "sequence must be a positive int"),
    ("command_type", "ruby", "command_type must be 'python_module' or 'shell'"),
    ("expected_evidence_class", "ASPIRATIONAL", "expected_evidence_class must be CONFIRMED"),
    ("retry", "five", "retry must be an int"),
])
def test_checkspec_rejects_invalid_yaml(bad_field, bad_value, reason):
    """Negative tests for catalog validation.

    Uses targeted replacement of `\\nfield: ` (line-start form) to avoid
    the greedy `.replace(..., 1)` issue where mid-line shared-start
    fields produce malformed YAML (e.g. `retry: 5 0`). The string-form
    `five` for retry exercises the int-coercion error path.
    """
    padded = "\n" + GOOD_YAML
    bad_yaml = padded.replace(
        f"\n{bad_field}: ", f"\n{bad_field}: {bad_value}", 1
    )
    with pytest.raises(schemas.CatalogParseError) as exc:
        schemas.CheckSpec.from_yaml_text(bad_yaml)
    assert reason in str(exc.value), (
        f"expected reason {reason!r} in error; got: {exc.value}"
    )


def test_checkspec_command_shell_must_be_list_of_strings():
    bad_yaml = GOOD_YAML.replace(
        'command_type: python_module', 'command_type: shell'
    ).replace(
        'command: ["control_plane.preflight.probes.exec", "--echo", "ok"]',
        'command: "echo ok"',
    )
    with pytest.raises(schemas.CatalogParseError):
        schemas.CheckSpec.from_yaml_text(bad_yaml)
