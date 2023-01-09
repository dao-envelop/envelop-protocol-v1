import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

def test_wrap(accounts, erc721mock, wrapperLight,  wnft721ForWrapperLightV1):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapperLight.lastWNFTId(out_type)[1] == 0):
        wrapperLight.setWNFTId(out_type, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})
        
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
        '0'
        )

    #check without erc20 collateral - only native tokens
    wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1], "value": eth_amount})

    wTokenId = wrapperLight.lastWNFTId(out_type)[1]

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
    assert wrapperLight.balance() == eth_amount
    assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]


