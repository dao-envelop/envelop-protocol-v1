import pytest
import logging
from brownie import Wei, reverts, chain
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

def test_unwrap(accounts, erc721mock, wrapperUsers, dai, weth, wnft721SBT, niftsy20):
	
	erc721_property = (0, zero_address)

	erc721_data = (erc721_property, 0, 0)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, Wei(eth_amount))

	dai.approve(wrapperUsers.address, call_amount, {'from':accounts[0]})
	weth.approve(wrapperUsers.address, 2*call_amount, {'from':accounts[0]})

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
		Web3.toBytes(0x0004)  #rules - No Transfer
		)

	tx= wrapperUsers.wrapIn(wNFT, [eth_data, dai_data, weth_data], accounts[3], wnft721SBT,  {"from": accounts[0], "value": eth_amount})

	wTokenId = tx.return_value[1]
	wNFT = wrapperUsers.getWrappedToken(wnft721SBT, wTokenId)
	logging.info(wNFT[1])
	assert wNFT[1] == [eth_data, dai_data, weth_data]

	
	contract_eth_balance = wrapperUsers.balance()
	before_dai_balance = wNFT[1][1][2]
	before_weth_balance = wNFT[1][2][2]
	before_eth_balance = wNFT[1][0][2]
	before_acc_balance = accounts[3].balance()


	#unwrap by not owner and UnwrapDestination
	with reverts("Only owner can unwrap it"):
		wrapperUsers.unWrap(3, wnft721SBT.address, wTokenId, {"from": accounts[9]})

	#unwrap by UnwrapDestination
	with reverts("Only owner can unwrap it"):
		wrapperUsers.unWrap(3, wnft721SBT.address, wTokenId, {"from": accounts[2]})

	wrapperUsers.unWrap(3, wnft721SBT.address, wTokenId, {"from": accounts[3]})

	
	#checks
	assert wrapperUsers.balance() == 0
	assert accounts[3].balance() == before_acc_balance + contract_eth_balance
	assert dai.balanceOf(wrapperUsers) == 0
	assert weth.balanceOf(wrapperUsers) == 0
	assert dai.balanceOf(accounts[3]) == before_dai_balance
	assert weth.balanceOf(accounts[3]) == before_weth_balance
