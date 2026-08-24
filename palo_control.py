import requests

import urllib3

import getpass

import argparse

import time

import xml.etree.ElementTree as ET



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)





def generate_api_key(firewall_ip, user, password):

    keygen_url = f"https://{firewall_ip}/api/"

    params = {

        "type": "keygen",

        "user": user,

        "password": password

    }

    response = requests.get(keygen_url, params=params, verify=False, timeout=10)



    if "success" not in response.text:

        print(f"[-] Authentication Failed: {response.text}")

        return None



    root = ET.fromstring(response.text)

    key_el = root.find(".//key")

    return key_el.text if key_el is not None else None





def create_address_object(firewall_ip, api_key, name, ip_address):

    """

    Create an address object and commit the changes to apply them on the firewall.

    """

    xpath = (

          "/config/devices/entry[@name='localhost.localdomain']"
        "/vsys/entry[@name='vsys1']/address/entry[@name='" + name + "']"
    )
    element = f"<ip-netmask>{ip_address}</ip-netmask><description>Created via Python Automation</description>"

    url = f"https://{firewall_ip}/api/"
    params = {
        "type": "config",
        "action": "set",
        "xpath": xpath,
        "element": element,
        "key": api_key
    }
    response = requests.post(url, params=params, verify=False, timeout=10)

    if response.status_code == 200 and 'status="success"' in response.text:
        print(f"[+] Address Object '{name}' created successfully in candidate config.")
        commit_and_wait(firewall_ip, api_key)
    else:
        print(f"[-] Operation failed: {response.text}")

def commit_and_wait(firewall_ip, api_key, poll_interval=3, timeout=120):
    """
    Trigger a commit and poll the job status until it finishes,
    since PAN-OS commits are asynchronous and return a job ID immediately.
    """
    url = f"https://{firewall_ip}/api/"
    commit_params = {
        "type": "commit",
        "cmd": "<commit></commit>",
        "key": api_key
    }
    commit_res = requests.post(url, params=commit_params, verify=False, timeout=10)

    if 'status="success"' not in commit_res.text:
        print(f"[-] Commit request failed: {commit_res.text}")
        return

    root = ET.fromstring(commit_res.text)
    job_el = root.find(".//job")
    if job_el is None:
        print("[-] Could not find job ID in commit response.")
        return

    job_id = job_el.text
    print(f"[*] Commit started (job ID: {job_id}). Waiting for it to finish...")

    elapsed = 0
    while elapsed < timeout:
        status_params = {
            "type": "op",
              "cmd": f"<show><jobs><id>{job_id}</id></jobs></show>",
            "key": api_key
        }
        status_res = requests.get(url, params=status_params, verify=False, timeout=10)
        status_root = ET.fromstring(status_res.text)
        status = status_root.find(".//job/status")

        if status is not None and status.text == "FIN":
            result = status_root.find(".//job/result")
            if result is not None and result.text == "OK":
                print("[+] Configuration successfully COMMITTED to the firewall!")
            else:
                print("[-] Commit finished but did not report success. Check the firewall's job log.")
            return

        time.sleep(poll_interval)
        elapsed += poll_interval

    print("[-] Timed out waiting for commit to finish. Check the job status manually on the firewall.")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a PAN-OS address object via the REST/XML API")
    parser.add_argument("-f", "--firewall", required=True, help="Firewall management IP or hostname")
    parser.add_argument("-u", "--user", required=True, help="Admin username")
    parser.add_argument("-n", "--name", default="Test_Server_Python", help="Address object name")
    parser.add_argument("-i", "--ip", default="10.0.0.5", help="IP address for the address object")
    args = parser.parse_args()

    admin_password = getpass.getpass(prompt="Firewall admin password: ")

    token = generate_api_key(args.firewall, args.user, admin_password)
    if token:
        create_address_object(args.firewall, token, args.name, args.ip)
