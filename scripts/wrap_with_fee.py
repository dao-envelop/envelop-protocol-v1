import logging
import time
from brownie import *
from web3 import Web3
LOGGER = logging.getLogger(__name__)



#0-0xeC060A763ACf876a0f25D7796497174B834140b5
private_key='7a1851357aebcd2b94291fa3a321901430ed7715fa48906ec1b6d7dd28b1b723'
accounts.add(private_key)

#1-0xE71978b1696a972b1a8f724A4eBDB906d9dA0885
private_key='2cdbeadae3122f6b30a67733fd4f0fb6c27ccd85c3c68de97c8ff534c87603c8'
accounts.add(private_key)

'''#2-0xAeb5a5FaB00b30d5d34257317882Ff1561e23755
private_key='???'
accounts.add(private_key)

#3-0xbD7E5fB7525ED8583893ce1B1f93E21CC0cf02F6
private_key='???'
accounts.add(private_key)'''


def main():
    #techERC20 = TechTokenV1.at('0xE1604b54CaC27970aa67b4e38495F206b59CEe42')
    wrapper = WrapperBaseV1.at('0x352cbAF36eDD05e6a85A7BFA9f5d91Ef4Ea13F39')
    wnft1155 = EnvelopwNFT1155.at('0x0ff3a4F7De32588CFfe22A838D5a18A45CD4358a')
    wnft721 = EnvelopwNFT721.at('0xdFeB55cBD23c13C4aC3195048824D14787E10732')
    erc721mock = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')
    #erc721mock = Envelop721Mock.at('0x166f56bd3fe11bc55a981a99dcc61ab931585abd')
    erc1155mock = Token1155Mock.at('0x403cEDfF16ad12d4Ef53b2D8aFe55965a1a61BFE')
    #whiteLists = AdvancedWhiteList.at('0x0Cbc46647D4529E8f9bbB13c0F2113B1E74c7Aed')
    niftsy20 = Niftsy.at('0x3125B3b583D576d86dBD38431C937F957B94B47d')
    price = "2 gwei"

    zero_address = '0x0000000000000000000000000000000000000000'
    call_amount = 1e18
    eth_amount = "0.0001 ether"
    transfer_fee_amount = 100

    #make wrap NFT
    in_type = 3
    out_type = 3
    in_nft_amount = 3
    out_nft_amount = 5

    #wl_data = (True, True, False, techERC20.address)
    #whiteLists.setWLItem(niftsy20.address, wl_data, {"from": accounts[1]})
    
    #niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[1], "gas_price": price})
    #erc721mock.mint(accounts[0], {"from": accounts[0], "gas_price": price})
    #erc1155mock.mint(accounts[0], 3, in_nft_amount, {"from": accounts[0], "gas_price": price})
    
    
    origTokenId = 13 #erc721mock.tokenOfOwnerByIndex(accounts[0], erc721mock.balanceOf(accounts[0])-1)
    #erc721mock.approve(wrapper.address, origTokenId, {"from": accounts[0], "gas_price": price})
    #erc1155mock.setApprovalForAll(wrapper.address, True, {"from": accounts[0], "gas_price": price})

    #token_property = (in_type, erc721mock)
    '''token_property = (in_type, erc1155mock)

    #token_data = (token_property, origTokenId, 0)
    token_data = (token_property, origTokenId, in_nft_amount)

    fee = [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
    lock = lock = [('0x0', chain.time() + 100)]
    royalty = [(accounts[0], 10000)]

    wNFT = ( token_data,
        accounts[0],
        fee,
        lock,
        royalty,
        out_type,
        #0,
        out_nft_amount,
        Web3.toBytes(0x0000)
        )

    #collateral = [((2, niftsy20.address),0, call_amount)]
    collateral = []
    #niftsy20.approve(wrapper.address, call_amount, {"from": accounts[0], "gas_price": price})


    wrapper.wrap(wNFT, collateral , accounts[0], {"from": accounts[0],'gas_price': price})  '''
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    print("wTokenId = {}".format(wTokenId))

    #niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[3], "gas_price": price})


    wrapper.unWrap(wnft721.address, wTokenId, {"from": accounts[0],'gas_price':  price})

