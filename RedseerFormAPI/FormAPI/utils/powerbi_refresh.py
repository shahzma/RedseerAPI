import datetime
import requests
import ast
import json


class PowerbiRefresh:
    def test(self, report_name):
        try:
            workspace_id = "5323522b-f0c6-4c0f-a8d3-76347bcadd5b"

            ### 1) Getting Access Token

            url = "https://login.microsoftonline.com/common/oauth2/token"
            data = {"grant_type":"password", 
                    "username":"digital@beeroute.onmicrosoft.com", 
                    "password":"Redseer@123", 
                "client_id":"48ac3ed4-da07-47b6-be7f-a606360f5b7f",
                "client_secret":"jMB8Q~EO1lS7Ix2nHfbP7i2Aw-hUMX0Ogdvw6btk",
                "resource":"https://analysis.windows.net/powerbi/api"}

            login_output = requests.post(url, data=data)
            login_output = login_output.json()
            access_token = login_output["access_token"]

            ### 2) Getting Datasets Id

            auth_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/"
            auth_output = requests.get(auth_url, headers={'Authorization': f'Bearer {access_token}'})

            report_list = auth_output.json()["value"]

            all_report_name_list = [x["name"] for x in report_list]
            print(all_report_name_list)

            ### 3) Required Report Name

            # required_name_list = ["Content Social Media", "OTT Audio", "OTT Video", "Shortform Video", "Online_Retail",
            #                      "Food Aggregators Beta", "RMG Beta", "Used Cars Beta", "D2C Omni Beta", "Meat Beta","FoodTech Report"]
            required_name_list = [report_name]

            ### 4) Refreshing all required data

            for report in report_list:
                if report["name"] in required_name_list:
                    dataset_id = report["datasetId"]
                    refresh_url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes"
                    response = requests.post(refresh_url, headers={'Authorization': f'Bearer {access_token}'})
                    print(report["name"], response)
        except Exception as e:
            print(
                    f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} PowerbiRefresh:- Error in test:- ', e)
    def prod(self, report_name):
        try:
            workspace_id = "67294232-0c81-43c2-a16d-22544a0a390b"

            ### 1) Getting Access Token
            url = "https://login.microsoftonline.com/common/oauth2/token"
            data = {"grant_type":"password", 
                    "username":"digital@redseerconsulting.com", 
                    "password":"Waj179490", 
                "client_id":"a9826bb1-7b52-4b3f-80f2-2ffa4d1cd578",
                "client_secret":"cuV8Q~hl7__PcjsvYSxTDHraG4vcMMLTRQRtyceA",
                "resource":"https://analysis.windows.net/powerbi/api"}

            login_output = requests.post(url, data=data)
            login_output = login_output.json()
            access_token = login_output["access_token"]

            ### 2) Getting Datasets Id

            auth_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/"
            auth_output = requests.get(auth_url, headers={'Authorization': f'Bearer {access_token}'})

            report_list = auth_output.json()["value"]

            all_report_name_list = [x["name"] for x in report_list]
            print(all_report_name_list)

            ### 3) Required Report Name

            # required_name_list = ["Content Social Media", "OTT Audio", "OTT Video", "Shortform Video", "Online_Retail",
            #                      "Food Aggregators Beta", "RMG Beta", "Used Cars Beta", "D2C Omni Beta", "Meat Beta","FoodTech Report"]
            required_name_list = [report_name]

            ### 4) Refreshing all required data

            for report in report_list:
                if report["name"] in required_name_list:
                    dataset_id = report["datasetId"]
                    refresh_url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes"
                    response = requests.post(refresh_url, headers={'Authorization': f'Bearer {access_token}'})
                    print(report["name"], response)
        except Exception as e:
            print(
                    f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} PowerbiRefresh:- Error in prod:- ', e)