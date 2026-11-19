import os
import json
import requests
from dotenv import load_dotenv

requests.packages.urllib3.disable_warnings()
load_dotenv()
BASE_URL = f"https://{os.getenv('OPNSENSE_HOST')}/api"
AUTH = (os.getenv("OPNSENSE_KEY"), os.getenv("OPNSENSE_SECRET"))

# ---------------- Parametres du scenario zero-touch ----------------
CONFIG = {
    "dhcp": {
        "interface": "lan",
        "subnet": "192.168.56.0/24",
        "pool": "192.168.56.150-192.168.56.200",
        "gateway": "192.168.56.101",
        "dns": "8.8.8.8,1.1.1.1",
    },
    "nat": {
        "description": "TP7 - port forward 8080",
        "interface": "wan",
        "protocol": "TCP",
        "dest_port": "8080",
        "target_ip": "192.168.56.10",
        "target_port": "8080",
    },
}
# --------------------------------------------------------------------


def api(method, path, payload=None):
    resp = requests.request(
        method, f"{BASE_URL}{path}", json=payload,
        auth=AUTH, verify=False, timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def ensure_dhcp(cfg):
    api("POST", "/kea/dhcpv4/set", {
        "dhcpv4": {"general": {"enabled": "1", "interfaces": cfg["interface"]}}
    })
    rows = api("GET", "/kea/dhcpv4/search_subnet").get("rows", [])
    if any(row.get("subnet") == cfg["subnet"] for row in rows):
        print(f"[SKIP]   DHCP : subnet {cfg['subnet']} existe deja")
    else:
        res = api("POST", "/kea/dhcpv4/add_subnet", {
            "subnet4": {
                "subnet": cfg["subnet"],
                "pools": cfg["pool"],
                "option_data_autocollect": "0",
                "option_data": {
                    "routers": cfg["gateway"],
                    "domain_name_servers": cfg["dns"],
                },
            }
        })
        if res.get("result") != "saved":
            raise SystemExit(f"Echec creation subnet : {res}")
        print(f"[CREATE] DHCP : subnet {cfg['subnet']} pool {cfg['pool']}")
    api("POST", "/kea/service/reconfigure")
    print("         DHCP : service", api("GET", "/kea/service/status").get("status"))


def ensure_nat(cfg):
    rows = api("GET", "/firewall/d_nat/search_rule").get("rows", [])
    if any(cfg["description"] in json.dumps(row, ensure_ascii=False) for row in rows):
        print(f"[SKIP]   NAT : regle '{cfg['description']}' existe deja")
    else:
        res = api("POST", "/firewall/d_nat/add_rule", {
            "rule": {
                "disabled": "0",
                "interface": cfg["interface"],
                "ipprotocol": "inet",
                "protocol": cfg["protocol"],
                "destination": {"network": "(self)", "port": cfg["dest_port"]},
                "target": cfg["target_ip"],
                "local-port": cfg["target_port"],
                "descr": cfg["description"],
                "description": cfg["description"],
            }
        })
        if res.get("result") != "saved":
            raise SystemExit(f"Echec creation regle NAT : {res}")
        print(f"[CREATE] NAT : regle '{cfg['description']}'")
    api("POST", "/firewall/filter/apply")
    print("         NAT : configuration appliquee")


def main():
    try:
        ensure_dhcp(CONFIG["dhcp"])
        ensure_nat(CONFIG["nat"])
    except requests.exceptions.HTTPError as e:
        raise SystemExit(f"Erreur HTTP : {e}")
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"Erreur reseau : {type(e).__name__}")
    print("Provisioning termine.")


if __name__ == "__main__":
    main()
