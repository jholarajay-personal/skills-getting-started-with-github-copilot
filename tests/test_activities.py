import pytest


def test_root_redirect(client):
    """Test that root path redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(client, reset_activities):
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities


def test_get_activities_structure(client, reset_activities):
    """Test that activities have the correct structure"""
    response = client.get("/activities")
    activities = response.json()
    
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    
    assert isinstance(chess_club["participants"], list)
    assert len(chess_club["participants"]) > 0


def test_signup_for_activity(client, reset_activities):
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu",
        follow_redirects=True
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert "newstudent@mergington.edu" in result["message"]


def test_signup_already_registered(client, reset_activities):
    """Test that duplicate signup returns an error"""
    # Try to sign up with an email already registered
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu",
        follow_redirects=True
    )
    
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"]


def test_signup_nonexistent_activity(client, reset_activities):
    """Test that signup for nonexistent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu",
        follow_redirects=True
    )
    
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "not found" in result["detail"]


def test_unregister_from_activity(client, reset_activities):
    """Test unregistering a participant from an activity"""
    # First verify the participant is registered
    response = client.get("/activities")
    activities = response.json()
    assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
    
    # Unregister the participant
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu",
        follow_redirects=True
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert "michael@mergington.edu" in result["message"]
    
    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_not_registered(client, reset_activities):
    """Test that unregistering non-registered participant returns error"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu",
        follow_redirects=True
    )
    
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "not registered" in result["detail"]


def test_unregister_nonexistent_activity(client, reset_activities):
    """Test that unregister for nonexistent activity returns 404"""
    response = client.delete(
        "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu",
        follow_redirects=True
    )
    
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "not found" in result["detail"]


def test_signup_updates_participant_count(client, reset_activities):
    """Test that signup updates the participants list"""
    # Get initial participants
    response = client.get("/activities")
    initial_participants = response.json()["Chess Club"]["participants"]
    initial_count = len(initial_participants)
    
    # Sign up new participant
    client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu",
        follow_redirects=True
    )
    
    # Verify count increased
    response = client.get("/activities")
    updated_participants = response.json()["Chess Club"]["participants"]
    assert len(updated_participants) == initial_count + 1
    assert "newstudent@mergington.edu" in updated_participants


def test_multiple_signup_and_unregister(client, reset_activities):
    """Test multiple signup and unregister operations"""
    # Sign up two new participants
    client.post("/activities/Chess%20Club/signup?email=student1@mergington.edu")
    client.post("/activities/Chess%20Club/signup?email=student2@mergington.edu")
    
    response = client.get("/activities")
    participants = response.json()["Chess Club"]["participants"]
    assert "student1@mergington.edu" in participants
    assert "student2@mergington.edu" in participants
    
    # Unregister one participant
    client.delete("/activities/Chess%20Club/unregister?email=student1@mergington.edu")
    
    response = client.get("/activities")
    participants = response.json()["Chess Club"]["participants"]
    assert "student1@mergington.edu" not in participants
    assert "student2@mergington.edu" in participants
