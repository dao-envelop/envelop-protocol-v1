import logging
import time
from brownie import *
from web3 import Web3
LOGGER = logging.getLogger(__name__)

accounts.clear()

#0-0xa11103Da33d2865C3B70947811b1436ea6Bb32eF
private_key='c4f373082110065841b63c9e005710309756f78bc7b09dbf2a242442173b1ddc'
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
    techERC20 = TechTokenV1.at('0xc7F296aF2E3698B4157BDBA573bdcbcE6D3e3660')
    wrapper = WrapperBaseV1.at('0xa459d2f635812792Df0F175B2263D4bE15A0D5aa')
    wnft1155 = EnvelopwNFT1155.at('0xD7C46FbBD3e6E4Af1E3ced59d74A506E33181b7D')
    wnft721 = EnvelopwNFT721.at('0xb9c9CBe8a55e67C2d8a14A3472E8f2a3f09f8dC6')
    #erc721mock = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')
    erc721mock = Envelop721Mock.at('0x166f56bD3fE11bc55A981a99dCC61Ab931585AbD')
    erc1155mock = Token1155Mock.at('0x2d65336E7AEc57F52D76a333eD65Ee5e29F7eB25')
    whiteLists = AdvancedWhiteList.at('0x3C23392cee7BA6fc33c4E166122E690be977C94E')
    erc20Mock = Niftsy.at('0xB7Ca883C29045D435d01de25b9522b937964f583')
    #niftsy201 = Niftsy.at('0xcF54c844DBe67b3976667698552EaAAb12333b0B')
    print(wnft1155.name())

    price = "10 gwei"
    print(accounts[0].balance())
    #niftsy201 = Niftsy.deploy(accounts[0], {'from':accounts[0]})

    wl_data = (False, True, False, techERC20.address)
    #whiteLists.setWLItem(erc721mock.address, wl_data, {"from": accounts[0]})

    '''zero_address = '0x0000000000000000000000000000000000000000'
    call_amount = 1e18
    eth_amount = "0.0001 ether"
    transfer_fee_amount = 100

    #make wrap NFT
    in_type = 4
    out_type = 4
    in_nft_amount = 2
    out_nft_amount = 5
    #print(wnft721.wnftInfo(300))

   
    
    #niftsy20.approve(wrapper.address, call_amount, {"from": accounts[0], "gas_price": price})
    #niftsy201.approve(wrapper.address, call_amount, {"from": accounts[0], "gas_price": price})
    #erc721mock.mint(accounts[0], {"from": accounts[0], "gas_price": price})
    #erc1155mock.mint(accounts[0], 3, in_nft_amount, {"from": accounts[0], "gas_price": price})
    
    #erc721tokenId = 4
    #erc721mock.mint(accounts[0], erc721tokenId, {"from": accounts[0], "gas_price": price})
    #erc721mock.approve(wrapper.address, erc721tokenId, {"from": accounts[0], "gas_price": price})
    
    
    #erc721tokenId = erc721mock.tokenOfOwnerByIndex(accounts[0], erc721mock.balanceOf(accounts[0])-1)
    #erc721mock.approve(wrapper.address, erc721tokenId, {"from": accounts[0], "gas_price": price})
    #erc1155mock.approve(wrapper.address, origTokenId, in_nft_amount {"from": accounts[0], "gas_price": price})
    #erc1155mock.setApprovalForAll(wrapper.address, True, {"from": accounts[0], "gas_price": price})

    #erc721mock.mint(accounts[0], {"from": accounts[0], "gas_price": price})
    #erc721tokenId_coll = erc721mock.tokenOfOwnerByIndex(accounts[0], erc721mock.balanceOf(accounts[0])-1)
    #erc721mock.approve(wrapper.address, erc721tokenId_coll, {"from": accounts[0], "gas_price": price})

    token_property = (in_type, erc1155mock)
    #token_property = (0, zero_address)

    token_data = (token_property, 3, in_nft_amount)
    #token_data = (token_property, erc721tokenId, 0)

    #fee = [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
    fee = []
    lock = [('0x00', chain.time() + 100), ('0x01', 100)]
    #lock = []
    #royalty = [(accounts[0], 5000), (accounts[1], 5000)]
    royalty = []

    wNFT = ( token_data,
        accounts[0],
        fee,
        lock,
        royalty,
        #3,
        4,
        #0,
        out_nft_amount,
        Web3.toBytes(0x0000)
        )
    #collateral = [((3, erc721mock.address),erc721tokenId_coll, 0), ((4, erc1155mock.address), 11, in_nft_amount), ((2, niftsy20.address),0, call_amount) ]
    collateral = []
    #tx = wrapper.wrap(wNFT, collateral , accounts[0], {"from": accounts[0],'gas_price': price, "value": "0.00001 ether"})
    wTokenId = wrapper.lastWNFTId(4)[1]
    #print(wnft721.wnftInfo(wTokenId))
    print(wnft1155.wnftInfo(wTokenId))
    #print("wTokenId = {}".format(wTokenId))

    #wnft721.transferFrom(accounts[0], '0x88Bd8864e90e851BaB14E9c22b3a342AF6e43CE8', 32, {"from": accounts[0], 'gas_price': price})

    #print(tx)

    #niftsy20.approve(wrapper.address, call_amount/10, {"from": accounts[0], "gas_price": price})
    #wrapper.addCollateral(wnft1155.address, wTokenId, [((2, niftsy20.address), 0, call_amount/10), ((3, erc721mock.address), erc721tokenId, 0), ((4, erc1155mock.address), 4, in_nft_amount)], {"from": accounts[0], "gas_price": price})
    #wrapper.addCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), 5, in_nft_amount-1)], {"from": accounts[0], "gas_price": price})
    #wrapper.addCollateral(wnft1155.address, wTokenId, [((2, niftsy201.address), 0, 3*transfer_fee_amount)], {"from": accounts[0], "gas_price": price, "value": "10 wei"})



    #niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[3], "gas_price": price})


    #wrapper.unWrap(wnft721.address, wTokenId, {"from": accounts[0],'gas_price':  price})

    #print(wnft721.wnftInfo(303))'''



