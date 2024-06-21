import os
from functools import lru_cache

from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel


load_dotenv(find_dotenv())

app = FastAPI()

API_KEY = os.getenv(
    "EXCHANGE_RATE_API_KEY"
)  # Make sure to set this environment variable

BASE_URL = "https://v6.exchangerate-api.com/v6"


class ConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


@lru_cache(maxsize=10)
def get_exchange_rates(base_currency: str):
    url = f"{BASE_URL}/{API_KEY}/latest/{base_currency}"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Error fetching exchange rates"
        )
    return response.json()["conversion_rates"]


@app.get("/rates")
def read_rates(base_currency: str = "USD"):
    rates = get_exchange_rates(base_currency)
    return rates


@app.get("/convert")
def convert(amount: float, from_currency: str, to_currency: str):
    rates = get_exchange_rates(from_currency)
    if to_currency not in rates:
        raise HTTPException(status_code=404, detail="Currency not found")
    converted_amount = amount * rates[to_currency]
    return {"amount": converted_amount, "currency": to_currency}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
