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
in_type = 4
out_type = 4
in_nft_amount = 3
out_nft_amount = 5
transfer_fee_amount = 1


#transfer with fee without royalty
def test_transfer(accounts, erc1155mock, wrapperLight, wnft1155ForWrapperLightV1, erc721mock):

    #make 1155 token for wrapping
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapperLight.address,True,  {"from": accounts[1]})

    #make 721 token for transfer fee
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.transferFrom(accounts[0], accounts[3], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[1], {"from": accounts[3]})


    if (wrapperLight.lastWNFTId(out_type)[1] == 0):
        wrapperLight.setWNFTId(out_type, wnft1155ForWrapperLightV1.address, 0, {'from':accounts[0]})

    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    
    fee = [(Web3.toBytes(0x00), transfer_fee_amount, erc721mock.address)]
    lock = []
    royalty = [(wrapperLight.address, 10000)]

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )


    tx = wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

    assert erc1155mock.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount

    wTokenId = wrapperLight.lastWNFTId(out_type)[1]


    #fee is erc721 token. It is absurd, but we check the case
    wnft1155ForWrapperLightV1.safeTransferFrom(accounts[3], accounts[2], wTokenId, out_nft_amount, "",  {"from": accounts[3]})

    assert wnft1155ForWrapperLightV1.balanceOf(accounts[2], wTokenId) == out_nft_amount