import pytest
import logging
from brownie import chain, Wei, reverts
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
		'0'
		)

	with reverts("Ownable: caller is not the owner"):
		whiteLists.setBLItem(erc721mock.address, True, {"from": accounts[2]})

	#switch on white list
	wrapper.setWhiteList(whiteLists.address, {"from": accounts[0]})
	whiteLists.setBLItem(erc721mock.address, True, {"from": accounts[0]})

	with reverts("WL:Asset disabled for wrap"):
		wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

	whiteLists.setBLItem(erc1155mock.address, True, {"from": accounts[0]})
	whiteLists.setBLItem(erc721mock1.address, True, {"from": accounts[0]})

	assert whiteLists.getBLItemCount() == 3
    
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[1]

	whiteLists.setBLItem(erc721mock.address, False, {"from": accounts[0]})

	assert whiteLists.getBLItemCount() == 2

	wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address

	#add in blist again
	whiteLists.setBLItem(erc721mock.address, True, {"from": accounts[0]})
	assert whiteLists.getBLItemCount() == 3

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
		'0'
		)

	with reverts("WL:Asset disabled for wrap"):
		wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})





    
	