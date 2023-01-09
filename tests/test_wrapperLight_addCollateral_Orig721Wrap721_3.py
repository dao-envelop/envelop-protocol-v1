import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateralLight


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
amount = 100

def test_addColl(accounts, erc721mock, wrapperLight, wnft721ForWrapperLightV1, niftsy20, mockHacker20_1):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
	mockHacker20_1.mint(accounts[1], amount)
	mockHacker20_1.setFailReciever(accounts[9])
	mockHacker20_1.setWrapper(wrapperLight.address)
	mockHacker20_1.approve(wrapperLight.address, amount, {"from": accounts[1]})

	#make wrap NFT 721
	wTokenId = makeFromERC721ToERC721WithoutCollateralLight(accounts, erc721mock, wrapperLight, wnft721ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
	
	assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]

	#with erc20. Token Contract changes reciver in transfer
	with reverts("Suspicious asset for wrap"):
		wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, mockHacker20_1.address), 0, amount)], {'from': accounts[1]})

	
	collateral = wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)[1]
	assert collateral == []
	assert mockHacker20_1.balanceOf(accounts[1]) == amount
	assert mockHacker20_1.balanceOf(wrapperLight.address) == 0
	assert mockHacker20_1.balanceOf(accounts[9]) == 0
	

