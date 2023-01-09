import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721Light, makeNFTForTest1155, makeFromERC1155ToERC1155Light


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3
out_nft_amount = 5

def test_addCollateral(accounts, erc721mock, erc1155mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, wnft1155ForWrapperLightV1, niftsy20):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)

    #make wrap NFT 721
    wTokenId721 = makeFromERC721ToERC721Light(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
    assert wnft721ForWrapperLightV1.ownerOf(wTokenId721) == accounts[3]
    
    #make wrap NFT 1155
    wTokenId1155 = makeFromERC1155ToERC1155Light(accounts, erc1155mock, wrapperLight, dai, weth, wnft1155ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], in_nft_amount, out_nft_amount, accounts[3])
    assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId1155) == out_nft_amount

    wnft1155ForWrapperLightV1.setApprovalForAll(wrapperLight.address,True, {"from": accounts[3]})
    erc1155_data = ((4, wnft1155ForWrapperLightV1.address), wTokenId1155, out_nft_amount)

    wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId721, [erc1155_data], {"from": accounts[3]})
    assert wnft1155ForWrapperLightV1.balanceOf(wrapperLight.address, wTokenId1155) == out_nft_amount

    wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId721, {"from": accounts[3]})

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3] 
    assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId1155) == out_nft_amount

    wrapperLight.unWrap(4, wnft1155ForWrapperLightV1.address, wTokenId1155, {"from": accounts[3]})
    assert erc1155mock.balanceOf(accounts[3] , ORIGINAL_NFT_IDs[0]) == in_nft_amount


