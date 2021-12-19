import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateral, makeNFTForTest1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5
coll_amount = 2
amount = 100

def test_addColl(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, erc721mock1, erc1155mock1):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    
    #make wrap NFT 721
    wTokenId = makeFromERC721ToERC721WithoutCollateral(accounts, erc721mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])

    #PREPARE DATA
    #make 721 for collateral
    makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
    erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]} )

    #make 1155 for collateral
    makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock1.setApprovalForAll(wrapper.address,True, {"from": accounts[1]})

    #make erc20 for collateral
    dai.transfer(accounts[1], amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 10*amount, {"from": accounts[0]})
    weth.approve(wrapper.address, 10*amount, {"from": accounts[1]})

    #add collateral
    with reverts("ERC20: transfer amount exceeds allowance"):
        wrapper.addCollateral(wnft721.address, wTokenId, [((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount),
            ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0),
            ((2, dai.address), 0, amount),
            ((2, weth.address), 0, 10*amount),
            ], {'from': accounts[1], "value": "1 ether"})

    collateral = wrapper.getWrappedToken(wnft721, wTokenId)[1]

    assert wrapper.balance() == 0
    assert erc1155mock1.balanceOf(accounts[1], ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[1]
    assert dai.balanceOf(wrapper.address) == 0
    assert weth.balanceOf(wrapper.address) == 0
    assert collateral == []

