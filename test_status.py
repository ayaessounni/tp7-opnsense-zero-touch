import os
import requests
from dotenv import load_dotenv

requests.packages.urllib3.disable_warnings()
load_dotenv()
BASE_URL = f"https://{os.getenv('OPNSENSE_HOST')}/api"
AUTH = (os.getenv("OPNSENSE_KEY"), os.getenv("OPNSENSE_SECRET"))

resp = requests.get(f"{BASE_URL}/core/system/status", auth=AUTH, verify=False, timeout=5)
resp.raise_for_status()
print(resp.json())
