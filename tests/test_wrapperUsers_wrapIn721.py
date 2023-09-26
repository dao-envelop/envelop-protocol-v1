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


def test_simple_wrap(accounts, erc721mock, wrapperUsers, dai, weth, wnft721SBT, niftsy20):
	#make test data
	erc721mock.mint(ORIGINAL_NFT_IDs[0], {"from": accounts[0]})

	erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[0], {'from':accounts[0]})

	dai.approve(wrapperUsers.address, call_amount, {'from':accounts[0]})
	weth.approve(wrapperUsers.address, 2*call_amount, {'from':accounts[0]})

	erc721_property = (in_type, erc721mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 0)
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, Wei(eth_amount))

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

	tx = wrapperUsers.wrapIn(wNFT, [dai_data, weth_data, eth_data], accounts[3], wnft721SBT,  {"from": accounts[0], "value": eth_amount})
	
	#checks
	assert wrapperUsers.balance() == eth_amount
	assert dai.balanceOf(wrapperUsers) == call_amount
	assert weth.balanceOf(wrapperUsers) == 2*call_amount
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperUsers.address
	assert wnft721SBT.ownerOf(wnft721SBT.tokenOfOwnerByIndex(accounts[3], 0)) == accounts[3].address
	logging.info(wnft721SBT.totalSupply())
	logging.info(wnft721SBT.tokenOfOwnerByIndex(accounts[3], 0))
	#assert wnft721SBT.totalSupply() == 1
	logging.info(tx.return_value)

	wTokenId = tx.return_value[1]
	wNFT = wrapperUsers.getWrappedToken(wnft721SBT, wTokenId)
	assert wNFT[0] == erc721_data
	assert wNFT[1] == [eth_data, dai_data, weth_data]
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0005'

	erc721_property = (0, zero_address)

	erc721_data = (erc721_property, 0, 0)

	fee = []
	lock = []
	royalty = []

	tx = wNFT = ( erc721_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		Web3.toBytes(0x0005)  #rules - NO Unwrap, No Transfer
		)

	tx= wrapperUsers.wrapIn(wNFT, [], accounts[3], wnft721SBT,  {"from": accounts[0]})

	wTokenId = tx.return_value[1]
	wNFT = wrapperUsers.getWrappedToken(wnft721SBT, wTokenId)
	#logging.info(wNFT)
	assert wNFT[0] == erc721_data
	assert wNFT[1] == []
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0005'
