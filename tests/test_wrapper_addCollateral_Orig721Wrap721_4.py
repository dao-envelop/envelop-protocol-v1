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

	#with asset data - ERC721 token. Contract of token change the address @to. Token id 0
	mockHacker721_1.setFailReciever(accounts[9],2)
	mockHacker721_1.setWrapper(wrapper.address)
	mockHacker721_1.mint(accounts[1], 0, {"from": accounts[1]})
	mockHacker721_1.approve(wrapper.address, 0, {"from": accounts[1]})
	
	wrapper.addCollateral(wnft721.address, wTokenId, [((3, mockHacker721_1.address), 0, 0)], {'from': accounts[1]})

	assert mockHacker721_1.balanceOf(accounts[1]) == 0 #check balance
	assert mockHacker721_1.ownerOf(0) == wrapper #check owner
	assert wrapper.getWrappedToken(wnft721, wTokenId)[1] == [((3, mockHacker721_1.address), 0, 0)]

	logging.info(wrapper.getWrappedToken(wnft721, wTokenId)[1])

	mockHacker721_1.burn(0)

	#revert not must be 
	wrapper.unWrap(3, wnft721.address, wTokenId, {"from": accounts[3]})
