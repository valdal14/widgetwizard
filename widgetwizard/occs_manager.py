import requests
from requests.exceptions import HTTPError


class OracleCommerceCloudManager:
    server_endpoint = ""
    username = ""
    password = ""
    pass_code = ""
    token = ""
    token_upload = ""

    def __init__(self, server, username, password, pass_code):
        """
        Init method
        :param server: string
        :param username: string
        :param password: string
        :param pass_code: string
        """
        self.server_endpoint = server
        self.username = username
        self.password = password
        self.pass_code = pass_code

    def get_token(self):
        """
        Get the Oracle Commerce Cloud Token
        :return: boolean
        """
        endpoint_login = "{}/ccadmin/v1/mfalogin?".format(self.server_endpoint)
        authentication_str = "grant_type=password&username={}&password={}&totp_code={}".format(self.username,
                                                                                               self.password,
                                                                                               self.pass_code)
        endpoint = endpoint_login + authentication_str
        headers = {"Content-type": "application/x-www-form-urlencoded"}

        try:
            r = requests.post(endpoint, headers=headers)
            if r.status_code == 200:
                data = r.json()
                self.token = data["access_token"]
                return True
            else:
                return False
        except HTTPError:
            return False

    def start_file_upload(self):
        """
        Start the file upload process in Oracle Commerce Cloud
        :return: boolean
        """
        endpoint_start_upload = "{}/ccadmin/v1/files".format(self.server_endpoint)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + self.token
        }
        data = {
            "filename": "extensions/archive.zip",
            "segments": 1
        }

        try:
            r = requests.put(endpoint_start_upload, headers=headers, json=data)
            if r.status_code == 200:
                data = r.json()
                self.token_upload = data["token"]
                return True
            else:
                return False
        except HTTPError:
            return False

    def do_file_segment_upload(self, base_64_str):
        """
        Upload the current file
        :return: boolean
        """
        endpoint_start_upload = "{}/ccadmin/v1/files/{}".format(self.server_endpoint, self.token_upload)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + self.token
        }
        data = {
            "filename": "extensions/archive.zip",
            "file": base_64_str,
            "index": 0,
            "token": self.token_upload
        }

        try:
            r = requests.post(endpoint_start_upload, headers=headers, json=data)
            if r.status_code == 200:
                data = r.json()
                if data["success"]:
                    return True
                else:
                    return False
            else:
                return False
        except HTTPError:
            return False

    def create_extension(self):
        """
        Create the previously saved extension in Oracle Commerce Cloud
        :return: boolean
        """
        endpoint_start_upload = "{}/ccadmin/v1/extensions".format(self.server_endpoint)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + self.token
        }
        data = {"name": "archive.zip"}

        try:
            r = requests.post(endpoint_start_upload, headers=headers, json=data)
            if r.status_code == 200:
                data = r.json()
                if data["success"]:
                    return True
                else:
                    return False
            else:
                return False
        except HTTPError:
            return False
