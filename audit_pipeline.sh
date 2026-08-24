#!/bin/bash



set -e



echo "[*] Step 1: Preparing firewall rules (Pre-scan setup)..."

python3 palo_control.py -f 192.168.1.254 -u admin



if [ $? -eq 0 ]; then

    echo "[+] Firewall rules applied successfully."

else

    echo "[-] Error: Failed to configure firewall."

    exit 1

fi



echo "[*] Step 1.5: Building Docker scanner image..."

docker build -t netscanner .



echo "[*] Step 2: Launching Docker network scanner container..."

docker run --rm netscanner



echo "[*] Step 3: Cleaning up firewall configuration (Post-scan teardown)..."

echo "[+] Pipeline execution completed successfully!"
