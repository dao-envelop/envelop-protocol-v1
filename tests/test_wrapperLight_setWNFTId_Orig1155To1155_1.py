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
def test_transfer(accounts, erc1155mock, wrapperLight, wnft1155ForWrapperLightV1, niftsy20, wnft1155ForWrapperLightV1_1):

    #make 1155 token for wrapping
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapperLight.address, True, {"from": accounts[1]})

    if (wrapperLight.lastWNFTId(out_type)[1] == 0):
        wrapperLight.setWNFTId(out_type, wnft1155ForWrapperLightV1.address, 0, {'from':accounts[0]})

    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    
    fee = [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
    lock = []
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

    assert erc1155mock.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount
    wTokenId = wrapperLight.lastWNFTId(out_type)[1]
    assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId) == out_nft_amount

    erc1155mock.safeTransferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], in_nft_amount, "", {"from": accounts[0]})
    token_data = (token_property, ORIGINAL_NFT_IDs[1], in_nft_amount-1)

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
    assert erc1155mock.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[1]) == in_nft_amount-1
    wTokenId = wrapperLight.lastWNFTId(out_type)[1]
    assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId) == out_nft_amount

    #switch on new wnft1155ForWrapperLightV1
    wrapperLight.setWNFTId(out_type, wnft1155ForWrapperLightV1_1.address, 0, {'from':accounts[0]})

    erc1155mock.safeTransferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[2], in_nft_amount, "", {"from": accounts[0]})
    token_data = (token_property, ORIGINAL_NFT_IDs[2], in_nft_amount-2)

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

    assert erc1155mock.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[2]) == in_nft_amount-2
    wTokenId = wrapperLight.lastWNFTId(out_type)[1]
    assert wnft1155ForWrapperLightV1_1.balanceOf(accounts[3], wTokenId) == out_nft_amount



    niftsy20.transfer(accounts[3], transfer_fee_amount, {"from": accounts[0]})
    niftsy20.approve(wrapperLight.address, transfer_fee_amount, {"from": accounts[3]})
    wnft1155ForWrapperLightV1.safeTransferFrom(accounts[3], accounts[2], 1, out_nft_amount, "",  {"from": accounts[3]})

    assert wnft1155ForWrapperLightV1.balanceOf(accounts[2], 1) == out_nft_amount

    wrapperLight.unWrap(out_type, wnft1155ForWrapperLightV1.address, 1, {"from": accounts[2]})
    wrapperLight.unWrap(out_type, wnft1155ForWrapperLightV1.address, 2, {"from": accounts[3]})
    wrapperLight.unWrap(out_type, wnft1155ForWrapperLightV1_1.address, 1, {"from": accounts[3]})

    assert erc1155mock.balanceOf(accounts[2], ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert erc1155mock.balanceOf(accounts[3], ORIGINAL_NFT_IDs[1]) == in_nft_amount-1
    assert erc1155mock.balanceOf(accounts[3], ORIGINAL_NFT_IDs[2]) == in_nft_amount-2

