import requests

url = "https://api.coingecko.com/api/v3/coins/markets"
params = {"vs_currency": "inr", "order": "market_cap_desc", "per_page": "100", "page": "1", "sparkline": "false"}
response = requests.get(url,params=params)
data = response.json()
print(data)
for coin in data:
    print(coin['name'])