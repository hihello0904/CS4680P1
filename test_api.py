import requests
import json

# Test the investment projection API
url = "http://localhost:5000/api/investment-projection"
data = {
    "monthly_contribution_amount": 500,
    "risk_tolerance": "Average",
    "interests": "technology, healthcare, renewable energy"
}

response = requests.post(url, json=data)
print("Status Code:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2))
