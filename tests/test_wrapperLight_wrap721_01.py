import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721
from web3 import Web3


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3


def wnft_pretty_print(_wrapper, _wnft721, _wTokenId):
    logging.info(
        '\n=========wNFT=============\nwNFT:{0},{1}\nInAsset: {2}\nCollrecords:\n{3}\nunWrapDestination: {4}'
        '\nFees: {5} \nLocks: {6} \nRoyalty: {7} \nrules: {8}({9:0>16b}) \n=========================='.format(
        _wnft721, _wTokenId,
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[0],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[1],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[2],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[3],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[4],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[5],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[6],
        Web3.toInt(_wrapper.getWrappedToken(_wnft721, _wTokenId)[6]),
        
    ))

def test_simple_wrap(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapperLight.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapperLight.address, 2*call_amount, {'from':accounts[1]})

    wrapperLight.setWNFTId(out_type, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})

    erc721_property = (in_type, erc721mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    eth_property = (1, zero_address)

    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 1)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = (eth_property, 0, Wei(eth_amount))

    fee = []
    lock = [('0x0', chain.time() + 10), ('0x0', chain.time() + 20)]
    royalty = []

    wNFT = ( erc721_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    wrapperLight.wrap(wNFT, [dai_data, weth_data, eth_data], accounts[3], {"from": accounts[1], "value": eth_amount})
    wTokenId = wrapperLight.lastWNFTId(out_type)[1]
    wNFT = wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)   
    wnft_pretty_print(wrapperLight, wnft721ForWrapperLightV1, wTokenId)
    #checks
    assert wrapperLight.balance() == eth_amount
    assert dai.balanceOf(wrapperLight) == call_amount
    assert weth.balanceOf(wrapperLight) == 2*call_amount
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
    assert wnft721ForWrapperLightV1.ownerOf(wrapperLight.lastWNFTId(out_type)[1]) == accounts[3].address
    assert wnft721ForWrapperLightV1.totalSupply() == 1

    #logging.info(wNFT)
    assert wNFT[0] == erc721_data
    assert wNFT[1] == [eth_data, dai_data, weth_data]
    assert wNFT[2] == zero_address
    assert wNFT[3] == fee
    assert wNFT[4] == lock
    assert wNFT[5] == royalty
    assert wNFT[6] == '0x0' 
    
    with reverts("TimeLock error"):
        wrapperLight.unWrap(3, wnft721ForWrapperLightV1, wTokenId, {'from': accounts[3]})

    chain.sleep(250)
    chain.mine()

    wrapperLight.unWrap(3, wnft721ForWrapperLightV1, wTokenId, {'from': accounts[3]})
        
