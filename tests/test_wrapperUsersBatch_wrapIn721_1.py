import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721
from web3 import Web3


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222,33333,44444]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = 1e18
in_type = 3
out_type = 3
count = 5

# with eth in collateral data

def test_call_factory(accounts, usersSBTRegistry, wrapperUsersBatch, wnft721SBT1forBatch, wnft1155SBT):
    usersSBTRegistry.addImplementation((3,wnft721SBT1forBatch), {'from': accounts[0]})
    usersSBTRegistry.addImplementation((4,wnft1155SBT), {'from': accounts[0]})
    usersSBTRegistry.deployNewCollection(
        wnft721SBT1forBatch, 
        accounts[0],'', '', '', wrapperUsersBatch, {'from': accounts[0]}
    )

    #logging.info(usersSBTRegistry.getUsersCollections(accounts[0]))
    assert len(usersSBTRegistry.getUsersCollections(accounts[0])) == 1

def test_wrapBatch_ownerSBT(accounts, erc721mock, wrapperUsersBatch, dai, weth, wnft721SBT1forBatch, niftsy20):
	#make wNFTs by the batch
	i = 0
	while i < count:
		erc721mock.mint(ORIGINAL_NFT_IDs[i], {"from": accounts[0]})
		erc721mock.approve(wrapperUsersBatch.address, ORIGINAL_NFT_IDs[i], {'from':accounts[0]})
		i = i + 1

	dai.approve(wrapperUsersBatch.address, call_amount * count, {'from':accounts[0]})
	weth.approve(wrapperUsersBatch.address, 2 * call_amount * count, {'from':accounts[0]})

	erc721_property = (in_type, erc721mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, eth_amount)
	logging.info(dai_data)

	fee = []
	lock = []
	royalty = []

	i = 0
	wNFTs = []
	receivers = []
	while i < count:
		erc721_data = (erc721_property, ORIGINAL_NFT_IDs[i], 0)
		wNFT = ( erc721_data,
			accounts[2],
			fee,
			lock,
			royalty,
			out_type,
			0,
			Web3.toBytes(0x0005)  #rules - NO Unwrap, No Transfer
			)
		wNFTs.append(wNFT)
		receivers.append(accounts[i])
		i = i + 1

	tx = wrapperUsersBatch.wrapBatch(
		wNFTs, 
		[dai_data, weth_data, eth_data], 
		receivers, 
		wnft721SBT1forBatch,  
		{"from": accounts[0], "value": eth_amount * count})
	logging.info(wnft721SBT1forBatch.totalSupply())

	j = 0
	while j < count:
		assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[j]) == wrapperUsersBatch.address
		assert wnft721SBT1forBatch.ownerOf(wnft721SBT1forBatch.tokenOfOwnerByIndex(accounts[j], 0)) == accounts[j].address
		wNFT = wrapperUsersBatch.getWrappedToken(wnft721SBT1forBatch, j)
		assert wNFT[0] == [erc721_property, ORIGINAL_NFT_IDs[j], 0]
		assert wNFT[1] == [dai_data, weth_data, eth_data]
		assert wNFT[2] == zero_address
		assert wNFT[3] == fee
		assert wNFT[4] == lock
		assert wNFT[5] == royalty
		assert wNFT[6] == '0x0005'
		j = j + 1

	#checks
	assert wrapperUsersBatch.balance() == eth_amount * count
	assert dai.balanceOf(wrapperUsersBatch) == call_amount * count
	assert weth.balanceOf(wrapperUsersBatch) == 2 * call_amount * count
	
	assert wnft721SBT1forBatch.totalSupply() == count
	assert wrapperUsersBatch.getOriginalURI(wnft721SBT1forBatch, count - 1) == erc721mock.tokenURI(ORIGINAL_NFT_IDs[count - 1])

	# check - not owner  tries to add collateral - expected revert
	with reverts('Only wNFT contract owner able to add collateral'):
		wrapperUsersBatch.addCollateral(wnft721SBT1forBatch, count - 1, [], {"from": accounts[2], "value": 1})

def test_addCollateralBatch_ownerSBT1(accounts, erc721mock, wrapperUsersBatch, dai, weth, wnft721SBT1forBatch, niftsy20):
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, eth_amount)

	dai.approve(wrapperUsersBatch.address, call_amount * count, {'from':accounts[0]})
	weth.approve(wrapperUsersBatch.address, 2 * call_amount * count, {'from':accounts[0]})

	i = 0
	wNFTAddresses = []
	wNFTIds = []
	while i < count:
		wNFTAddresses.append(wnft721SBT1forBatch.address)
		wNFTIds.append(i)
		i = i + 1

	wrapperUsersBatch.addCollateralBatch(
		wNFTAddresses, 
		wNFTIds, 
		[dai_data, weth_data, eth_data], 
		{"from": accounts[0], "value": eth_amount * count})




	

