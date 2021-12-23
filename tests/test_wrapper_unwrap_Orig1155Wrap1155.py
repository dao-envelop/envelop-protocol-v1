import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest1155, makeFromERC1155ToERC1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5

def test_unwrap(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20):
	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)

	#make wrap NFT 1155
	wTokenId = makeFromERC1155ToERC1155(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20, ORIGINAL_NFT_IDs[0], in_nft_amount, out_nft_amount, accounts[3])
	
	assert wnft1155.balanceOf(accounts[3].address, wTokenId) == out_nft_amount

	contract_eth_balance = wrapper.balance()
	before_dai_balance = wrapper.getERC20CollateralBalance(wnft1155.address, wTokenId, dai.address)
	before_weth_balance = wrapper.getERC20CollateralBalance(wnft1155.address, wTokenId, weth.address)
	before_eth_balance = wrapper.getERC20CollateralBalance(wnft1155.address, wTokenId, zero_address)
	before_acc_balance = accounts[2].balance()

	#unwrap by UnwrapDestinition
	wrapper.unWrap(4, wnft1155.address, wTokenId, {"from": accounts[2]})
	
	#checks
	assert wrapper.balance() == 0
	assert accounts[2].balance() == before_acc_balance + contract_eth_balance
	assert dai.balanceOf(wrapper) == 0
	assert weth.balanceOf(wrapper) == 0
	assert dai.balanceOf(accounts[2]) == before_dai_balance
	assert weth.balanceOf(accounts[2]) == before_weth_balance
	assert erc1155mock.balanceOf(accounts[2].address, ORIGINAL_NFT_IDs[0]) == in_nft_amount
	assert wnft1155.totalSupply(wTokenId) == 0
