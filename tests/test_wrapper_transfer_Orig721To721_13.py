import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
transfer_fee_amount = 100

def test_wrap(accounts, erc721mock, wrapper, wnft721, niftsy20, techERC20, wrapperChecker):
#make wrap NFT
	in_type = 3
	out_type = 3

	#service methods
	wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})


	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
	erc721mock.approve(wrapper.address,ORIGINAL_NFT_IDs[0], {"from": accounts[1]})


	token_property = (in_type, erc721mock)
	token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
	
	fee =  [(Web3.toBytes(0x00), transfer_fee_amount, techERC20.address)]
	lock = []
	royalty = []

	wNFT = ( token_data,
	accounts[2],
	fee,
	lock,
	royalty,
	out_type,
	0,
	0
	)


	wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	wTokenId = wrapper.lastWNFTId(out_type)[1]
	wnft721.transferFrom(accounts[3], accounts[4], wTokenId, {"from": accounts[3]} )

	assert techERC20.balanceOf(wrapper.address) == transfer_fee_amount
	assert wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId, techERC20.address)[0] == transfer_fee_amount


	

	