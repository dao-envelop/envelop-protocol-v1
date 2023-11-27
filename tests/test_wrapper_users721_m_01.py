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

#owner case - only owner can create sbt!

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

def test_check_mock_registry(accounts, usersSBTRegistry, wrapperUsers, wnft721SBT, wnft1155SBT):
    usersSBTRegistry.addImplementation((3,wnft721SBT), {'from': accounts[0]})
    usersSBTRegistry.addImplementation((4,wnft1155SBT), {'from': accounts[0]})
    usersSBTRegistry.deployNewCollection(
        wnft721SBT, 
        accounts[1],'', '', '', wrapperUsers, {'from': accounts[0]}
    )

    usersSBTRegistry.deployNewCollection(
        wnft1155SBT, 
        accounts[1],'', '', '', wrapperUsers, {'from': accounts[0]}
    )
    logging.info(usersSBTRegistry.getUsersCollections(accounts[0]))
    assert len(usersSBTRegistry.getUsersCollections(accounts[1])) == 2


def test_wNFTType (accounts, usersSBTRegistry, wrapperUsers, wnft721SBT, wnft1155SBT, erc721mock):
    nfttype721 = wrapperUsers.getNFTType(wnft721SBT, 0);
    nfttype1155 = wrapperUsers.getNFTType(wnft1155SBT, 0);
    logging.info('721: {}, 1155: {}'.format(nfttype721, nfttype1155))
    assert nfttype721 == 3
    assert nfttype1155 == 4

def test_check_wrap_721(accounts, usersSBTRegistry, wrapperUsers, wnft721SBT, wnft1155SBT, erc721mock):
     #without possible rules
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    token_data = ((in_type, erc721mock), ORIGINAL_NFT_IDs[0], 0)
    
    fee = []
    lock = []
    royalty = []

    indata = ( 
        token_data,   # inAsset
        accounts[2],  # unWrapDestinition
        fee,
        lock,
        royalty,
        out_type,
        0,            # outBalance
        Web3.toBytes(0x0005)  #rules - NO Unwrap, No Transfer
    )

    with reverts(''):
        # This revert mean that used Registry has no 
        # isWrapEnabled method implementation
        wrapperUsers.wrapIn(indata, [], accounts[3], wnft721SBT, {"from": accounts[0]})
    
    tx = wrapperUsers.wrapIn(indata, [], accounts[3], wnft721SBT, {"from": accounts[1]})
    logging.info(tx.return_value)
    assert wnft721SBT.balanceOf(accounts[3]) == 1
    assert wnft721SBT.totalSupply() == 1

def test_rules_721(accounts, wrapperUsers, wnft721SBT, erc721mock):
    with reverts('Transfer was disabled by author'):
        wnft721SBT.transferFrom(accounts[3], accounts[0], 0, {'from': accounts[3]})
    with reverts('UnWrap was disabled by author'):    
        wrapperUsers.unWrap(wnft721SBT, 0, {'from': accounts[3]})

def test_add_collateral(accounts, wrapperUsers, wnft721SBT, erc721mock, niftsy20):
    coll = [((2, niftsy20.address), 0, 1e18)]
    niftsy20.transfer(accounts[1], 1e18, {"from": accounts[0]})
    niftsy20.approve(wrapperUsers.address, 1e18, {"from": accounts[0]})
    wrapperUsers.addCollateral(wnft721SBT,0, coll, {"from": accounts[0]})
    with reverts('Only wNFT contract owner able to add collateral'):
        wrapperUsers.addCollateral(wnft721SBT,0, coll, {"from": accounts[1]})

def test_check_wrap_721_unwrap(
    accounts, 
    usersSBTRegistry, 
    wrapperUsers, wnft721SBT, wnft1155SBT, erc721mock, niftsy20):
     #without possible rules
    #makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[1], {"from": accounts[1]})

    token_data = ((in_type, erc721mock), ORIGINAL_NFT_IDs[1], 0)
    
    fee = []
    lock = []
    royalty = []

    indata = ( 
        token_data,   # inAsset
        accounts[2],  # unWrapDestinition
        fee,
        lock,
        royalty,
        out_type,
        0,            # outBalance
        Web3.toBytes(0x0004)  #rules - NO Unwrap, No Transfer
    )
    tx = wrapperUsers.wrapIn(indata, [], accounts[3], wnft721SBT, {"from": accounts[1]})
    coll = [((2, niftsy20.address), 0, 1e18)]
    niftsy20.transfer(accounts[1], 1e18, {"from": accounts[0]})
    niftsy20.approve(wrapperUsers.address, 1e18, {"from": accounts[0]})
    wrapperUsers.addCollateral(wnft721SBT,1, coll, {"from": accounts[0]})
    logging.info(tx.return_value)
    with reverts('Only owner can unwrap it'):
        tx = wrapperUsers.unWrap(wnft721SBT, 1, {'from': accounts[0]})
    tx = wrapperUsers.unWrap(wnft721SBT, 1, {'from': accounts[3]})
    logging.info(tx.events)
    assert wnft721SBT.balanceOf(accounts[3]) == 1

