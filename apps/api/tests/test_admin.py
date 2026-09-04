"""Admin compatibility-rule editor: fixture test reflects active rule flags."""
from fastapi.testclient import TestClient

from inqetra import app

client = TestClient(app)


def test_rules_fixture():
    rules = client.get("/api/v1/admin/rules").json()["items"]
    assert rules, "no compatibility rules seeded"
    target = rules[0]
    original = {"active": target["active"], "severity": target["severity"]}
    try:
        toggled = client.patch(f"/api/v1/admin/rules/{target['rule']}",
                               json={"active": not original["active"]}).json()
        assert toggled["active"] == (not original["active"])
        t = client.post("/api/v1/admin/rules/test", json={}).json()
        assert target["rule"] not in t["active_rules"] if not toggled["active"] \
            else target["rule"] in t["active_rules"]
        assert t["full_overall"] in ("PASS", "WARN", "FAIL")
        assert t["scoped_overall"] in ("PASS", "WARN", "FAIL")
        assert t["checks"] > 0
        assert target["rule"] in t["skipped"] if not toggled["active"] else True
    finally:
        client.patch(f"/api/v1/admin/rules/{target['rule']}", json=original)
    # unknown rule → 404
    assert client.patch("/api/v1/admin/rules/not-a-rule", json={"active": True}).status_code == 404


def test_admin_audit_log_present():
    a = client.get("/api/v1/admin/audit").json()["items"]
    assert isinstance(a, list)
