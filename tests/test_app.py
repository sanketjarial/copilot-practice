import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import activities, app

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)
client = TestClient(app)


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(email) == 1


def test_unregister_participant_removes_participant():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email, safe='')}" )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email, safe='')}" )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def reset_activity_data():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def setup_function():
    reset_activity_data()
