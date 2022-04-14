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

def wnft_pretty_print(_wrapper, _wnft721, _wTokenId):
	logging.info(
		'\n=========wNFT=============\nwNFT:{},{}\nInAsset: {}\nCollrecords:\n{}\nunWrapDestination: {}'
		'\nFees: {} \nLocks: {} \nRoyalty: {} \n rules: {} \n=========================='.format(
		_wnft721, _wTokenId,
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[0],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[1],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[2],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[3],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[4],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[5],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[6],
	))

def test_addColl(accounts, wrapper, wnft721, niftsy20,  mockHacker721_1, erc1155mock1, erc721mock1):
	#make test data
	mockHacker721_1.setFailReciever(accounts[9],2)
	mockHacker721_1.setWrapper(wrapper.address)
	mockHacker721_1.mint(accounts[1], ORIGINAL_NFT_IDs[0], {"from": accounts[1]})
	mockHacker721_1.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

	
	#with asset data - ERC1155 token. Token will be burnt after adding to collateral
	wTokenId = makeFromERC721ToERC721WithoutCollateral(accounts, mockHacker721_1, wrapper, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
	
	assert wnft721.ownerOf(wTokenId) == accounts[3]
	
	#make 721 for collateral - normal token
	makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
	erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

	#make 1155 for collateral - normal token
	makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
	erc1155mock1.setApprovalForAll(wrapper.address,True, {"from": accounts[1]})

	wrapper.addCollateral(wnft721.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
		], {'from': accounts[1]})
	wrapper.addCollateral(wnft721.address, wTokenId, [((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)
		], {'from': accounts[1]})

	collateral = wrapper.getWrappedToken(wnft721, wTokenId)[1]
	assert mockHacker721_1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
	assert collateral[0] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
	assert collateral[1] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)

	#burn wrapped original 721 token
	mockHacker721_1.burn(ORIGINAL_NFT_IDs[0])

	# logging.info('\nwNFT:{},{}\nInAsset:{}\nCollrecords:\n{}'.format(
	# 	wnft721, wTokenId,
	# 	wrapper.getWrappedToken(wnft721, wTokenId)[0],
	# 	wrapper.getWrappedToken(wnft721, wTokenId)[1]
	# ))
	wnft_pretty_print(wrapper, wnft721, wTokenId)

	#revert must be 
	with reverts ("ERC721: owner query for nonexistent token"):
		wrapper.unWrap(3, wnft721.address, wTokenId, {"from": accounts[3]})
	
	assert wnft721.ownerOf(wTokenId) == accounts[3]
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
	assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	
	#Emergency mode
	tx = wrapper.unWrap(3, wnft721.address, wTokenId, True, {"from": accounts[3]})
	# logging.info('\nwNFT:{},{}\nInAsset:{}\nCollrecords:\n{}'.format(
	# 	wnft721, wTokenId,
	# 	wrapper.getWrappedToken(wnft721, wTokenId)[0],
	# 	wrapper.getWrappedToken(wnft721, wTokenId)[1]
	# ))
	logging.info(tx.events)
	wnft_pretty_print(wrapper, wnft721, wTokenId)


	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == coll_amount

