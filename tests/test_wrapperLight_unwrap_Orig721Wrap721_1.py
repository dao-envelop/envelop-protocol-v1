import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateral, makeNFTForTest1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5
coll_amount = 2

def test_addColl(accounts, wrapperLight, wnft721ForWrapperLightV1, niftsy20,  mockHacker721_1, erc1155mock1, erc721mock1):
	#make test data
	mockHacker721_1.setFailReciever(accounts[9],2)
	mockHacker721_1.setWrapper(wrapperLight.address)
	mockHacker721_1.mint(accounts[1], ORIGINAL_NFT_IDs[0], {"from": accounts[1]})
	mockHacker721_1.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

	
	#wrap nft

	in_type = 3
	out_type = 3
	mockHacker721_1.setApprovalForAll(wrapperLight.address, True, {'from':accounts[1]})
	if (wrapperLight.lastWNFTId(out_type)[1] == 0):
		wrapperLight.setWNFTId(out_type, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})
	erc721_property = (in_type, mockHacker721_1.address)
	erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 1)
	fee = []
	lock = []
	royalty = []
	wNFT = ( erc721_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		'0'
		)
	wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	wTokenId = wrapperLight.lastWNFTId(out_type)[1]
	
	assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]
	
	#make 721 for collateral - normal token
	makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
	erc721mock1.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

	#make 1155 for collateral - normal token
	makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
	erc1155mock1.setApprovalForAll(wrapperLight.address,True, {"from": accounts[1]})

	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
		], {'from': accounts[1]})
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)
		], {'from': accounts[1]})

	collateral = wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)[1]
	assert mockHacker721_1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
	assert collateral[0] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
	assert collateral[1] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)

	logging.info(wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)[1])

	#revert must be 
	with reverts ("Hack your Wrapper"):
		wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, {"from": accounts[3]})
	
	assert mockHacker721_1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
	assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
	assert erc1155mock1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	
	#Emergency mode
	wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, True, {"from": accounts[3]})

	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == coll_amount

