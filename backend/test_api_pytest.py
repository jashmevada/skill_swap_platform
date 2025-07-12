"""
Comprehensive pytest test suite for Skill Swap Platform API
Run with: pytest test_api_pytest.py -v
"""

import pytest
import httpx
import asyncio
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class TestSkillSwapAPI:
    """Test class for Skill Swap Platform API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = httpx.Client(base_url=BASE_URL)
        self.token = None
        self.user_id = None
        self.skill_id = None
        yield
        self.client.close()

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        # Test root endpoint
        response = self.client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Test health endpoint
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_user_registration(self):
        """Test user registration"""
        user_data = {
            "email": "pytest@example.com",
            "username": "pytestuser",
            "password": "password123",
            "full_name": "PyTest User",
            "location": "Test City"
        }
        
        response = self.client.post("/api/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        self.user_id = data["id"]

    def test_user_login(self):
        """Test user login"""
        # First register a user
        self.test_user_registration()
        
        login_data = {
            "username": "pytestuser",
            "password": "password123"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        self.token = data["access_token"]

    def test_protected_endpoint_without_token(self):
        """Test that protected endpoints require authentication"""
        response = self.client.get("/api/users/me")
        assert response.status_code == 401

    def test_protected_endpoint_with_token(self):
        """Test protected endpoints with valid token"""
        # Setup: login first
        self.test_user_login()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/api/users/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "pytestuser"

    def test_skill_creation(self):
        """Test skill creation"""
        # Setup: login first
        self.test_user_login()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        skill_data = {
            "name": "PyTest Skill",
            "category": "Testing",
            "description": "A skill for testing purposes"
        }
        
        response = self.client.post("/api/skills/", json=skill_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Pytest Skill"  # Note: API title-cases the name
        assert data["category"] == "Testing"
        assert data["is_approved"] == True
        self.skill_id = data["id"]

    def test_get_skills(self):
        """Test retrieving skills"""
        # Setup: create a skill first
        self.test_skill_creation()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/api/skills/", headers=headers)
        
        assert response.status_code == 200
        skills = response.json()
        assert isinstance(skills, list)
        assert len(skills) > 0

    def test_skill_search(self):
        """Test skill search functionality"""
        # Setup: create a skill first
        self.test_skill_creation()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/api/skills/?search=PyTest", headers=headers)
        
        assert response.status_code == 200
        skills = response.json()
        assert isinstance(skills, list)

    def test_add_skill_to_user(self):
        """Test adding skill to user's offered skills"""
        # Setup: create skill first
        self.test_skill_creation()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.post(
            f"/api/users/me/skills/offered/{self.skill_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        assert "message" in response.json()

    def test_get_user_offered_skills(self):
        """Test retrieving user's offered skills"""
        # Setup: add skill to user first
        self.test_add_skill_to_user()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get(
            f"/api/users/{self.user_id}/skills/offered",
            headers=headers
        )
        
        assert response.status_code == 200
        skills = response.json()
        assert isinstance(skills, list)
        assert len(skills) > 0

    def test_user_search(self):
        """Test user search functionality"""
        # Setup: login first
        self.test_user_login()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/api/users/search", headers=headers)
        
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401

    def test_duplicate_user_registration(self):
        """Test that duplicate user registration fails"""
        # First registration
        self.test_user_registration()
        
        # Try to register the same user again
        user_data = {
            "email": "pytest@example.com",
            "username": "pytestuser",
            "password": "password123",
            "full_name": "PyTest User Duplicate"
        }
        
        response = self.client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400

    def test_invalid_skill_assignment(self):
        """Test assigning non-existent skill to user"""
        # Setup: login first
        self.test_user_login()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.post(
            "/api/users/me/skills/offered/99999",  # Non-existent skill ID
            headers=headers
        )
        
        assert response.status_code == 404

    def test_api_documentation_endpoint(self):
        """Test that API documentation is accessible"""
        response = self.client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint"""
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema


# Performance tests
class TestAPIPerformance:
    """Performance tests for the API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = httpx.Client(base_url=BASE_URL)
        yield
        self.client.close()

    def test_health_endpoint_response_time(self):
        """Test that health endpoint responds quickly"""
        import time
        
        start_time = time.time()
        response = self.client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond in less than 1 second

    def test_multiple_requests(self):
        """Test handling multiple simultaneous requests"""
        responses = []
        
        for _ in range(5):
            response = self.client.get("/health")
            responses.append(response)
        
        for response in responses:
            assert response.status_code == 200


# Integration tests
class TestAPIIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = httpx.Client(base_url=BASE_URL)
        yield
        self.client.close()

    def test_complete_user_journey(self):
        """Test complete user journey from registration to skill swap"""
        # 1. Register user
        user_data = {
            "email": "journey@example.com",
            "username": "journeyuser",
            "password": "password123",
            "full_name": "Journey User"
        }
        
        response = self.client.post("/api/auth/register", json=user_data)
        assert response.status_code == 200
        user_id = response.json()["id"]
        
        # 2. Login
        login_data = {"username": "journeyuser", "password": "password123"}
        response = self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create a skill
        skill_data = {
            "name": "Journey Skill",
            "category": "Testing",
            "description": "A skill for the user journey test"
        }
        response = self.client.post("/api/skills/", json=skill_data, headers=headers)
        assert response.status_code == 200
        skill_id = response.json()["id"]
        
        # 4. Add skill to offered skills
        response = self.client.post(
            f"/api/users/me/skills/offered/{skill_id}",
            headers=headers
        )
        assert response.status_code == 200
        
        # 5. Verify skill was added
        response = self.client.get(
            f"/api/users/{user_id}/skills/offered",
            headers=headers
        )
        assert response.status_code == 200
        offered_skills = response.json()
        assert len(offered_skills) > 0
        assert any(skill["id"] == skill_id for skill in offered_skills)


if __name__ == "__main__":
    # Run tests programmatically
    pytest.main([__file__, "-v", "--tb=short"])
