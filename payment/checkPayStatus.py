import os

from yoomoney import Client


def check_pay_status(label):
    token = os.getenv("PAYMENT_TOKEN")
    client = Client(token)
    history = client.operation_history(label=label)
    for operation in history.operations:
       return operation.status