import folium
import webbrowser
import os
import math
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# Dummy coordinates for example (Replace with actual geocoding API if needed)
coordinates = {
    "Amberpet": (17.3665, 78.5626),
    "LB Nagar": (17.3683, 78.5243),
    "Anmagal Hayathnagar": (17.3753, 78.5481),
    "Madhapur": (17.4504, 78.3886),
    "Kukatpally": (17.4849, 78.4138),
    "Secunderabad": (17.4399, 78.4983),
    "Dilsukh Nagar": (17.3699, 78.5314)
}

# Ensure at least 3 locations are entered
while True:
    locations_input = input("Enter at least 3 waste collection areas (comma-separated): ")
    location_names = [name.strip() for name in locations_input.split(",") if name.strip()]
    if len(location_names) >= 3:
        break
    else:
        print("❌ Please enter at least 3 locations!")

# Convert user input into coordinates (defaulting to a central location if not found)
locations = {name: coordinates.get(name, (17.3700, 78.5400)) for name in location_names}

# Convert locations to lists for easy indexing
places_list = list(locations.keys())
coords_list = list(locations.values())

# Haversine function to compute distance (in kilometers) between two points
def haversine_distance(coord1, coord2):
    R = 6371  # Earth's radius in kilometers
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Build the distance matrix (in meters)
n = len(coords_list)
distance_matrix = []
for i in range(n):
    row = []
    for j in range(n):
        if i == j:
            row.append(0)
        else:
            # Convert kilometers to meters and cast to integer
            row.append(int(haversine_distance(coords_list[i], coords_list[j]) * 1000))
    distance_matrix.append(row)

# Create the data model for OR-Tools
def create_data_model():
    data = {}
    data['distance_matrix'] = distance_matrix  # cost between locations
    data['num_vehicles'] = 1                   # single truck for now
    data['depot'] = 0                          # starting location index (first in the list)
    return data

data_model = create_data_model()

# Create the routing index manager and model (CSP formulation)
manager = pywrapcp.RoutingIndexManager(len(data_model['distance_matrix']),
                                       data_model['num_vehicles'],
                                       data_model['depot'])
routing = pywrapcp.RoutingModel(manager)

# Define the distance callback (used as cost function)
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data_model['distance_matrix'][from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Set search parameters for the CSP solver
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

# Solve the problem using CSP (constraint programming)
solution = routing.SolveWithParameters(search_parameters)

def get_route(manager, routing, solution):
    """Extracts the route from the solution."""
    index = routing.Start(0)
    route_order = []
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        route_order.append(node)
        index = solution.Value(routing.NextVar(index))
    # Optionally, add the depot to complete the cycle
    route_order.append(manager.IndexToNode(index))
    return route_order

if solution:
    route_order = get_route(manager, routing, solution)
    # Remove the final depot repetition for mapping (if desired)
    if route_order[0] == route_order[-1]:
        route_order = route_order[:-1]
    ordered_coords = [coords_list[i] for i in route_order]
    ordered_places = [places_list[i] for i in route_order]
    
    print("Optimal route order:", ordered_places)
else:
    print("No solution found!")
    exit()

# Create a map centered around Hyderabad
map_center = (17.3700, 78.5400)
waste_map = folium.Map(location=map_center, zoom_start=12)

# Set base collection time (starting at 1:00)
collection_hour = 1
collection_minute = 0

# Add markers with dynamic collection times for the optimal route using truck icons
for i, (place, coords) in enumerate(zip(ordered_places, ordered_coords)):
    # Color-code: first stop green, last stop red, intermediate blue
    if i == 0:
        color = "green"
    elif i == len(ordered_coords) - 1:
        color = "red"
    else:
        color = "blue"
    
    collection_time = f"{collection_hour}:{collection_minute:02d}"  # Format time as HH:MM
    
    folium.Marker(
        location=coords,
        popup=f"{place}<br>Collection Time: {collection_time}",
        icon=folium.Icon(color=color, icon="truck", prefix="fa"),  # Truck icon from Font Awesome
    ).add_to(waste_map)
    
    # Increase time by 30 minutes for the next stop
    collection_minute += 30
    if collection_minute >= 60:
        collection_hour += 1
        collection_minute %= 60

# Draw a polyline along the optimal route
folium.PolyLine(ordered_coords, color="green", weight=2.5, opacity=1).add_to(waste_map)

# Save and open the map in the browser
map_filename = "aiproject.html"
waste_map.save(map_filename)
webbrowser.open("file://" + os.path.abspath(map_filename))

print(f"✅ Map has been saved as {map_filename} and opened in your browser.")
