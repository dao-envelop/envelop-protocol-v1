import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721
from web3 import Web3


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [1,2,3,4, 5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22, 23, 24, 25, 26, 27]
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


def test_addColl(accounts, erc721mock, wrapperUsers, wnft721SBT, niftsy20, erc721mock1):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    
    #make wrap NFT 721erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[0], {'from':accounts[0]})
    erc721mock.transferFrom(accounts[1], accounts[0], ORIGINAL_NFT_IDs[0], {"from": accounts[1]})
    erc721mock.approve(wrapperUsers, ORIGINAL_NFT_IDs[0], {"from": accounts[0]})

    erc721_property = (in_type, erc721mock.address)
    
    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 0)

    fee = []
    lock = []
    royalty = []

    wNFT = ( erc721_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        Web3.toBytes(0x0005)  #rules - NO Unwrap, No Transfer
        )

    tx = wrapperUsers.wrapIn(wNFT, [], accounts[3], wnft721SBT,  {"from": accounts[0]})
    wTokenId = tx.return_value[1]

    
    #PREPARE DATA
    #make 721 for collateral
    i = 1
    while i < wrapperUsers.MAX_COLLATERAL_SLOTS()+2:
        erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[i], {"from": accounts[0]} )
        if (i == wrapperUsers.MAX_COLLATERAL_SLOTS()+1):
            with reverts("Too much tokens in collateral"):    
                wrapperUsers.addCollateral(wnft721SBT.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[i], 0)], {'from': accounts[0]})
        else:
            wrapperUsers.addCollateral(wnft721SBT.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[i], 0)], {'from': accounts[0]})
        collateral = wrapperUsers.getWrappedToken(wnft721SBT, wTokenId)[1]
        i += 1

    collateral = wrapperUsers.getWrappedToken(wnft721SBT, wTokenId)[1]

    i = 1
    while i < wrapperUsers.MAX_COLLATERAL_SLOTS()+1:
        assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[i]) == wrapperUsers.address
        assert collateral[i-1] == ((3, erc721mock.address), ORIGINAL_NFT_IDs[i], 0)
        i += 1
    


