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

def test_addColl(accounts, wrapperLight, wnft1155ForWrapperLightV1, niftsy20,  mockHacker1155_1, erc1155mock1, erc721mock1):
	#make test data
	mockHacker1155_1.setFailReciever(accounts[9],2) #will be block transfer from wrapperLight to account
	mockHacker1155_1.setWrapper(wrapperLight.address)
	makeNFTForTest1155(accounts, mockHacker1155_1, ORIGINAL_NFT_IDs, in_nft_amount)
	
	#with asset data - ERC1155 token. Token will be burnt after adding to collateral
	wTokenId = makeFromERC1155ToERC1155WithoutCollateralLight(accounts, mockHacker1155_1, wrapperLight, wnft1155ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], in_nft_amount, out_nft_amount, accounts[3])
	
	assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId) == out_nft_amount
	
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
	assert mockHacker1155_1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount #check balance
	assert collateral[0] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
	assert collateral[1] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)

	logging.info(wrapperLight.getWrappedToken(wnft1155ForWrapperLightV1, wTokenId)[1])

	#revert must be 
	with reverts ("Hack your Wrapper"):
		wrapperLight.unWrap(4, wnft1155ForWrapperLightV1.address, wTokenId, {"from": accounts[3]})
	
	assert mockHacker1155_1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount
	assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId) == out_nft_amount
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
	assert erc1155mock1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	
	#Emergency mode
	wrapperLight.unWrap(4, wnft1155ForWrapperLightV1.address, wTokenId, True, {"from": accounts[3]})

	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == coll_amount

