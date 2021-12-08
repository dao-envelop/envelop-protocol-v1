import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "4 ether"
in_type = 4
out_type = 4
nft_amount = 5


def test_simple_wrap(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20):
	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, nft_amount)


	erc1155mock.setApprovalForAll(wrapper.address,True, {'from':accounts[1]})
	dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
	weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

	wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})
	dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
	weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

	wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})

	erc1155_property = (in_type, erc1155mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], nft_amount)
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, Wei(eth_amount))

	fee = [('0x0', Wei(1e18), niftsy20.address)]
	lock = [('0x0', chain.time() + 10), ('0x0', chain.time() + 20)]
	royalty = [(accounts[1], 100), (accounts[2], 200)]

	wNFT = ( erc1155_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		nft_amount,
		'0'
		)

	wrapper.wrap(wNFT, [dai_data, weth_data, eth_data], accounts[3], {"from": accounts[1], "value": "4 ether"})
	
	#checks
	assert wrapper.balance() == eth_amount
	assert dai.balanceOf(wrapper) == call_amount
	assert weth.balanceOf(wrapper) == 2*call_amount
	assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == nft_amount
	assert wnft1155.balanceOf(accounts[3].address,wrapper.lastWNFTId(out_type)[1]) == nft_amount
	assert wnft1155.totalSupply(wrapper.lastWNFTId(out_type)[1]) == nft_amount

	wTokenId = wrapper.lastWNFTId(out_type)[1]
	wNFT = wrapper.getWrappedToken(wnft1155, wTokenId)
	#logging.info(wNFT)
	assert wNFT[0] == erc1155_data
	assert wNFT[1] == [eth_data, dai_data, weth_data]
	assert wNFT[2] == accounts[2]
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0'	
