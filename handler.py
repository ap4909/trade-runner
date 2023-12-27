from alpaca.broker.client import BrokerClient
from alpaca.broker.requests import ListAccountsRequest
from alpaca.broker.enums import AccountEntities
import datetime
from secrets_helper import get_secret


def lambda_handler(event, context):
    secret = get_secret()
    alpaca_api_key = secret['alpaca_api_key']
    alpaca_secret_key = secret['alpaca_secret_key']

    broker_client = BrokerClient(alpaca_api_key, alpaca_secret_key)

    # search for accounts created after January 30th 2022.
    # Response should contain Contact and Identity fields for each account.
    filter = ListAccountsRequest(
                        created_after=datetime.datetime.strptime("2022-01-30", "%Y-%m-%d"),
                        entities=[AccountEntities.CONTACT, AccountEntities.IDENTITY]
                        )

    accounts = broker_client.list_accounts(search_parameters=filter)