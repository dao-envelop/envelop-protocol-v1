import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

def test_unwrap(accounts, wrapperLight, dai, weth, wnft1155ForWrapperLightV1, erc1155mock1, erc721mock1, mockHacker721_1):
    #make wrap NFT with empty
	in_type = 3
	out_type = 3
	in_nft_amount = 3
	out_nft_amount = 5
	
	#wrap ERC721 token. Contract of token change the balance for reciever. Token id 0
	mockHacker721_1.setFailReciever(accounts[9], 1)
	mockHacker721_1.setWrapper(wrapperLight.address)
	mockHacker721_1.mint(accounts[1], 0, {"from": accounts[1]})
	mockHacker721_1.approve(wrapperLight.address, 0, {"from": accounts[1]})

	dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
	weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

	dai.approve(wrapperLight.address, call_amount, {'from':accounts[1]})
	weth.approve(wrapperLight.address, 2*call_amount, {'from':accounts[1]})

	#make 721 for collateral - normal token
	makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
	erc721mock1.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

	#make 1155 for collateral - normal token
	makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
	erc1155mock1.setApprovalForAll(wrapperLight.address,True, {"from": accounts[1]})

	if (wrapperLight.lastWNFTId(out_type)[1] == 0):
		wrapperLight.setWNFTId(out_type, wnft1155ForWrapperLightV1.address, 0, {'from':accounts[0]})

	hack_property = (in_type, mockHacker721_1)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)
	erc721_property = (3, erc721mock1.address)
	erc1155_property = (4, erc1155mock1.address)

	hack_data = (hack_property, 0, 0)
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, Wei(eth_amount))
	erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 0)
	erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], in_nft_amount)

	fee = []
	lock = [('0x0', chain.time() + 100), ('0x0', chain.time() + 200)]
	royalty = []

	wNFT = ( hack_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		out_nft_amount,
		'0'
		)

	with reverts("Suspicious asset for wrap"):
		wrapperLight.wrap(wNFT, [dai_data, weth_data, erc721_data, erc1155_data], accounts[3], {"from": accounts[1], "value": eth_amount})
	wTokenId = wrapperLight.lastWNFTId(out_type)[1]
    
	assert dai.balanceOf(wrapperLight.address) == 0
	assert weth.balanceOf(wrapperLight.address) == 0
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[1]
	assert erc1155mock1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == 0
	assert wrapperLight.balance() == 0
	assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId) == 0
    
	