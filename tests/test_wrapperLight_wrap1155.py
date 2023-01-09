import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 4
out_type = 4
nft_amount = 5


def test_simple_wrap(accounts, erc1155mock, wrapperLight, dai, weth, wnft1155ForWrapperLightV1):
	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, nft_amount)


	erc1155mock.setApprovalForAll(wrapperLight.address,True, {'from':accounts[1]})
	dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
	weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

	dai.approve(wrapperLight.address, call_amount, {'from':accounts[1]})
	weth.approve(wrapperLight.address, 2*call_amount, {'from':accounts[1]})

	wrapperLight.setWNFTId(out_type, wnft1155ForWrapperLightV1.address, 0, {'from':accounts[0]})

	erc1155_property = (in_type, erc1155mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], nft_amount)
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, Wei(eth_amount))

	fee = []
	lock = [('0x0', chain.time() + 10), ('0x0', chain.time() + 20)]
	royalty = []

	wNFT = ( erc1155_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		nft_amount,
		'0'
		)

	tx = wrapperLight.wrap(wNFT, [dai_data, weth_data, eth_data], accounts[3], {"from": accounts[1], "value": eth_amount})
	#tx = wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	#checks
	assert wrapperLight.balance() == eth_amount
	assert dai.balanceOf(wrapperLight) == call_amount
	assert weth.balanceOf(wrapperLight) == 2*call_amount
	assert erc1155mock.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == nft_amount
	assert wnft1155ForWrapperLightV1.balanceOf(accounts[3].address,wrapperLight.lastWNFTId(out_type)[1]) == nft_amount
	assert wnft1155ForWrapperLightV1.totalSupply(wrapperLight.lastWNFTId(out_type)[1]) == nft_amount

	wTokenId = wrapperLight.lastWNFTId(out_type)[1]
	wNFT = wrapperLight.getWrappedToken(wnft1155ForWrapperLightV1, wTokenId)
	#logging.info(wNFT)
	assert wNFT[0] == erc1155_data
	assert wNFT[1] == [eth_data, dai_data, weth_data]
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0'	
