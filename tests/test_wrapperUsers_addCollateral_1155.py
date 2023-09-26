import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721
from web3 import Web3


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 4
out_type = 4
out_amount = 3



def test_call_factory(accounts, usersSBTRegistry, wrapperUsers, wnft1155SBT, wnft721SBT):
    usersSBTRegistry.addImplementation((3,wnft721SBT), {'from': accounts[0]})
    usersSBTRegistry.addImplementation((4,wnft1155SBT), {'from': accounts[0]})
    usersSBTRegistry.deployNewCollection(
        wnft1155SBT, 
        accounts[0],'', '', '', wrapperUsers, {'from': accounts[0]}
    )

    logging.info(usersSBTRegistry.getUsersCollections(accounts[0]))
    assert len(usersSBTRegistry.getUsersCollections(accounts[0])) == 1

def test_addColl(accounts, erc721mock, wrapperUsers, wnft1155SBT, niftsy20, erc721mock1, erc1155mock, dai):
	#make test data
	erc1155mock.mint(accounts[0], ORIGINAL_NFT_IDs[1], 2, {"from": accounts[0]})
	erc721mock.mint(ORIGINAL_NFT_IDs[0], {"from": accounts[0]})
	erc721mock1.mint(ORIGINAL_NFT_IDs[0], {"from": accounts[0]})
	erc1155mock.mint(accounts[0], ORIGINAL_NFT_IDs[0], 1, {"from": accounts[0]})
	

	#make wrap NFT 1155
	erc1155mock.setApprovalForAll(wrapperUsers, True, {"from": accounts[0]})
	erc1155_property = (in_type, erc1155mock.address)
	erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], 1)

	fee = []
	lock = []
	royalty = []

	wNFT = ( erc1155_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		out_amount,
		Web3.toBytes(0x0004)  #rules - No Transfer
		)

	tx = wrapperUsers.wrapIn(wNFT, [], accounts[3], wnft1155SBT,  {"from": accounts[0]})

	wTokenId = tx.return_value[1]
	
	assert wnft1155SBT.balanceOf(accounts[3], wTokenId) == out_amount

	
	#without asset data
	wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [], {'from': accounts[0], "value": '1 ether'})

	#with asset data - empty type
	with reverts(""):
		wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((0, zero_address), 0, 10)], {'from': accounts[0], "value": '1 ether'})

	#with asset data - native type, amount in array is less than in value
	wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((1, zero_address), 0, 10)], {'from': accounts[0], "value": '1 ether'})

	#with asset data - native type, amount in array is more than in value
	wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((1, zero_address), 0, Wei("10 ether"))], {'from': accounts[0], "value": '1 ether'})


	#with asset data - ERC721 and native tokens. Not exists allowance
	erc721mock.mint(ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
	with reverts("ERC721: caller is not token owner or approved"):
		wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[1], 0)], {'from': accounts[0], "value": '1 ether'})

	erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
	wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[1], 0)], {'from': accounts[0], "value": '1 ether'})

	
	#with asset data - ERC721 token. Wrong type
	erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[0], {"from": accounts[0]})
	with reverts(""):
		wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((4, erc721mock.address), ORIGINAL_NFT_IDs[0], 0)], {'from': accounts[0]})	
	
	#with asset data - ERC721 token. Msg.Sender is not owner of token
	with reverts("Only wNFT contract owner able to add collateral"):
		wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[0], 0)], {'from': accounts[8]})
	
	#with asset data - ERC721 token. Second token to collateral
	wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[0], 0)], {'from': accounts[0]})

	#with asset data - ERC721 token. Second contract to collateral
	erc721mock1.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[0], {"from": accounts[0]})
	wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)], {'from': accounts[0]})
	
	dai.transfer(accounts[1], dai.balanceOf(accounts[0]),  {"from": accounts[0]})
	with reverts("ERC1155: insufficient balance for transfer"):
		wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[1], 3), ((2, dai),0, call_amount)], {'from': accounts[0]})
	with reverts("ERC20: insufficient allowance"):
		wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[1], 2), ((2, dai),0, call_amount)], {'from': accounts[0]})
	dai.approve(wrapperUsers, call_amount,  {"from": accounts[0]})
	with reverts("ERC20: transfer amount exceeds balance"):
		wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[1], 2), ((2, dai),0, call_amount)], {'from': accounts[0]})
	dai.transfer(accounts[0], dai.balanceOf(accounts[1]),  {"from": accounts[1]})
	with reverts("TokenId must be zero"):
		wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[1], 2), ((2, dai),1, call_amount)], {'from': accounts[0]})
	wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[1], 2), ((2, dai),0, call_amount)], {'from': accounts[0]})

	logging.info(wrapperUsers.getWrappedToken(wnft1155SBT, wTokenId)[1])
	logging.info(wrapperUsers.getWrappedToken(wnft1155SBT, wTokenId)[1][0])

	assert wrapperUsers.balance() == "4 ether"

	collateral = wrapperUsers.getWrappedToken(wnft1155SBT, wTokenId)[1]
	assert collateral[0][2] == "4 ether"
	assert collateral[0][0][0] == 1
	assert collateral[1][0][0] == 3
	assert collateral[2][0][0] == 3
	assert collateral[3][0][0] == 3
	assert collateral[4][0][0] == 4
	assert collateral[5][0][0] == 2
	assert collateral[1][1] == ORIGINAL_NFT_IDs[1]
	assert collateral[2][1] == ORIGINAL_NFT_IDs[0]
	assert collateral[3][1] == ORIGINAL_NFT_IDs[0]
	assert collateral[4][1] == ORIGINAL_NFT_IDs[1]
	assert collateral[1][0][1] == erc721mock.address
	assert collateral[2][0][1] == erc721mock.address
	assert collateral[3][0][1] == erc721mock1.address
	assert collateral[4][0][1] == erc1155mock.address
	assert collateral[5][0][1] == dai.address
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperUsers.address
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapperUsers.address
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperUsers.address
	assert erc1155mock.balanceOf(wrapperUsers, ORIGINAL_NFT_IDs[0]) == 1
	assert erc1155mock.balanceOf(wrapperUsers, ORIGINAL_NFT_IDs[1]) == 2
	assert erc721mock.balanceOf(wrapperUsers.address) == 2
	assert erc721mock1.balanceOf(wrapperUsers.address) == 1
	assert dai.balanceOf(wrapperUsers) == call_amount
	assert wrapperUsers.balance() == 4e18

	assert wrapperUsers.getCollateralBalanceAndIndex(wnft1155SBT.address, wTokenId, 3, erc721mock1.address, ORIGINAL_NFT_IDs[0])[0] == 0
	assert wrapperUsers.getCollateralBalanceAndIndex(wnft1155SBT.address, wTokenId, 3, erc721mock1.address, ORIGINAL_NFT_IDs[0])[1] == 3

	wrapperUsers.unWrap(4, wnft1155SBT.address, wTokenId, {"from": accounts[3]})

	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[3]
	assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
	assert erc1155mock.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == 1
	assert erc1155mock.balanceOf(accounts[3], ORIGINAL_NFT_IDs[1]) == 2
	assert erc721mock.balanceOf(accounts[3]) == 2
	assert erc721mock1.balanceOf(accounts[3]) == 1
	assert dai.balanceOf(accounts[3]) == call_amount

	with reverts("wNFT not exists"):
		wrapperUsers.addCollateral(wnft1155SBT.address, wTokenId, [], {'from': accounts[0], "value": "1 ether"})