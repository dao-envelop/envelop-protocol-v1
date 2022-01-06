import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest1155, makeFromERC721ToERC721WithoutCollateral, makeNFTForTest721

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "4 ether"

def test_addCollateral(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, erc1155mock, whiteLists):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3
    coll_amount = 2


    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    #wrap 721to721
    wTokenId = makeFromERC721ToERC721WithoutCollateral(accounts, erc721mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], accounts[1])

    #prepare collateral
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapper.address,True, {"from": accounts[1]})
    erc1155_property = (4, erc1155mock.address)
    erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], coll_amount)

    #switch on white list
    wrapper.setWhiteList(whiteLists.address, {"from": accounts[0]})

    #try to add collaterall
    with reverts("WL:Some assets Not enabled for collateral"):
        wrapper.addCollateral(wnft721.address, wTokenId, [erc1155_data], {"from": accounts[1], "value": eth_amount})

    #add items in whiteList
    wl_data = (False, True, False,  False, '0x0', accounts[9])
    whiteLists.setItem(erc1155mock.address, wl_data, {"from": accounts[0]})

    #add collaterall
    wrapper.addCollateral(wnft721.address, wTokenId, [erc1155_data], {"from": accounts[1], "value": eth_amount})


    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
    assert wrapper.balance() == eth_amount
    assert wnft721.ownerOf(wTokenId) == accounts[1]
    assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == coll_amount


