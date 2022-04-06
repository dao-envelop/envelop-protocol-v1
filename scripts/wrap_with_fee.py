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
private_key='???'
accounts.add(private_key)

#3-0xbD7E5fB7525ED8583893ce1B1f93E21CC0cf02F6
private_key='???'
accounts.add(private_key)


def main():
    techERC20 = TechTokenV1.at('0xE1604b54CaC27970aa67b4e38495F206b59CEe42')
    wrapper = WrapperBaseV1.at('0x352cbAF36eDD05e6a85A7BFA9f5d91Ef4Ea13F39')
    wnft1155 = EnvelopwNFT1155.at('0x0ff3a4F7De32588CFfe22A838D5a18A45CD4358a')
    wnft721 = EnvelopwNFT721.at('0xdFeB55cBD23c13C4aC3195048824D14787E10732')
    #erc721mock = OrigNFT.at('0x11d30360d423DC2ACf8705007F87957739438aB6')
    erc721mock = OrigNFT.at('0x862A23E2DD96ea83A0444706261571D013685cfb')
    whiteLists = AdvancedWhiteList.at('0x0Cbc46647D4529E8f9bbB13c0F2113B1E74c7Aed')
    niftsy20 = Niftsy.at('0x1E991eA872061103560700683991A6cF88BA0028')
    price = "2 gwei"

    zero_address = '0x0000000000000000000000000000000000000000'
    call_amount = 1e18
    eth_amount = "0.0001 ether"
    transfer_fee_amount = 100

    #make wrap NFT
    in_type = 3
    out_type = 3
    
    #niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[1], "gas_price": price})
    #erc721mock.mint(accounts[1], {"from": accounts[1], "gas_price": price})
    
    
    origTokenId = erc721mock.tokenOfOwnerByIndex(accounts[1], erc721mock.balanceOf(accounts[1])-1)
    erc721mock.approve(wrapper.address, origTokenId, {"from": accounts[1], "gas_price": price})

    token_property = (in_type, erc721mock)

    token_data = (token_property, origTokenId, 0)

    fee = [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
    lock = []
    royalty = [(accounts[2], 5000), (accounts[3], 5000)]

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        Web3.toBytes(0x0000)
        )


    wrapper.wrap(wNFT, [] , accounts[3], {"from": accounts[1], "gas_price": price})    
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    print("wTokenId = {}".format(wTokenId))

    #niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[3], "gas_price": price})


   