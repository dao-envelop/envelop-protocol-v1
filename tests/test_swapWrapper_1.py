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
	swapChecker.setTrustedAddress(multisig, True, {"from": accounts[0]})

	swapWrapper.setWNFTId(out_type, swapWnft721.address, 0, {'from':accounts[0]})

	wNFT = ( ((0, zero_address), 0,0), #empty
		accounts[1], 
		[], #fee
		[('0x00', chain.time() + 100)], #timelock
		[(accounts[1], 10000), (multisig, 0)], #royalty --!! special case
		out_type, 
		0,
		Web3.toBytes(0x0004) #rules (no transferable)
		)

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

	#wrap
	with reverts("Trusted multisig not found in royalty"):
		tx = swapWrapper.wrap(wNFT, [((2, niftsy20.address), 0, call_amount), ((2, dai.address), 0, 2*call_amount)], accounts[1], {"from": accounts[1]})

	wNFT = ( ((0, zero_address), 0,0), #empty
		accounts[1], 
		[], #fee
		[('0x00', chain.time() + 100)], #timelock
		[(multisig, 0), (accounts[1], 10000)], #royalty --!! special case
		out_type, 
		0,
		Web3.toBytes(0x0004) #rules (no transferable)
	)

	#wrap
	with reverts("Trusted multisig not found in royalty"):
		tx = swapWrapper.wrap(wNFT, [((2, niftsy20.address), 0, call_amount), ((2, dai.address), 0, 2*call_amount)], accounts[1], {"from": accounts[1]})

	wNFT = ( ((0, zero_address), 0,0), #empty
		accounts[1], 
		[], #fee
		[('0x00', chain.time() + 100)], #timelock
		[(multisig, 0)], #royalty --!! special case
		out_type, 
		0,
		Web3.toBytes(0x0004) #rules (no transferable)
	)

	tx = swapWrapper.wrap(wNFT, [((2, niftsy20.address), 0, call_amount), ((2, dai.address), 0, 2*call_amount)], accounts[1], {"from": accounts[1]})


	wTokenId = tx.events['WrappedV1']['outTokenId']
	assert swapWnft721.ownerOf(wTokenId) == accounts[1]

	#add collateral (niftsy)
	niftsy20.approve(swapWrapper.address, call_amount, {"from": accounts[1]})
	niftsy20.transfer(accounts[1], call_amount, {"from": accounts[0]})
	tx = swapWrapper.addCollateral(swapWnft721.address, wTokenId, [((2, niftsy20.address), 0, call_amount)], {"from": accounts[1]})


	#remove removable token - NOT MULTISIG REMOVES!!!!!!!
	before_balance_w  = niftsy20.balanceOf(swapWrapper)
	before_balance_m  = niftsy20.balanceOf(multisig)
	with reverts("Sender is not in beneficiary list"):
		swapWrapper.removeERC20CollateralAmount(swapWnft721.address, wTokenId, niftsy20.address, 1, {"from": accounts[1]})

	swapWrapper.removeERC20CollateralAmount(swapWnft721.address, wTokenId, niftsy20.address, 1, {"from": multisig})

	assert niftsy20.balanceOf(swapWrapper) == before_balance_w - 1
	assert niftsy20.balanceOf(multisig) == before_balance_m + 1

	