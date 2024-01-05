#%%
import requests

base_url = "http://127.0.0.1:5001"

response = requests.get(base_url)

response.content