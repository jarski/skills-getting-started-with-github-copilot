import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# --- GET /activities ---
def test_get_activities():
    # Arrange: nothing needed
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

# --- GET / (redirect to static/index.html) ---
def test_root_redirect():
    # Arrange: nothing needed
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code in (200, 307, 302)
    # Should redirect to /static/index.html
    assert "static/index.html" in response.headers.get("location", "") or str(response.url).endswith("/static/index.html")

# --- POST /activities/{activity_name}/signup ---
def test_signup_for_activity():
    # Arrange
    activity = "Chess Club"
    email = "testuser@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert f"Signed up {email} for {activity}" in response.json()["message"]
    # Check participant added
    get_resp = client.get("/activities")
    assert email in get_resp.json()[activity]["participants"]

# --- POST duplicate signup ---
def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    email = "testuser@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

# --- POST invalid activity ---
def test_signup_invalid_activity():
    # Arrange
    activity = "Nonexistent Club"
    email = "someone@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

# --- DELETE /activities/{activity_name}/unregister ---
def test_unregister_for_activity():
    # Arrange
    activity = "Chess Club"
    email = "testuser@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert f"Removed {email} from {activity}" in response.json()["message"]
    # Check participant removed
    get_resp = client.get("/activities")
    assert email not in get_resp.json()[activity]["participants"]

# --- DELETE non-existent participant ---
def test_unregister_nonexistent():
    # Arrange
    activity = "Chess Club"
    email = "notfound@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]

# --- DELETE invalid activity ---
def test_unregister_invalid_activity():
    # Arrange
    activity = "Nonexistent Club"
    email = "someone@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
