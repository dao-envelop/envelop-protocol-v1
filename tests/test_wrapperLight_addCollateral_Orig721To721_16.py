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
def test_transfer(accounts, erc721mock, wrapperLight, wnft721ForWrapperLightV1, niftsy20):
    
    niftsy20.transfer(accounts[3], 2*transfer_fee_amount, {"from": accounts[0]})    
    niftsy20.approve(wrapperLight.address, transfer_fee_amount, {"from": accounts[3]})  


    
    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapperLight.lastWNFTId(out_type)[1] == 0):
        wrapperLight.setWNFTId(out_type, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    
    fee = [] #[(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address), (Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
    lock = []
    royalty = [] #[(accounts[4], 9000), (accounts[4], 1000)]

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

    niftsy20.approve(wrapperLight.address, 2*transfer_fee_amount, {"from": accounts[3]})
    wTokenId = wrapperLight.lastWNFTId(out_type)[1]

    wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, niftsy20.address), 0, transfer_fee_amount)], {"from": accounts[3]})
    with reverts("TokenId must be zero"):
        wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, niftsy20.address), 1, transfer_fee_amount)], {"from": accounts[3]})

    #wnft721ForWrapperLightV1.transferFrom(accounts[3], accounts[4], wTokenId, {"from": accounts[3]})
    wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, {"from": accounts[3]})

    logging.info(wrapperLight.getWrappedToken(wnft721ForWrapperLightV1.address, wTokenId))

    logging.info(niftsy20.balanceOf(accounts[4]))


   