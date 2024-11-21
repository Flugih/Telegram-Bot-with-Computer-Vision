import os
from yoomoney import Quickpay


def create_paylink(label):
    quickpay = Quickpay(
                receiver=os.getenv("WALLET"),
                quickpay_form="shop",
                targets="",
                paymentType="SB",
                sum=149,
                label=label
                )
    return quickpay.base_url