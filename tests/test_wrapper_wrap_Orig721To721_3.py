import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

def test_wrap(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1, whiteLists):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

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

    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    dai_property = (2, dai.address)
    dai_data = (dai_property, 0, Wei(call_amount))

    #switch on white list
    wrapper.setWhiteList(whiteLists.address, {"from": accounts[0]})

    #check with erc20 collateral
    with reverts("WL:Some assets are not enabled for collateral"):
        wrapper.wrap(wNFT, [dai_data], accounts[3], {"from": accounts[1], "value": eth_amount})

    #check without erc20 collateral - only native tokens
    wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1], "value": eth_amount})

    wTokenId = wrapper.lastWNFTId(out_type)[1]

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
    assert wrapper.balance() == eth_amount
    assert wnft721.ownerOf(wTokenId) == accounts[3]


