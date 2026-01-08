import unittest
from unittest.mock import patch, MagicMock
from program_files.api_client import ScheduleAPI
from datetime import datetime, timedelta
import requests  

class TestScheduleAPI(unittest.TestCase):
    def setUp(self):
        self.sample = {
                        "week": {"date_start": "2026.01.05", "date_end": "2026.01.11", "is_odd": True},
            "days": [],
            "group": {
                "id": 40521,
                "name": "5130904/30101",
                "level": 4,
                "type": "common",
                "kind": 0,
                "spec": "",
                "year": 2026,
                "faculty": {
                    "id": 125,
                    "name": "Институт компьютерных наук и кибербезопасности",
                    "abbr": "ИКНК"
                }
            }
        }

    @patch("program_files.api_client.requests.get")
    def test_get_group_info_success(self, mock_get):
        pass

    @patch("program_files.api_client.requests.get")
    def test_get_group_info_fallback(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("oops")
        fb = ScheduleAPI.get_group_info(999)
        self.assertIn("5130904/30101", fb["name"])

    @patch("program_files.api_client.requests.get")
    def test_get_group_schedule_success(self, mock_get):
        pass

    @patch("program_files.api_client.requests.get")
    def test_get_group_schedule_fallback(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("fail")
        fb = ScheduleAPI.get_group_schedule(123)
        self.assertIn("Математика", fb["days"][0]["lessons"][0]["subject"])