import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest1155, makeFromERC1155ToERC1155WithoutCollateralLight, makeNFTForTest721


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5
coll_amount = 2

def test_addColl(accounts, erc1155mock, wrapperLight, wnft1155ForWrapperLightV1, niftsy20,  mockHacker1155_1, erc1155mock1, erc721mock1):
	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
	
	#with asset data - ERC1155 token. Token will be burnt after adding to collateral
	wTokenId = makeFromERC1155ToERC1155WithoutCollateralLight(accounts, erc1155mock, wrapperLight, wnft1155ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], in_nft_amount, out_nft_amount, accounts[3])
	
	assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId) == out_nft_amount

	#with asset data - ERC1155 token. Contract of token change the address @to. Token id 0
	mockHacker1155_1.setFailReciever(accounts[9],2)
	mockHacker1155_1.setWrapper(wrapperLight.address)
	mockHacker1155_1.mint(accounts[1], 0, coll_amount, {"from": accounts[1]})
	mockHacker1155_1.setApprovalForAll(wrapperLight.address, True, {"from": accounts[1]})
	
	wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((4, mockHacker1155_1.address), 0, coll_amount)], {'from': accounts[1], "value": "1 ether"})

	 #make 721 for collateral - normal token
	makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
	erc721mock1.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

	#make 1155 for collateral - normal token
	makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
	erc1155mock1.setApprovalForAll(wrapperLight.address,True, {"from": accounts[1]})

	wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
		], {'from': accounts[1]})
	wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)
		], {'from': accounts[1]})

	collateral = wrapperLight.getWrappedToken(wnft1155ForWrapperLightV1, wTokenId)[1]
	assert mockHacker1155_1.balanceOf(accounts[1], 0) == 0 #check balance
	assert mockHacker1155_1.balanceOf(wrapperLight.address, 0) == coll_amount #check balance
	assert collateral[0] == ((1, zero_address), 0 , Wei("1 ether"))
	assert collateral[1] == ((4, mockHacker1155_1.address), 0, coll_amount)
	assert collateral[2] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
	assert collateral[3] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)

	logging.info(wrapperLight.getWrappedToken(wnft1155ForWrapperLightV1, wTokenId)[1])

	logging.info(mockHacker1155_1.balanceOf(wrapperLight.address, 0))

	#burn collateral 1155 token
	mockHacker1155_1.burn(wrapperLight.address, 0, coll_amount)
	#change mode on hacker contract
	mockHacker1155_1.setFailReciever(accounts[9],0)

	#revert must be 
	with reverts ("ERC1155: insufficient balance for transfer"):
		wrapperLight.unWrap(4, wnft1155ForWrapperLightV1.address, wTokenId, {"from": accounts[3]})

	assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId) == out_nft_amount
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
	assert erc1155mock1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	assert wrapperLight.balance() == "1 ether"

	eth_balance_acc = accounts[3].balance()
	eth_balance_contract = wrapperLight.balance()

	wrapperLight.unWrap(4, wnft1155ForWrapperLightV1.address, wTokenId, True, {"from": accounts[3]})

	assert erc1155mock.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == in_nft_amount
	assert wrapperLight.balance() == 0
	assert accounts[3].balance() == eth_balance_acc+eth_balance_contract
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == coll_amount

