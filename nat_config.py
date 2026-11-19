import os
import json
import requests
from dotenv import load_dotenv

requests.packages.urllib3.disable_warnings()
load_dotenv()
BASE_URL = f"https://{os.getenv('OPNSENSE_HOST')}/api"
AUTH = (os.getenv("OPNSENSE_KEY"), os.getenv("OPNSENSE_SECRET"))

# --- Parametres du scenario ---
DESCRIPTION = "TP7 - port forward 8080"
INTERFACE = "wan"
PROTOCOL = "TCP"
DEST_PORT = "8080"
TARGET_IP = "192.168.56.10"
TARGET_PORT = "8080"


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


# 1) Regle existante ?
rows = get("/firewall/d_nat/search_rule").get("rows", [])
exists = any(DESCRIPTION in json.dumps(row, ensure_ascii=False) for row in rows)

if exists:
    print(f"[SKIP]   regle '{DESCRIPTION}' existe deja")
else:
    res = post("/firewall/d_nat/add_rule", {
        "rule": {
            "disabled": "0",
            "interface": INTERFACE,
            "ipprotocol": "inet",
            "protocol": PROTOCOL,
            "destination": {"network": "(self)", "port": DEST_PORT},
            "target": TARGET_IP,
            "local-port": TARGET_PORT,
            "descr": DESCRIPTION,
            "description": DESCRIPTION,
        }
    })
    if res.get("result") != "saved":
        raise SystemExit(f"Echec creation regle NAT : {res}")
    print(f"[CREATE] regle '{DESCRIPTION}'")

# 2) Appliquer
post("/firewall/filter/apply")

