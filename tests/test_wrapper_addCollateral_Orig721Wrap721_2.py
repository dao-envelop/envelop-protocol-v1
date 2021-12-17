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

	
	'''collateral = wrapper.getWrappedToken(wnft721, wTokenId)[1]
	assert collateral[0][2] == "4 ether"
	assert collateral[0][0][0] == 1
	assert collateral[1][0][0] == 3
	assert collateral[2][0][0] == 3
	assert collateral[3][0][0] == 3
	assert collateral[1][1] == ORIGINAL_NFT_IDs[1]
	assert collateral[2][1] == ORIGINAL_NFT_IDs[2]
	assert collateral[3][1] == ORIGINAL_NFT_IDs[0]
	assert collateral[1][0][1] == erc721mock.address
	assert collateral[2][0][1] == erc721mock.address
	assert collateral[3][0][1] == erc721mock1.address
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapper.address
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[2]) == wrapper.address
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
	assert erc721mock.balanceOf(wrapper.address) == 3
	assert erc721mock1.balanceOf(wrapper.address) == 1'''

