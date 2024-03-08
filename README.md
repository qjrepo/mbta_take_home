# This program is for interacting with MBTA Web API

# Installation
1. `git clone https://github.com/qjrepo/mbta_take_home.git`
2. `cd mbta_take_home`
1. Ensure Python3 is installed
2. Install the necessary packages using pip3: `pip3 install -r requirements.txt`

# Usage
All the code for interacting with the MBTA Web API is located in `Questions.py`
Command to run Questions.py: `python3 Questions.py`

- **The program will display the following:**:
- **Question 1**: Displays a list of subway routes long names.
- **Question 2**: Shows the routes with the most and least stops, their number of stops, and a list of stops connecting two or more subway routes, along with the relevant route names for each of these stops.
- **Question 3**: After inputting the start and end stops, displays a rail route connecting the two stops.

# Testing
- `Test.py` file contains tests for the functions in `Questions.py`
- To run the tests, execute command: `python3 Test.py`
