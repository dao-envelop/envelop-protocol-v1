import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateral


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'

def test_unwrap(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, mockHacker721_1):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

	#make wrap NFT 721
	wTokenId = makeFromERC721ToERC721WithoutCollateral(accounts, erc721mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
	
	assert wnft721.ownerOf(wTokenId) == accounts[3]

	#without asset data
	wrapper.addCollateral(wnft721.address, wTokenId, [], {'from': accounts[9], "value": '1 ether'})

	#with asset data - empty type
	with reverts(""):
		wrapper.addCollateral(wnft721.address, wTokenId, [((0, zero_address), 0, 10)], {'from': accounts[9], "value": '1 ether'})

	#with asset data - native type, amount in array is less than in value
	wrapper.addCollateral(wnft721.address, wTokenId, [((1, zero_address), 0, 10)], {'from': accounts[3], "value": '1 ether'})

	#with asset data - native type, amount in array is more than in value
	wrapper.addCollateral(wnft721.address, wTokenId, [((1, zero_address), 0, Wei("10 ether"))], {'from': accounts[3], "value": '1 ether'})


	#with asset data - ERC721 and native tokens. Not exists allowance
	erc721mock.transferFrom(accounts[0], accounts[9], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
	with reverts(""):
		wrapper.addCollateral(wnft721.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[1], 0)], {'from': accounts[9], "value": '1 ether'})

	#with asset data - ERC721 and native tokens. Exists allowance
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {"from": accounts[9]})
	wrapper.addCollateral(wnft721.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[1], 0)], {'from': accounts[9], "value": '1 ether'})
	
	#with asset data - ERC721 token. Wrong type
	erc721mock.transferFrom(accounts[0], accounts[9], ORIGINAL_NFT_IDs[2], {"from": accounts[0]})
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[2], {"from": accounts[9]})
	with reverts(""):
		wrapper.addCollateral(wnft721.address, wTokenId, [((4, erc721mock.address), ORIGINAL_NFT_IDs[2], 0)], {'from': accounts[9]})	

	#with asset data - ERC721 token. Msg.Sender is not owner of token
	with reverts("ERC721: transfer of token that is not own"):
		wrapper.addCollateral(wnft721.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[2], 0)], {'from': accounts[8]})

	#with asset data - ERC721 token. Contract of token change the address @to. Token id 0
	mockHacker721_1.setFailReciever(accounts[9])
	mockHacker721_1.setWrapper(wrapper.address)
	mockHacker721_1.mint(accounts[1], 0, {"from": accounts[1]})
	
	wrapper.addCollateral(wnft721.address, wTokenId, [((3, mockHacker721_1.address), 0, 0)], {'from': accounts[1]})