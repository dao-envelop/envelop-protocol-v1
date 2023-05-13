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
transfer_fee_amount = 100

def test_wrap(accounts, erc1155mock, wrapper, wnft1155, niftsy20, techERC20, wrapperChecker):
#make wrap NFT
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
	
	fee =  [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
	lock = []
	royalty = []

	wNFT = ( token_data,
	accounts[2],
	fee,
	lock,
	royalty,
	out_type,
	out_nft_amount,
	0
	)

	niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[3]})
	niftsy20.transfer(accounts[3], transfer_fee_amount, {"from": accounts[0]})

	wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	wTokenId = wrapper.lastWNFTId(out_type)[1]

	wnft1155.safeTransferFrom(accounts[3], accounts[4], wTokenId, out_nft_amount, "", {"from": accounts[3]} )

	assert niftsy20.balanceOf(wrapper.address) == transfer_fee_amount
	assert wrapperChecker.getERC20CollateralBalance(wnft1155.address, wTokenId, niftsy20.address)[0] == transfer_fee_amount


	

	