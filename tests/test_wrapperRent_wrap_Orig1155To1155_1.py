import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

#wrap again
#not add collateral
#transfer
#not unwrap by owner
def wnft_pretty_print(_wrapper, _wnft721, _wTokenId):
	logging.info(
		'\n=========wNFT=============\nwNFT:{0},{1}\nInAsset: {2}\nCollrecords:\n{3}\nunWrapDestinition: {4}'
		'\nFees: {5} \nLocks: {6} \nRoyalty: {7} \nrules: {8}({9:0>16b}) \n=========================='.format(
		_wnft721, _wTokenId,
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[0],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[1],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[2],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[3],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[4],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[5],
		_wrapper.getWrappedToken(_wnft721, _wTokenId)[6],
		Web3.toInt(_wrapper.getWrappedToken(_wnft721, _wTokenId)[6]),
		
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
	Web3.toBytes(0x0008)
	)

	wrapperRent.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	wTokenId = wrapperRent.lastWNFTId(out_type)[1]
	wnft_pretty_print(wrapperRent, wnft1155, wTokenId)
	assert erc1155mock.balanceOf(wrapperRent.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount
	
	#transfer
	wnft1155.safeTransferFrom(accounts[3], accounts[9], wTokenId, 1, '', {"from": accounts[3]})
	wnft1155.safeTransferFrom(accounts[9], accounts[3], wTokenId, 1, '', {"from": accounts[9]})

	#refuse to deposit collateral
	with reverts("Forbidden add collateral"):
		wrapperRent.addCollateral(wnft1155.address, wTokenId, [], {"from": accounts[1], "value": "1 ether"})

	# unwrap by owner
	wrapperRent.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]})

	
	#wrap wNFT
	erc1155mock.safeTransferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], in_nft_amount, "", {"from": accounts[0]})
	token_data = (token_property, ORIGINAL_NFT_IDs[1], coll_amount)
	wNFT = ( token_data,
	accounts[2], #leasingPool
	fee,
	lock,
	royalty,
	out_type,
	out_nft_amount,
	Web3.toBytes(0x0008)
	)

	wrapperRent.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	wnft1155.setApprovalForAll(wrapperRent, True, {"from": accounts[3]})
	wTokenId = wrapperRent.lastWNFTId(out_type)[1]

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
	
	# wrap again
	wrapperRent.wrap(wNFT, [], accounts[4], {"from": accounts[3]})

	