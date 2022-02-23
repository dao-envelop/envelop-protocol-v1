import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest1155, makeFromERC1155ToERC721


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5

def test_unwrap(accounts, erc1155mock, wrapper, dai, weth, wnft721, niftsy20, wrapperChecker):
	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)

	#make wrap NFT 721
	wTokenId = makeFromERC1155ToERC721(accounts, erc1155mock, wrapper, dai, weth, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], in_nft_amount, accounts[3], True)
	
	assert wnft721.ownerOf(wTokenId) == accounts[3]

	contract_eth_balance = wrapper.balance()
	before_dai_balance = wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId, dai.address)[0]
	before_weth_balance = wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId, weth.address)[0]
	before_eth_balance = wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId, zero_address)[0]
	before_acc_balance = accounts[3].balance()

	#check tokenUri
	orig_token_uri = wrapper.getOriginalURI(wnft721.address, wTokenId)
	logging.info(orig_token_uri)
	logging.info(wnft721.tokenURI(wTokenId))
	logging.info(wnft721.baseURI())
	logging.info(erc1155mock.uri(0))
	assert orig_token_uri.find(wnft721.baseURI()) == -1
	assert orig_token_uri == erc1155mock.uri(0)


	chain.sleep(120)
	chain.mine()

	#unwrap by UnwrapDestinition
	with reverts("Only owner can unwrap it"):
		wrapper.unWrap(3, wnft721.address, wTokenId, {"from": accounts[2]})

	#unwrap by owner
	wrapper.unWrap(3, wnft721.address, wTokenId, {"from": accounts[3]})
	
	#checks
	assert wrapper.balance() == 0
	assert accounts[3].balance() == before_acc_balance + contract_eth_balance
	assert dai.balanceOf(wrapper) == 0
	assert weth.balanceOf(wrapper) == 0
	assert dai.balanceOf(accounts[3]) == before_dai_balance
	assert weth.balanceOf(accounts[3]) == before_weth_balance
	assert erc1155mock.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == in_nft_amount
