import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]

def test_unwrap(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

	#make wrap NFT 721
	wTokenId = makeFromERC721ToERC721(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
	
	assert wnft721.ownerOf(wTokenId) == accounts[3]

	wrapper.unWrap(3, wnft721.address, wTokenId, {"from": accounts[3]})
	'''
	#checks
	assert wrapper.balance() == eth_amount
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
	assert wNFT[2] == accounts[2]
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0'	'''
