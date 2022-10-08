import pytest
import logging
from brownie import *
LOGGER = logging.getLogger(__name__)
from web3 import Web3

accounts.load('secret2')
accounts.add('') #max_siz
accounts.add('') #accounts for deployment
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3
call_amount = 1e18


def main():
    caller = accounts[0]
    multisig = accounts[2]

    techERC20 = TechTokenV1.at('0x7a6A73BE2E6b81cF1067c5D51BdBfA225166ec85')
    checker = CheckerExchange.at('0x0373494c0B9fD878e7B1CA55AaC58513F0aA6C37')
    wrapper = WrapperRemovableAdvanced.at('0x8E25948aA3910C01f8908F09F3fEb5c5cB2c1198')
    wnft721 = EnvelopwNFT721.at('0x014Aa0eEEcea3733F41934973ff4e00fCBb1187c')
    whitelist = AdvancedWhiteList.at('0x586f6781cBf1c506EeE0Da14E28DB1F63723234c')
    niftsy20 = TokenMock.at('0x376e8EA664c2E770E1C45ED423F62495cB63392D')
    

    wTokenId = 2
    print(niftsy20.balanceOf(multisig))
    print(niftsy20.balanceOf(wrapper))
    wNFT = ( ((0, zero_address), 0,0),
        accounts[1],
        [],
        [('0x00', chain.time() + 10)],
        [(multisig, 10000)],
        out_type,
        0,
        Web3.toBytes(0x0004)
        )

    niftsy20.approve(wrapper.address, call_amount, {"from": accounts[1]})
    niftsy20.transfer(accounts[1], call_amount, {"from": accounts[0], "gas_price": "30 gwei"})

    #msg.sender is trusted address
    tx = wrapper.wrap(wNFT, [((2, niftsy20.address), 0, call_amount)], accounts[1], {"from": accounts[1], "gas_price": "30 gwei"})

    wTokenId = tx.events['WrappedV1']['outTokenId']
    print(wTokenId)
    try:
        wrapper.removeERC20CollateralAmount(wnft721.address, wTokenId, niftsy20.address, 1, {"from": accounts[1], "gas_price": "30 gwei"})
    except ValueError as ve:
        print(ve)

    wrapper.removeERC20CollateralAmount(wnft721.address, wTokenId, niftsy20.address, 1, {"from": multisig, "gas_price": "30 gwei"})
    
    wrapper.unWrap(wnft721, wTokenId, {"from": accounts[1], "gas_price": "30 gwei"})

    assert niftsy20.balanceOf(wrapper) == 0
    assert niftsy20.balanceOf(accounts[1]) > 1