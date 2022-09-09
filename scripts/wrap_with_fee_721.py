import logging
import time
from brownie import *
from web3 import Web3
LOGGER = logging.getLogger(__name__)

accounts.clear()



#0-0x5992Fe461F81C8E0aFFA95b831E50e9b3854BA0E
#private_key=''
accounts.load('secret2')
#accounts.add(private_key)

#1-0xa11103Da33d2865C3B70947811b1436ea6Bb32eF
#private_key=''
#accounts.add(private_key)




def main():
    #techERC20 = TechTokenV1.at('0xc7F296aF2E3698B4157BDBA573bdcbcE6D3e3660')
    wrapper = WrapperBaseV1.at('0x352cbaf36edd05e6a85a7bfa9f5d91ef4ea13f39')
    #wnft1155 = EnvelopwNFT1155.at('0xD7C46FbBD3e6E4Af1E3ced59d74A506E33181b7D')
    #wnft1155_1 = EnvelopwNFT1155.at('0x528255B1F6b0Ff8379C29515262Bb3b4EFBB1D45')
    wnft721 = EnvelopwNFT721.at('0xdFeB55cBD23c13C4aC3195048824D14787E10732')
    #erc721mock = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')
    #erc721mock = Envelop721Mock.at('0x166f56bD3fE11bc55A981a99dCC61Ab931585AbD')
    #erc1155mock = Token1155Mock.at('0x2d65336E7AEc57F52D76a333eD65Ee5e29F7eB25')
    #whiteLists = AdvancedWhiteList.at('0x3C23392cee7BA6fc33c4E166122E690be977C94E')
    #erc20Mock = TokenMock.at('0xB7Ca883C29045D435d01de25b9522b937964f583')
    niftsy20 = Niftsy.at('0x3125b3b583d576d86dbd38431c937f957b94b47d')
    #originalNFT = OrigNFT.at('0x196869B37cf08731e7eFcB75a40703894fBB66E1')


    #wrapper.transferOwnership('0xa0cff013918ddaED7F2e6066D0403C6D50a58a7c', {"from": accounts[0]})
    #whiteLists.transferOwnership('0xa0cff013918ddaED7F2e6066D0403C6D50a58a7c', {"from": accounts[0]})


    price = "20 gwei"
    #niftsy201 = Niftsy.deploy(accounts[0], {'from':accounts[0]})

    #wl_data = (False, True, False, techERC20.address)
    #whiteLists.setWLItem(originalNFT, wl_data, {"from": accounts[1]})



    #whiteLists.setRules('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578', '0x0000', '0x0000', {"from": accounts[0], "gas_price": price})

    zero_address = '0x0000000000000000000000000000000000000000'
    call_amount = 1e18
    eth_amount = "0.0001 ether"
    transfer_fee_amount = 100

    #make wrap NFT
    in_type = 3
    out_type = 3
    in_nft_amount = 2
    out_nft_amount = 5

    #erc20Mock.approve(wrapper.address, call_amount, {"from": accounts[0], "gas_price": price})
    
    
    #ColltokenId = 16
    #erc1155mock.mint(accounts[0], ColltokenId, in_nft_amount, {"from": accounts[0], "gas_price": price})

    #erc721tokenId = originalNFT.totalSupply()+1
    #erc721mock.mint(accounts[0], erc721tokenId, {"from": accounts[0], "gas_price": price})
    #originalNFT.mint(accounts[0], {"from": accounts[0], "gas_price": price})
    #erc721mock.approve(wrapper.address, erc721tokenId, {"from": accounts[0], "gas_price": price})
    #originalNFT.approve(wrapper.address, erc721tokenId, {"from": accounts[0], "gas_price": price})

    #erc721tokenId_coll = originalNFT.totalSupply()+1
    #erc721mock.mint(accounts[0], erc721tokenId_coll, {"from": accounts[0], "gas_price": price})
    #originalNFT.mint(accounts[0], {"from": accounts[0], "gas_price": price})
    #erc721mock.approve(wrapper.address, erc721tokenId_coll, {"from": accounts[0], "gas_price": price})
    #originalNFT.approve(wrapper.address, erc721tokenId_coll, {"from": accounts[0], "gas_price": price})



    #token_property = (in_type, erc721mock)
    token_property = (0, zero_address)

    token_data = (token_property, 0, 0)

    fee = [(Web3.toBytes(0x00), 15*10e18, niftsy20)]
    #fee = []
    lock = []
    #lock = []
    royalty = [(accounts[0], 10000)]
    #royalty = []

    wNFT = ( token_data,
        accounts[0],
        fee,
        lock,
        royalty,
        3,
        0,
        Web3.toBytes(0x0000)
        )
    #collateral = [((3, erc721mock.address),erc721tokenId_coll, 0), ((4, erc1155mock.address), ColltokenId, in_nft_amount), ((2, erc20Mock.address),0, call_amount) ]
    #collateral = [((3, originalNFT.address),erc721tokenId_coll, 0), ((4, erc1155mock.address), ColltokenId, in_nft_amount), ((2, erc20Mock.address),0, call_amount) ]
    collateral = []
    tx = wrapper.wrap(wNFT, collateral , accounts[0], {"from": accounts[0],'gas_price': price})
    wTokenId = wrapper.lastWNFTId(3)[1]

    print(wnft721.wnftInfo(wTokenId))
    print("wTokenId = {}".format(wTokenId))
    #print(wnft721.uri(wTokenId))
    #print(wrapper.getOriginalURI(wnft721.address, wTokenId))




    #okx originalNFT = OrigNFT.at('0x196869B37cf08731e7eFcB75a40703894fBB66E1')

    '''wTokenId = 14

    ColltokenId = 17
    erc1155mock.mint(accounts[0], ColltokenId, in_nft_amount+5, {"from": accounts[0], "gas_price": price})
    collateral = [((4, erc1155mock.address), ColltokenId, in_nft_amount+5)]

    wrapper.addCollateral(wnft1155, wTokenId, collateral, {"from": accounts[0], "value": 1})
    print(wnft1155.wnftInfo(wTokenId))'''
