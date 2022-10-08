import pytest
import logging
from brownie import Wei, reverts, chain
from web3 import Web3


LOGGER = logging.getLogger(__name__)
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3
call_amount = 1e18


def test_simple_wrap(accounts, swapWrapper, dai, weth, swapWnft721, niftsy20, swapChecker, swapTechERC20, swapWhiteLists):
	
	caller = accounts[0]
	multisig = accounts[9]
	with reverts("Ownable: caller is not the owner"):
		swapChecker.setTrustedAddress(multisig, True, {"from": accounts[1]})
	swapChecker.setTrustedAddress(multisig, True, {"from": accounts[0]})

	swapWrapper.setWNFTId(out_type, swapWnft721.address, 0, {'from':accounts[0]})
	swapWnft721.setMinter(swapWrapper.address, {"from": accounts[0]})

	
	wNFT = ( ((0, zero_address), 0,0),
		accounts[1],
		[],
		[],
		[],
		out_type,
		0,
		'0'
		)

	with reverts("No Time Lock found"):
		swapWrapper.wrap(wNFT, [], accounts[1], {"from": caller})

	wNFT = ( ((0, zero_address), 0,0),
		accounts[1],
		[],
		[('0x00', chain.time() + 100)],
		[],
		out_type,
		0,
		'0'
		)
	with reverts("NoTransfer rule not set"):
		swapWrapper.wrap(wNFT, [], accounts[1], {"from": caller})

	wNFT = ( ((0, zero_address), 0,0),
		accounts[1],
		[],
		[('0x00', chain.time() + 100)],
		[],
		out_type,
		0,
		Web3.toBytes(0x0001)
		)
	with reverts("NoTransfer rule not set"):
		swapWrapper.wrap(wNFT, [], accounts[1], {"from": caller})

	wNFT = ( ((0, zero_address), 0,0),
		accounts[1],
		[],
		[('0x00', chain.time() + 100)],
		[],
		out_type,
		0,
		Web3.toBytes(0x0004)
		)
	with reverts("Trusted multisig not found in royalty"):
		swapWrapper.wrap(wNFT, [], accounts[1], {"from": caller})

	wNFT = ( ((0, zero_address), 0,0),
		accounts[1],
		[],
		[('0x00', chain.time() + 100)],
		[(multisig, 10000)],
		out_type,
		0,
		Web3.toBytes(0x0004)
		)
	'''with reverts('Only trusted address'):
		swapWrapper.wrap(wNFT, [], accounts[1], {"from": accounts[1]})'''

	#set whiteList
	swapWrapper.setWhiteList(swapWhiteLists.address, {"from": accounts[0]})

	#no removable token
	wl_data = (True, True, False, swapTechERC20.address)
	swapWhiteLists.setWLItem((2, dai), wl_data, {"from": accounts[0]})


	#removable token
	wl_data = (True, True, True, swapTechERC20.address)
	swapWhiteLists.setWLItem((2, niftsy20), wl_data, {"from": accounts[0]})
	#wrap for acc1 and allowance from acc1 for wrapper
	niftsy20.approve(swapWrapper.address, call_amount, {"from": accounts[1]})
	dai.approve(swapWrapper.address, 2*call_amount, {"from": accounts[1]})
	niftsy20.transfer(accounts[1], call_amount, {"from": accounts[0]})
	dai.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

	#msg.sender is trusted address
	tx = swapWrapper.wrap(wNFT, [((2, niftsy20.address), 0, call_amount), ((2, dai.address), 0, 2*call_amount)], accounts[1], {"from": accounts[1]})

	wTokenId = tx.events['WrappedV1']['outTokenId']
	assert swapWnft721.ownerOf(wTokenId) == accounts[1]

	#try to remove irremovable token
	#msg.sender is not allowed remover
	with reverts("Sender is not in beneficiary list"):
		swapWrapper.removeERC20CollateralAmount(swapWnft721.address, wTokenId, dai.address, 1, {"from": accounts[1]})	

	logging.info(dai.balanceOf(swapWrapper))
	#try to remove irremuvable token - need check
	#swapWrapper.removeERC20CollateralAmount(swapWnft721.address, wTokenId, dai.address, 1, {"from": multisig})
	with reverts("Amount exceed balance"):
		swapWrapper.removeERC20CollateralAmount(swapWnft721.address, wTokenId, dai.address, int(2*call_amount)+1, {"from": multisig})

	#remove removable token
	before_balance_w  = niftsy20.balanceOf(swapWrapper)
	swapWrapper.removeERC20CollateralAmount(swapWnft721.address, wTokenId, niftsy20.address, 1, {"from": multisig})

	assert niftsy20.balanceOf(multisig) == 1
	assert niftsy20.balanceOf(swapWrapper) == int(before_balance_w) - 1
	assert swapWrapper.getCollateralBalanceAndIndex(swapWnft721, wTokenId, 2, niftsy20.address, 0)[0] == int(before_balance_w) - 1
                

	#try to unwrap wnft
	with reverts("TimeLock error"):	
		swapWrapper.unWrap(swapWnft721, wTokenId, {"from": accounts[1]})

	chain.sleep(100)
	chain.mine()
	#not owner tries to unwrap
	with reverts("Only owner can unwrap it"):
		swapWrapper.unWrap(swapWnft721, wTokenId, {"from": accounts[0]})

	before_balance_niftsy1 = niftsy20.balanceOf(accounts[1])
	before_balance_dai1 = dai.balanceOf(accounts[1])
	mustAddedAmount_dai = swapWrapper.getCollateralBalanceAndIndex(swapWnft721, wTokenId, 2, dai.address, 0)[0]
	mustAddedAmount_niftsy = swapWrapper.getCollateralBalanceAndIndex(swapWnft721, wTokenId, 2, niftsy20.address, 0)[0]
	swapWrapper.unWrap(swapWnft721, wTokenId, {"from": accounts[1]})

	assert niftsy20.balanceOf(swapWrapper) == 0
	assert dai.balanceOf(swapWrapper) == 0
	assert dai.balanceOf(accounts[1]) == before_balance_dai1 + mustAddedAmount_dai
	assert niftsy20.balanceOf(accounts[1]) == before_balance_niftsy1 + mustAddedAmount_niftsy