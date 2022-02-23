import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateral

LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [1,2,3,4, 5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22, 23, 24, 25, 26, 27]
zero_address = '0x0000000000000000000000000000000000000000'


def test_addColl(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, erc721mock1, erc1155mock1):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    
    #make wrap NFT 721
    wTokenId = makeFromERC721ToERC721WithoutCollateral(accounts, erc721mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])

    
    #PREPARE DATA
    #make 721 for collateral
    makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
    i = 1
    while i < wrapper.MAX_COLLATERAL_SLOTS()+2:
        erc721mock1.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[i], {"from": accounts[0]} )
        erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[i], {"from": accounts[1]} )
        if (i == wrapper.MAX_COLLATERAL_SLOTS()+1):
            with reverts("Too much tokens in collateral"):
                wrapper.addCollateral(wnft721.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[i], 0)], {'from': accounts[1]})
        else:
            wrapper.addCollateral(wnft721.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[i], 0)], {'from': accounts[1]})
        i += 1

    collateral = wrapper.getWrappedToken(wnft721, wTokenId)[1]

    i = 1
    while i < wrapper.MAX_COLLATERAL_SLOTS():
        assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[i]) == wrapper.address
        assert collateral[i-1] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[i], 0)
        i += 1
    


