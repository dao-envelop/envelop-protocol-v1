import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest1155, makeFromERC1155ToERC1155WithoutCollateral


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5
coll_amount = 2

def test_addColl(accounts, erc1155mock, wrapper, wnft1155, niftsy20,  mockHacker1155_1):
	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
	
	#with asset data - ERC1155 token. Token will be burnt after adding to collateral
	wTokenId = makeFromERC1155ToERC1155WithoutCollateral(accounts, erc1155mock, wrapper, wnft1155, niftsy20, ORIGINAL_NFT_IDs[0], in_nft_amount, out_nft_amount, accounts[3])
	
	assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount

	#with asset data - ERC1155 token. Contract of token change the address @to. Token id 0
	mockHacker1155_1.setFailReciever(accounts[9],2)
	mockHacker1155_1.setWrapper(wrapper.address)
	mockHacker1155_1.mint(accounts[1], 0, coll_amount, {"from": accounts[1]})
	mockHacker1155_1.setApprovalForAll(wrapper.address, True, {"from": accounts[1]})
	
	wrapper.addCollateral(wnft1155.address, wTokenId, [((4, mockHacker1155_1.address), 0, coll_amount)], {'from': accounts[1], "value": "1 ether"})

	assert mockHacker1155_1.balanceOf(accounts[1], 0) == 0 #check balance
	assert mockHacker1155_1.balanceOf(wrapper.address, 0) == coll_amount #check balance
	assert wrapper.getWrappedToken(wnft1155, wTokenId)[1] == [((1, zero_address), 0 , Wei("1 ether")), ((4, mockHacker1155_1.address), 0, coll_amount)]

	logging.info(wrapper.getWrappedToken(wnft1155, wTokenId)[1])

	logging.info(mockHacker1155_1.balanceOf(wrapper.address, 0))
	mockHacker1155_1.burn(wrapper.address, 0, coll_amount)

	#revert not must be 
	wrapper.unWrap(4, wnft1155.address, wTokenId, {"from": accounts[3]})
