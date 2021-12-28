import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5

def test_unwrap(accounts, erc721mock, wrapper, dai, weth, wnft1155, niftsy20):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

	#make wrap NFT 1155
	wTokenId = makeFromERC721ToERC1155(accounts, erc721mock, wrapper, dai, weth, wnft1155, niftsy20, ORIGINAL_NFT_IDs[0], out_nft_amount, accounts[3], True)
	
	assert wnft1155.balanceOf(accounts[3].address, wTokenId) == out_nft_amount

	contract_eth_balance = wrapper.balance()
	before_dai_balance = wrapper.getERC20CollateralBalance(wnft1155.address, wTokenId, dai.address)
	before_weth_balance = wrapper.getERC20CollateralBalance(wnft1155.address, wTokenId, weth.address)
	before_eth_balance = wrapper.getERC20CollateralBalance(wnft1155.address, wTokenId, zero_address)
	before_acc_balance = accounts[2].balance()

	#check tokenUri
	orig_token_uri = wrapper.getOriginalURI(wnft1155.address, wTokenId)
	logging.info(orig_token_uri)
	logging.info(wnft1155.uri(wTokenId))
	logging.info(erc721mock.tokenURI(ORIGINAL_NFT_IDs[0]))
	logging.info(erc721mock)
	logging.info(wnft1155.baseurl())
	assert orig_token_uri.find(wnft1155.baseurl(), 0) == -1
	assert orig_token_uri == erc721mock.tokenURI(ORIGINAL_NFT_IDs[0])

	chain.sleep(120)
	chain.mine()

	wrapper.unWrap(4, wnft1155.address, wTokenId, {"from": accounts[3]})
	
	#checks
	assert wrapper.balance() == 0
	assert accounts[2].balance() == before_acc_balance + contract_eth_balance
	assert dai.balanceOf(wrapper) == 0
	assert weth.balanceOf(wrapper) == 0
	assert dai.balanceOf(accounts[2]) == before_dai_balance
	assert weth.balanceOf(accounts[2]) == before_weth_balance
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[2]
	assert wnft1155.totalSupply(wTokenId) == 0
