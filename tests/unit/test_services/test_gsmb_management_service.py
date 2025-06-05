import pytest
from unittest.mock import patch, Mock
from services.gsmb_managemnt_service import GsmbManagmentService  # replace with actual import path

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
