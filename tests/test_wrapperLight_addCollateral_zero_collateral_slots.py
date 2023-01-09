import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3
in_nft_amount = 3
transfer_fee_amount = 100


#transfer with fee without royalty
def test_transfer(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20, wrapperCheckerLightV1):

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapperLight.lastWNFTId(out_type)[1] == 0):
        wrapperLight.setWNFTId(out_type, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    
    fee = [(0x00, transfer_fee_amount, niftsy20.address)]
    lock = [('0x02', 0)]
    royalty = [(wrapperLight.address, 10000)]

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        Web3.toBytes(0x0000)
        )


    wrapperLight.wrap(wNFT, [], accounts[2], {"from": accounts[1]})

    niftsy20.approve(wrapperLight.address, transfer_fee_amount, {"from": accounts[2]})

    niftsy20.transfer(accounts[2], transfer_fee_amount, {"from": accounts[0]})
    wTokenId = wrapperLight.lastWNFTId(3)[1]

    wnft721ForWrapperLightV1.transferFrom(accounts[2], accounts[1], wTokenId, {"from": accounts[2]})


    #next token
    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[1], 0)
    
    fee = [(0x00, transfer_fee_amount, niftsy20.address)]
    lock = [('0x02', 2)]
    royalty = [(wrapperLight.address, 10000)]

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        Web3.toBytes(0x0000)
        )


    wrapperLight.wrap(wNFT, [], accounts[2], {"from": accounts[0]})
    wTokenId = wrapperLight.lastWNFTId(3)[1]

    wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, niftsy20.address), 0, 0)], {"from": accounts[0]})

    dai.approve(wrapperLight.address, 1e18, {"from": accounts[0]})
    wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, dai.address), 0, 1e18)], {"from": accounts[0]})

    weth.approve(wrapperLight.address, 1e18, {"from": accounts[0]})
    with reverts('Too much collateral slots for this wNFT'):
         wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, weth.address), 0, 1e18)], {"from": accounts[0]})

    logging.info(wrapperLight.getCollateralBalanceAndIndex(wnft721ForWrapperLightV1.address, wTokenId, 2, niftsy20.address, 0))
    logging.info(wrapperLight.getCollateralBalanceAndIndex(wnft721ForWrapperLightV1.address, wTokenId, 2, dai.address, 0))

    
    niftsy20.approve(wrapperLight.address, transfer_fee_amount, {"from": accounts[2]})

    niftsy20.transfer(accounts[2], transfer_fee_amount, {"from": accounts[0]})
    wTokenId = wrapperLight.lastWNFTId(3)[1]

    wnft721ForWrapperLightV1.transferFrom(accounts[2], accounts[1], wTokenId, {"from": accounts[2]})


    assert dai.balanceOf(wrapperLight.address) == 1e18
    assert len(wrapperLight.getWrappedToken(wnft721ForWrapperLightV1.address, wTokenId)[1]) == 2
    assert wrapperLight.getCollateralBalanceAndIndex(wnft721ForWrapperLightV1.address, wTokenId, 2, dai.address, 0)[0] == 1e18
    assert wrapperLight.getCollateralBalanceAndIndex(wnft721ForWrapperLightV1.address, wTokenId, 2, dai.address, 0)[1] == 1




    