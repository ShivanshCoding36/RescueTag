import requests

url = "http://127.0.0.1:5050/post_location"  # Change to your server's URL
payload = {"name": "Amb-2", "medicines": "3","latitude": "27.402181616652717", "longitude": "77.05144317678668", "time":"12:31:34"}  # The data to send  , medicines, latitude, longitude, time
headers = {"Content-Type": "application/json"}  # Ensure JSON format

response = requests.post(url, json=payload, headers=headers)

# Print the server's response
print(response.status_code)  # Should be 200 if successful
print(response.json())       # Server's JSON response
