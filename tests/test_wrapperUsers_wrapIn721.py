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
in_type = 3
out_type = 3



def test_call_factory(accounts, usersSBTRegistry, wrapperUsers, wnft721SBT, wnft1155SBT):
    usersSBTRegistry.addImplementation((3,wnft721SBT), {'from': accounts[0]})
    usersSBTRegistry.addImplementation((4,wnft1155SBT), {'from': accounts[0]})
    usersSBTRegistry.deployNewCollection(
        wnft721SBT, 
        accounts[0],'', '', '', wrapperUsers, {'from': accounts[0]}
    )

    logging.info(usersSBTRegistry.getUsersCollections(accounts[0]))
    assert len(usersSBTRegistry.getUsersCollections(accounts[0])) == 1


def test_wrap_ownerSBT(accounts, erc721mock, wrapperUsers, dai, weth, wnft721SBT, niftsy20):
	#make test data
	erc721mock.mint(ORIGINAL_NFT_IDs[0], {"from": accounts[0]})

	erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[0], {'from':accounts[0]})

	dai.approve(wrapperUsers.address, call_amount, {'from':accounts[0]})
	weth.approve(wrapperUsers.address, 2*call_amount, {'from':accounts[0]})

	erc721_property = (in_type, erc721mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 0)
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, Wei(eth_amount))

	fee = []
	lock = []
	royalty = []

	wNFT = ( erc721_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		Web3.toBytes(0x0005)  #rules - NO Unwrap, No Transfer
		)

	tx = wrapperUsers.wrapIn(wNFT, [dai_data, weth_data, eth_data], accounts[3], wnft721SBT,  {"from": accounts[0], "value": eth_amount})
	
	#checks
	assert wrapperUsers.balance() == eth_amount
	assert dai.balanceOf(wrapperUsers) == call_amount
	assert weth.balanceOf(wrapperUsers) == 2*call_amount
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperUsers.address
	assert wnft721SBT.ownerOf(wnft721SBT.tokenOfOwnerByIndex(accounts[3], 0)) == accounts[3].address
	logging.info(wnft721SBT.totalSupply())
	logging.info(wnft721SBT.tokenOfOwnerByIndex(accounts[3], 0))
	#assert wnft721SBT.totalSupply() == 1


	wTokenId = tx.return_value[1]

	assert wrapperUsers.getOriginalURI(wnft721SBT, wTokenId) == erc721mock.tokenURI(ORIGINAL_NFT_IDs[0])
	logging.info(erc721mock.tokenURI(ORIGINAL_NFT_IDs[0]))

	wNFT = wrapperUsers.getWrappedToken(wnft721SBT, wTokenId)
	assert wNFT[0] == erc721_data
	assert wNFT[1] == [eth_data, dai_data, weth_data]
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0005'

	erc721_property = (0, zero_address)

	erc721_data = (erc721_property, 0, 0)

	fee = []
	lock = []
	royalty = []

	wNFT = ( erc721_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		Web3.toBytes(0x0005)  #rules - NO Unwrap, No Transfer
		)

	tx= wrapperUsers.wrapIn(wNFT, [], accounts[3], wnft721SBT,  {"from": accounts[0]})

	wTokenId = tx.return_value[1]
	assert wrapperUsers.getOriginalURI(wnft721SBT, wTokenId) == ''
	wNFT = wrapperUsers.getWrappedToken(wnft721SBT, wTokenId)
	#logging.info(wNFT)
	assert wNFT[0] == erc721_data
	assert wNFT[1] == []
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0005'

	assert tx.events['WrappedV1']['inAssetAddress'] == zero_address
	assert tx.events['WrappedV1']['outAssetAddress'] == wnft721SBT
	assert tx.events['WrappedV1']['inAssetTokenId'] == 0
	assert tx.events['WrappedV1']['outTokenId'] == wTokenId
	assert tx.events['WrappedV1']['wnftFirstOwner'] == accounts[3]
	assert tx.events['WrappedV1']['nativeCollateralAmount'] == 0
	assert tx.events['WrappedV1']['rules'] == '0x0005'

	empty_property = (0, zero_address)

	empty_data = (empty_property, 0, 0)

	fee = []
	lock = []
	royalty = []

	wNFT = ( empty_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		Web3.toBytes(0x0001)  #rules - NO Unwrap
		)

	tx= wrapperUsers.wrapIn(wNFT, [], accounts[3], wnft721SBT,  {"from": accounts[0]})

	wTokenId = tx.return_value[1]
	wNFT = wrapperUsers.getWrappedToken(wnft721SBT, wTokenId)
	#logging.info(wNFT)
	assert wNFT[6] == '0x0001'

	with reverts('ERC721: caller is not token owner or approved'):
		wnft721SBT.transferFrom(accounts[3], accounts[0], wTokenId, {"from": accounts[0]})

	wnft721SBT.transferFrom(accounts[3], accounts[0], wTokenId, {"from": accounts[3]})

	assert wnft721SBT.ownerOf(wTokenId) == accounts[0]

	with reverts('UnWrap was disabled by author'):
		wrapperUsers.unWrap(3, wnft721SBT, wTokenId, {"from": accounts[0]})

def test_wrap_userSBT(accounts, erc721mock, wrapperUsers1, dai, weth, wnft721SBT1, niftsy20, eventManager):
	#make test data
	erc721mock.mint(ORIGINAL_NFT_IDs[1], {"from": accounts[1]})

	erc721mock.approve(wrapperUsers1.address, ORIGINAL_NFT_IDs[1], {'from':accounts[1]})

	#make settings for event
	eventManager.setTicketsForEvents(erc721mock, wnft721SBT1)  #fill in ticketsForEvents
	data = ((chain.time() + 100, chain.time() + 200),(chain.time() + 1000, chain.time() + 2000), Web3.toBytes(0x0001)) 
	eventManager.setEventData(wnft721SBT1, data) #fill in event data

	eventManager.addImplementation((3,wnft721SBT1), {'from': accounts[0]})
	eventManager.deployNewCollection(
		wnft721SBT1, 
		accounts[0],'', '', '', wrapperUsers1, {'from': accounts[0]}
	)


	dai.approve(wrapperUsers1.address, call_amount, {'from':accounts[0]})
	weth.approve(wrapperUsers1.address, 2*call_amount, {'from':accounts[0]})

	erc721_property = (in_type, erc721mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	erc721_data = (erc721_property, ORIGINAL_NFT_IDs[1], 0)
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, Wei(eth_amount))

	fee = []
	lock = []
	royalty = []

	wNFT = ( erc721_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		Web3.toBytes(0x0000)  #rules - NO rules
		)

	logging.info(eventManager.isWrapEnabled(erc721mock, wnft721SBT1))
	logging.info(eventManager.getUsersCollections(accounts[1]))

	with reverts('Wrap check fail'):
		tx = wrapperUsers1.wrapIn(wNFT, [dai_data, weth_data, eth_data], accounts[3], wnft721SBT1,  {"from": accounts[1], "value": eth_amount})

	chain.sleep(150)
	chain.mine()
	logging.info(eventManager.isWrapEnabled(erc721mock, wnft721SBT1))
	with reverts('Only wNFT contract owner able to add collateral'):
		tx = wrapperUsers1.wrapIn(wNFT, [dai_data, weth_data, eth_data], accounts[3], wnft721SBT1,  {"from": accounts[1], "value": eth_amount})
	tx = wrapperUsers1.wrapIn(wNFT, [], accounts[3], wnft721SBT1,  {"from": accounts[1]})
	wTokenId = tx.return_value[1]

	#try to update to sbt by not owner
	with reverts('Only wNFT owner can upgrade rules'):
		wrapperUsers1.upgradeRules(((3,wnft721SBT1),wTokenId,0), {"from": accounts[0]})

	#time of sbt has not started
	wrapperUsers1.upgradeRules(((3,wnft721SBT1),wTokenId,0), {"from": accounts[3]})

	
	#checks
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapperUsers1.address
	assert wnft721SBT1.ownerOf(wnft721SBT1.tokenOfOwnerByIndex(accounts[3], 0)) == accounts[3].address
	logging.info(wnft721SBT1.totalSupply())
	logging.info(wnft721SBT1.tokenOfOwnerByIndex(accounts[3], 0))
	#assert wnft721SBT.totalSupply() == 1


	

	assert wrapperUsers1.getOriginalURI(wnft721SBT1, wTokenId) == erc721mock.tokenURI(ORIGINAL_NFT_IDs[1])
	logging.info(erc721mock.tokenURI(ORIGINAL_NFT_IDs[0]))

	wNFT = wrapperUsers1.getWrappedToken(wnft721SBT1, wTokenId)
	assert wNFT[0] == erc721_data
	assert wNFT[1] == []
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0000'

	#move time to check update wnft to sbt
	chain.sleep(1000)
	chain.mine()

	#update wnft to sbt
	wrapperUsers1.upgradeRules(((3,wnft721SBT1),wTokenId,0), {"from": accounts[3]})
	wNFT = wrapperUsers1.getWrappedToken(wnft721SBT1, wTokenId)
	assert wNFT[6] == '0x0001'

	#check repeating of update rules
	with reverts('Only once to SBT'):
		wrapperUsers1.upgradeRules(((3,wnft721SBT1),wTokenId,0), {"from": accounts[3]})



	#check collateral case
	with reverts("Only wNFT contract owner able to add collateral"):
		wrapperUsers1.addCollateral(wnft721SBT1, wTokenId, [dai_data, weth_data, eth_data], {"from": accounts[3], "value": eth_amount})

	wrapperUsers1.addCollateral(wnft721SBT1, wTokenId, [dai_data, weth_data, eth_data], {"from": accounts[0], "value": eth_amount})
	#check info and balances
	assert wrapperUsers1.getWrappedToken(wnft721SBT1, wTokenId)[1] == [eth_data, dai_data, weth_data ]
	assert dai.balanceOf(wrapperUsers1) == Wei(call_amount)
	assert weth.balanceOf(wrapperUsers1) == Wei(2*call_amount)
	assert wrapperUsers1.balance() == Wei(eth_amount)

	#wnft with empty inside
	erc721_property = (0, zero_address)

	erc721_data = (erc721_property, 0, 0)

	fee = []
	lock = []
	royalty = []

	wNFT = ( erc721_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		Web3.toBytes(0x0005)  #rules - NO Unwrap, No Transfer
		)

	tx= wrapperUsers1.wrapIn(wNFT, [], accounts[3], wnft721SBT1,  {"from": accounts[0]})

	wTokenId = tx.return_value[1]
	assert wrapperUsers1.getOriginalURI(wnft721SBT1, wTokenId) == ''
	wNFT = wrapperUsers1.getWrappedToken(wnft721SBT1, wTokenId)
	#logging.info(wNFT)
	assert wNFT[0] == erc721_data
	assert wNFT[1] == []
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0005'

	assert tx.events['WrappedV1']['inAssetAddress'] == zero_address
	assert tx.events['WrappedV1']['outAssetAddress'] == wnft721SBT1
	assert tx.events['WrappedV1']['inAssetTokenId'] == 0
	assert tx.events['WrappedV1']['outTokenId'] == wTokenId
	assert tx.events['WrappedV1']['wnftFirstOwner'] == accounts[3]
	assert tx.events['WrappedV1']['nativeCollateralAmount'] == 0
	assert tx.events['WrappedV1']['rules'] == '0x0005'

	with reverts('Transfer was disabled by author'):
		wnft721SBT1.transferFrom(accounts[3], accounts[0], wTokenId, {"from": accounts[3]})

	empty_property = (0, zero_address)

	empty_data = (empty_property, 0, 0)

	fee = []
	lock = []
	royalty = []

	wNFT = ( empty_data,
		accounts[2],
		fee,
		lock,
		royalty,
		out_type,
		0,
		Web3.toBytes(0x0001)  #rules - NO Unwrap
		)

	tx= wrapperUsers1.wrapIn(wNFT, [], accounts[3], wnft721SBT1,  {"from": accounts[0]})

	wTokenId = tx.return_value[1]
	wNFT = wrapperUsers1.getWrappedToken(wnft721SBT1, wTokenId)
	#logging.info(wNFT)
	assert wNFT[6] == '0x0001'

	with reverts('ERC721: caller is not token owner or approved'):
		wnft721SBT1.transferFrom(accounts[3], accounts[0], wTokenId, {"from": accounts[0]})

	wnft721SBT1.transferFrom(accounts[3], accounts[0], wTokenId, {"from": accounts[3]})

	assert wnft721SBT1.ownerOf(wTokenId) == accounts[0]

	with reverts('UnWrap was disabled by author'):
		wrapperUsers1.unWrap(3, wnft721SBT1, wTokenId, {"from": accounts[0]})
