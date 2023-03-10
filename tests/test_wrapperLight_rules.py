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
def test_wrap(accounts, erc721mock, wrapperLight, wnft721ForWrapperLightV1, niftsy20, wnft1155ForWrapperLightV1):
    
      
    #without possible rules
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapperLight.lastWNFTId(3)[1] == 0):
        wrapperLight.setWNFTId(3, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})

    if (wrapperLight.lastWNFTId(4)[1] == 0):
        wrapperLight.setWNFTId(4, wnft1155ForWrapperLightV1.address, 0, {'from':accounts[0]})

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

    wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
    wTokenId = wrapperLight.lastWNFTId(out_type)[1]

    wnft721ForWrapperLightV1.safeTransferFrom(accounts[3], accounts[4], wTokenId, {"from": accounts[3]})

    assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[4]

    niftsy20.approve(wrapperLight.address, 1e18, {"from": accounts[0]})
    wrapperLight.addCollateral(wnft721ForWrapperLightV1, wTokenId, [((2, niftsy20.address), 0, 1e18)], {"from": accounts[0]})

    assert niftsy20.balanceOf(wrapperLight) == 1e18

    wrapperLight.unWrap(wnft721ForWrapperLightV1, wTokenId, {"from": accounts[4]})

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[4]
    assert niftsy20.balanceOf(accounts[4]) == 1e18


    #with possible rules - erc721
    erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[1], {"from": accounts[1]})

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

    wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
    wTokenId = wrapperLight.lastWNFTId(out_type)[1]

    wnft721ForWrapperLightV1.safeTransferFrom(accounts[3], accounts[5], wTokenId, {"from": accounts[3]})

    assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[5]

    niftsy20.approve(wrapperLight.address, 1e18, {"from": accounts[0]})
    wrapperLight.addCollateral(wnft721ForWrapperLightV1, wTokenId, [((2, niftsy20.address), 0, 1e18)], {"from": accounts[0]})

    assert niftsy20.balanceOf(wrapperLight) == 1e18

    wrapperLight.unWrap(wnft721ForWrapperLightV1, wTokenId, {"from": accounts[5]})

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[5]
    assert niftsy20.balanceOf(accounts[5]) == 1e18


    #with possible rules - erc1155
    erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[2], {"from": accounts[0]})
    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[2], {"from": accounts[1]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[2], 0)
    
    fee = []
    lock = []
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        4,
        3,
        Web3.toBytes(0x001F)  #rules = 11111
        )

    wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
    wTokenId = wrapperLight.lastWNFTId(4)[1]

    wnft1155ForWrapperLightV1.safeTransferFrom(accounts[3], accounts[5], wTokenId, 3, '', {"from": accounts[3]})

    assert wnft1155ForWrapperLightV1.balanceOf(accounts[5], wTokenId) == 3

    niftsy20.approve(wrapperLight.address, 1e18, {"from": accounts[0]})
    wrapperLight.addCollateral(wnft1155ForWrapperLightV1, wTokenId, [((2, niftsy20.address), 0, 1e18)], {"from": accounts[0]})

    assert niftsy20.balanceOf(wrapperLight) == 1e18

    wrapperLight.unWrap(wnft1155ForWrapperLightV1, wTokenId, {"from": accounts[5]})

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[2]) == accounts[5]
    assert niftsy20.balanceOf(accounts[5]) == 2e18
