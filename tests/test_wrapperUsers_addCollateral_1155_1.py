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
in_type = 4
out_type = 4
in_nft_amount = 3
out_nft_amount = 3
transfer_fee_amount = 100



def test_call_factory(accounts, usersSBTRegistry, wrapperUsers, wnft721SBT, wnft1155SBT):
    usersSBTRegistry.addImplementation((3,wnft721SBT), {'from': accounts[0]})
    usersSBTRegistry.addImplementation((4,wnft1155SBT), {'from': accounts[0]})
    usersSBTRegistry.deployNewCollection(
        wnft1155SBT, 
        accounts[0],'', '', '', wrapperUsers, {'from': accounts[0]}
    )

    logging.info(usersSBTRegistry.getUsersCollections(accounts[0]))
    assert len(usersSBTRegistry.getUsersCollections(accounts[0])) == 1


#transfer with fee without royalty
def test_transfer(accounts, erc1155mock, wrapperUsers, wnft1155SBT, niftsy20):

    erc1155mock.mintBatch(
        accounts[0], 
        ORIGINAL_NFT_IDs,
        [in_nft_amount,in_nft_amount,in_nft_amount],
        '',
        {"from": accounts[0]})

    erc1155mock.setApprovalForAll(wrapperUsers.address,True, {"from": accounts[0]})


    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    
    fee = []
    lock = []
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        Web3.toBytes(0x0004)  #rules - No Transfer
        )


    tx = wrapperUsers.wrapIn(wNFT, [], accounts[0], wnft1155SBT,  {"from": accounts[0]})
    wTokenId = tx.return_value[1]

    assert erc1155mock.balanceOf(wrapperUsers.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount

    wnft1155SBT.setApprovalForAll(wrapperUsers.address, True, {"from": accounts[0]})

    logging.info("add wnft with transfer fee to collateral yourself*************************")
    with reverts('Trasfer was disabled by author'):
        wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((out_type, wnft1155SBT.address), wTokenId, out_nft_amount)], {"from": accounts[0]})

    assert wnft1155SBT.balanceOf(wrapperUsers.address, wTokenId) == 0
