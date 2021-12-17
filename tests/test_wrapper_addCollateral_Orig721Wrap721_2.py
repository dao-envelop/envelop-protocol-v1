import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateral


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
amount = 100

def test_addColl(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

	#make wrap NFT 721
	wTokenId = makeFromERC721ToERC721WithoutCollateral(accounts, erc721mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
	
	assert wnft721.ownerOf(wTokenId) == accounts[3]

	#with erc20 and native tokens. Not exists allowance
	dai.transfer(accounts[1], amount, {"from": accounts[0]})
	with reverts("ERC20: transfer amount exceeds allowance"):
		wrapper.addCollateral(wnft721.address, wTokenId, [((2, dai.address), 0, amount)], {'from': accounts[1], "value": "1 ether"})

	#with erc20 and native tokens. Not enough balance
	dai.approve(wrapper.address, 10*amount, {"from": accounts[1]})
	with reverts("ERC20: transfer amount exceeds balance"):
		wrapper.addCollateral(wnft721.address, wTokenId, [((2, dai.address), 0, amount+1)], {'from': accounts[1], "value": "1 ether"})

	#with erc20 and native tokens. Success
	dai.approve(wrapper.address, 10*amount, {"from": accounts[1]})
	wrapper.addCollateral(wnft721.address, wTokenId, [((2, dai.address), 0, amount)], {'from': accounts[1], "value": "1 ether"})

	#with erc20 and native tokens. Add second token. Success
	weth.transfer(accounts[1], 10*amount, {"from": accounts[0]})
	weth.approve(wrapper.address, 10*amount, {"from": accounts[1]})
	wrapper.addCollateral(wnft721.address, wTokenId, [((2, weth.address), 0, 5*amount)], {'from': accounts[1], "value": "1 ether"})	

	#with erc20. Add amount. Success
	dai.transfer(accounts[1], 2*amount, {"from": accounts[0]})
	wrapper.addCollateral(wnft721.address, wTokenId, [((2, dai.address), 0, 2*amount)], {'from': accounts[1]})

	
	collateral = wrapper.getWrappedToken(wnft721, wTokenId)[1]
	assert collateral[0][2] == "2 ether"
	assert collateral[0][0][0] == 1
	assert collateral[0][0][1] == zero_address
	

	assert collateral[1][0][0] == 2
	assert collateral[1][0][1] == dai.address
	assert collateral[1][2] == 3*amount


	assert collateral[2][0][0] == 2
	assert collateral[2][0][1] == weth.address
	assert collateral[2][2] == 5*amount

	assert dai.balanceOf(wrapper.address) == 3*amount
	assert weth.balanceOf(wrapper.address) == 5*amount
	assert wrapper.balance() == "2 ether"

