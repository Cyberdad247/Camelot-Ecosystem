from excalibur.pii import redact, scan

def test_redacts_email_and_ssn():
    t = "ping me at vf@head.io ssn 123-45-6789"
    out = redact(t)
    assert "vf@head.io" not in out and "123-45-6789" not in out
    assert "[REDACTED:EMAIL]" in out and "[REDACTED:SSN]" in out

def test_scan_counts():
    c = scan("a@b.co c@d.io 555-123-4567")
    assert c["EMAIL"] == 2 and c["PHONE"] == 1
