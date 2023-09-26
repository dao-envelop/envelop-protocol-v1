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

def test_simple_wrap(accounts, erc1155mock, wrapperUsers, dai, weth, wnft1155SBT):
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
