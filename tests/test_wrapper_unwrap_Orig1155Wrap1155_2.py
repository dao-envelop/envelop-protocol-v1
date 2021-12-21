import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest1155, makeFromERC1155ToERC1155WithoutCollateral, makeNFTForTest721


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5
coll_amount = 2

def test_addColl(accounts, erc1155mock, wrapper, wnft1155, niftsy20,  mockHacker1155_1, erc1155mock1, erc721mock1):
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

	 #make 721 for collateral - normal token
	makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
	erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

	#make 1155 for collateral - normal token
	makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
	erc1155mock1.setApprovalForAll(wrapper.address,True, {"from": accounts[1]})

	wrapper.addCollateral(wnft1155.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
		], {'from': accounts[1]})
	wrapper.addCollateral(wnft1155.address, wTokenId, [((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)
		], {'from': accounts[1]})

	collateral = wrapper.getWrappedToken(wnft1155, wTokenId)[1]
	assert mockHacker1155_1.balanceOf(accounts[1], 0) == 0 #check balance
	assert mockHacker1155_1.balanceOf(wrapper.address, 0) == coll_amount #check balance
	assert collateral[0] == ((1, zero_address), 0 , Wei("1 ether"))
	assert collateral[1] == ((4, mockHacker1155_1.address), 0, coll_amount)
	assert collateral[2] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
	assert collateral[3] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)

	logging.info(wrapper.getWrappedToken(wnft1155, wTokenId)[1])

	logging.info(mockHacker1155_1.balanceOf(wrapper.address, 0))

	#revert must be 
	with reverts ("Hack your Wrapper"):
		wrapper.unWrap(4, wnft1155.address, wTokenId, {"from": accounts[3]})

	assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
	assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	assert wrapper.balance() == "1 ether"

	eth_balance_acc = accounts[2].balance()
	eth_balance_contract = wrapper.balance()

	wrapper.unWrap(4, wnft1155.address, wTokenId, True, {"from": accounts[3]})

	assert erc1155mock.balanceOf(accounts[2], ORIGINAL_NFT_IDs[0]) == in_nft_amount
	assert wrapper.balance() == 0
	assert accounts[2].balance() == eth_balance_acc+eth_balance_contract
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[2]
	assert erc1155mock1.balanceOf(accounts[2], ORIGINAL_NFT_IDs[0]) == in_nft_amount
	assert accounts[2].balance() == eth_balance_acc+eth_balance_contract

