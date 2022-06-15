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

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    
    fee = [(0x00, transfer_fee_amount, niftsy20.address)]
    lock = [('0x02', 0)]
    royalty = [(wrapper.address, 10000)]

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        Web3.toBytes(0x0000)
        )


    #switch on white list
    wrapper.setWhiteList(whiteLists.address, {"from": accounts[0]})
    
    wl_data = (True, True, False, techERC20.address)
    whiteLists.setWLItem((2, niftsy20.address), wl_data, {"from": accounts[0]})

    wrapper.wrap(wNFT, [], accounts[2], {"from": accounts[1]})

    niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[2]})

    niftsy20.transfer(accounts[2], transfer_fee_amount, {"from": accounts[0]})
    wTokenId = wrapper.lastWNFTId(3)[1]

    with reverts('Too much collateral slots for this wNFT'):
        wnft721.transferFrom(accounts[2], accounts[1], wTokenId, {"from": accounts[2]})


    #next token
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[1], 0)
    
    fee = [(0x00, transfer_fee_amount, niftsy20.address)]
    lock = [('0x02', 2)]
    royalty = [(wrapper.address, 10000)]

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        Web3.toBytes(0x0000)
        )


    #switch on white list
    wrapper.setWhiteList(whiteLists.address, {"from": accounts[0]})
    
    wl_data = (True, True, False, techERC20.address)
    whiteLists.setWLItem((2, niftsy20.address), wl_data, {"from": accounts[0]})
    whiteLists.setWLItem((2, dai.address), wl_data, {"from": accounts[0]})
    whiteLists.setWLItem((2, weth.address), wl_data, {"from": accounts[0]})

    wrapper.wrap(wNFT, [], accounts[2], {"from": accounts[0]})
    wTokenId = wrapper.lastWNFTId(3)[1]

    wrapper.addCollateral(wnft721.address, wTokenId, [((2, niftsy20.address), 0, 0)], {"from": accounts[0]})

    dai.approve(wrapper.address, 1e18, {"from": accounts[0]})
    wrapper.addCollateral(wnft721.address, wTokenId, [((2, dai.address), 0, 1e18)], {"from": accounts[0]})

    weth.approve(wrapper.address, 1e18, {"from": accounts[0]})
    with reverts('Too much collateral slots for this wNFT'):
         wrapper.addCollateral(wnft721.address, wTokenId, [((2, weth.address), 0, 1e18)], {"from": accounts[0]})

    logging.info(wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0))
    logging.info(wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, dai.address, 0))

    
    niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[2]})

    niftsy20.transfer(accounts[2], transfer_fee_amount, {"from": accounts[0]})
    wTokenId = wrapper.lastWNFTId(3)[1]

    with reverts("Too much collateral slots for this wNFT"):
        wnft721.transferFrom(accounts[2], accounts[1], wTokenId, {"from": accounts[2]})




    