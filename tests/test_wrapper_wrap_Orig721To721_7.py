import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3
in_nft_amount = 3

def test_wrap(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1, whiteLists):
    #make wrap NFT with empty
    

    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

    token_property = (in_type, erc721mock)
    dai_property = (2, dai.address)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    dai_data = (dai_property, 0, Wei(call_amount))

    fee = []
    lock = []
    royalty = []

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

    with reverts("WL:Some assets are not enabled for collateral"):
        wrapper.wrap(wNFT, [dai_data], accounts[3], {"from": accounts[1], "value": eth_amount})

    wl_data = (False, False, False, accounts[9])
    tx=whiteLists.setWLItem(dai.address, wl_data, {"from": accounts[0]})
    logging.info('Events from DAI WL set:{}'.format(tx.events))
    with reverts("WL:Some assets are not enabled for collateral"):
        wrapper.wrap(wNFT, [dai_data], accounts[3], {"from": accounts[1], "value": eth_amount})

    #there is other allowed token for collateral
    wl_data = (False, True, False,accounts[9])
    whiteLists.setWLItem(weth.address, wl_data, {"from": accounts[0]})   
    with reverts("WL:Some assets are not enabled for collateral"):
        wrapper.wrap(wNFT, [dai_data], accounts[3], {"from": accounts[1], "value": eth_amount}) 

    wl_data = (False, True, False, accounts[9])
    whiteLists.setWLItem(dai.address, wl_data, {"from": accounts[0]})

    whiteLists.setWLItem(erc721mock1.address, wl_data, {"from": accounts[0]})
    whiteLists.setWLItem(erc1155mock1.address, wl_data, {"from": accounts[0]})

    wrapper.wrap(wNFT, [dai_data], accounts[3], {"from": accounts[1], "value": eth_amount})    
    wTokenId = wrapper.lastWNFTId(out_type)[1]

    assert dai.balanceOf(wrapper.address) == call_amount
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
    assert wrapper.balance() == eth_amount
    assert wnft721.ownerOf(wTokenId) == accounts[3]
    assert whiteLists.getWLItem(dai.address)[0] == False
    assert whiteLists.getWLItem(dai.address)[1] == True
    assert whiteLists.getWLItem(dai.address)[2] == False
    assert whiteLists.getWLItem(dai.address)[3] == accounts[9]
    #assert len(whiteLists.listAssets()) == 4
    #logging.info(whiteLists.listAssets())

def test_wrap1(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1, whiteLists):
    with reverts("Ownable: caller is not the owner"):
        whiteLists.removeWLItem(dai.address, {"from": accounts[1]})

    whiteLists.removeWLItem(dai.address, {"from": accounts[0]})
    dai.transfer(accounts[1], call_amount+1, {"from": accounts[0]})
    dai.approve(wrapper.address, call_amount+1, {'from':accounts[1]})
    wTokenId = wrapper.lastWNFTId(out_type)[1]

    dai_property = (2, dai.address)
    dai_data = (dai_property, 0, Wei(call_amount+1))

    with reverts("WL:Some assets are not enabled for collateral"):
        wrapper.addCollateral(wnft721.address, wTokenId, [dai_data], {"from": accounts[1]})

    #assert len(whiteLists.listAssets()) == 3
    #logging.info(whiteLists.listAssets())

    wl_data = (False, True, False, accounts[9])
    whiteLists.setWLItem(dai.address, wl_data, {"from": accounts[0]})

    wrapper.addCollateral(wnft721.address, wTokenId, [dai_data], {"from": accounts[1]})

    assert dai.balanceOf(wrapper.address) == 2*call_amount+1

    #delete last element in array
    whiteLists.removeWLItem(dai.address, {"from": accounts[0]})




