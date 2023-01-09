import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721, makeNFTForTest1155, makeFromERC1155ToERC1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3
out_nft_amount = 5

def test_addCollateral(accounts, erc721mock, erc1155mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, wnft1155ForWrapperLightV1, niftsy20):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)

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
    wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
    wTokenId721 = wrapperLight.lastWNFTId(out_type)[1]

    assert wnft721ForWrapperLightV1.ownerOf(wTokenId721) == accounts[3]
    
    #make wrap NFT 1155
    in_type = 4
    out_type = 4
    erc1155mock.setApprovalForAll(wrapperLight.address,True, {"from": accounts[1]}) 
    if (wrapperLight.lastWNFTId(out_type)[1] == 0):
        wrapperLight.setWNFTId(out_type, wnft1155ForWrapperLightV1.address, 0, {'from':accounts[0]})
    token_property = (in_type, erc1155mock)
    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    fee = []
    lock = []
    royalty = []
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )
    wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
    assert erc1155mock.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount
    wTokenId1155 = wrapperLight.lastWNFTId(out_type)[1]

    assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId1155) == out_nft_amount

    wnft721ForWrapperLightV1.approve(wrapperLight.address, wTokenId721, {"from": accounts[3]})
    erc721_data = ((3, wnft721ForWrapperLightV1.address), wTokenId721, 0)

    wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId1155, [erc721_data], {"from": accounts[3]})
    assert wnft721ForWrapperLightV1.ownerOf(wTokenId721) == wrapperLight.address

    wrapperLight.unWrap(4, wnft1155ForWrapperLightV1.address, wTokenId1155, {"from": accounts[3]})

    assert erc1155mock.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert wnft721ForWrapperLightV1.ownerOf(wTokenId721) == accounts[3]

    wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId721, {"from": accounts[3]})    
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]    