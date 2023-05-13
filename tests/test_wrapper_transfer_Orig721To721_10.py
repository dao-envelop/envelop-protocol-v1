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
def test_transfer(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1, whiteLists, techERC20, wrapperChecker):
    
    niftsy20.transfer(accounts[3], transfer_fee_amount, {"from": accounts[0]})    
    niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[3]})  
    logging.info("balance_acc3 = {}".format(niftsy20.balanceOf(accounts[3])))
    logging.info("balance_acc4 = {}".format(niftsy20.balanceOf(accounts[4])))

    
    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    
    fee = [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
    lock = []
    royalty = [(wrapper.address, 9000), (accounts[4], 1000)]

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

    #transferFee flag is switched on
    wl_data = (True, False, False, techERC20.address)
    whiteLists.setWLItem((2, niftsy20.address), wl_data, {"from": accounts[0]})

    logging.info("wrap1*************************")
    wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

    logging.info("balance_acc3 = {}".format(niftsy20.balanceOf(accounts[3])))
    logging.info("balance_acc4 = {}".format(niftsy20.balanceOf(accounts[4])))

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address

    wTokenId = wrapper.lastWNFTId(out_type)[1]

    wnft721.approve(wrapper.address, wTokenId, {"from": accounts[3]})


    token_property = (in_type, wnft721.address)

    token_data = (token_property, wTokenId, 0)


    fee = [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
    lock = []
    royalty = [(wrapper.address, 9000), (accounts[4], 1000)]

    wNFT = ( token_data,
        accounts[3],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )
    logging.info("wrap2*************************")
    wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[3]})

    logging.info("balance_wrapper = {}".format(niftsy20.balanceOf(wrapper)))
    logging.info("balance_acc3 = {}".format(niftsy20.balanceOf(accounts[3])))
    logging.info("balance_acc4 = {}".format(niftsy20.balanceOf(accounts[4])))
    logging.info(wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId, niftsy20.address))

    wTokenId = wrapper.lastWNFTId(out_type)[1]

    logging.info("unwrap1*************************")
    wrapper.unWrap(out_type, wnft721.address, wTokenId, {"from": accounts[3]})

    logging.info("balance_wrapper = {}".format(niftsy20.balanceOf(wrapper)))

    logging.info("balance_acc2 = {}".format(niftsy20.balanceOf(accounts[2])))
    logging.info("balance_acc3 = {}".format(niftsy20.balanceOf(accounts[3])))
    logging.info("balance_acc4 = {}".format(niftsy20.balanceOf(accounts[4])))

    logging.info("collateral = {}".format(wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId-1, niftsy20.address)))


    logging.info("add niftsy balance to wrapper 200")
    niftsy20.transfer(wrapper.address, 2*transfer_fee_amount, {"from": accounts[0]})   

    logging.info("unwrap2*************************")
    wrapper.unWrap(out_type, wnft721.address, wTokenId-1, {"from": accounts[3]}) 

    logging.info("balance_wrapper = {}".format(niftsy20.balanceOf(wrapper)))

    logging.info("balance_acc2 = {}".format(niftsy20.balanceOf(accounts[2])))
    logging.info("balance_acc3 = {}".format(niftsy20.balanceOf(accounts[3])))
    logging.info("balance_acc4 = {}".format(niftsy20.balanceOf(accounts[4])))

    assert niftsy20.balanceOf(accounts[4]) + niftsy20.balanceOf(accounts[3]) == transfer_fee_amount
    assert niftsy20.balanceOf(wrapper.address) == 2*transfer_fee_amount
    assert niftsy20.balanceOf(accounts[2]) == 0