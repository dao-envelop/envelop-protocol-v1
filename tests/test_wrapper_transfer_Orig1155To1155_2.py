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
def test_transfer(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20, whiteLists, techERC20, wrapperChecker):
    
    #make 1155 token for wrapping
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapper.address, True, {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})

    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    
    fee = [(Web3.toBytes(0x00), transfer_fee_amount, techERC20.address)]
    lock = []
    royalty = [(wrapper.address, 10000)]

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )


    #switch on white list
    wrapper.setWhiteList(whiteLists.address, {"from": accounts[0]})

    #transferFee flag is switched on
    wl_data = (True, False, False, techERC20.address)
    whiteLists.setWLItem(techERC20.address, wl_data, {"from": accounts[0]})

    wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

    assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount 

    wTokenId = wrapper.lastWNFTId(out_type)[1]


    wnft1155.safeTransferFrom(accounts[3], accounts[2], wTokenId, out_nft_amount, "", {"from": accounts[3]})
    assert techERC20.balanceOf(accounts[3]) == 0
    assert techERC20.balanceOf(wrapper.address) == transfer_fee_amount
    assert wrapperChecker.getERC20CollateralBalance(wnft1155.address, wTokenId, techERC20.address)[0] == transfer_fee_amount

    assert wnft1155.balanceOf(accounts[2], wTokenId) == out_nft_amount 
    assert wnft1155.balanceOf(accounts[3], wTokenId) == 0





    