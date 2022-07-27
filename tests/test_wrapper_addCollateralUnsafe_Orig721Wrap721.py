import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

def test_addCollateral(accounts, erc721mock, wrapperTrusted, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1, whiteLists, techERC20ForTrustedWrapper):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapperTrusted.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapperTrusted.lastWNFTId(out_type)[1] == 0):
        wrapperTrusted.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperTrusted.address, {"from": accounts[0]})

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

    #switch on white list
    wrapperTrusted.setWhiteList(whiteLists.address, {"from": accounts[0]})

    wrapperTrusted.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
    wTokenId = wrapperTrusted.lastWNFTId(out_type)[1]

    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    dai.approve(wrapperTrusted.address, call_amount, {'from':accounts[1]})
    dai_property = (2, dai.address)
    dai_data = (dai_property, 0, Wei(call_amount))

    with reverts("WL:Some assets are not enabled for collateral"):
        wrapperTrusted.addCollateral(wnft721.address, wTokenId, [dai_data], {"from": accounts[1]})

    with reverts("Only trusted address"):
        wrapperTrusted.addCollateralUnsafe(wnft721.address, wTokenId, [], {"from": accounts[9], "value": eth_amount})

    wrapperTrusted.setTrustedAddres(accounts[1], True, {"from": accounts[0]})
    wl_data = (False, True, False, techERC20ForTrustedWrapper.address)
    whiteLists.setWLItem((2, dai.address), wl_data, {"from": accounts[0]})
    wrapperTrusted.addCollateralUnsafe(wnft721.address, wTokenId, [dai_data], {"from": accounts[1], "value": eth_amount})



    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperTrusted.address
    assert wrapperTrusted.balance() == eth_amount
    assert dai.balanceOf(wrapperTrusted.address) == call_amount
    assert wnft721.ownerOf(wTokenId) == accounts[3]


