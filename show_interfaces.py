import os
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
print("Interfaces proposees par Kea :")
for name, opt in kea["dhcpv4"]["general"]["interfaces"].items():
    print("  ", repr(name), "->", opt.get("value"))

print()
print("Interfaces d'OPNsense :")
try:
    info = get("/interfaces/overview/interfacesInfo")
    for row in info.get("rows", []):
        print("  ", row.get("identifier"), "|", row.get("device"), "|", row.get("description"), "|", row.get("addr4"))
except Exception as e:
    print("   indisponible :", type(e).__name__)
