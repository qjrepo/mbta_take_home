import unittest
from unittest.mock import patch, MagicMock
import Questions
import requests

class Test(unittest.TestCase):
    # Test method for successfully retrieving subway routes using a mock response
    @patch('Questions.requests.get')
    def test_get_subway_routes_success(self, mock_get):
        # Mock successful API response
        mock_response = MagicMock()
        # Setting up mock response to return predefined JSON data
        mock_response.json.return_value = {
            "data": [
                {
                    "attributes": {
                        "long_name": "Purple Line",
                    },
                    "id": "Purple",
                    "type": "route"
                },
                {
                    "attributes": {
                        "long_name": "Silver Line",
                    },
                    "id": "Silver",
                    "type": "route"
                },
                {
                    "attributes": {
                        "long_name": "Yellow Line",
                    },
                    "id": "Yellow",
                    "type": "route"
                }
                ],
            }
        # Setting mock status code to 200 to simulate a successful response
        mock_get.status_code = 200
        mock_get.return_value = mock_response
        # Define the expected result to verify the test
        expected_result = ["Purple Line", "Silver Line", "Yellow Line"]
        # Call the actual method and store the result
        result = Questions.get_subway_routes()
        # Assert to check if the actual result matches the expected result
        self.assertEqual(result, expected_result)
    
    # Test method for handling HTTP errors while retrieving subway routes
    @patch('Questions.requests.get')
    def test_get_subway_routes_http_error(self, mock_get):
        # Simulate an HTTP error
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP Error")
        # Test case to check if RuntimeError is raised as expected
        with self.assertRaises(RuntimeError):
            Questions.get_subway_routes()

    #Test method for successfully retrieving stops for each route and identifying routes with the most and least stops
    @patch('Questions.requests.get')
    def test_routes_stops_success(self, mock_get):
        # Setting up mock responses
        mock_get.return_value.json.side_effect = [
        {"data": [{"attributes": {"name": "Stop 1"}}, {"attributes": {"name": "Stop 3"}}]},  # Mock data for first route
        {"data": [{"attributes": {"name": "Stop 2"}}, {"attributes": {"name": "Stop 3"}}]}, # Mock data for second route
        {"data": [{"attributes": {"name": "Stop 2"}}, {"attributes": {"name": "Stop 3"}}, {"attributes": {"name": "Stop 4"}}]}# Mock data for third route
    ]
        mock_get.return_value.status_code = 200

        Questions.route_ids = ["Purple", "Silver", "Yellow"]
        Questions.id_long_name_dict = {"Purple": "Purple Line", "Silver": "Silver Line", "Yellow": "Yellow Line"}

        # Defining expected results for the test
        expected_most_stops = [["Yellow Line", 3]]
        expected_least_stops = [["Purple Line", 2], ["Silver Line", 2]]
        # Call the actual method and store the results
        most_stops, least_stops = Questions.routes_stops()
        # Check if results equals expected results
        self.assertEqual(most_stops, expected_most_stops)
        self.assertEqual(least_stops, expected_least_stops)

    #Test method for handling HTTP errors while retrieving routes and stops
    @patch('Questions.requests.get')
    def test_routes_stops_http_error(self, mock_get):
        Questions.route_ids = ["Purple", "Silver", "Yellow"] 

        # Simulate an HTTP error for the requests
        mock_get.side_effect = requests.exceptions.HTTPError()
        # Check if RuntimeError is raised as expected
        with self.assertRaises(RuntimeError):
            Questions.routes_stops()

    def test_stops_with_more_than_one_route(self):
        # Setting up test data
        Questions.route_stops = {"Purple": ["Stop 1", "Stop 3"], "Silver": ["Stop 2", "Stop 3"],"Yellow": ["Stop 2", "Stop 3", "Stop 4"]}
        Questions.id_long_name_dict = {"Purple": "Purple Line", "Silver": "Silver Line", "Yellow": "Yellow Line"}

        # Defining the expected result
        expected_result = {"Stop 3": ["Purple Line", "Silver Line", "Yellow Line"],
                           "Stop 2": ["Silver Line", "Yellow Line"]
                        }
        # Call the actual method and store the result
        result = Questions.stops_with_more_than_one_route()
        # Check if result equals expected result
        self.assertEqual(result, expected_result)

    def test_find_a_route_between_two_stops(self):
        # Setting up the test data
        Questions.stop_routes = {"Stop 1": ["Purple"], "Stop 2": ["Silver", "Yellow"], "Stop 3": ["Purple", "Silver", "Yellow"], "Stop 4": ["Yellow"]}
        Questions.route_stops = {"Purple": ["Stop 1", "Stop 3"], "Silver": ["Stop 2", "Stop 3"],"Yellow": ["Stop 2", "Stop 3", "Stop 4"]}
        Questions.id_long_name_dict = {"Purple": "Purple Line", "Silver": "Silver Line", "Yellow": "Yellow Line"}

        # Defining expected routes
        expected_route_1= ["Purple Line", "Yellow Line"]
        expected_route_2= ["Purple Line", "Silver Line"]

        # Call the actual method and store the result
        result = Questions.find_a_route_between_two_stops("Stop 1", "Stop 2")
        # Assertion to check if result equals to either of the expected routes
        self.assertTrue(result == expected_route_1 or result == expected_route_2)

        # Test for same start and end stops
        # result = Questions.find_a_route_between_two_stops("Stop 1", "Stop 1")
        # self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
