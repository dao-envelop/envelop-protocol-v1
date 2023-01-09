import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3


def test_simple_wrap(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

	erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
	weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

	dai.approve(wrapperLight.address, call_amount, {'from':accounts[1]})
	weth.approve(wrapperLight.address, 2*call_amount, {'from':accounts[1]})

	wrapperLight.setWNFTId(out_type, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})

	erc721_property = (in_type, erc721mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 1)
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, Wei(eth_amount))

	fee = [('0x00', 1e18, niftsy20.address)]
	lock = [('0x0', chain.time() + 10)]
	royalty = [(accounts[1], 10000)]

	wNFT = ( erc721_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		'0'
		)

	wrapperLight.wrap(wNFT, [dai_data, weth_data, eth_data], accounts[3], {"from": accounts[1], "value": eth_amount})
	
	#checks
	assert wrapperLight.balance() == eth_amount
	assert dai.balanceOf(wrapperLight) == call_amount
	assert weth.balanceOf(wrapperLight) == 2*call_amount
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
	assert wnft721ForWrapperLightV1.ownerOf(wrapperLight.lastWNFTId(out_type)[1]) == accounts[3].address
	assert wnft721ForWrapperLightV1.totalSupply() == 1

	wTokenId = wrapperLight.lastWNFTId(out_type)[1]
	wNFT = wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)
	#logging.info(wNFT)
	assert wNFT[0] == erc721_data
	assert wNFT[1] == [eth_data, dai_data, weth_data]
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0'	
