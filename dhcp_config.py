import os
import json
import requests
from dotenv import load_dotenv

requests.packages.urllib3.disable_warnings()
load_dotenv()
BASE_URL = f"https://{os.getenv('OPNSENSE_HOST')}/api"
AUTH = (os.getenv("OPNSENSE_KEY"), os.getenv("OPNSENSE_SECRET"))

# --- Parametres du scenario ---
INTERFACE = "lan"
SUBNET = "192.168.56.0/24"
POOL = "192.168.56.150-192.168.56.200"
GATEWAY = "192.168.56.101"
DNS = "8.8.8.8,1.1.1.1"


def get(path):
    r = requests.get(f"{BASE_URL}{path}", auth=AUTH, verify=False, timeout=30)
    r.raise_for_status()
    return r.json()


def post(path, payload=None):
    r = requests.post(f"{BASE_URL}{path}", json=payload or {}, auth=AUTH, verify=False, timeout=60)
    r.raise_for_status()
    data = r.json()
    print(path, "->", json.dumps(data)[:300])
    return data


# 1) Activer Kea sur l'interface LAN
post("/kea/dhcpv4/set", {
    "dhcpv4": {"general": {"enabled": "1", "interfaces": INTERFACE}}
})

# 2) Creer le subnet s'il n'existe pas deja
rows = get("/kea/dhcpv4/search_subnet").get("rows", [])
if any(row.get("subnet") == SUBNET for row in rows):
    print(f"[SKIP]   subnet {SUBNET} existe deja")
else:
    res = post("/kea/dhcpv4/add_subnet", {
        "subnet4": {
            "subnet": SUBNET,
            "pools": POOL,
            "option_data_autocollect": "0",
            "option_data": {
                "routers": GATEWAY,
                "domain_name_servers": DNS,
            },
        }
    })
    if res.get("result") != "saved":
        raise SystemExit(f"Echec creation subnet : {res}")
    print(f"[CREATE] subnet {SUBNET} pool {POOL}")

# 3) Appliquer
post("/kea/service/reconfigure")
print("Etat du service :", get("/kea/service/status").get("status"))
