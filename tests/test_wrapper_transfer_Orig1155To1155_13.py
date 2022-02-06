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
out_nft_amount = 3
transfer_fee_amount = 100


#transfer with fee without royalty
def test_transfer(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20, erc1155mock1, whiteLists, techERC20, wrapperChecker):
    
    niftsy20.transfer(accounts[3], transfer_fee_amount, {"from": accounts[0]})    
    niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[3]})  
    logging.info("balance_acc3 = {}".format(niftsy20.balanceOf(accounts[3])))
    logging.info("balance_acc4 = {}".format(niftsy20.balanceOf(accounts[4])))

    
    #make 1155 token for wrapping
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapper.address,True, {"from": accounts[1]}) 

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})

    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    
    fee = [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
    lock = []
    royalty = [(wrapper.address, 9000), (accounts[4], 1000)]

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
    whiteLists.setWLItem(niftsy20.address, wl_data, {"from": accounts[0]})

    #wnft can be in collateral
    wl_data = (False, True, False, accounts[9])
    whiteLists.setWLItem(wnft1155.address, wl_data, {"from": accounts[0]})

    logging.info("wrap1*************************")
    wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

    assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount

    wTokenId = wrapper.lastWNFTId(out_type)[1]

    wnft1155.setApprovalForAll(wrapper.address, True, {"from": accounts[3]})

    logging.info("add wnft with transfer fee to collateral yourself*************************")
    wrapper.addCollateral(wnft1155.address, wTokenId, [((out_type, wnft1155.address), wTokenId, out_nft_amount)], {"from": accounts[3]})


    logging.info("balance_wrapper = {}".format(niftsy20.balanceOf(wrapper)))
    logging.info("balance_acc3 = {}".format(niftsy20.balanceOf(accounts[3])))
    logging.info("balance_acc4 = {}".format(niftsy20.balanceOf(accounts[4])))
    logging.info(wrapperChecker.getERC20CollateralBalance(wnft1155.address, wTokenId, niftsy20.address))
    assert wnft1155.balanceOf(wrapper.address, wTokenId) == out_nft_amount

    with reverts("ERC115 unwrap available only for all totalSupply"):
        wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]})