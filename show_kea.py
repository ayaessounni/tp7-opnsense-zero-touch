import os
import json
import requests
from dotenv import load_dotenv

requests.packages.urllib3.disable_warnings()
load_dotenv()
BASE_URL = f"https://{os.getenv('OPNSENSE_HOST')}/api"
AUTH = (os.getenv("OPNSENSE_KEY"), os.getenv("OPNSENSE_SECRET"))


def get(path):
    r = requests.get(f"{BASE_URL}{path}", auth=AUTH, verify=False, timeout=30)
    r.raise_for_status()
    return r.json()


kea = get("/kea/dhcpv4/get")
general = kea["dhcpv4"]["general"]
print("enabled     :", general.get("enabled"))
print("interfaces  :", [k for k, v in general.get("interfaces", {}).items() if v.get("selected")])
print("subnets     :", json.dumps(get("/kea/dhcpv4/search_subnet"), indent=2)[:1500])
print("service     :", get("/kea/service/status"))
print("dnat rules  :", get("/firewall/d_nat/search_rule").get("rowCount"))
