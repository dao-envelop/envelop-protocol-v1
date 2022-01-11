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
def test_wrap(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1, whiteLists, techERC20):
    #make wrap NFT with empty
    

    
    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    
    fee = [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
    lock = []
    royalty = [(wrapper.address, 10000)]

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

    with reverts("WL:Some assets are not enabled for fee"):
        wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
    
    wl_data = (False, False, False, techERC20.address)
    whiteLists.setWLItem(niftsy20.address, wl_data, {"from": accounts[0]})

    with reverts("WL:Some assets are not enabled for fee"):
        wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

    #transferFee flag is switched on
    wl_data = (True, False, False, techERC20.address)
    whiteLists.setWLItem(niftsy20.address, wl_data, {"from": accounts[0]})

    
    wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address

    niftsy20.transfer(accounts[3], transfer_fee_amount, {"from": accounts[0]})

    wTokenId = wrapper.lastWNFTId(out_type)[1]

    niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[3]})
    wnft721.transferFrom(accounts[3], accounts[2], wTokenId, {"from": accounts[3]})

    logging.info(niftsy20.balanceOf(accounts[3]))
    logging.info(niftsy20.balanceOf(wrapper.address))
    logging.info(wrapper.protocolWhiteList())
    fees = wrapper.getWrappedToken(wnft721.address, wTokenId)[3]
    royalty = wrapper.getWrappedToken(wnft721.address, wTokenId)[5]
    logging.info(fees[0][0])
    logging.info(fees[0][1])
    logging.info(fees[0][2])
    logging.info(royalty)
    logging.info(whiteLists.getWLItem(fees[0][2])[3])
    logging.info(techERC20.address)
    logging.info(techERC20.getTransfersList(fees[0], royalty, accounts[3], accounts[2]))



    