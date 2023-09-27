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


def test_simple_wrap(accounts, erc721mock, wrapperUsers, dai, weth, wnft721SBT, niftsy20, hackERC20Users):
	#make test data
	dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
	weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})
	hackERC20Users.transfer(accounts[1], 3*call_amount, {"from": accounts[0]})

	dai.approve(wrapperUsers.address, call_amount, {'from':accounts[0]})
	weth.approve(wrapperUsers.address, 2*call_amount, {'from':accounts[0]})
	hackERC20Users.approve(wrapperUsers.address, 3*call_amount, {'from':accounts[0]})

	empty_data = ((0, zero_address), 0, 0)
	dai_data = ((2, dai.address), 0, Wei(call_amount))
	weth_data = ((2, weth.address), 0, Wei(2*call_amount))
	hackERC20Users_data = ((2, hackERC20Users.address), 0, Wei(3*call_amount))
	eth_data = ((1, zero_address), 0, Wei(eth_amount))

	fee = []
	lock = []
	royalty = []

	wNFT = ( empty_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		Web3.toBytes(0x0004)  #rules -  No Transfer
		)
	# hackERC20Users_data
	tx = wrapperUsers.wrapIn(wNFT, [dai_data, weth_data, hackERC20Users_data], accounts[3], wnft721SBT, {"from": accounts[0], "value": eth_amount})
	wTokenId = tx.return_value[1]

	#checks
	assert wrapperUsers.balance() == eth_amount
	assert dai.balanceOf(wrapperUsers) == call_amount
	assert weth.balanceOf(wrapperUsers) == 2*call_amount
	assert hackERC20Users.balanceOf(wrapperUsers) == 3*call_amount
	assert wnft721SBT.ownerOf(wTokenId) == accounts[3].address

	logging.info(tx.events['WrappedV1'])


	#add to wrapperUsers tokens
	dai.transfer(wrapperUsers.address, call_amount, {"from": accounts[0]})
	weth.transfer(wrapperUsers.address, 2*call_amount, {"from": accounts[0]})
	hackERC20Users.transfer(wrapperUsers.address, 3*call_amount, {"from": accounts[0]})

	#try to attack
	with reverts("ReentrancyGuard: reentrant call"):
		wrapperUsers.unWrap(3, wnft721SBT.address, wTokenId, {"from": accounts[3]})
	



	