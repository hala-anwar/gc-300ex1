from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant():
    response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 200
    assert "new.student@mergington.edu" in activities["Art Club"]["participants"]


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email():
    response = client.post("/activities/Art%20Club/signup")

    assert response.status_code == 422


def test_signup_rejects_duplicate_participant():
    email = activities["Chess Club"]["participants"][0]

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_rejects_full_activity():
    activity = activities["Art Club"]
    activity["participants"][:] = [
        f"student{number}@mergington.edu"
        for number in range(activity["max_participants"])
    ]

    response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": "extra.student@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
    assert "extra.student@mergington.edu" not in activity["participants"]


def test_unregister_removes_participant():
    response = client.delete(
        "/activities/Gym%20Class/participants/olivia%40mergington.edu"
    )

    assert response.status_code == 200
    assert "olivia@mergington.edu" not in activities["Gym Class"]["participants"]


def test_unregister_rejects_unknown_activity():
    response = client.delete(
        "/activities/Unknown%20Club/participants/student%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_missing_participant():
    response = client.delete(
        "/activities/Art%20Club/participants/missing%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
