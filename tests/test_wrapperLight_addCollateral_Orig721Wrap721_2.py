import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateralLight


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
amount = 100

def test_addColl(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

	#make wrap NFT 721
	wTokenId = makeFromERC721ToERC721WithoutCollateralLight(accounts, erc721mock, wrapperLight, wnft721ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
	
	assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]

	#with erc20 and native tokens. Not exists allowance
	dai.transfer(accounts[1], amount, {"from": accounts[0]})
	with reverts("ERC20: insufficient allowance"):
		wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, dai.address), 0, amount)], {'from': accounts[1], "value": "1 ether"})

	#with erc20 and native tokens. Not enough balance
	dai.approve(wrapperLight.address, 10*amount, {"from": accounts[1]})
	with reverts("ERC20: transfer amount exceeds balance"):
		wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, dai.address), 0, amount+1)], {'from': accounts[1], "value": "1 ether"})

	#with erc20 and native tokens. Success
	dai.approve(wrapperLight.address, 10*amount, {"from": accounts[1]})
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, dai.address), 0, amount)], {'from': accounts[1], "value": "1 ether"})

	#with erc20 and native tokens. Add second token. Success
	weth.transfer(accounts[1], 10*amount, {"from": accounts[0]})
	weth.approve(wrapperLight.address, 10*amount, {"from": accounts[1]})
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, weth.address), 0, 5*amount)], {'from': accounts[1], "value": "1 ether"})	

	#with erc20. Add amount. Success
	dai.transfer(accounts[1], 2*amount, {"from": accounts[0]})
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, dai.address), 0, 2*amount)], {'from': accounts[1]})

	
	collateral = wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)[1]
	assert collateral[0][2] == "2 ether"
	assert collateral[0][0][0] == 1
	assert collateral[0][0][1] == zero_address
	

	assert collateral[1][0][0] == 2
	assert collateral[1][0][1] == dai.address
	assert collateral[1][2] == 3*amount


	assert collateral[2][0][0] == 2
	assert collateral[2][0][1] == weth.address
	assert collateral[2][2] == 5*amount

	assert dai.balanceOf(wrapperLight.address) == 3*amount
	assert weth.balanceOf(wrapperLight.address) == 5*amount
	assert wrapperLight.balance() == "2 ether"

