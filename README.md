This project provides an optimal waste collection route for selected locations in Hyderabad using Google OR-Tools. The computed route is displayed on an interactive map using Folium, with estimated collection times and clear route visualization.

Overview
The system:

Accepts at least three waste collection locations from the user.

Calculates pairwise distances using the Haversine formula.

Optimizes the route using Google OR-Tools to minimize total travel distance.

Displays the route and collection sequence on an interactive HTML map.

Features
User-defined waste pickup areas.

Optimal route generation using constraint programming.

Dynamic map generation with:

Location markers (start, intermediate, end).

Estimated collection times at each stop.

Connected route path.

Technologies Used
Python

Folium for map visualization

Google OR-Tools for route optimization

Haversine formula for geographic distance calculation

How to Run
1)Install required libraries:

2) pip install folium ortools
Run the Python script:


3) python Optimal Trash Collection Map.py
Enter at least three valid location names when prompted:


Amberpet, LB Nagar, Madhapur, Kukatpally, Secunderabad, Dilsukh Nagar, Anmagal Hayathnagar (or u can try any area from hyderabad)
The application will open a map in your default browser showing the optimized route.

Output
A file named aiproject.html is generated.

The map displays:

All locations in the order of visit.

Color-coded markers for start (green), intermediate (blue), and end (red).

Estimated collection times (starting at 1:00, with 30-minute intervals).
