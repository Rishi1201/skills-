import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def setup_function():
    # Reset activities to initial state before each test
    for activity in activities.values():
        activity["participants"] = []

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_success():
    email = "testuser@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    email = "testuser2@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=someone@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_success():
    email = "testuser3@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_not_found():
    response = client.delete("/activities/Chess Club/unregister?email=notfound@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"

def test_signup_max_capacity():
    # Fill up the activity
    activity = activities["Chess Club"]
    activity["participants"] = [f"user{i}@mergington.edu" for i in range(activity["max_participants"])]
    response = client.post("/activities/Chess Club/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is at max capacity"
