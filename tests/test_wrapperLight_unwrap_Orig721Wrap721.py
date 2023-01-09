import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721Light


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'

def test_unwrap(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20, wrapperCheckerLightV1):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

	#make wrap NFT 721
	wTokenId = makeFromERC721ToERC721Light(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])

	#check tokenUri
	orig_token_uri = wrapperLight.getOriginalURI(wnft721ForWrapperLightV1.address, wTokenId)
	logging.info(orig_token_uri)
	logging.info(wnft721ForWrapperLightV1.tokenURI(wTokenId))
	logging.info(wnft721ForWrapperLightV1.baseURI())
	logging.info(erc721mock.tokenURI(ORIGINAL_NFT_IDs[0]))
	assert orig_token_uri.find(wnft721ForWrapperLightV1.baseURI()) == -1
	assert orig_token_uri == erc721mock.tokenURI(ORIGINAL_NFT_IDs[0])

	
	assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]

	contract_eth_balance = wrapperLight.balance()
	before_dai_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, dai.address)[0]
	before_weth_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, weth.address)[0]
	before_eth_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, zero_address)[0]
	before_acc_balance = accounts[3].balance()


	#unwrap by not owner and UnwrapDestination
	with reverts("Only owner can unwrap it"):
		wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, {"from": accounts[9]})

	#unwrap by UnwrapDestination
	with reverts("Only owner can unwrap it"):
		wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, {"from": accounts[2]})

	wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, {"from": accounts[3]})

	
	#checks
	assert wrapperLight.balance() == 0
	assert accounts[3].balance() == before_acc_balance + contract_eth_balance
	assert dai.balanceOf(wrapperLight) == 0
	assert weth.balanceOf(wrapperLight) == 0
	assert dai.balanceOf(accounts[3]) == before_dai_balance
	assert weth.balanceOf(accounts[3]) == before_weth_balance

	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert wnft721ForWrapperLightV1.totalSupply() == 0
