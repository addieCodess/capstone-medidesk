from conftest import client


def _create(payload=None):
    payload = payload or {
        "patient_name": "Aarav Sharma",
        "doctor_name": "Dr. Rao",
        "reason": "Fever + checkup",
        "status": "scheduled",
        "priority": "high",
        "scheduled_for": "2026-10-20T10:00",
    }
    return client.post("/api/appointments", json=payload)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_root_ok():
    r = client.get("/")
    assert r.status_code == 200


def test_create_appointment():
    r = _create()
    assert r.status_code == 201, r.text
    assert r.json()["patient_name"] == "Aarav Sharma"


def test_list_appointments():
    _create({"patient_name": "Meera", "doctor_name": "Dr. Iyer", "reason": "Dental"})
    r = client.get("/api/appointments")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_get_appointment_by_id():
    created = _create().json()
    r = client.get(f"/api/appointments/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_update_appointment():
    created = _create().json()
    r = client.put(f"/api/appointments/{created['id']}", json={"status": "checked-in"})
    assert r.status_code == 200
    assert r.json()["status"] == "checked-in"


def test_stats_endpoint():
    _create()
    r = client.get("/api/appointments/stats")
    assert r.status_code == 200
    assert "total" in r.json()


def test_delete_appointment():
    created = _create().json()
    r = client.delete(f"/api/appointments/{created['id']}")
    assert r.status_code == 204
    r2 = client.get(f"/api/appointments/{created['id']}")
    assert r2.status_code == 404


def test_metrics_endpoint():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests" in r.text or "http_request" in r.text or "process_" in r.text
