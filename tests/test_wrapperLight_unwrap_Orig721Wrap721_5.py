import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateralLight, makeNFTForTest1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
amount = 100
in_nft_amount = 3
coll_amount = 2

def test_addColl(accounts, erc721mock, wrapperLight, wnft721ForWrapperLightV1, niftsy20, erc1155mock1, erc721mock1, mockHacker):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
	
	#make wrap NFT 721
	wTokenId = makeFromERC721ToERC721WithoutCollateralLight(accounts, erc721mock, wrapperLight, wnft721ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
	
	assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]

	#with asset data - ERC20 token. Token will block transfer from wrapperLight to account
	mockHacker.setFailSender(wrapperLight.address)
	mockHacker.transfer(accounts[1], amount, {"from": accounts[0]})
	mockHacker.approve(wrapperLight.address, amount, {"from": accounts[1]})
	
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((2, mockHacker.address), 0, amount)], {'from': accounts[1], "value": "1 ether"})

    #make 721 for collateral - normal token
	makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
	erc721mock1.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

	#make 1155 for collateral - normal token
	makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
	erc1155mock1.setApprovalForAll(wrapperLight.address,True, {"from": accounts[1]})

	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
		], {'from': accounts[1]})
	wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)
		], {'from': accounts[1]})

	collateral = wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)[1]
	
	assert mockHacker.balanceOf(accounts[1]) == 0 #check balance
	assert mockHacker.balanceOf(wrapperLight.address) == amount #check balance
	assert collateral[0] == ((1, zero_address), 0 , Wei("1 ether"))
	assert collateral[1] == ((2, mockHacker.address), 0, amount)
	assert collateral[2] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
	assert collateral[3] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)

	logging.info(wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)[1])
	
	#revert - usual method
	with reverts("Hack your Wrapper"):
		wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, {"from": accounts[3]})

	assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
	assert erc1155mock1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	assert wrapperLight.balance() == "1 ether"


	eth_balance_acc = accounts[3].balance()
	eth_balance_contract = wrapperLight.balance()

	#Emergency mode for unWrap
	tx = wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, True,  {"from": accounts[3]})

	logging.info(tx.events)

	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == coll_amount
	assert wrapperLight.balance() == 0
	assert accounts[3].balance() == eth_balance_acc+eth_balance_contract
	assert mockHacker.balanceOf(wrapperLight.address) == amount #check balance


