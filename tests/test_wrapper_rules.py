import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3
in_nft_amount = 3
transfer_fee_amount = 100


#using rules and without
def test_wrap(accounts, erc721mock, wrapper, wnft721, niftsy20):
    
      
    #without possible rules
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    
    fee = []
    lock = []
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        Web3.toBytes(0x0010)  #rules = 10000
        )

    wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
    wTokenId = wrapper.lastWNFTId(out_type)[1]

    wnft721.safeTransferFrom(accounts[3], accounts[4], wTokenId, {"from": accounts[3]})

    assert wnft721.ownerOf(wTokenId) == accounts[4]

    niftsy20.approve(wrapper.address, 1e18, {"from": accounts[0]})
    wrapper.addCollateral(wnft721, wTokenId, [((2, niftsy20.address), 0, 1e18)], {"from": accounts[0]})

    assert niftsy20.balanceOf(wrapper) == 1e18

    wrapper.unWrap(wnft721, wTokenId, {"from": accounts[4]})

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[4]
    assert niftsy20.balanceOf(accounts[4]) == 1e18


    #with possible rules
    erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {"from": accounts[1]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[1], 0)
    
    fee = []
    lock = []
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        Web3.toBytes(0x001F)  #rules = 11111
        )

    wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
    wTokenId = wrapper.lastWNFTId(out_type)[1]

    with reverts("Transfer was disabled by author"):
        wnft721.safeTransferFrom(accounts[3], accounts[5], wTokenId, {"from": accounts[3]})

    niftsy20.approve(wrapper.address, 1e18, {"from": accounts[0]})
    with reverts("Forbidden add collateral"):
        wrapper.addCollateral(wnft721, wTokenId, [((2, niftsy20.address), 0, 1e18)], {"from": accounts[0]})

    with reverts("UnWrapp forbidden by author"):
        wrapper.unWrap(wnft721, wTokenId, {"from": accounts[5]})

    token_property = (in_type, wnft721)
    token_data = (token_property, wTokenId, 0)

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        Web3.toBytes(0x0000)  #rules = 0000
        )

    with reverts("Wrap check fail"):
        wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[3]})

