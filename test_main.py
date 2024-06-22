import unittest
from unittest.mock import patch, Mock

from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app, get_exchange_rates

client = TestClient(app)


def test_read_rates():
    response = client.get("/rates?base_currency=USD")
    assert response.status_code == 200
    assert "USD" in response.json()


def test_convert():
    response = client.get("/convert?amount=100&from_currency=USD&to_currency=EUR")
    assert response.status_code == 200
    assert "amount" in response.json()


class TestGetExchangeRate(unittest.TestCase):

    response_dict = {"conversion_rates": {"USD": 1, "EUR": 1.2, "GBP": 1.4}}

    def _mock_response_setup(self, status_code : int):
        # Define mock response
        mock_response = Mock()

        # Set up the mock response
        mock_response.json.return_value = self.response_dict
        mock_response.status_code = status_code

        return mock_response

    @patch('main.requests.get')
    def test_conversion_rate_return(self, mock_get):

        mock_response = self._mock_response_setup(status_code = 200)
        mock_get.return_value = mock_response

        # Clear the cache before testing
        get_exchange_rates.cache_clear()

        response = get_exchange_rates('USD')

        self.assertEqual(response, self.response_dict['conversion_rates'])

    @patch("main.requests.get")
    def test_conversion_rate_http_exception(self, mock_get):

        # Define mock response
        mock_response = self._mock_response_setup(status_code=403)
        mock_get.return_value = mock_response

        # Clear the cache before testing
        get_exchange_rates.cache_clear()

        # Assert that an HTTPException is raised
        with self.assertRaises(HTTPException) as context:
            get_exchange_rates("USD")

    @patch('main.requests.get')
    def test_caching_behavior(self, mock_get):
        # Use the helper method to set up the mock response
        mock_response = self._mock_response_setup(status_code=200)
        mock_get.return_value = mock_response

        # Clear the cache before testing
        get_exchange_rates.cache_clear()

        # Call the function multiple times
        response1 = get_exchange_rates('USD')
        response2 = get_exchange_rates('USD')
        response3 = get_exchange_rates('USD')

        # Verify the response is as expected
        self.assertEqual(response1, self.response_dict['conversion_rates'])
        self.assertEqual(response2, self.response_dict['conversion_rates'])
        self.assertEqual(response3, self.response_dict['conversion_rates'])

        # Verify that the requests.get was called only once
        self.assertEqual(mock_get.call_count, 1)
