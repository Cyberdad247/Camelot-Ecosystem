# SPDX-License-Identifier: MIT

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


def test_checkspec_accepts_string_form_sequence():
    """Sequence can be a YAML 1.1 octal-style leading-zero string
    ('010') as well as a plain int. The schema coerces to int.

    This is critical because YAML 1.1 parses bare `010` as octal 8,
    quoting the catalog value preserves the spec's stride-10
    readability. The schema MUST accept both forms."""
    yaml_with_str_sequence = (
        'sequence: "010"\nid: a\ndisplay_name: A\n'
        'command_type: shell\ncommand: ["echo", "ok"]\n'
    )
    spec = schemas.CheckSpec.from_yaml_text(yaml_with_str_sequence)
    assert spec.sequence == 10
    assert isinstance(spec.sequence, int)


def test_checkspec_rejects_negative_or_zero_string_sequence():
    yaml_with_zero = (
        'sequence: "0"\nid: a\ndisplay_name: A\n'
        'command_type: shell\ncommand: ["echo", "ok"]\n'
    )
    with pytest.raises(schemas.CatalogParseError) as exc:
        schemas.CheckSpec.from_yaml_text(yaml_with_zero)
    assert "positive" in str(exc.value).lower()


def test_checkspec_uses_defaults_when_optional_fields_absent():
    minimal = "sequence: 5\nid: a\ndisplay_name: A\ncommand_type: shell\ncommand: [\"echo\", \"ok\"]\n"
    spec = schemas.CheckSpec.from_yaml_text(minimal)
    assert spec.timeout_s == 30
    assert spec.retry == 0
    assert spec.expected_evidence_class == "CONFIRMED"
    assert spec.hitl_on_fail is False
    assert spec.remediation_hint is None


# Original token values in GOOD_YAML, used to produce precise
# single-line replacements for the negative tests below.
_GOOD_YAML_ORIGINAL_VALUES = {
    "sequence": "10",
    "id": "synthetic",
    "display_name": "Synthetic",
    "command_type": "python_module",
    "command": (
        '["control_plane.preflight.probes.exec", "--echo", "ok"]'
    ),
    "timeout_s": "5",
    "retry": "0",
    "expected_evidence_class": "CONFIRMED",
    "hitl_on_fail": "false",
    "remediation_hint": '"do a thing"',
}


@pytest.mark.parametrize("bad_field,bad_value,reason", [
    ("sequence", "ten", "sequence must be coercible to int"),
    ("command_type", "ruby", "command_type must be 'python_module' or 'shell'"),
    ("expected_evidence_class", "ASPIRATIONAL", "expected_evidence_class must be CONFIRMED"),
    ("retry", "five", "retry must be an int"),
])
def test_checkspec_rejects_invalid_yaml(bad_field, bad_value, reason):
    """Negative tests for catalog validation.

    Uses precise full-token replacement (matching the original value
    in GOOD_YAML) to avoid the shared-prefix whitespace-glob problem
    where mid-token replacement produces malformed YAML.
    """
    original = _GOOD_YAML_ORIGINAL_VALUES[bad_field]
    padded = "\n" + GOOD_YAML
    bad_yaml = padded.replace(
        f"\n{bad_field}: {original}",
        f"\n{bad_field}: {bad_value}",
        1,
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
