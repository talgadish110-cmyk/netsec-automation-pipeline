import requests

# Target URL pointing to our local Nginx container
TARGET_URL = "http://localhost:8080"

def inspect_server():
    print(f"[*] Starting reconnaissance on target: {TARGET_URL}")
    
    try:
        # Sending an HTTP GET request to the target
        response = requests.get(TARGET_URL)
        
        # Inspecting server response details
        print(f"[+] Status Code: {response.status_code}")
        print(f"[+] Server Header: {response.headers.get('Server', 'Not Found')}")
        
        if response.status_code == 200:
            print("[+] Target is ACTIVE and responding!")
        else:
            print("[-] Target responded with an unexpected status code.")
            
    except requests.exceptions.ConnectionError:
        print("[-] Error: Could not connect to the target server.")

if __name__ == "__main__":
    inspect_server()
