import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest1155
from web3 import Web3


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 4
out_type = 4
nft_amount = 5


def test_call_factory(accounts, usersSBTRegistry, wrapperUsers, wnft721SBT, wnft1155SBT):
    usersSBTRegistry.addImplementation((3,wnft721SBT), {'from': accounts[0]})
    usersSBTRegistry.addImplementation((4,wnft1155SBT), {'from': accounts[0]})
    usersSBTRegistry.deployNewCollection(
        wnft1155SBT, 
        accounts[0],'', '', '', wrapperUsers, {'from': accounts[0]}
    )

    logging.info(usersSBTRegistry.getUsersCollections(accounts[0]))
    assert len(usersSBTRegistry.getUsersCollections(accounts[0])) == 1

def test_wrap_ownerSBT(accounts, erc1155mock, wrapperUsers, dai, weth, wnft1155SBT):
	#make test data
	erc1155mock.mint(accounts[0],  ORIGINAL_NFT_IDs[0], nft_amount, {"from": accounts[0]})


	erc1155mock.setApprovalForAll(wrapperUsers.address,True, {'from':accounts[0]})

	dai.approve(wrapperUsers.address, call_amount, {'from':accounts[0]})
	weth.approve(wrapperUsers.address, 2*call_amount, {'from':accounts[0]})

	erc1155_property = (in_type, erc1155mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], nft_amount)
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, Wei(eth_amount))

	fee = []
	lock = []
	royalty = []

	wNFT = ( erc1155_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		nft_amount,
		Web3.toBytes(0x0005)  #rules - NO Unwrap, No Transfer
		)

	tx = wrapperUsers.wrapIn(wNFT, [dai_data, weth_data, eth_data], accounts[3], wnft1155SBT,  {"from": accounts[0], "value": eth_amount})
	#tx = wrapperUsers.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	#checks
	wTokenId = tx.return_value[1]
	assert wrapperUsers.getOriginalURI(wnft1155SBT, wTokenId) == erc1155mock.uri(ORIGINAL_NFT_IDs[0])
	assert wrapperUsers.balance() == eth_amount
	assert dai.balanceOf(wrapperUsers) == call_amount
	assert weth.balanceOf(wrapperUsers) == 2*call_amount
	assert erc1155mock.balanceOf(wrapperUsers.address, ORIGINAL_NFT_IDs[0]) == nft_amount
	assert wnft1155SBT.balanceOf(accounts[3].address,wTokenId) == nft_amount
	#assert wnft721SBT.totalSupply(wrapperUsers.lastWNFTId(out_type)[1]) == nft_amount

	
	wNFT = wrapperUsers.getWrappedToken(wnft1155SBT, wTokenId)
	#logging.info(wNFT)
	assert wNFT[0] == erc1155_data
	assert wNFT[1] == [eth_data, dai_data, weth_data]
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0005'	

	empty_property = (0, zero_address)

	empty_data = (empty_property, 0, 0)

	fee = []
	lock = []
	royalty = []

	tx = wNFT = ( empty_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		nft_amount,
		Web3.toBytes(0x0001)  #rules - NO Unwrap
		)

	tx= wrapperUsers.wrapIn(wNFT, [], accounts[3], wnft1155SBT,  {"from": accounts[0]})

	wTokenId = tx.return_value[1]
	wNFT = wrapperUsers.getWrappedToken(wnft1155SBT, wTokenId)
	#logging.info(wNFT)
	assert wNFT[6] == '0x0001'

	with reverts('ERC1155: caller is not token owner or approved'):
		wnft1155SBT.safeTransferFrom(accounts[3], accounts[0], wTokenId, nft_amount, '', {"from": accounts[0]})

	wnft1155SBT.safeTransferFrom(accounts[3], accounts[0], wTokenId, nft_amount, '', {"from": accounts[3]})

	assert wnft1155SBT.balanceOf(accounts[0], wTokenId) == nft_amount

	with reverts('UnWrap was disabled by author'):
		wrapperUsers.unWrap(4, wnft1155SBT, wTokenId, {"from": accounts[0]})

def test_wrap_userSBT(accounts, erc1155mock, wrapperUsers1, dai, weth, wnft1155SBT1, eventManager):
	#make test data
	erc1155mock.mint(accounts[1],  ORIGINAL_NFT_IDs[1], nft_amount, {"from": accounts[1]})
	erc1155mock.setApprovalForAll(wrapperUsers1.address,True, {'from':accounts[1]})

	#make settings for event
	eventManager.setTicketsForEvents(erc1155mock, wnft1155SBT1)  #fill in ticketsForEvents
	data = ((chain.time() + 100, chain.time() + 200),(chain.time() + 1000, chain.time() + 2000), Web3.toBytes(0x0001)) 
	eventManager.setEventData(wnft1155SBT1, data) #fill in event data

	eventManager.addImplementation((4,wnft1155SBT1), {'from': accounts[0]})
	eventManager.deployNewCollection(
		wnft1155SBT1, 
		accounts[0],'', '', '', wrapperUsers1, {'from': accounts[0]}
	)

	dai.approve(wrapperUsers1.address, call_amount, {'from':accounts[0]})
	weth.approve(wrapperUsers1.address, 2*call_amount, {'from':accounts[0]})

	erc1155_property = (in_type, erc1155mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[1], nft_amount)
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, Wei(eth_amount))

	fee = []
	lock = []
	royalty = []

	wNFT = ( erc1155_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		nft_amount,
		Web3.toBytes(0x0005)  #rules - NO Unwrap, No Transfer
		)

	#wrap by user with collateral
	with reverts('Wrap check fail'):
		tx = wrapperUsers1.wrapIn(wNFT, [dai_data, weth_data, eth_data], accounts[3], wnft1155SBT1,  {"from": accounts[1], "value": eth_amount})
	
	#wrap by user - wrap time has not started
	with reverts('Wrap check fail'): 
		tx = wrapperUsers1.wrapIn(wNFT, [], accounts[3], wnft1155SBT1,  {"from": accounts[1]})

	#move time fot wrapping
	chain.sleep(150)
	chain.mine()

	#wrap by user - rules must be zero
	with reverts('Wrap check fail'): 
		tx = wrapperUsers1.wrapIn(wNFT, [], accounts[3], wnft1155SBT1,  {"from": accounts[1]})

	wNFT = ( erc1155_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		nft_amount,
		Web3.toBytes(0x0000)  #rules - only zero
		)

	tx = wrapperUsers1.wrapIn(wNFT, [], accounts[3], wnft1155SBT1,  {"from": accounts[1]})


	#checks
	wTokenId = tx.return_value[1]

	#time of sbt has not started
	#wrapperUsers1.upgradeRules(((4,wnft1155SBT1),wTokenId,0), {"from": accounts[3]})

	assert wrapperUsers1.getOriginalURI(wnft1155SBT1, wTokenId) == erc1155mock.uri(ORIGINAL_NFT_IDs[1])
	assert erc1155mock.balanceOf(wrapperUsers1.address, ORIGINAL_NFT_IDs[1]) == nft_amount
	assert wnft1155SBT1.balanceOf(accounts[3].address,wTokenId) == nft_amount
	#assert wnft721SBT.totalSupply(wrapperUsers.lastWNFTId(out_type)[1]) == nft_amount

	wNFT = wrapperUsers1.getWrappedToken(wnft1155SBT1, wTokenId)
	#logging.info(wNFT)
	assert wNFT[0] == erc1155_data
	assert wNFT[1] == []
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0000'	

	#move time to check update wnft to sbt
	chain.sleep(1000)
	chain.mine()

	#wait fix for 1155 - check in wrapper about owner of wnft
	#update wnft to sbt
	'''wrapperUsers1.upgradeRules(((4,wnft1155SBT1),wTokenId,0), {"from": accounts[3]})
	wNFT = wrapperUsers1.getWrappedToken(wnft1155SBT1, wTokenId)
	assert wNFT[6] == '0x0001'

	#check repeating of update rules
	with reverts('Only once to SBT'):
		wrapperUsers1.upgradeRules(((4,wnft1155SBT1),wTokenId,0), {"from": accounts[3]})'''
