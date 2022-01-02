import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "4 ether"

def test_addCollateral(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1, whiteLists):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    #make 1155 token for collateral
    makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock1.setApprovalForAll(wrapper.address,True, {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

    token_property = (in_type, erc721mock)
    erc1155_property = (4, erc1155mock1)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], in_nft_amount)

    fee = [('0x0', Wei(1e18), niftsy20.address)]
    lock = []
    royalty = [(accounts[1], 100), (accounts[2], 200)]

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )


    #switch on white list
    wrapper.setWhiteList(whiteLists.address, {"from": accounts[0]})

    with reverts("WL:Some assets Not enabled for collateral"):
        wrapper.wrap(wNFT, [erc1155_data], accounts[3], {"from": accounts[1], "value": eth_amount})

    wl_data = (False, True, False, False, '0x0', zero_address)
    whiteLists.setItem(erc1155mock1.address, wl_data, {"from": accounts[0]})

    wrapper.wrap(wNFT, [erc1155_data], accounts[3], {"from": accounts[1], "value": eth_amount})    
    wTokenId = wrapper.lastWNFTId(out_type)[1]

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
    assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert wrapper.balance() == eth_amount
    assert wnft721.ownerOf(wTokenId) == accounts[3]


