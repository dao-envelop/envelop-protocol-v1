import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateral, makeNFTForTest1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5
coll_amount = 2

def test_addColl(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, mockHacker721_1, erc1155mock1, erc721mock1):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
	
	#make wrap NFT 721
	wTokenId = makeFromERC721ToERC721WithoutCollateral(accounts, erc721mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])
	
	assert wnft721.ownerOf(wTokenId) == accounts[3]

	#with asset data - ERC721 token. Token will be burnt after adding to collateral
	mockHacker721_1.setFailReciever(accounts[9],2)
	mockHacker721_1.setWrapper(wrapper.address)
	mockHacker721_1.mint(accounts[1], 0, {"from": accounts[1]})
	mockHacker721_1.approve(wrapper.address, 0, {"from": accounts[1]})
	
	wrapper.addCollateral(wnft721.address, wTokenId, [((3, mockHacker721_1.address), 0, 0)], {'from': accounts[1], "value": "1 ether"})

    #make 721 for collateral - normal token
	makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
	erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

	#make 1155 for collateral - normal token
	makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
	erc1155mock1.setApprovalForAll(wrapper.address,True, {"from": accounts[1]})

	wrapper.addCollateral(wnft721.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
		], {'from': accounts[1]})
	wrapper.addCollateral(wnft721.address, wTokenId, [((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)
		], {'from': accounts[1]})

	collateral = wrapper.getWrappedToken(wnft721, wTokenId)[1]
	
	assert mockHacker721_1.balanceOf(accounts[1]) == 0 #check balance
	assert mockHacker721_1.ownerOf(0) == wrapper #check owner
	assert collateral[0] == ((1, zero_address), 0 , Wei("1 ether"))
	assert collateral[1] == ((3, mockHacker721_1.address), 0, 0)
	assert collateral[2] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
	assert collateral[3] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)

	logging.info('\nwNFT:{},{}\nIn asset:{},\nCollateral records:\n {}'.format(
		wnft721, wTokenId,
		wrapper.getWrappedToken(wnft721, wTokenId)[0],
		wrapper.getWrappedToken(wnft721, wTokenId)[1]
	)
	)
	#burn collateral 721 token
	mockHacker721_1.burn(0)

	#revert - usual method
	with reverts("ERC721: owner query for nonexistent token"):
		wrapper.unWrap(3, wnft721.address, wTokenId, {"from": accounts[3]})

	assert wnft721.ownerOf(wTokenId) == accounts[3]
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
	assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	assert wrapper.balance() == "1 ether"


	eth_balance_acc = accounts[3].balance()
	eth_balance_contract = wrapper.balance()

	#Emergency mode for unWrap
	tx = wrapper.unWrap(3, wnft721.address, wTokenId, True,  {"from": accounts[3]})

	logging.info(tx.events)
	logging.info('\nwNFT:{},{}\nIn asset:{},\nCollateral records:\n {}'.format(
		wnft721, wTokenId,
		wrapper.getWrappedToken(wnft721, wTokenId)[0],
		wrapper.getWrappedToken(wnft721, wTokenId)[1]
	)
	)

	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == coll_amount
	assert wrapper.balance() == 0
	assert accounts[3].balance() == eth_balance_acc+eth_balance_contract


