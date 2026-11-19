import os
import requests
from dotenv import load_dotenv

requests.packages.urllib3.disable_warnings()
load_dotenv()
BASE_URL = f"https://{os.getenv('OPNSENSE_HOST')}/api"
AUTH = (os.getenv("OPNSENSE_KEY"), os.getenv("OPNSENSE_SECRET"))

ENDPOINTS = [
    "/dhcpv4/settings/get",
    "/dhcpv4/service/status",
    "/kea/dhcpv4/get",
    "/kea/service/status",
    "/firewall/d_nat/search_rule",
    "/firewall/source_nat/search_rule",
]

for ep in ENDPOINTS:
    try:
        r = requests.get(f"{BASE_URL}{ep}", auth=AUTH, verify=False, timeout=30)
        print(r.status_code, ep)
    except requests.exceptions.RequestException as e:
        print("ERREUR", ep, type(e).__name__)
