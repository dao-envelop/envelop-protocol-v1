import logging
import time
from brownie import *
from web3 import Web3
LOGGER = logging.getLogger(__name__)

#0-0xE71978b1696a972b1a8f724A4eBDB906d9dA0885
private_key='???'
accounts.add(private_key)

#1-0x989FA3062bc4329B2E3c5907c48Ea48a38437fB7
private_key='???'
accounts.add(private_key)

#2-0xAeb5a5FaB00b30d5d34257317882Ff1561e23755
#private_key='???'
#accounts.add(private_key)

#3-0xbD7E5fB7525ED8583893ce1B1f93E21CC0cf02F6
#private_key='???'
#accounts.add(private_key)


def main():
    #techERC20 = TechTokenV1.at('0x20e30c7c1295FCD1A78528078b83aaf16C5CE032')
    wrapper = WrapperBaseV1.at('0x352cbAF36eDD05e6a85A7BFA9f5d91Ef4Ea13F39')
    #wnft1155 = EnvelopwNFT1155.at('0x0ff3a4F7De32588CFfe22A838D5a18A45CD4358a')
    #wnft721 = EnvelopwNFT721.at('0x9F4e63Df5D1d21DbD8cdCfa556bFcDf32E89eB7f')
    #erc721mock =  Envelop721Mock.at('0xb7A2E3BE7ce700F00ea2e2BA037Ad9321c81Ae1A')
    #whiteLists = AdvancedWhiteList.at('0x1331dc4f98F74C237Db6E92DD2eAf55bAfce00Ef')
    price = "2 gwei"
    tx_params={'from':accounts[0], 'allow_revert': True,'gas_price': '5 gwei', 'gas_limit': 1e8}

    zero_address = '0x0000000000000000000000000000000000000000'
    call_amount = 1e18
    eth_amount = "0.0001 ether"
    transfer_fee_amount = 100

    #make wrap NFT
    in_type = 0
    out_type = 4

    #erc721mock.mint(accounts[0], 1, {"from": accounts[0], "gas_price": price})
    #erc721mock.mint(accounts[0], 1, tx_params)
    
    #origTokenId = 1
    #erc721mock.approve(wrapper.address, origTokenId, tx_params)

    token_property = (in_type, zero_address)

    token_data = (token_property, 0, 0)
    #token_data = (token_property, 0, 0)

    fee = []
    lock = []
    royalty = []

    wNFT = ( token_data,
        accounts[1],
        fee,
        lock,
        royalty,
        out_type,
        6,
        Web3.toBytes(0x0000)
        )


    wrapper.wrap(wNFT, [] , accounts[0], {"from": accounts[0]})    
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    print("wTokenId = {}".format(wTokenId))

    #unwrap by owner
    #wrapper.unWrap(3, wnft721.address, wTokenId, tx_params)

    #, "gas_price": price


   