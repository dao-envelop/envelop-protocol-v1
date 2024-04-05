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



def test_call_factory(accounts, usersSBTRegistry, wrapperUsersBatch, wnft721SBT1forBatch, wnft1155SBT):
    usersSBTRegistry.addImplementation((3,wnft721SBT1forBatch), {'from': accounts[0]})
    usersSBTRegistry.addImplementation((4,wnft1155SBT), {'from': accounts[0]})
    usersSBTRegistry.deployNewCollection(
        wnft721SBT1forBatch, 
        accounts[0],'', '', '', wrapperUsersBatch, {'from': accounts[0]}
    )

    logging.info(usersSBTRegistry.getUsersCollections(accounts[0]))
    assert len(usersSBTRegistry.getUsersCollections(accounts[0])) == 1


def test_wrap_ownerSBT(accounts, erc721mock, wrapperUsersBatch, dai, weth, wnft721SBT1forBatch, niftsy20):
	#make test data
	i = 0
	while i < 5:
		erc721mock.mint(ORIGINAL_NFT_IDs[i], {"from": accounts[0]})
		erc721mock.approve(wrapperUsersBatch.address, ORIGINAL_NFT_IDs[i], {'from':accounts[0]})
		i = i + 1

	dai.approve(wrapperUsersBatch.address, call_amount * 5, {'from':accounts[0]})
	weth.approve(wrapperUsersBatch.address, 2 * call_amount * 5, {'from':accounts[0]})

	erc721_property = (in_type, erc721mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	
	dai_data = (dai_property, 0, Wei(call_amount))
	weth_data = (weth_property, 0, Wei(2*call_amount))
	eth_data = (eth_property, 0, eth_amount)

	fee = []
	lock = []
	royalty = []

	i = 0
	wNFTs = []
	receivers = []
	while i < 5:
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

	tx = wrapperUsersBatch.wrapBatch(wNFTs, [dai_data, weth_data, eth_data], receivers, wnft721SBT1forBatch,  {"from": accounts[0], "value": eth_amount * 5})

	#checks
	assert wrapperUsersBatch.balance() == eth_amount * 5
	assert dai.balanceOf(wrapperUsersBatch) == call_amount * 5
	assert weth.balanceOf(wrapperUsersBatch) == 2 * call_amount * 5
	
	i = 0
	while i < 5:
		assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[i]) == wrapperUsersBatch.address
		assert wnft721SBT1forBatch.ownerOf(wnft721SBT1forBatch.tokenOfOwnerByIndex(accounts[i], 0)) == accounts[i].address
		i = i + 1
	logging.info(wnft721SBT1forBatch.totalSupply())
	assert wnft721SBT1forBatch.totalSupply() == 5

	'''
	wTokenId = tx.return_value[1]

	assert wrapperUsersBatch.getOriginalURI(wnft721SBT1forBatch, wTokenId) == erc721mock.tokenURI(ORIGINAL_NFT_IDs[0])
	logging.info(erc721mock.tokenURI(ORIGINAL_NFT_IDs[0]))

	wNFT = wrapperUsersBatch.getWrappedToken(wnft721SBT1forBatch, wTokenId)
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

	tx= wrapperUsersBatch.wrapIn(wNFT, [], accounts[3], wnft721SBT1forBatch,  {"from": accounts[0]})

	wTokenId = tx.return_value[1]
	assert wrapperUsersBatch.getOriginalURI(wnft721SBT1forBatch, wTokenId) == ''
	wNFT = wrapperUsersBatch.getWrappedToken(wnft721SBT1forBatch, wTokenId)
	#logging.info(wNFT)
	assert wNFT[0] == erc721_data
	assert wNFT[1] == []
	assert wNFT[2] == zero_address
	assert wNFT[3] == fee
	assert wNFT[4] == lock
	assert wNFT[5] == royalty
	assert wNFT[6] == '0x0005'

	assert tx.events['WrappedV1']['inAssetAddress'] == zero_address
	assert tx.events['WrappedV1']['outAssetAddress'] == wnft721SBT1forBatch
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

	tx= wrapperUsersBatch.wrapIn(wNFT, [], accounts[3], wnft721SBT1forBatch,  {"from": accounts[0]})

	wTokenId = tx.return_value[1]
	wNFT = wrapperUsersBatch.getWrappedToken(wnft721SBT1forBatch, wTokenId)
	#logging.info(wNFT)
	assert wNFT[6] == '0x0001'

	with reverts('ERC721: caller is not token owner or approved'):
		wnft721SBT1forBatch.transferFrom(accounts[3], accounts[0], wTokenId, {"from": accounts[0]})

	wnft721SBT1forBatch.transferFrom(accounts[3], accounts[0], wTokenId, {"from": accounts[3]})

	assert wnft721SBT1forBatch.ownerOf(wTokenId) == accounts[0]

	with reverts('UnWrap was disabled by author'):
		wrapperUsersBatch.unWrap(3, wnft721SBT1forBatch, wTokenId, {"from": accounts[0]})'''


