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

def test_addColl(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20):
	#make test data
	makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)

	#make wrap NFT 1155
	wTokenId = makeFromERC1155ToERC1155WithoutCollateral(accounts, erc1155mock, wrapper, wnft1155, niftsy20, ORIGINAL_NFT_IDs[0], in_nft_amount, out_nft_amount, accounts[3])
	
	
	assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount

	#with asset data - ERC1155 and native tokens. Not exists allowance
	erc1155mock.safeTransferFrom(accounts[0], accounts[9], ORIGINAL_NFT_IDs[1], in_nft_amount, '', {"from": accounts[0]})
	with reverts(""):
		wrapper.addCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[1], coll_amount)], {'from': accounts[9], "value": '1 ether'})
	
	#with asset data - ERC1155 and native tokens. Exists allowance
	erc1155mock.setApprovalForAll(wrapper.address,True, {"from": accounts[9]})
	wrapper.addCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[1], coll_amount)], {'from': accounts[9], "value": '1 ether'})
	
	#with asset data - ERC1155 token. Wrong type
	erc1155mock.safeTransferFrom(accounts[0], accounts[9], ORIGINAL_NFT_IDs[2], in_nft_amount, '', {"from": accounts[0]})
	with reverts(""):
		wrapper.addCollateral(wnft1155.address, wTokenId, [((3, erc1155mock.address), ORIGINAL_NFT_IDs[2], coll_amount-1)], {'from': accounts[9]})	

	#with asset data - ERC1155 token. Msg.Sender is not owner of token
	with reverts("ERC1155: caller is not owner nor approved"):
		wrapper.addCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[2], coll_amount-1)], {'from': accounts[8]})

	#with asset data - ERC1155 token. Not enough balance for transfer
	with reverts("ERC1155: insufficient balance for transfer"):
		wrapper.addCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[2], coll_amount+10)], {'from': accounts[9]})

	#with asset data - ERC1155 token. Second token to collateral
	wrapper.addCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[2], coll_amount-1)], {'from': accounts[9]})

	#with asset data - ERC1155 token. Second token to collateral. Add balance
	wrapper.addCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[2], 1)], {'from': accounts[9]})


	logging.info(wrapper.getWrappedToken(wnft1155, wTokenId)[1])
	logging.info(wrapper.getWrappedToken(wnft1155, wTokenId)[1][0])

	assert wrapper.balance() == "1 ether"

	collateral = wrapper.getWrappedToken(wnft1155, wTokenId)[1]
	assert collateral[0][2] == "1 ether"
	assert collateral[0][0][0] == 1
	assert collateral[1][0][0] == 4
	assert collateral[1][1] == ORIGINAL_NFT_IDs[1]
	assert collateral[1][2] == coll_amount
	assert collateral[1][0][1] == erc1155mock.address
	assert collateral[2][1] == ORIGINAL_NFT_IDs[2]
	assert collateral[2][2] == coll_amount
	assert collateral[2][0][1] == erc1155mock.address
	assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[1]) == coll_amount
	assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[2]) == coll_amount
	assert erc1155mock.balanceOf(accounts[9], ORIGINAL_NFT_IDs[1]) == in_nft_amount-coll_amount
	assert erc1155mock.balanceOf(accounts[9], ORIGINAL_NFT_IDs[2]) == in_nft_amount-coll_amount

