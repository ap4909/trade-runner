from handler import lambda_handler

if __name__ == "__main__":
    event = {"symb": "AAPL"}
    lambda_handler(event, None)
