import pytest
import logging
from brownie import *
LOGGER = logging.getLogger(__name__)
from web3 import Web3

accounts.load('secret2')
zero_address = '0x0000000000000000000000000000000000000000'
out_type = 3
amount = 100000
wnft_collection = '0x6F7B3f8cbEbFCBf83A927eF21805EAFFa735f870'
usdc_address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
gas_price = "40 gwei"

def main():
    
    wrapper = WrapperUsersV1Batch.at('0x9992325EFC8c62C24DedF61Fb60Cf6a632Eea36c')
    usdc = TokenMock.at(usdc_address)
    


    wNFT = (((0, zero_address), 0,0),
        zero_address,
        [],
        [],
        [],
        out_type,
        0,
        Web3.toBytes(0x0000)
        )

    usdc.approve(wrapper.address, amount, {"from": accounts[0], "gas_price": gas_price})
    tx = wrapper.wrapIn(wNFT, [((2, usdc_address), 0, amount)], accounts[0], wnft_collection, {"from": accounts[0], "gas_price": gas_price})