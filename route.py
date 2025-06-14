import pandas as pd
import requests
import time
# Inserting API key for ORS
ORS_API_KEY = "-------------Private_data----------------------"
# Inserting latitude longitude Data for mines, processing plants, Norway ports, German Ports and
Companies
norway_mines = [ 
{"name": "NM0", "lat": 68.749141, "lon": 15.308953},
{"name": "NM1", "lat": 69.4416021, "lon": 17.3246456},
{"name": "NM2", "lat": 66.738289, "lon": 13.588947},
{"name": "NM3", "lat": 58.41667, "lon": 6.55},
{"name": "NM4", "lat": 59.6441014, "lon": 9.574412},
{"name": "NM5", "lat": 60.182578, "lon": 5.477146},
{"name": "NM6", "lat": 68.753699, "lon": 15.206967} ]
#NMn names of norway mmines
norway_processing_plants = [ 
{"name": "NPP0", "lat": 59.921156, "lon": 10.671268},
{"name": "NPP1", "lat": 58.5003035, "lon": 8.8012461},
{"name": "NPP2", "lat": 63.0139393, "lon": 7.1086872},
{"name": "NPP3", "lat": 58.1265168, "lon": 7.9625812} ]
#NPPn names of norway processing plants
norway_ports = [ 
{"name": "NP0", "lat": 69.628354, "lon": 18.950019},
{"name": "NP1", "lat": 59.906775, "lon": 10.7301858},
{"name": "NP2", "lat": 60.7923295, "lon": 5.0563414},
{"name": "NP3", "lat": 60.401401, "lon": 5.3030389},
{"name": "NP4", "lat": 59.352118, "lon": 5.284662},
{"name": "NP5", "lat": 68.413457, "lon": 17.418876},
{"name": "NP6", "lat": 59.920105, "lon": 10.691098},
{"name": "NP7", "lat": 58.972094, "lon": 5.726945} ]
#NPn names of Norway Port
germany_ports = [ 
{"name": "GP1", "lat": 54.328177, "lon": 10.144998},
{"name": "GP2", "lat": 53.901198, "lon": 11.459634},
{"name": "GP3", "lat": 54.149366, "lon": 12.099209},
{"name": "GP4", "lat": 53.542035, "lon": 9.965300},
{"name": "GP5", "lat": 53.513406, "lon": 8.115549},
{"name": "GP6", "lat": 53.344505, "lon": 7.207409} ]
#GPn Names of German Ports
germany_companies = 
[ {"name": "GC0", "lat": 51.074572, "lon": 6.798028},
{"name": "GC1", "lat": 52.390747, "lon": 13.791035},
{"name": "GC2, "lat": 51.411052, "lon": 12.448194},
{"name": "GC3", "lat": 50.668283, "lon": 7.182067},
{"name": "GC4", "lat": 48.972826, "lon": 10.077863},
{"name": "GC5", "lat": 50.052209, "lon": 8.985948},
{"name": "GC6", "lat": 48.520129, "lon": 9.088619},
{"name": "GC7", "lat": 48.058537, "lon": 8.564512},
{"name": "GC8", "lat": 51.883984, "lon": 12.563810} ]
#GCn names of German companies
# Data frame creation using panda library
mines_df = pd.DataFrame(norway_mines)
plants_df = pd.DataFrame(norway_processing_plants)
norway_ports_df = pd.DataFrame(norway_ports)
germany_ports_df = pd.DataFrame(germany_ports)
germany_companies_df = pd.DataFrame(germany_companies)
# OpenRouteService API endpoint
ORS_API_ENDPOINT = "https://api.openrouteservice.org/v2/directions/driving-car"
# Creating a session to make requests to server
session = requests.Session()
session.headers.update({"Authorization": ORS_API_KEY, "Content-Type": "application/json"})
# Initialize results list
results = []
def calculate_route(from_df, to_df, from_label, to_label):
for from_index, from_row in from_df.iterrows():
for to_index, to_row in to_df.iterrows():
payload = {"coordinates": [ [from_row['lon'], from_row['lat']],
[to_row['lon'], to_row['lat']]]}
try:
response = session.post(ORS_API_ENDPOINT, json=payload)
# Handle rate limit and other potential issues
if response.status_code == 429:
print("Rate limit exceeded, waiting for 60 seconds...")
time.sleep(60)
response = session.post(ORS_API_ENDPOINT, json=payload)
elif response.status_code != 200:
print(f"Request failed with status code {response.status_code}.")
response.raise_for_status()
data = response.json()
# Print response for debugging
print(f"Calculating from {from_row['name']} to {to_row['name']}")
if "routes" in data and data["routes"]:
route = data["routes"][0]
distance_meters = route["summary"]["distance"]
duration_seconds = route["summary"]["duration"]
# Convert distance from meters to kilometers
distance_km = distance_meters / 1000
# Convert duration from seconds to hours
duration_hours = duration_seconds / 3600
results.append({
"from": from_row['name'],
  "from_lat": from_row['lat'], # Latitude of origin
"from_lon": from_row['lon'], # Longitude of origin
"to": to_row['name'],
"to_lat": to_row['lat'], # Latitude of destination
"to_lon": to_row['lon'], # Longitude of destination
"distance_km": distance_km,
"duration_hours": duration_hours})
else: print(f"No routes found from {from_row['name']} to {to_row['name']}.")
except requests.exceptions.RequestException as e:
print(f"Request failed from {from_row['name']} to {to_row['name']}. Error: {e}")
# To prevent hitting the rate limit, add a small delay between requests
time.sleep(2)
# Calculate routes from Norway mines to Norway processing plants
calculate_route(mines_df, plants_df, 'Mine', 'Plant')
# Calculate routes from Norway processing plants to Norway ports
calculate_route(plants_df, norway_ports_df, 'Plant', 'Port')
# Calculate routes from Germany companies to Germany ports
calculate_route(germany_ports_df, germany_companies_df, 'Port', 'Company')
# Convert the results to a DataFrame
results_df = pd.DataFrame(results)
# Saves the results to a CSV file
csv_filename = 'routes_results_with_coordinates.csv'
results_df.to_csv(csv_filename, index=False)
# Print the results
print(results_df)
# Close the session
session.close()
