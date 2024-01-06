# %%
import json

import requests

base_url = "http://127.0.0.1:5001"

response = requests.get(base_url)

session = requests.Session()
response = session.post(base_url + "/fetch", data=json.dumps({"root_ids": [0, 1, 4]}))
json.loads(response.text)

# %%
from cloudfiles import CloudFiles

out_path = "allen-minnie-phase3/skervice"
cf = CloudFiles("gs://" + out_path)

cf.put("0.json", json.dumps({}))
