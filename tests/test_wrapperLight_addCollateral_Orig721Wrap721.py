import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateralLight


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'

def test_addColl(accounts, erc721mock, wrapperLight, wnft721ForWrapperLightV1, niftsy20, erc721mock1):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
	makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)

	#make wrap NFT 721
	wTokenId = makeFromERC721ToERC721WithoutCollateralLight(accounts, erc721mock, wrapperLight, wnft721ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
	
	assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]

	
	#without asset data
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [], {'from': accounts[9], "value": '1 ether'})

	#with asset data - empty type
	with reverts(""):
		wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((0, zero_address), 0, 10)], {'from': accounts[9], "value": '1 ether'})

	#with asset data - native type, amount in array is less than in value
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((1, zero_address), 0, 10)], {'from': accounts[3], "value": '1 ether'})

	#with asset data - native type, amount in array is more than in value
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((1, zero_address), 0, Wei("10 ether"))], {'from': accounts[3], "value": '1 ether'})


	#with asset data - ERC721 and native tokens. Not exists allowance
	erc721mock.transferFrom(accounts[0], accounts[9], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
	with reverts(""):
		wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[1], 0)], {'from': accounts[9], "value": '1 ether'})

	#with asset data - ERC721 and native tokens. Exists allowance
	erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[1], {"from": accounts[9]})
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[1], 0)], {'from': accounts[9], "value": '1 ether'})
	
	#with asset data - ERC721 token. Wrong type
	erc721mock.transferFrom(accounts[0], accounts[9], ORIGINAL_NFT_IDs[2], {"from": accounts[0]})
	erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[2], {"from": accounts[9]})
	with reverts(""):
		wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((4, erc721mock.address), ORIGINAL_NFT_IDs[2], 0)], {'from': accounts[9]})	
	
	#with asset data - ERC721 token. Msg.Sender is not owner of token
	with reverts(""):
		wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[2], 0)], {'from': accounts[8]})
	
	#with asset data - ERC721 token. Second token to collateral
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[2], 0)], {'from': accounts[9]})

	#with asset data - ERC721 token. Second contract to collateral
	erc721mock1.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)], {'from': accounts[1]})

	logging.info(wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)[1])
	logging.info(wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)[1][0])

	assert wrapperLight.balance() == "4 ether"

	collateral = wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)[1]
	assert collateral[0][2] == "4 ether"
	assert collateral[0][0][0] == 1
	assert collateral[1][0][0] == 3
	assert collateral[2][0][0] == 3
	assert collateral[3][0][0] == 3
	assert collateral[1][1] == ORIGINAL_NFT_IDs[1]
	assert collateral[2][1] == ORIGINAL_NFT_IDs[2]
	assert collateral[3][1] == ORIGINAL_NFT_IDs[0]
	assert collateral[1][0][1] == erc721mock.address
	assert collateral[2][0][1] == erc721mock.address
	assert collateral[3][0][1] == erc721mock1.address
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapperLight.address
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[2]) == wrapperLight.address
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
	assert erc721mock.balanceOf(wrapperLight.address) == 3
	assert erc721mock1.balanceOf(wrapperLight.address) == 1

	assert wrapperLight.getCollateralBalanceAndIndex(wnft721ForWrapperLightV1.address, wTokenId, 3, erc721mock1.address, ORIGINAL_NFT_IDs[0])[0] == 0
	assert wrapperLight.getCollateralBalanceAndIndex(wnft721ForWrapperLightV1.address, wTokenId, 3, erc721mock1.address, ORIGINAL_NFT_IDs[0])[1] == 3

