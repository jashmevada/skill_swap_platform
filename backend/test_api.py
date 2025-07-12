#!/usr/bin/env python3
"""
Simple test script for Skill Swap Platform API
Run this script to test all major endpoints
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

def print_test_header(test_name: str):
    print(f"\n{'='*50}")
    print(f"Testing: {test_name}")
    print(f"{'='*50}")

def print_result(success: bool, message: str, data: Any = None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if data:
        print(f"Response: {json.dumps(data, indent=2)}")

class SkillSwapTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.admin_token = None
        self.skill_id = None

    def test_health_check(self):
        """Test basic health endpoints"""
        print_test_header("Health Check")
        
        try:
            # Test root endpoint
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print_result(True, "Root endpoint working", response.json())
            else:
                print_result(False, f"Root endpoint failed: {response.status_code}")

            # Test health endpoint
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print_result(True, "Health endpoint working", response.json())
            else:
                print_result(False, f"Health endpoint failed: {response.status_code}")

        except Exception as e:
            print_result(False, f"Health check failed: {str(e)}")

    def test_user_registration(self):
        """Test user registration"""
        print_test_header("User Registration")
        
        try:
            user_data = {
                "email": "testuser@example.com",
                "username": "testuser",
                "password": "password123",
                "full_name": "Test User",
                "location": "Test City",
                "bio": "A test user for API testing"
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/auth/register",
                json=user_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get("id")
                print_result(True, "User registration successful", data)
            else:
                print_result(False, f"Registration failed: {response.status_code} - {response.text}")

        except Exception as e:
            print_result(False, f"Registration test failed: {str(e)}")

    def test_user_login(self):
        """Test user login"""
        print_test_header("User Login")
        
        try:
            login_data = {
                "username": "testuser",
                "password": "password123"
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print_result(True, "Login successful", {"token_preview": self.token[:20] + "..."})
            else:
                print_result(False, f"Login failed: {response.status_code} - {response.text}")

        except Exception as e:
            print_result(False, f"Login test failed: {str(e)}")

    def test_protected_endpoint(self):
        """Test protected endpoints with authentication"""
        print_test_header("Protected Endpoints")
        
        if not self.token:
            print_result(False, "No token available for protected endpoint test")
            return

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test get current user
            response = self.session.get(
                f"{BASE_URL}/api/users/me",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, "Get current user successful", data)
            else:
                print_result(False, f"Get current user failed: {response.status_code}")

        except Exception as e:
            print_result(False, f"Protected endpoint test failed: {str(e)}")

    def test_skills_management(self):
        """Test skills creation and management"""
        print_test_header("Skills Management")
        
        if not self.token:
            print_result(False, "No token available for skills test")
            return

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create a skill
            skill_data = {
                "name": "Python Programming",
                "category": "Programming",
                "description": "Backend development with Python"
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/skills/",
                json=skill_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.skill_id = data.get("id")
                print_result(True, "Skill creation successful", data)
            else:
                print_result(False, f"Skill creation failed: {response.status_code}")

            # Get all skills
            response = self.session.get(
                f"{BASE_URL}/api/skills/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, f"Retrieved {len(data)} skills", data)
            else:
                print_result(False, f"Get skills failed: {response.status_code}")

        except Exception as e:
            print_result(False, f"Skills test failed: {str(e)}")

    def test_user_skills_assignment(self):
        """Test assigning skills to users"""
        print_test_header("User Skills Assignment")
        
        if not self.token or not self.skill_id:
            print_result(False, "Token or skill_id not available")
            return

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Add skill to user's offered skills
            response = self.session.post(
                f"{BASE_URL}/api/users/me/skills/offered/{self.skill_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                print_result(True, "Skill added to offered skills", response.json())
            else:
                print_result(False, f"Add skill failed: {response.status_code}")

            # Get user's offered skills
            response = self.session.get(
                f"{BASE_URL}/api/users/{self.user_id}/skills/offered",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, f"User has {len(data)} offered skills", data)
            else:
                print_result(False, f"Get offered skills failed: {response.status_code}")

        except Exception as e:
            print_result(False, f"User skills assignment test failed: {str(e)}")

    def test_user_search(self):
        """Test user search functionality"""
        print_test_header("User Search")
        
        if not self.token:
            print_result(False, "No token available for search test")
            return

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Search users (should return empty since we only have one user)
            response = self.session.get(
                f"{BASE_URL}/api/users/search",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, f"Search returned {len(data)} users", data)
            else:
                print_result(False, f"User search failed: {response.status_code}")

        except Exception as e:
            print_result(False, f"User search test failed: {str(e)}")

    def create_admin_user(self):
        """Create an admin user for admin tests"""
        print_test_header("Creating Admin User")
        
        try:
            admin_data = {
                "email": "admin@example.com",
                "username": "admin",
                "password": "admin123",
                "full_name": "Admin User"
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/auth/register",
                json=admin_data
            )
            
            if response.status_code == 200:
                print_result(True, "Admin user created")
                
                # Login as admin
                login_data = {
                    "username": "admin",
                    "password": "admin123"
                }
                
                response = self.session.post(
                    f"{BASE_URL}/api/auth/login",
                    json=login_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.admin_token = data.get("access_token")
                    print_result(True, "Admin login successful")
                    
                    # Note: In a real scenario, you'd need to manually set is_admin=True in the database
                    print("⚠️  Note: You need to manually set is_admin=True for the admin user in the database")
                    
            else:
                print_result(False, f"Admin creation failed: {response.status_code}")

        except Exception as e:
            print_result(False, f"Admin user creation failed: {str(e)}")

    def test_error_handling(self):
        """Test error handling"""
        print_test_header("Error Handling")
        
        try:
            # Test unauthorized access
            response = self.session.get(f"{BASE_URL}/api/users/me")
            if response.status_code == 401:
                print_result(True, "Unauthorized access properly blocked")
            else:
                print_result(False, f"Expected 401, got {response.status_code}")

            # Test invalid endpoint
            response = self.session.get(f"{BASE_URL}/api/nonexistent")
            if response.status_code == 404:
                print_result(True, "404 for invalid endpoint")
            else:
                print_result(False, f"Expected 404, got {response.status_code}")

        except Exception as e:
            print_result(False, f"Error handling test failed: {str(e)}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Skill Swap Platform API Tests")
        print(f"Base URL: {BASE_URL}")
        
        tests = [
            self.test_health_check,
            self.test_user_registration,
            self.test_user_login,
            self.test_protected_endpoint,
            self.test_skills_management,
            self.test_user_skills_assignment,
            self.test_user_search,
            self.create_admin_user,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                print_result(False, f"Test {test.__name__} crashed: {str(e)}")
        
        print(f"\n{'='*50}")
        print("🏁 All tests completed!")
        print(f"{'='*50}")

if __name__ == "__main__":
    tester = SkillSwapTester()
    tester.run_all_tests()
