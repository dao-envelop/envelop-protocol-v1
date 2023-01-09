import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest1155, makeFromERC1155ToERC721


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5

def test_unwrap(accounts, erc1155mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20, wrapperCheckerLightV1):
	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)

	#make wrap NFT 721
	#wTokenId = makeFromERC1155ToERC721(accounts, erc1155mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], in_nft_amount, accounts[3], True)
	erc1155mock.setApprovalForAll(wrapperLight.address,True, {'from':accounts[1]})
	in_type = 4
	out_type = 3
	if (wrapperLight.lastWNFTId(out_type)[1] == 0):
		wrapperLight.setWNFTId(out_type, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})
	token_property = (in_type, erc1155mock)
	token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
	fee = []
	lock = []
	royalty = []
	wNFT = ( token_data,
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
	assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]

	contract_eth_balance = wrapperLight.balance()
	before_dai_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, dai.address)[0]
	before_weth_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, weth.address)[0]
	before_eth_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, zero_address)[0]
	before_acc_balance = accounts[3].balance()

	#check tokenUri
	orig_token_uri = wrapperLight.getOriginalURI(wnft721ForWrapperLightV1.address, wTokenId)
	logging.info(orig_token_uri)
	logging.info(wnft721ForWrapperLightV1.tokenURI(wTokenId))
	logging.info(wnft721ForWrapperLightV1.baseURI())
	logging.info(erc1155mock.uri(0))
	assert orig_token_uri.find(wnft721ForWrapperLightV1.baseURI()) == -1
	assert orig_token_uri == erc1155mock.uri(0)


	chain.sleep(120)
	chain.mine()

	#unwrap by UnwrapDestination
	with reverts("Only owner can unwrap it"):
		wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, {"from": accounts[2]})

	#unwrap by owner
	wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, {"from": accounts[3]})
	
	#checks
	assert wrapperLight.balance() == 0
	assert accounts[3].balance() == before_acc_balance + contract_eth_balance
	assert dai.balanceOf(wrapperLight) == 0
	assert weth.balanceOf(wrapperLight) == 0
	assert dai.balanceOf(accounts[3]) == before_dai_balance
	assert weth.balanceOf(accounts[3]) == before_weth_balance
	assert erc1155mock.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == in_nft_amount
