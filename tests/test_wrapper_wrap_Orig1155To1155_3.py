import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

def test_wrap(accounts, erc1155mock, wrapper, wnft1155, whiteLists, erc721mock, erc721mock1):
    #make wrap NFT with empty
	in_type = 4
	out_type = 4
	in_nft_amount = 3
	out_nft_amount = 5

	#make 1155 for wrap
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
	erc1155mock.setApprovalForAll(wrapper.address,True, {'from':accounts[1]})

	if (wrapper.lastWNFTId(out_type)[1] == 0):
		wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
	wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})

	erc1155_property = (4, erc1155mock.address)
	erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], in_nft_amount)

	fee = []
	lock = []
	royalty = []

	wNFT = ( erc1155_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		out_nft_amount,
		'0'
		)

	with reverts("Ownable: caller is not the owner"):
		whiteLists.setBLItem(erc1155mock.address, True, {"from": accounts[2]})

	#switch on white list
	wrapper.setWhiteList(whiteLists.address, {"from": accounts[0]})
	whiteLists.setBLItem(erc1155mock.address, True, {"from": accounts[0]})

	with reverts("WL:Asset disabled for wrap"):
		wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

	whiteLists.setBLItem(erc721mock.address, True, {"from": accounts[0]})
	whiteLists.setBLItem(erc721mock1.address, True, {"from": accounts[0]})

	assert whiteLists.getBLItemCount() == 3
    
	assert erc1155mock.balanceOf(accounts[1], ORIGINAL_NFT_IDs[0]) == in_nft_amount

	whiteLists.setBLItem(erc1155mock.address, False, {"from": accounts[0]})

	assert whiteLists.getBLItemCount() == 2

	wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount

	#add in blist again
	whiteLists.setBLItem(erc1155mock.address, True, {"from": accounts[0]})
	assert whiteLists.getBLItemCount() == 3

	erc1155mock.safeTransferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], in_nft_amount, "",  {"from": accounts[0]})
	erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[1], in_nft_amount)

	wNFT = ( erc1155_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		out_nft_amount,
		'0'
		)

	with reverts("WL:Asset disabled for wrap"):
		wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})





    
	