import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "4 ether"


def wnft_pretty_print(_wrapper, _wnft721, _wTokenId):
	logging.info(
		'\n=========wNFT=============\nwNFT:{},{}\nInAsset: {}\nCollrecords:\n{}\nunWrapDestinition: {}'
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

def test_unwrap(accounts, erc1155mock, wrapperRent, wnft1155, niftsy20):
#make wrap NFT with empty
	in_type = 4
	out_type = 4
	in_nft_amount = 3
	out_nft_amount = 5
	coll_amount = 2

	#service methods
	wrapperRent.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
	wnft1155.setMinterStatus(wrapperRent.address, {"from": accounts[0]})


	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
	erc1155mock.setApprovalForAll(wrapperRent.address, True, {"from": accounts[1]})


	token_property = (in_type, erc1155mock)
	token_data = (token_property, ORIGINAL_NFT_IDs[0], coll_amount)
	
	fee = []
	lock = []
	royalty = []

	wNFT = ( token_data,
	accounts[2], #leasingPool
	fee,
	lock,
	royalty,
	out_type,
	out_nft_amount,
	'3'
	)



	wrapperRent.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	wTokenId = wrapperRent.lastWNFTId(out_type)[1]
	wnft_pretty_print(wrapperRent, wnft1155, wTokenId)
	assert erc1155mock.balanceOf(wrapperRent.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount
    
    # wNFT2 = ( ((in_type, wnft1155), wTokenId, out_nft_amount),
	# accounts[2], #leasingPool
	# fee,
	# lock,
	# royalty,
	# out_type,
	# out_nft_amount,
	# '0'
	# )
	#wrapperRent.wrap(wNFT2, [], accounts[3], {"from": accounts[3]})
	

	#refuse to transfer
	# with reverts("r"):
	# 	wnft1155.safeTransferFrom(accounts[3], accounts[9], wTokenId, 1, '', {"from": accounts[3]})

	# #refuse to deposit collateral
	# with reverts("r"):
	# 	wrapperRent.addCollateral(wnft1155.address, wTokenId, [], {"from": accounts[1], "value": "1 ether"})

	#refuse to wrap wNFT
	wnft1155.setApprovalForAll(wrapperRent, True, {"from": accounts[3]})

	token_property = (in_type, wnft1155)
	token_data = (token_property, wTokenId, coll_amount)
	
	fee = []
	lock = []
	royalty = []

	wNFT = ( token_data,
	accounts[2], #leasingPool
	fee,
	lock,
	royalty,
	out_type,
	out_nft_amount,
	'0'
	)
	
	#refuse to wrap again
	#with reverts("r"):
		#wrapperRent.wrap(wNFT, [], accounts[4], {"from": accounts[3]})

	#refuse to unwrap by owner
	#with reverts("r"):
		#wrapperRent.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]})

	#unwrap by UnwrapDestinition
	wrapperRent.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[2]})