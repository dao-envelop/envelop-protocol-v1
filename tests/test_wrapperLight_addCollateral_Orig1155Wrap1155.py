import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest1155, makeFromERC1155ToERC1155WithoutCollateral


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5
coll_amount = 2
in_type = 4
out_type = 4

def test_addColl(accounts, erc1155mock, wrapperLight, dai, weth, wnft1155ForWrapperLightV1, niftsy20, erc1155mock1):
	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
	makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)

	#make wrap NFT 1155
	#wTokenId = makeFromERC1155ToERC1155WithoutCollateral(accounts, erc1155mock, wrapperLight, wnft1155ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], in_nft_amount, out_nft_amount, accounts[3])
	erc1155mock.setApprovalForAll(wrapperLight.address,True, {"from": accounts[1]}) 
	if (wrapperLight.lastWNFTId(out_type)[1] == 0):
		wrapperLight.setWNFTId(out_type, wnft1155ForWrapperLightV1.address, 0, {'from':accounts[0]})
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
	assert erc1155mock.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount
	wTokenId = wrapperLight.lastWNFTId(out_type)[1]
	assert wnft1155ForWrapperLightV1.balanceOf(accounts[3], wTokenId) == out_nft_amount

	#with asset data - ERC1155 and native tokens. Not exists allowance
	erc1155mock.safeTransferFrom(accounts[0], accounts[9], ORIGINAL_NFT_IDs[1], in_nft_amount, '', {"from": accounts[0]})
	with reverts(""):
		wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[1], coll_amount)], {'from': accounts[9], "value": '1 ether'})
	
	#with asset data - ERC1155 and native tokens. Exists allowance
	erc1155mock.setApprovalForAll(wrapperLight.address,True, {"from": accounts[9]})
	wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[1], coll_amount)], {'from': accounts[9], "value": '1 ether'})
	
	#with asset data - ERC1155 token. Wrong type
	erc1155mock.safeTransferFrom(accounts[0], accounts[9], ORIGINAL_NFT_IDs[2], in_nft_amount, '', {"from": accounts[0]})
	with reverts(""):
		wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((3, erc1155mock.address), ORIGINAL_NFT_IDs[2], coll_amount-1)], {'from': accounts[9]})	

	#with asset data - ERC1155 token. Msg.Sender is not owner of token
	with reverts("ERC1155: caller is not token owner nor approved"):
		wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[2], coll_amount-1)], {'from': accounts[8]})

	#with asset data - ERC1155 token. Not enough balance for transfer
	with reverts("ERC1155: insufficient balance for transfer"):
		wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[2], coll_amount+10)], {'from': accounts[9]})

	#with asset data - ERC1155 token. Second token to collateral
	wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[2], coll_amount-1)], {'from': accounts[9]})

	#with asset data - ERC1155 token. Second token to collateral. Add balance
	wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[2], 1)], {'from': accounts[9]})

	#with asset data - ERC1155 token. Second contract to collateral
	erc1155mock1.setApprovalForAll(wrapperLight.address,True, {'from':accounts[1]})
	wrapperLight.addCollateral(wnft1155ForWrapperLightV1.address, wTokenId, [((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)], {'from': accounts[1]})

	logging.info(wrapperLight.getWrappedToken(wnft1155ForWrapperLightV1, wTokenId)[1])
	logging.info(wrapperLight.getWrappedToken(wnft1155ForWrapperLightV1, wTokenId)[1][0])

	assert wrapperLight.balance() == "1 ether"

	collateral = wrapperLight.getWrappedToken(wnft1155ForWrapperLightV1, wTokenId)[1]
	assert collateral[0][2] == "1 ether"
	assert collateral[0][0][0] == 1
	assert collateral[1][0][0] == 4
	assert collateral[2][0][0] == 4
	assert collateral[3][0][0] == 4
	assert collateral[1][1] == ORIGINAL_NFT_IDs[1]
	assert collateral[1][2] == coll_amount
	assert collateral[1][0][1] == erc1155mock.address
	assert collateral[2][1] == ORIGINAL_NFT_IDs[2]
	assert collateral[2][2] == coll_amount
	assert collateral[2][0][1] == erc1155mock.address
	assert collateral[3][1] == ORIGINAL_NFT_IDs[0]
	assert collateral[3][2] == coll_amount
	assert collateral[3][0][1] == erc1155mock1.address
	assert erc1155mock.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[1]) == coll_amount
	assert erc1155mock.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[2]) == coll_amount
	assert erc1155mock1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	assert erc1155mock.balanceOf(accounts[9], ORIGINAL_NFT_IDs[1]) == in_nft_amount-coll_amount
	assert erc1155mock.balanceOf(accounts[9], ORIGINAL_NFT_IDs[2]) == in_nft_amount-coll_amount
	assert erc1155mock1.balanceOf(accounts[1], ORIGINAL_NFT_IDs[0]) == in_nft_amount-coll_amount

