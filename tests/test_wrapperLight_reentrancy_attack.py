import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3


def test_simple_wrap(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20, hackERC20LightV1):
	#make test data
	dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
	weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})
	hackERC20LightV1.transfer(accounts[1], 3*call_amount, {"from": accounts[0]})

	dai.approve(wrapperLight.address, call_amount, {'from':accounts[1]})
	weth.approve(wrapperLight.address, 2*call_amount, {'from':accounts[1]})
	hackERC20LightV1.approve(wrapperLight.address, 3*call_amount, {'from':accounts[1]})

	wrapperLight.setWNFTId(out_type, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})

	empty_data = ((0, zero_address), 0, 0)
	dai_data = ((2, dai.address), 0, Wei(call_amount))
	weth_data = ((2, weth.address), 0, Wei(2*call_amount))
	hackERC20LightV1_data = ((2, hackERC20LightV1.address), 0, Wei(3*call_amount))
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
		'0'
		)

	tx = wrapperLight.wrap(wNFT, [dai_data, weth_data, hackERC20LightV1_data], accounts[3], {"from": accounts[1], "value": eth_amount})
	
	#checks
	assert wrapperLight.balance() == eth_amount
	assert dai.balanceOf(wrapperLight) == call_amount
	assert weth.balanceOf(wrapperLight) == 2*call_amount
	assert hackERC20LightV1.balanceOf(wrapperLight) == 3*call_amount
	assert wnft721ForWrapperLightV1.ownerOf(wrapperLight.lastWNFTId(out_type)[1]) == accounts[3].address
	assert wnft721ForWrapperLightV1.totalSupply() == 1

	logging.info(tx.events['WrappedV1'])


	#add to wrapperLight tokens
	dai.transfer(wrapperLight.address, call_amount, {"from": accounts[0]})
	weth.transfer(wrapperLight.address, 2*call_amount, {"from": accounts[0]})
	hackERC20LightV1.transfer(wrapperLight.address, 3*call_amount, {"from": accounts[0]})

	#try to attack
	with reverts("Only owner can unwrap it"):
		wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, tx.events['WrappedV1']['outTokenId'], {"from": accounts[3]})



	