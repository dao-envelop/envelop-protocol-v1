import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest1155, makeFromERC721ToERC721WithoutCollateral, makeNFTForTest721

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

def test_addCollateral(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20, erc1155mock):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3
    coll_amount = 2


    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    #wrap 721to721
    in_type = 3
    out_type = 3

    erc721mock.setApprovalForAll(wrapperLight.address, True, {'from':accounts[1]})
    
    if (wrapperLight.lastWNFTId(out_type)[1] == 0):
        wrapperLight.setWNFTId(out_type, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})

    erc721_property = (in_type, erc721mock.address)
    
    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 1)

    fee = []
    lock = []
    royalty = []

    wNFT = ( erc721_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    wrapperLight.wrap(wNFT, [], accounts[1], {"from": accounts[1]})
    wTokenId = wrapperLight.lastWNFTId(out_type)[1]


    #prepare collateral
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapperLight.address,True, {"from": accounts[1]})
    erc1155_property = (4, erc1155mock.address)
    erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], coll_amount)

    #add collaterall
    wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [erc1155_data], {"from": accounts[1], "value": eth_amount})


    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
    assert wrapperLight.balance() == eth_amount
    assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[1]
    assert erc1155mock.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == coll_amount


