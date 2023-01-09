import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest1155, makeNFTForTest1155
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 4
out_type = 4
in_nft_amount = 3
out_nft_amount = 5
transfer_fee_amount = 100


#transfer with fee without royalty
def test_addCollateral(accounts, erc1155mock, wrapperLight, dai, weth, wnft1155ForWrapperLightV1, niftsy20, wrapperCheckerLightV1):
    
    #make 1155 token for wrapping
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapperLight.address, True, {"from": accounts[1]})

    if (wrapperLight.lastWNFTId(out_type)[1] == 0):
        wrapperLight.setWNFTId(out_type, wnft1155ForWrapperLightV1.address, 0, {'from':accounts[0]})

    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    
    fee = []
    lock = [(0x02, 2)]
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

    wTokenId = wrapperLight.lastWNFTId(out_type)[1]

    niftsy20.approve(wrapperLight.address, call_amount, {"from": accounts[0]})
    wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((2,niftsy20.address), 0, call_amount)], {"from": accounts[0]})

    dai.approve(wrapperLight.address, call_amount, {"from": accounts[0]})
    with reverts("Too much collateral slots for this wNFT"):
        wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((2,dai.address), 0, call_amount)], {"from": accounts[0], "value": "1 ether"})

    wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((2,dai.address), 0, call_amount)], {"from": accounts[0]})

    weth.approve(wrapperLight.address, call_amount, {"from": accounts[0]})
    with reverts("Too much collateral slots for this wNFT"):
        wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((2,weth.address), 0, call_amount)], {"from": accounts[0]})

    niftsy20.approve(wrapperLight.address, 2*call_amount, {"from": accounts[0]})
    wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((2,niftsy20.address), 0, 2*call_amount)], {"from": accounts[0]})    

    dai.approve(wrapperLight.address, 3*call_amount, {"from": accounts[0]})
    wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((2,dai.address), 0, 3*call_amount)], {"from": accounts[0]})

    assert niftsy20.balanceOf(wrapperLight.address) == 3*call_amount
    assert dai.balanceOf(wrapperLight.address) == 4*call_amount
    assert wrapperCheckerLightV1.getERC20CollateralBalance(wnft1155ForWrapperLightV1.address, wTokenId, niftsy20.address)[0] == 3*call_amount
    assert wrapperCheckerLightV1.getERC20CollateralBalance(wnft1155ForWrapperLightV1.address, wTokenId, dai.address)[0] == 4*call_amount

    with reverts("Too much collateral slots for this wNFT"):
        wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [], {"from": accounts[0], "value": "2 ether"})    

def test_addCollateral1(accounts, erc1155mock, wrapperLight, dai, weth, wnft1155ForWrapperLightV1, niftsy20, wrapperCheckerLightV1 ):
    erc1155mock.setApprovalForAll(wrapperLight.address, True, {"from": accounts[0]})

    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[1], in_nft_amount)

    fee = []
    lock = [(0x02, 2)]
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

    collateral = [((2, niftsy20.address), 0, call_amount), ((2, dai.address), 0, 2*call_amount)]
    dai.approve(wrapperLight.address, 2*call_amount, {"from": accounts[0]})
    niftsy20.approve(wrapperLight.address, call_amount, {"from": accounts[0]})

    with reverts("Too much collateral slots for this wNFT"):
        wrapperLight.wrap(wNFT, collateral, accounts[3], {"from": accounts[0], "value": "1 ether"})