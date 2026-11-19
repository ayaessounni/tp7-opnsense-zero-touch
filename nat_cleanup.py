import os
import json
import requests
from dotenv import load_dotenv

requests.packages.urllib3.disable_warnings()
load_dotenv()
BASE_URL = f"https://{os.getenv('OPNSENSE_HOST')}/api"
AUTH = (os.getenv("OPNSENSE_KEY"), os.getenv("OPNSENSE_SECRET"))
DESCRIPTION = "TP7 - port forward 8080"

r = requests.get(f"{BASE_URL}/firewall/d_nat/search_rule", auth=AUTH, verify=False, timeout=30)
r.raise_for_status()
rows = r.json().get("rows", [])
print("Champs d'une ligne :", sorted(rows[0].keys()) if rows else "aucune regle")

matches = [row for row in rows if DESCRIPTION in json.dumps(row, ensure_ascii=False)]
print(len(matches), "regle(s) trouvee(s)")

for row in matches[1:]:
    uuid = row["uuid"]
    d = requests.post(f"{BASE_URL}/firewall/d_nat/del_rule/{uuid}", auth=AUTH, verify=False, timeout=30)
    d.raise_for_status()
    print("supprimee :", uuid, d.json())

a = requests.post(f"{BASE_URL}/firewall/filter/apply", auth=AUTH, verify=False, timeout=60)
print("apply :", a.json())
