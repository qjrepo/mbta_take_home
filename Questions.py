import requests
import collections
import os

# api_key = os.environ.get('API_KEY_MBTA')

#Question 1:
'''
I choose the second option, rely on the server API to filter before the results are received.

Because of the following reasons:

1. The question asks for data on subway routes (types 0 and 1), which is very specific. 
Therefore, utilizing the API's filtering capabilities to directly obtain the data is more efficient 
than sifting through a larger dataset. This approach saves time and avoids unnecessary data processing.

2. The data for routes of types 0 and 1 can be acquired with a single API call. 
I don't foresee a need for the entire dataset later, so downloading and locally saving the entire 
dataset to prevent redundant API calls for the same data is unnecessary. 
Thus, in this case, filtering the data before receiving it saves resources 
and prevents unnecessary data transfer and data storage.
'''
# List of routes ids, for the use of question 2
route_ids = []

# Dictionary of routes ids and their corresponding names for the use of question 2 and 3
id_long_name_dict = {}

def get_subway_routes():
    # Initialize an empty list to store the long names of the subway routes
    routes_list = []
    # Set up HTTP headers with Accept(content type that the client expects to receive) and Authorization for API access
    headers = {
        'Accept': 'application/json',
        # 'Authorization': f'Bearer {api_key}'
    }
    try:
        # Send a GET request to the MBTA API to retrieve subway routes data
        r = requests.get('https://api-v3.mbta.com/routes?filter[type]=0,1', headers = headers)
    except requests.exceptions.RequestException as e:
        # Raise an error if the API request fails
        raise RuntimeError("Error occured when fetching data: " + str(e))
    
    # Parse the JSON response from the API
    data = r.json()
    # Extract the 'data' field from the JSON, which contains the routes details
    routes = data.get("data")
    # Loop through each route in the data
    for route in routes:
        route_long_name = route.get("attributes").get("long_name")
        routes_list.append(route_long_name)
        # Extract the route ID
        route_id = route.get('id')
        # Append the route ID to the global route_ids list
        route_ids.append(route_id)
        # Map the route ID to its long name in the global dictionary
        id_long_name_dict[route_id] = route_long_name
    return routes_list

#Question 2:
#Dictionary to store routes and their corresponding stops
route_stops = collections.defaultdict(list)
def routes_stops():
    """
    Calculate the number of stops for each route and identifies routes with the most and least stops.
    This function returns two lists: one for routes with the most stops and another for routes with the least stops.
    and also updates the global 'route_stops' dictionary with a list of stops for each route.
    """
    # List of tuples containing routes and their respective number of stops
    route_num_stops = []
    # Variables to track the maximum and minimum number of stops
    max_stops = 0
    min_stops = float('inf')

    # Iterate through each route ID
    for r_id in route_ids:
        try:
            # Set up HTTP headers with Accept(content type that the client expects to receive) and Authorization for API access
            headers = {
                'Accept': 'application/json',
                # 'Authorization': f'Bearer {api_key}'
            }
            # Get stops data for each route from the API
            r_stops = requests.get('https://api-v3.mbta.com/stops?filter[route]='+ r_id, headers = headers)
        except requests.exceptions.RequestException as e:
            # Raise an error if the API request fails
            raise RuntimeError("Error fetching data: " + str(e))
        
        # Parse the JSON response to get stops data
        data = r_stops.json()
        stops = data.get("data")
        num_of_stops = len(stops)
        # Add the route ID and number of stops to the list
        route_num_stops.append((r_id, num_of_stops))
        # Update max and min stop counts
        max_stops = max(max_stops, num_of_stops)
        min_stops = min(min_stops, num_of_stops)

        #List to store the names of all stops on the route
        route_list_of_stops= []
        for stop in stops:
            route_list_of_stops.append(stop.get("attributes").get("name"))
        route_stops[r_id] = route_list_of_stops
    
    # Lists to store routes with the most and least number of stops
    routes_with_most_stops = []
    routes_with_least_stops = []

    # Determine which routes have the most and least stops
    for r, n in route_num_stops:
        route_long_name = id_long_name_dict[r]
        if n == max_stops:
            routes_with_most_stops.append([route_long_name,n])
        elif n == min_stops:
            routes_with_least_stops.append([route_long_name,n])

    return routes_with_most_stops, routes_with_least_stops

#Dictionary to store stops and their corresponding routes
stop_routes = collections.defaultdict(list)
def stops_with_more_than_one_route():
    """
    Identifies stops that connect two or more subway routes
    Returns a dictionary where each key is a stop that has multiple routes, 
    and the value is a list of those routes names.
    """
    #Populate stop_routes with routes for each stop
    for route, stops in route_stops.items():
        for s in stops:
            if route not in stop_routes[s]:
                stop_routes[s].append(route)

    #Dictionary to store stops with 2 or more routes
    res = collections.defaultdict(list)
    # Iterate through each stop and its routes
    for s, r in stop_routes.items():
        # Check if a stop has 2 or more routes
        if len(r) >= 2:
            # Append route long names to the result dictionary
            for x in r:
                res[s].append(id_long_name_dict[x])
    return res

#Question 3
def find_a_route_between_two_stops(start, end):
    """
    Finds a route between two stops using breadth-first search algorithm.

    Inputs:
    start: The starting stop
    end: The destination stop

    Returns:
    A rail route (list of route long names) that connects the start and end stops. 
    If no rail route is found, returns an empty list.
    """

    # Check if either start or end stop is not in the stop_routes dictionary just in case
    if start not in stop_routes or end not in stop_routes:
        print("No route found")
        return []
    # Check if start and end stops are the same
    if start == end:
        print("Start and end stops are the same. No need to take any rail routes")
        return []
    # Initialize a graph to represent connections between stops
    graph = collections.defaultdict(list)
    for stop, routes in stop_routes.items():
        for r in routes:
            # For each route, add an edge for each stop connected by this route
            for s in route_stops[r]:
                if s != stop:
                    # Append a tuple of connected stop and the route to the graph
                    graph[stop].append((s,r))

    # Initialize a queue for breadth-first search and a set for visited stops
    queue = collections.deque()
    # A set to keep track of visited stops to avoid revisiting them
    visited = set()

    # This list will store (stop, route) pairs taken so far, initialized as empty
    path = []

    stop_route= (start, "")
    # Add the starting stop to the queue and visited set
    queue.append((stop_route, path))
    visited.add((start, ""))

    #This list will store the final (stop, route) pairs that can be taken to get to the destination from the start
    path_with_stop_names = []
    while queue:
        curr_stop_route, path = queue.popleft()
        curr_stop = curr_stop_route[0]
        # If the current stop is the destination, end the search
        if curr_stop == end:
            path_with_stop_names = path
            break
        # Visit all connected stops
        for next_stop_route in graph[curr_stop]:
            if next_stop_route not in visited:
                # Add the connected stop to the visited set and queue
                visited.add(next_stop_route)
                # Append the next stop to the current path and enqueue it
                queue.append((next_stop_route, path + [next_stop_route]))

    routes = []
    # Convert the route short names to long names using 'id_long_name_dict'
    for s, r in path_with_stop_names:
        r_long_name = id_long_name_dict[r]
        routes.append(r_long_name)
    # print(path_with_stop_names)
    return routes

if __name__ == "__main__":
    print("Question 1:")
    # Calling the function to get a list of subway route long names
    route_long_names = get_subway_routes()
    # Displaying the list of subway routes
    print("Subway Routes long names:\n" + "\n".join(route_long_names))
    print("\n")

    print("Question 2:")
    # Calling the function to get routes with the most and least stops
    routes_with_most_stops, routes_with_least_stops = routes_stops()

    # Displaying the routes with the most stops
    print("Routes with most stops are as follows:")
    for r, s in routes_with_most_stops:
        print('Route Name: ' + r + ',' +' Number of stops: ' + str(s))
    print("\n")

    # Displaying the routes with the least stops
    print("Routes with least stops are as follows:")
    for r, s in routes_with_least_stops:
        print('Route Name: ' + r + ',' +' Number of stops: ' + str(s))
    print("\n")

    # Calling the function to find stops that connect two or more subway routes
    stops_multiple_routes = stops_with_more_than_one_route()
    # Displaying the stops that connect two or more subway routes
    print("Stops with more than one route along with the routes names:")
    print("\n".join("{}:\t{}".format(k, v) for k, v in stops_multiple_routes.items()))
    print("\n")

    print("Question 3:")
    # Getting user input for the start and end stops
    start = input("Please enter the name of the stop you are traveling from: ")
    end = input("Please enter the name of the stop you are traveling to: ")
    # Calling the function to find a route between the two stops
    route = find_a_route_between_two_stops(start, end)
    # Displaying a rail route between the provided stops
    print("A rail route you can take to travel from " + start+ " to " + end + " is: "+ ",".join(route))