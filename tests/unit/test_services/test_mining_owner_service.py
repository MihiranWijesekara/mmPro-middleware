from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock
import os
import requests
from services.mining_owner_service import MLOwnerService
from typing import Tuple, List, Dict, Optional
from datetime import datetime as real_datetime

class TestMiningLicenses:

    @patch.dict('os.environ', {'REDMINE_URL': 'http://gsmb.aasait.lk'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    @patch('services.mining_owner_service.LimitUtils.get_limit')
    @patch('services.mining_owner_service.requests.get')
    def test_mining_licenses_success(self, mock_get, mock_limit, mock_user_info, mock_api_key):
        # Setup mocks
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)  # user_id, error
        mock_limit.return_value = 100

        # Mock response data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "id": 1,
                    "assigned_to": {"id": 123, "name": "Test User"},
                    "status": {"name": "Active"},
                    "start_date": "2023-01-01",
                    "due_date": "2023-12-31",
                    "custom_fields": [
                        {"name": "Mining License Number", "value": "ML-001"},
                        {"name": "Divisional Secretary Division", "value": "Test Division"},
                        {"name": "Name of village ", "value": "Test Village"},
                        {"name": "Remaining", "value": "500"},
                        {"name": "Royalty", "value": "1000"}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        # Call the method
        result, error = MLOwnerService.mining_licenses("valid_token")

        # Assertions
        assert error is None
        assert len(result) == 1
        assert result[0]["License Number"] == "ML-001"
        assert result[0]["Owner Name"] == "Test User"
        assert result[0]["Status"] == "Active"
        assert result[0]["Remaining Cubes"] == 500
        assert result[0]["Location"] == "Test Village"  # Note the space in field name
        
        # Corrected URL for the mock
        mock_get.assert_called_once_with(
            "http://gsmb.aasait.lk/projects/mmpro-gsmb/issues.json?offset=0&limit=100",
            params={"project_id": 1, "tracker_id": 4, "status_id": 7},
            headers={"X-Redmine-API-Key": "test_api_key"}
        )

    @patch.dict('os.environ', {'REDMINE_URL': ''})  # Empty URL
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    def test_mining_licenses_missing_redmine_url(self, mock_api_key):
        mock_api_key.return_value = 'test_api_key'  # Provide a dummy API key so the URL check happens
        result, error = MLOwnerService.mining_licenses("valid_token")
        assert result is None
        assert "Redmine URL or API Key is missing" in error

    @patch.dict('os.environ', {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    def test_mining_licenses_missing_api_key(self, mock_api_key):
        mock_api_key.return_value = None
        result, error = MLOwnerService.mining_licenses("valid_token")
        assert result is None
        assert "Redmine URL or API Key is missing" in error

    @patch.dict('os.environ', {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    def test_mining_licenses_user_info_error(self, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (None, "Token error")
        result, error = MLOwnerService.mining_licenses("valid_token")
        assert result is None
        assert error == "Token error"

    @patch.dict('os.environ', {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    @patch('services.mining_owner_service.LimitUtils.get_limit')
    @patch('services.mining_owner_service.requests.get')
    def test_mining_licenses_api_failure(self, mock_get, mock_limit, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)
        mock_limit.return_value = 100
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_get.return_value = mock_response
        
        result, error = MLOwnerService.mining_licenses("valid_token")
        assert result is None
        assert "Failed to fetch issues: 500 - Server error" in error

    @patch.dict('os.environ', {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    @patch('services.mining_owner_service.LimitUtils.get_limit')
    @patch('services.mining_owner_service.requests.get')
    def test_mining_licenses_no_assigned_licenses(self, mock_get, mock_limit, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)
        mock_limit.return_value = 100
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "id": 1,
                    "assigned_to": {"id": 456, "name": "Other User"},  # Different user ID
                    "status": {"name": "Active"},
                    "custom_fields": []
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result, error = MLOwnerService.mining_licenses("valid_token")
        assert error is None
        assert len(result) == 0  # No licenses assigned to this user

    @patch.dict('os.environ', {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    @patch('services.mining_owner_service.LimitUtils.get_limit')
    @patch('services.mining_owner_service.requests.get')
    def test_mining_licenses_invalid_remaining_cubes(self, mock_get, mock_limit, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)
        mock_limit.return_value = 100
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "id": 1,
                    "assigned_to": {"id": 123, "name": "Test User"},
                    "status": {"name": "Active"},
                    "custom_fields": [
                        {"name": "Remaining", "value": "invalid"},  # Non-numeric value
                        {"name": "Royalty", "value": "1000"}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result, error = MLOwnerService.mining_licenses("valid_token")
        assert error is None
        assert result[0]["Remaining Cubes"] == 0  # Should default to 0 for invalid values

    @patch.dict('os.environ', {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    def test_mining_licenses_exception_handling(self, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)
        
        with patch('services.mining_owner_service.requests.get', side_effect=Exception("Test exception")):
            result, error = MLOwnerService.mining_licenses("valid_token")
            assert result is None
            assert "Server error: Test exception" in error

    @patch.dict('os.environ', {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    @patch('services.mining_owner_service.LimitUtils.get_limit')
    @patch('services.mining_owner_service.requests.get')
    def test_mining_licenses_missing_fields(self, mock_get, mock_limit, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)
        mock_limit.return_value = 100
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "id": 1,
                    "assigned_to": {"id": 123},  # Missing name
                    "status": {},  # Missing status name
                    "custom_fields": []  # Empty custom fields
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result, error = MLOwnerService.mining_licenses("valid_token")
        assert error is None
        assert result[0]["Owner Name"] == "N/A"
        assert result[0]["Status"] == "Unknown"
        assert result[0]["License Number"] == "N/A"



class TestMiningHomeLicenses:

    # Common helper function to patch datetime correctly
    def _patch_datetime(self, mock_datetime, fixed_date):
        mock_datetime.now.return_value = fixed_date
        mock_datetime.strptime.side_effect = lambda date_string, fmt: datetime.strptime(date_string, fmt)

    @patch.dict(os.environ, {'REDMINE_URL': 'http://gsmb.aasait.lk'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    @patch('services.mining_owner_service.LimitUtils.get_limit')
    @patch('services.mining_owner_service.requests.get')
    @patch('services.mining_owner_service.datetime')
    def test_mining_home_licenses_success(self, mock_datetime, mock_get, mock_limit, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)
        mock_limit.return_value = 100
        
        today = datetime(2023, 6, 1)
        self._patch_datetime(mock_datetime, today)

        future_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "id": 1,
                    "assigned_to": {"id": 123, "name": "Test User"},
                    "start_date": "2023-01-01",
                    "due_date": future_date,
                    "custom_fields": [
                        {"name": "Mining License Number", "value": "ML-001"},
                        {"name": "Divisional Secretary Division", "value": "Test Division"},
                        {"name": "Name of village ", "value": "Test Village"},
                        {"name": "Remaining", "value": "500"},
                        {"name": "Royalty", "value": "1000"}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        result, error = MLOwnerService.mining_homeLicenses("valid_token")
        assert error is None
        assert len(result) == 1
        assert result[0]["License Number"] == "ML-001"
        assert result[0]["Owner Name"] == "Test User"
        assert result[0]["Due Date"] == future_date
        assert result[0]["Remaining Cubes"] == 500
        assert result[0]["Location"] == "Test Village"

    @patch.dict(os.environ, {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    @patch('services.mining_owner_service.LimitUtils.get_limit')
    @patch('services.mining_owner_service.requests.get')
    @patch('services.mining_owner_service.datetime')
    def test_mining_home_licenses_past_due_date(self, mock_datetime, mock_get, mock_limit, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)
        mock_limit.return_value = 100
        
        today = datetime(2023, 6, 1)
        self._patch_datetime(mock_datetime, today)

        past_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "id": 1,
                    "assigned_to": {"id": 123, "name": "Test User"},
                    "due_date": past_date,
                    "custom_fields": []
                }
            ]
        }
        mock_get.return_value = mock_response

        result, error = MLOwnerService.mining_homeLicenses("valid_token")
        assert error is None
        assert len(result) == 0

    @patch.dict(os.environ, {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    @patch('services.mining_owner_service.LimitUtils.get_limit')
    @patch('services.mining_owner_service.requests.get')
    @patch('services.mining_owner_service.datetime')
    def test_mining_home_licenses_invalid_remaining_cubes(self, mock_datetime, mock_get, mock_limit, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)
        mock_limit.return_value = 100
        
        today = datetime(2023, 6, 1)
        self._patch_datetime(mock_datetime, today)

        future_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "id": 1,
                    "assigned_to": {"id": 123, "name": "Test User"},
                    "due_date": future_date,
                    "custom_fields": [
                        {"name": "Remaining", "value": "invalid"},
                        {"name": "Royalty", "value": "1000"}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        result, error = MLOwnerService.mining_homeLicenses("valid_token")
        assert error is None
        assert result[0]["Remaining Cubes"] == 0

    @patch.dict(os.environ, {'REDMINE_URL': ''})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    def test_mining_home_licenses_missing_redmine_url(self, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        result, error = MLOwnerService.mining_homeLicenses("valid_token")
        assert result is None
        assert "Redmine URL or API Key is missing" in error

    @patch.dict(os.environ, {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    def test_mining_home_licenses_missing_api_key(self, mock_api_key):
        mock_api_key.return_value = None
        result, error = MLOwnerService.mining_homeLicenses("valid_token")
        assert result is None
        assert "Redmine URL or API Key is missing" in error

    @patch.dict(os.environ, {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    def test_mining_home_licenses_user_info_error(self, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (None, "Token error")
        result, error = MLOwnerService.mining_homeLicenses("valid_token")
        assert result is None
        assert error == "Token error"

    @patch.dict(os.environ, {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    @patch('services.mining_owner_service.LimitUtils.get_limit')
    @patch('services.mining_owner_service.requests.get')
    def test_mining_home_licenses_api_failure(self, mock_get, mock_limit, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)
        mock_limit.return_value = 100

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_get.return_value = mock_response

        result, error = MLOwnerService.mining_homeLicenses("valid_token")
        assert result is None
        assert "Failed to fetch issues: 500 - Server error" in error

    @patch.dict(os.environ, {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    @patch('services.mining_owner_service.LimitUtils.get_limit')
    @patch('services.mining_owner_service.requests.get')
    @patch('services.mining_owner_service.datetime')
    def test_mining_home_licenses_missing_fields(self, mock_datetime, mock_get, mock_limit, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)
        mock_limit.return_value = 100
        
        today = datetime(2023, 6, 1)
        self._patch_datetime(mock_datetime, today)

        future_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "id": 1,
                    "assigned_to": {"id": 123},
                    "due_date": future_date,
                    "custom_fields": []
                }
            ]
        }
        mock_get.return_value = mock_response

        result, error = MLOwnerService.mining_homeLicenses("valid_token")
        assert error is None
        assert result[0]["Owner Name"] == "N/A"
        assert result[0]["License Number"] == "N/A"
        assert result[0]["Location"] == "N/A"

    @patch.dict(os.environ, {'REDMINE_URL': 'http://test.redmine.com'})
    @patch('services.mining_owner_service.JWTUtils.get_api_key_from_token')
    @patch('services.mining_owner_service.MLOUtils.get_user_info_from_token')
    def test_mining_home_licenses_exception_handling(self, mock_user_info, mock_api_key):
        mock_api_key.return_value = 'test_api_key'
        mock_user_info.return_value = (123, None)

        with patch('services.mining_owner_service.requests.get', side_effect=Exception("Test exception")):
            result, error = MLOwnerService.mining_homeLicenses("valid_token")
            assert result is None
            assert "Server error: Test exception" in error