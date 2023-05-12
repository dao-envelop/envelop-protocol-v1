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

#not wrap again
#not add collateral
#not transfer
#not unwrap
def wnft_pretty_print(_wrapper, _wnft721, _wTokenId):
	logging.info(
		'\n=========wNFT=============\nwNFT:{0},{1}\nInAsset: {2}\nCollrecords:\n{3}\nunWrapDestination: {4}'
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

def test_unwrap(accounts, erc1155mock, wrapper, wnft1155, niftsy20):
#make wrap NFT with empty
	in_type = 4
	out_type = 4
	in_nft_amount = 3
	out_nft_amount = 5
	coll_amount = 2

	#service methods
	wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})

	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
	erc1155mock.setApprovalForAll(wrapper.address, True, {"from": accounts[1]})


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
	Web3.toBytes(0x000F)
	)



	wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	wTokenId = wrapper.lastWNFTId(out_type)[1]
	wnft_pretty_print(wrapper, wnft1155, wTokenId)
	assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount
	

	#refuse to transfer
	with reverts("Trasfer was disabled by author"):
	 	wnft1155.safeTransferFrom(accounts[3], accounts[9], wTokenId, 1, '', {"from": accounts[3]})

	#refuse to deposit collateral
	with reverts("Forbidden add collateral"):
		wrapper.addCollateral(wnft1155.address, wTokenId, [], {"from": accounts[1], "value": "1 ether"})

	#refuse to wrap wNFT
	wnft1155.setApprovalForAll(wrapper, True, {"from": accounts[3]})

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
	with reverts("Wrap check fail"):
		wrapper.wrap(wNFT, [], accounts[4], {"from": accounts[3]})

	#refuse unwrap by owner
	with reverts("UnWrapp forbidden by author"):
		wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]})