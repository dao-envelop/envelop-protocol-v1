import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateral


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'

def test_addColl(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, mockHacker721_1):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
	
	#make wrap NFT 721
	wTokenId = makeFromERC721ToERC721WithoutCollateral(accounts, erc721mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
	
	assert wnft721.ownerOf(wTokenId) == accounts[3]

	#with asset data - ERC721 token. Contract of token change the address @to. 
	mockHacker721_1.setFailReciever(accounts[9],0)
	mockHacker721_1.setWrapper(wrapper.address)
	mockHacker721_1.mint(accounts[1], 0, {"from": accounts[1]})
	mockHacker721_1.approve(wrapper.address, 0, {"from": accounts[1]})
	
	with reverts("Suspicious asset for wrap"):
		wrapper.addCollateral(wnft721.address, wTokenId, [((3, mockHacker721_1.address), 0, 0)], {'from': accounts[1]})

	assert mockHacker721_1.balanceOf(accounts[1]) == 1 #check balance
	assert mockHacker721_1.ownerOf(0) == accounts[1] #check owner
	assert wrapper.getWrappedToken(wnft721, wTokenId)[1] == []

	logging.info(wrapper.getWrappedToken(wnft721, wTokenId)[1])
