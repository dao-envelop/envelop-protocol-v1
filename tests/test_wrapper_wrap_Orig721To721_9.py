import pytest
import logging
from brownie import chain, Wei, reverts
from web3 import Web3
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

def test_wrap(accounts, erc721mock, wrapper, wnft721, whiteLists, erc1155mock, erc721mock1):
    #make wrap NFT with empty
	in_type = 3
	out_type = 3

	#make 721 for wrap
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

	if (wrapper.lastWNFTId(out_type)[1] == 0):
		wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
	wnft721.setMinter(wrapper.address, {"from": accounts[0]})

	erc721_property = (3, erc721mock.address)
	erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 0)

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
		Web3.toBytes(0x000F)
		)

	#switch on white list
	wrapper.setWhiteList(whiteLists.address, {"from": accounts[0]})
	
	with reverts("Ownable: caller is not the owner"):
		whiteLists.setRules(erc721mock.address, '0x0', '0x0001', {"from": accounts[1]})


	#prohibit rules for original token - disabled
	whiteLists.setRules(erc721mock.address, '0x0000', '0x0001', {"from": accounts[0]})

	assert whiteLists.validateRules(erc721mock.address, Web3.toBytes(0x000F)) != "0x000F"
	assert whiteLists.validateRules(erc721mock.address, Web3.toBytes(0x000F)) != "0x0000"
	with reverts("WL:Some rules are disabled for this asset"):
		wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})	

	logging.info(whiteLists.validateRules(erc721mock.address, Web3.toBytes(0x000F)))

	#allow use rules
	whiteLists.setRules(erc721mock.address, '0x0000', '0x0000', {"from": accounts[0]})

	wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address

	erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {"from": accounts[1]})
	erc721_data = (erc721_property, ORIGINAL_NFT_IDs[1], 0)

	wNFT = ( erc721_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		Web3.toBytes(0x000F)
	)

	#swith on OnliThis rule
	whiteLists.setRules(erc721mock.address, '0x0001', '0x0000', {"from": accounts[0]})

	with reverts("WL:Some rules are disabled for this asset"):
		wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

	whiteLists.setRules(erc721mock.address, '0x0000', '0x0000', {"from": accounts[0]})
	wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapper.address

	