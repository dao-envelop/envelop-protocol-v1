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



def test_call_factory(accounts, usersSBTRegistry, wrapperUsers, wnft721SBT, wnft1155SBT):
    usersSBTRegistry.addImplementation((3,wnft721SBT), {'from': accounts[0]})
    usersSBTRegistry.addImplementation((4,wnft1155SBT), {'from': accounts[0]})
    usersSBTRegistry.deployNewCollection(
        wnft721SBT, 
        accounts[0],'', '', '', wrapperUsers, {'from': accounts[0]}
    )

    logging.info(usersSBTRegistry.getUsersCollections(accounts[0]))
    assert len(usersSBTRegistry.getUsersCollections(accounts[0])) == 1


#try to wrap token which caller does not own
def test_wrap(accounts, erc721mock, wrapperUsers, wnft721SBT):
    
      
    #make 721 token for wrapping
    erc721mock.mint(ORIGINAL_NFT_IDs[0], {"from": accounts[1]})
    erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    
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
        Web3.toBytes(0x0004)  #rules - No Transfer
        )
    with reverts():
        tx = wrapperUsers.wrapIn(wNFT, [], accounts[3], wnft721SBT,  {"from": accounts[0]})
    #assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperUsers