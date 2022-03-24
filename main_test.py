from unittest.mock import Mock, MagicMock
from google.cloud import storage
from google.oauth2 import service_account
from flask import escape
from main import create_folder
from methods import search, create_excel, list_items

import os

def test_creation():
    data = {
        "dateArr": [
            "03-04-2022"
        ],
        "techByDate": {
            "03-04-2022": [
                {
                    "JobId": "21-0021",
                    "ReportType": "case-file-technician",
                    "formType": "case-report",
                    "teamMember": {
                        "name": "Test Employee",
                        "email": "test@test.com",
                        "employee_id": "test"
                    },
                    "date": "03-10-2022",
                    "evaluationLogs": [
                        {
                            "label": "Dispatch to Property",
                            "value": "03-10-2022 17:15:00"
                        },
                        {
                            "label": "Start Time",
                            "value": "03-10-2022 17:30:00"
                        },
                        {
                            "label": "End Time",
                            "value": "03-10-2022 23:15:00"
                        },
                        {
                            "label": "Total Time",
                            "value": "-975 minutes"
                        }
                    ]
                }
            ]
        }
    }
    file_name = {'filename': 'timesheet.xlsx'}
    req = Mock(get_json=Mock(return_value=data), args=file_name)
    print(req)
    assert create_excel(req) == req

def test_folder_create():
    data = {
        "folderPath": "jobid",
        "root": True,
        "storageBucket": "code-red-app-313517.appspot.com",
        "delimiter": "/"
    }
    req = Mock(get_json=Mock(return_value=data))
    print(req)
    assert create_folder(req) == req

def test_search():
    list = ["one", "two", "three"]
    search_term = "three"
    assert search(list, search_term)

def test_list_items():
    cred_path = os.path.join(os.getcwd(), 'code-red.json')
    cred = service_account.Credentials.from_service_account_file(cred_path)
    client = storage.Client(credentials=cred)
    prefix = "shinobu/rapid-response"
    assert list_items(client, "code-red-app-313517.appspot.com", prefix, "/")