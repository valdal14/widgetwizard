from datetime import date
import json
import os
from os import path
import shutil
import base64
import re
import requests
from requests.exceptions import HTTPError
data = None


class OracleCommerceCloudManager:
    occs_endpoint = ""
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
        self.occs_endpoint = server
        self.username = username
        self.password = password
        self.pass_code = pass_code

    def get_token(self):
        """
        Get the Oracle Commerce Cloud Token
        :return: boolean
        """
        endpoint_login = "{}/ccadmin/v1/mfalogin?".format(self.occs_endpoint)
        authentication_str = "grant_type=password&username={}&password={}&totp_code={}".format(self.username,
                                                                                               self.password,
                                                                                               self.pass_code)
        endpoint = endpoint_login + authentication_str
        headers = {"Content-type": "application/x-www-form-urlencoded"}

        try:
            r = requests.post(endpoint, headers=headers)
            if r.status_code == 200:
                d = r.json()
                self.token = d["access_token"]
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
        endpoint_start_upload = "{}/ccadmin/v1/files".format(self.occs_endpoint)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + self.token
        }
        d = {
            "filename": "extensions/archive.zip",
            "segments": 1
        }

        try:
            r = requests.put(endpoint_start_upload, headers=headers, json=d)
            if r.status_code == 200:
                d = r.json()
                self.token_upload = d["token"]
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
        endpoint_start_upload = "{}/ccadmin/v1/files/{}".format(self.occs_endpoint, self.token_upload)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + self.token
        }
        d = {
            "filename": "extensions/archive.zip",
            "file": base_64_str,
            "index": 0,
            "token": self.token_upload
        }

        try:
            r = requests.post(endpoint_start_upload, headers=headers, json=d)
            if r.status_code == 200:
                d = r.json()
                if d["success"]:
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
        endpoint_start_upload = "{}/ccadmin/v1/extensions".format(self.occs_endpoint)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + self.token
        }
        d = {"name": "archive.zip"}

        try:
            r = requests.post(endpoint_start_upload, headers=headers, json=d)
            if r.status_code == 200:
                d = r.json()
                if d["success"]:
                    return True
                else:
                    return False
            else:
                return False
        except HTTPError:
            return False


def welcome_message():
    """
    Prints out the welcome message
    :return:
    """
    json_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(json_file) as json_data_file:
        global data
        data = json.load(json_data_file)
        print(data["art_message"]["message"])
        print(data["welcome_message"]["welcome"])


def set_format_date():
    """
    Returns a string made of formatted date
    :return: string
    """
    today = date.today()

    if len(str(today.month)) == 1:
        month = "0" + str(today.month)
    else:
        month = today.month

    if len(str(today.day)) == 1:
        day = "0" + str(today.day)
    else:
        day = today.day

    return str("{}-{}-{}".format(today.year, month, day))


def set_extension_id():
    """
    Validates and returns the extension id
    :return: string
    """
    ext_id = input("Enter your extension id: ")
    while len(ext_id) < 36:
        print(data["extension"]["message"])
        ext_id = input("Enter your extension id: ")
    return ext_id


def set_developer_id():
    """
    Validates and returns the developer id
    :return: string
    """
    dev_id = input("Enter your developer id: ")
    while True:
        try:
            if len(dev_id) >= 8 and isinstance(int(dev_id), int):
                return dev_id
            else:
                print(data["developer_id"]["message"])
                dev_id = input("Enter your developer id: ")
        except ValueError as error:
            print("There was a problem registering your developer id: {}".format(error))
            print("We have selected a brand new id for you")
            return "123456789"


def set_created_by():
    """
    Validates and returns the developer name
    :return: string
    """
    dev_name = input("Enter the developer name: ")
    while True:
        if len(dev_name) >= 5:
            return dev_name
        else:
            print(data["developer_name"]["message"])
            dev_name = input("Enter your developer name: ")


def set_extension_name():
    """
    Validates and returns the extension name
    :return: string
    """
    ext_name = input("Enter the extension name: ").lower().replace(" ", "")
    while True:
        if len(ext_name) >= 5:
            return ext_name
        else:
            print(data["extension_name"]["message"])
            ext_name = input("Enter the extension name: ")


def set_extension_desc():
    """
    Validates and returns the extension description
    :return: string
    """
    ext_desc = input("Enter the extension description: ")
    while True:
        if len(ext_desc) >= 5:
            return ext_desc
        else:
            print(data["extension_desc"]["message"])
            ext_desc = input("Enter the extension description: ")


def verify_ext_folder(path_destination):
    """
    Verify the extension folder destination path
    :param path_destination: string
    :return: string
    """
    print("Your current path is {}".format(os.getcwd()))
    user_path = input("Do you want to save your extension in this location? ")
    if "y" in user_path or "Y" in user_path:
        if path.isdir(path_destination):
            return path_destination
        else:
            raise IOError(str(data["ext_location"]["message"]))
    else:
        while True:
            new_path = input("Please specify the path in which you want your extension to be saved: ")
            if path.isdir(new_path):
                return new_path
            else:
                print(data["ext_location"]["message"])


def create_ext_folders(path_destination, ext_name):
    """
    Create the main extension folder
    :param path_destination: string
    :param ext_name: string
    :return:
    """
    was_created = False
    dir_name = verify_ext_folder(path_destination)
    try:
        os.mkdir(dir_name + "/" + ext_name)
        os.mkdir(dir_name + "/" + ext_name + "/widget")
        os.mkdir(dir_name + "/" + ext_name + "/widget/" + ext_name)
        os.mkdir(dir_name + "/" + ext_name + "/widget/" + ext_name + "/js")
        os.mkdir(dir_name + "/" + ext_name + "/widget/" + ext_name + "/less")
        os.mkdir(dir_name + "/" + ext_name + "/widget/" + ext_name + "/templates")
        was_created = True
    except OSError as error:
        print("Creation of the directory {} failed with error {}".format(dir_name, error.errno))

    if was_created:
        return dir_name + "/" + ext_name
    else:
        raise IOError("Creation of the directory failed")


def create_ext_json(ext_id, dev_id, dev_name, ext_name, created_date, ext_desc, path_destination):
    """
    Create an ext.json file
    :param ext_id: string
    :param dev_id: string
    :param dev_name: string
    :param ext_name: string
    :param created_date: string
    :param ext_desc: string
    :param path_destination: string
    :return: void
    """
    dictionary_ext_json = {"extensionID": ext_id, "developerID": dev_id, "createdBy": dev_name, "name": ext_name,
                           "version": 1, "timeCreated": created_date, "description": ext_desc}
    with open(path_destination + "/ext.json", "w") as outfile:
        json.dump(dictionary_ext_json, outfile)


def create_widget_json(ext_name, path_destination):
    """
    Create the widget.json file
    :param ext_name: string
    :param path_destination: string
    :return: void
    """
    widget_dic = {
        "name": ext_name,
        "version": 1,
        "global": False,
        "javascript": "widget-js",
        "pageTypes": ["home"],
        "imports": ["product"],
        "jsEditable": True,
        "config": {
        }
    }

    with open(path_destination + '/widget/' + ext_name + "/widget.json", "w") as outfile:
        json.dump(widget_dic, outfile)


def create_html_template(ext_name, path_destination):
    """
    Create the display.template file
    :param ext_name: string
    :param path_destination: string
    :return: void
    """
    with open(path_destination + '/widget/' + ext_name + "/templates/" + "display.template", "w") as outfile:
        outfile.write("<!-- Your HTML code -->")


def create_widget_less(ext_name, path_destination):
    """
    Create the widget.less file
    :param ext_name: string
    :param path_destination: string
    :return: void
    """
    with open(path_destination + '/widget/' + ext_name + "/less/" + "widget.less", "w") as outfile:
        outfile.write("/* Your CSS code */")


def create_js_file(ext_name, path_destination):
    """
    Create the js file
    :param ext_name: string
    :param path_destination: string
    :return: void
    """
    with open(path_destination + '/widget/' + ext_name + "/js/" + "widget-js.js", "w") as outfile:
        outfile.write(data["js_code"]["code"])


def zip_content(ext_name, path_destination):
    """
    Create a zip archive
    :param ext_name: string
    :param path_destination: string
    :return: void
    """
    try:
        shutil.make_archive(path_destination + "/" + "archive", "zip", path_destination)
        if path.isfile(path_destination + "/archive.zip"):
            print("Your '{}' extension was successfully created at location {}\n".format(ext_name, path_destination))
            # convert file into base64 for possible upload
            encoded_file_upload = convert_archive_base64(path_destination + "/archive.zip")
            return encoded_file_upload
        else:
            print("Invalid file, please try again")
    except IOError as error:
        print("There was an error compressing your file: {}".format(error.errno))
        print(error)


def convert_archive_base64(path_destination):
    """
    Convert the zip archive into a base64 encoded string
    :param path_destination: string
    :return: string
    """
    with open(path_destination, "rb") as f:
        archive_bytes = f.read()
        encoded = base64.b64encode(archive_bytes)
    encoded_str = str(encoded)
    return encoded_str[2:-1]


def user_wants_upload():
    """
    Determines whether or not the user wants to upload the extension
    :return: boolean
    """
    choice = input("Do you want to upload your extension right now? :")
    if "y" in choice or "Y" in choice:
        return True
    else:
        return False


def set_user_input_server():
    """
    Set and validate user inputs Oracle Commerce Cloud backend URL
    :return: string
    """
    print("Backend URL format example: https://youroccsistanceurl.com")
    while True:
        server_url = input("Enter your Oracle Commerce Cloud backend URL: ")
        valid_url = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', server_url)
        if len(valid_url) is 1:
            return valid_url[0]


def set_username():
    """
    Set and validate the username
    :return: string
    """
    username = input("Enter your Oracle Commerce Cloud backend username: ")
    while True:
        if len(username) >= 3:
            return username
        else:
            username = input("Enter your Oracle Commerce Cloud backend username: ")


def set_password():
    """
    Set and validate the password
    :return: string
    """
    password = input("Enter your Oracle Commerce Cloud backend password: ")
    while True:
        if len(password) >= 3:
            return password
        else:
            password = input("Enter your Oracle Commerce Cloud backend password: ")


def set_pass_code():
    """
    Set and validate the password
    :return: string
    """
    pass_code = input("Enter your Oracle Commerce Cloud backend pass-code: ")
    while True:
        if len(pass_code) >= 5:
            return pass_code
        else:
            pass_code = input("Enter your Oracle Commerce Cloud backend pass-code: ")


def run_script():
    """
    Executes the application
    :return: void
    """
    welcome_message()
    e_id = set_extension_id()
    d_id = set_developer_id()
    d_name = set_created_by()
    e_name = set_extension_name()
    create_date = set_format_date()
    e_desc = set_extension_desc()

    # create the main ext dir
    destination_path = create_ext_folders(os.getcwd(), e_name)
    # create the ext.json
    create_ext_json(e_id, d_id, d_name, e_name, create_date, e_desc, destination_path)
    # create the widget.json
    create_widget_json(e_name, destination_path)
    # create html template
    create_html_template(e_name, destination_path)
    # create widget.less file
    create_widget_less(e_name, destination_path)
    # create js file
    create_js_file(e_name, destination_path)
    # zip the content and return the base64 string for file upload
    file_upload = zip_content(e_name, destination_path)
    # upload file
    if user_wants_upload():
        ser = set_user_input_server()
        usr = set_username()
        usr_pwd = set_password()
        p_code = set_pass_code()
        print("\n")
        print("Please wait... I am trying to upload your extension :) \n")
        # instance of OracleCommerceCloudManager
        occs_instance = OracleCommerceCloudManager(ser.replace(" ", ""), usr, usr_pwd, p_code)
        # check whether the token was generated
        if occs_instance.get_token():
            # get the new upload token
            if occs_instance.start_file_upload():
                # perform the doFileSegmentUpload call
                if occs_instance.do_file_segment_upload(file_upload):
                    # create the extension
                    if occs_instance.create_extension():
                        print("Extension successfully created, please login into your "
                              "Oracle Commerce Cloud backend instance to verify: {}"
                              "".format(ser + "/occs-admin"))
                        return
                    else:
                        print("There was a problem creating your extension, but you can still upload it manually")
                else:
                    print("There was a problem uploading your file, but you can still do it manually")
            else:
                print("There was a problem uploading your file, but you can still do it manually")
        else:
            print("There was a problem authenticating your user, but you can still manually upload your extension")
    else:
        print("\n")
        print("Thanks for using OCCS Widget Wizard")


def main():
    run_script()


if __name__ == "__main__":
    main()
