"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    original_activities = {
        "Football Team": {
            "description": "American football team for competitive play and training",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 40,
            "participants": ["alex@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Basketball practice and intramural competitions",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and theatrical productions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, sculpture and mixed media",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Participate in competitive debate and rhetoric competitions",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["liam@mergington.edu", "mia@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    yield
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        data = response.json()
        assert "Football Team" in data
        assert "Basketball Club" in data
        assert "Drama Club" in data
        assert "Chess Club" in data

    def test_get_activities_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Football Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_returns_200(self, client, reset_activities):
        """Test that signup returns a 200 status code"""
        response = client.post(
            "/activities/Football Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Football Team/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Football Team" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        response = client.post(
            f"/activities/Football Team/signup?email={email}"
        )
        assert response.status_code == 200
        response = client.get("/activities")
        data = response.json()
        assert email in data["Football Team"]["participants"]

    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signing up twice fails"""
        email = "alex@mergington.edu"  # Already in Football Team
        response = client.post(
            f"/activities/Football Team/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_invalid_activity_fails(self, client, reset_activities):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_returns_200(self, client, reset_activities):
        """Test that unregister returns a 200 status code"""
        response = client.post(
            "/activities/Football Team/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client, reset_activities):
        """Test that unregister returns a success message"""
        response = client.post(
            "/activities/Football Team/unregister?email=alex@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "alex@mergington.edu" in data["message"]
        assert "Football Team" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "alex@mergington.edu"
        response = client.post(
            f"/activities/Football Team/unregister?email={email}"
        )
        assert response.status_code == 200
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Football Team"]["participants"]

    def test_unregister_not_registered_fails(self, client, reset_activities):
        """Test that unregistering someone not registered fails"""
        response = client.post(
            "/activities/Football Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_invalid_activity_fails(self, client, reset_activities):
        """Test that unregistering from a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestIntegration:
    """Integration tests for signup and unregister flow"""

    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "integration@mergington.edu"
        activity = "Chess Club"

        # Sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200

        # Verify signup
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]

        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200

        # Verify unregister
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]

    def test_signup_multiple_activities(self, client, reset_activities):
        """Test signing up for multiple activities"""
        email = "multiactivity@mergington.edu"

        # Sign up for multiple activities
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Science Club/signup?email={email}"
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify both signups
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Science Club"]["participants"]
