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
    wrapper = WrapperBaseV1.at('0x8368f72a85f5b3bC9f41FF9f3a681b09DA0fE21f')
    #wnft1155 = EnvelopwNFT1155.at('0x0ff3a4F7De32588CFfe22A838D5a18A45CD4358a')
    wnft721 = EnvelopwNFT721.at('0xd3FDE1C83B144d07878CDa57b66B35176A785e61')
    erc721mock = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')
    #erc721mock = Envelop721Mock.at('0x166f56bd3fe11bc55a981a99dcc61ab931585abd')
    erc1155mock = Token1155Mock.at('0xD48fdbCf81070547d5a3fB276203b5bf96344b10')
    #whiteLists = AdvancedWhiteList.at('0x0Cbc46647D4529E8f9bbB13c0F2113B1E74c7Aed')
    niftsy20 = Niftsy.at('0x432cdbC749FD96AA35e1dC27765b23fDCc8F5cf1')
    #niftsy201 = Niftsy.at('0xcF54c844DBe67b3976667698552EaAAb12333b0B')

    price = "50 gwei"

    #niftsy201 = Niftsy.deploy(accounts[0], {'from':accounts[0]})
    

    zero_address = '0x0000000000000000000000000000000000000000'
    call_amount = 1e18
    eth_amount = "0.0001 ether"
    transfer_fee_amount = 100

    #make wrap NFT
    in_type = 3
    out_type = 3
    in_nft_amount = 3
    out_nft_amount = 5
    #print(wnft721.wnftInfo(300))

    #wl_data = (False, True, False, techERC20.address)
    #whiteLists.setWLItem(niftsy201, wl_data, {"from": accounts[1]})
    
    niftsy20.approve(wrapper.address, call_amount, {"from": accounts[0], "gas_price": price})
    #niftsy201.approve(wrapper.address, call_amount, {"from": accounts[0], "gas_price": price})
    erc721mock.mint(accounts[0], {"from": accounts[0], "gas_price": price})
    erc1155mock.mint(accounts[0], 6, in_nft_amount, {"from": accounts[0], "gas_price": price})
    
    
    erc721tokenId = erc721mock.tokenOfOwnerByIndex(accounts[0], erc721mock.balanceOf(accounts[0])-1)
    erc721mock.approve(wrapper.address, erc721tokenId, {"from": accounts[0], "gas_price": price})
    #erc1155mock.approve(wrapper.address, origTokenId, in_nft_amount {"from": accounts[0], "gas_price": price})
    #erc1155mock.setApprovalForAll(wrapper.address, True, {"from": accounts[0], "gas_price": price})

    erc721mock.mint(accounts[0], {"from": accounts[0], "gas_price": price})
    erc721tokenId_coll = erc721mock.tokenOfOwnerByIndex(accounts[0], erc721mock.balanceOf(accounts[0])-1)
    erc721mock.approve(wrapper.address, erc721tokenId_coll, {"from": accounts[0], "gas_price": price})

    token_property = (in_type, erc721mock)
    #token_property = (0, zero_address)

    #token_data = (token_property, origTokenId, 0)
    token_data = (token_property, erc721tokenId, 0)

    fee = [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
    #fee = []
    lock = [('0x00', chain.time() + 100), ('0x01', 100)]
    #lock = []
    royalty = [(accounts[0], 5000), (accounts[1], 5000)]
    #royalty = []

    wNFT = ( token_data,
        accounts[0],
        fee,
        lock,
        royalty,
        3,
        0,
        #out_nft_amount,
        Web3.toBytes(0x0000)
        )
    collateral = [((3, erc721mock.address),erc721tokenId_coll, 0), ((4, erc1155mock.address), 6, in_nft_amount), ((2, niftsy20.address),0, call_amount) ]
    tx = wrapper.wrap(wNFT, collateral , accounts[0], {"from": accounts[0],'gas_price': price, "value": "0.00001 ether"}) 
    wTokenId = wrapper.lastWNFTId(3)[1]
    print("wTokenId = {}".format(wTokenId))

    #wnft721.transferFrom(accounts[0], '0x88Bd8864e90e851BaB14E9c22b3a342AF6e43CE8', 32, {"from": accounts[0], 'gas_price': price})

    #print(tx)

    #niftsy20.approve(wrapper.address, call_amount/10, {"from": accounts[0], "gas_price": price})
    #wrapper.addCollateral(wnft1155.address, wTokenId, [((2, niftsy20.address), 0, call_amount/10), ((3, erc721mock.address), erc721tokenId, 0), ((4, erc1155mock.address), 4, in_nft_amount)], {"from": accounts[0], "gas_price": price})
    #wrapper.addCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), 5, in_nft_amount-1)], {"from": accounts[0], "gas_price": price})
    #wrapper.addCollateral(wnft1155.address, wTokenId, [((2, niftsy201.address), 0, 3*transfer_fee_amount)], {"from": accounts[0], "gas_price": price, "value": "10 wei"})



    #niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[3], "gas_price": price})


    #wrapper.unWrap(wnft721.address, wTokenId, {"from": accounts[0],'gas_price':  price})

