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


def test_simple_wrap(accounts, swapWrapper, dai, weth, swapWnft721, niftsy20, swapChecker):
	
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
		Web3.toBytes(0x0006)
		)
	with reverts("NoTransfer rule not set"):
		swapWrapper.wrap(wNFT, [], accounts[1], {"from": caller})
	
	#checks
	'''assert wrapper.balance() == eth_amount
	assert dai.balanceOf(wrapper) == call_amount
	assert weth.balanceOf(wrapper) == 2*call_amount
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
	assert wnft721.ownerOf(wrapper.lastWNFTId(out_type)[1]) == accounts[3].address
	assert wnft721.totalSupply() == 1

	wTokenId = wrapper.lastWNFTId(out_type)[1]
	wNFT = wrapper.getWrappedToken(wnft721, wTokenId)
	#logging.info(wNFT)
	assert wNFT[0] == erc721_data
	assert wNFT[1] == [eth_data, dai_data, weth_data]
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0'''	
