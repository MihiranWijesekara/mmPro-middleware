import pytest
from unittest.mock import patch, Mock
from services.gsmb_managemnt_service import GsmbManagmentService  # replace with actual import path
from flask import Response

@pytest.mark.usefixtures("mock_env")
def test_monthly_total_sand_cubes():
    mock_issues_page1 = {
        "issues": [
            {
                "created_on": "2025-01-15T12:34:56Z",
                "custom_fields": [
                    {"id": 58, "name": "Cubes", "value": "2.5"}
                ]
            },
            {
                "created_on": "2025-02-10T09:00:00Z",
                "custom_fields": [
                    {"id": 58, "name": "Cubes", "value": "3.0"}
                ]
            }
        ]
    }

    mock_issues_page2 = {"issues": []}  # End of pagination

    with patch("utils.jwt_utils.JWTUtils.get_api_key_from_token", return_value="fake-api-key"), \
         patch("services.gsmb_managemnt_service.requests.get") as mock_get:

        mock_get.side_effect = [
            Mock(status_code=200, json=Mock(return_value=mock_issues_page1)),
            Mock(status_code=200, json=Mock(return_value=mock_issues_page2)),
        ]

        result, error = GsmbManagmentService.monthly_total_sand_cubes("fake-jwt-token")

        assert error is None
        assert result is not None

        # Validate January and February
        jan = next((r for r in result if r["month"] == "Jan"), None)
        feb = next((r for r in result if r["month"] == "Feb"), None)

        assert jan["totalCubes"] == 2.5
        assert feb["totalCubes"] == 3.0

        # Validate other months are 0
        for r in result:
            if r["month"] not in ["Jan", "Feb"]:
                assert r["totalCubes"] == 0

@pytest.mark.usefixtures("mock_env")
def test_fetch_top_mining_holders():
    mock_issues_page1 = {
        "issues": [
            {
                "assigned_to": {"name": "Company A"},
                "custom_fields": [
                    {"name": "Capacity", "value": "100"},
                    {"name": "Used", "value": "75"}
                ]
            },
            {
                "assigned_to": {"name": "Company B"},
                "custom_fields": [
                    {"name": "Capacity", "value": "200"},
                    {"name": "Used", "value": "50"}
                ]
            }
        ]
    }

    mock_issues_page2 = {"issues": []}  # End of pagination

    with patch("utils.jwt_utils.JWTUtils.get_api_key_from_token", return_value="fake-api-key"), \
         patch("services.gsmb_managemnt_service.requests.get") as mock_get:

        # Simulate paginated API response
        mock_get.side_effect = [
            Mock(status_code=200, json=Mock(return_value=mock_issues_page1)),
            Mock(status_code=200, json=Mock(return_value=mock_issues_page2)),
        ]

        result, error = GsmbManagmentService.fetch_top_mining_holders("fake-jwt-token")

        assert error is None
        assert result is not None
        assert len(result) == 2

        # Ensure result is sorted by capacity descending
        assert result[0]["label"] == "Company B"
        assert result[0]["capacity"] == 200
        assert result[0]["value"] == 25.0  # 50/200 = 25%

        assert result[1]["label"] == "Company A"
        assert result[1]["capacity"] == 100
        assert result[1]["value"] == 75.0  # 75/100 = 75%

@pytest.mark.usefixtures("mock_env")
def test_fetch_royalty_counts_success(app):
    mock_issues_page1 = {
        "issues": [
            {
                "tracker": {"id": 4, "name": "ML"},
                "status": {"name": "Valid"},
                "assigned_to": {"name": "Company A"},
                "custom_fields": [{"name": "Royalty", "value": "1200"}]
            },
            {
                "tracker": {"id": 4, "name": "ML"},
                "status": {"name": "Valid"},
                "assigned_to": {"name": "Company B"},
                "custom_fields": [{"name": "Royalty", "value": "800"}]
            }
        ]
    }

    mock_issues_page2 = {"issues": []}  # Simulate end of pagination

    with app.app_context(), \
         patch("utils.jwt_utils.JWTUtils.get_api_key_from_token", return_value="fake-api-key"), \
         patch("services.gsmb_managemnt_service.requests.get") as mock_get:

        mock_get.side_effect = [
            Mock(status_code=200, json=Mock(return_value=mock_issues_page1)),
            Mock(status_code=200, json=Mock(return_value=mock_issues_page2)),
        ]

        # Service returns (response, error) tuple
        response, error = GsmbManagmentService.fetch_royalty_counts("fake-jwt-token")
        
        # Check error is None
        assert error is None
        
        # Verify response is a Flask Response
        assert isinstance(response, Response)
        assert response.status_code == 200
        
        # Get the JSON data from the response
        data = response.get_json()
        
        # Now make assertions on the data
        assert data is not None
        assert "total_royalty" in data
        assert data["total_royalty"] == 2000
        assert len(data["orders"]) == 2

        # Ensure result is sorted by royalty descending
        assert data["orders"][0]["title"] == "Company A"
        assert data["orders"][0]["royalty_value"] == 1200

        assert data["orders"][1]["title"] == "Company B"
        assert data["orders"][1]["royalty_value"] == 800

@pytest.mark.usefixtures("mock_env")
def test_monthly_mining_license_count_success():
    # Mock data
    mock_issues_page1 = {
        "issues": [
            {
                "tracker": {"id": 4, "name": "ML"},
                "created_on": "2023-01-15T12:34:56Z"
            },
            {
                "tracker": {"id": 4, "name": "ML"},
                "created_on": "2023-01-20T10:00:00Z"
            },
            {
                "tracker": {"id": 4, "name": "ML"},
                "created_on": "2023-02-10T09:00:00Z"
            },
            {
                "tracker": {"id": 5, "name": "Other"},  # Should be filtered out
                "created_on": "2023-01-25T11:00:00Z"
            }
        ]
    }

    mock_issues_page2 = {"issues": []}  # End of pagination

    with patch("utils.jwt_utils.JWTUtils.get_api_key_from_token", return_value="fake-api-key"), \
         patch("services.gsmb_managemnt_service.requests.get") as mock_get:

        # Set up mock responses
        mock_get.side_effect = [
            Mock(status_code=200, json=Mock(return_value=mock_issues_page1)),
            Mock(status_code=200, json=Mock(return_value=mock_issues_page2)),
        ]

        # Call the method
        result, error = GsmbManagmentService.monthly_mining_license_count("fake-token")

        # Assertions
        assert error is None
        assert result is not None
        
        # Find January and February in results
        jan = next((item for item in result if item["month"] == "Jan"), None)
        feb = next((item for item in result if item["month"] == "Feb"), None)
        
        # Verify counts
        assert jan["miningLicense"] == 2  # Two licenses in January
        assert feb["miningLicense"] == 1  # One license in February
        
        # Verify other months are 0
        for month_data in result:
            if month_data["month"] not in ["Jan", "Feb"]:
                assert month_data["miningLicense"] == 0