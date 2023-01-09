import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5

def test_unwrap(accounts, erc721mock, wrapperLight, dai, weth, wnft1155ForWrapperLightV1, niftsy20, wrapperCheckerLightV1):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

	#make wrap NFT 1155
	in_type = 3
	out_type = 4
	erc721mock.setApprovalForAll(wrapperLight.address, True, {'from':accounts[1]})
	if (wrapperLight.lastWNFTId(out_type)[1] == 0):
		wrapperLight.setWNFTId(out_type, wnft1155ForWrapperLightV1.address, 0, {'from':accounts[0]})
	erc721_property = (in_type, erc721mock.address)
	erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 1)
	fee = []
	lock = []
	royalty = []
	wNFT = ( erc721_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		out_nft_amount,
		'0'
		)
	wrapperLight.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	wTokenId = wrapperLight.lastWNFTId(out_type)[1]
	
	assert wnft1155ForWrapperLightV1.balanceOf(accounts[3].address, wTokenId) == out_nft_amount

	contract_eth_balance = wrapperLight.balance()
	before_dai_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft1155ForWrapperLightV1.address, wTokenId, dai.address)[0]
	before_weth_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft1155ForWrapperLightV1.address, wTokenId, weth.address)[0]
	before_eth_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft1155ForWrapperLightV1.address, wTokenId, zero_address)[0]
	before_acc_balance = accounts[3].balance()

	#check tokenUri
	orig_token_uri = wrapperLight.getOriginalURI(wnft1155ForWrapperLightV1.address, wTokenId)
	logging.info(orig_token_uri)
	logging.info(wnft1155ForWrapperLightV1.uri(wTokenId))
	logging.info(erc721mock.tokenURI(ORIGINAL_NFT_IDs[0]))
	logging.info(erc721mock)
	assert orig_token_uri == erc721mock.tokenURI(ORIGINAL_NFT_IDs[0])

	chain.sleep(120)
	chain.mine()

	wrapperLight.unWrap(4, wnft1155ForWrapperLightV1.address, wTokenId, {"from": accounts[3]})
	
	#checks
	assert wrapperLight.balance() == 0
	assert accounts[3].balance() == before_acc_balance + contract_eth_balance
	assert dai.balanceOf(wrapperLight) == 0
	assert weth.balanceOf(wrapperLight) == 0
	assert dai.balanceOf(accounts[3]) == before_dai_balance
	assert weth.balanceOf(accounts[3]) == before_weth_balance
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert wnft1155ForWrapperLightV1.totalSupply(wTokenId) == 0
