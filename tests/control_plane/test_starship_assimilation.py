from __future__ import annotations

from control_plane.starship_assimilation import powershell_snippet, run_starship_assimilation, starship_config_text


def test_starship_config_uses_camelot_custom_module() -> None:
    text = starship_config_text()

    assert "[custom.camelot]" in text
    assert "Invoke-Expression" not in text
    assert "starship_camelot_module.py" in text
    assert "add_newline = false" in text


def test_powershell_snippet_sets_explicit_config() -> None:
    snippet = powershell_snippet()

    assert "$env:STARSHIP_CONFIG" in snippet
    assert "starship init powershell" in snippet
    assert "Get-Command starship" in snippet


def test_starship_assimilation_payload_is_report_first() -> None:
    payload = run_starship_assimilation(write=False)

    assert payload["schema"] == "camelot.starship-assimilation/v1"
    assert payload["upstream"] == "https://github.com/starship/starship"
    assert payload["docs_source"] == "/websites/starship_rs via Context7"
    assert payload["config_path"].endswith("camelot-starship.toml")
    assert any("Do not auto-edit PowerShell profiles" in item for item in payload["feedback"])