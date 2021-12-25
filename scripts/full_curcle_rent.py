import logging
import time
from brownie import *
from web3 import Web3
LOGGER = logging.getLogger(__name__)


#0-0x989FA3062bc4329B2E3c5907c48Ea48a38437fB7  - leasingPool
private_key='???'
accounts.add(private_key)

#1-0xbD7E5fB7525ED8583893ce1B1f93E21CC0cf02F6 
private_key='???'
accounts.add(private_key)

#2-0xdf19CC2c917CD70D41071beBE9529E4d58868e27
private_key='???'
accounts.add(private_key)


def main():
	wrapper     = WrapperForRent.at('0x8904Ef7b93f6aAcbaF66E7Fe61616a92bC73Cfdd')
	wnft1155         = EnvelopwNFT1155.at('0x5bF8D8E84Ae2Ee9514bA37B18cfe1b868992ee6f')
	original_nft_contract = Token1155Mock.at('0xbeF5Be938a4417CE626380D9d2dbfAc07256778c')
	in_type = 4
	out_type = 4
	in_nft_amount = 5
	out_nft_amount = 5
	
	original_nft_id = 4
	price = "2 gwei"

	original_nft_contract.mint(accounts[0], original_nft_id, in_nft_amount, {"from": accounts[0], "gas_price": price})
	
	#make allowance to use original NFT
	original_nft_contract.setApprovalForAll(wrapper.address, True,  {"from": accounts[0], "gas_price": price})

	
	token_property = (in_type, original_nft_contract)
	token_data = (token_property, original_nft_id, in_nft_amount)
	
	fee = []
	lock = []
	royalty = []

	wNFT = ( token_data,
		accounts[0], #leasingPool
		fee,
		lock,
		royalty,
		out_type,
		out_nft_amount,
		Web3.toBytes(0x000F)
	)
	
	#wrap NFT
	wrapper.wrap(wNFT, [], accounts[1], {"from": accounts[0], "gas_price": price})
	wTokenId = wrapper.lastWNFTId(out_type)[1]

	assert wnft1155.balanceOf(accounts[1], wTokenId) == out_nft_amount
	assert original_nft_contract.balanceOf(wrapper.address, original_nft_id) == in_nft_amount

	#try to transfer wrapped NFT
	try:
		wnft1155.safeTransferFrom(accounts[1], accounts[0], wTokenId, 1, '', {"from": accounts[1], "gas_price": price})
	except ValueError as ve:
		print(ve)

	#try to deposit collateral
	try:
		wrapper.addCollateral(wnft1155.address, wTokenId, [], {"from": accounts[1], "value": 1, "gas_price": price})
	except ValueError as ve:
		print(ve)
	
	#####
	token_property = (in_type, wnft1155)
	token_data = (token_property, wTokenId, in_nft_amount)
	
	fee = []
	lock = []
	royalty = []

	wNFT = ( token_data,
	accounts[0], #leasingPool
	fee,
	lock,
	royalty,
	out_type,
	out_nft_amount,
	'0'
	)

	wnft1155.setApprovalForAll(wrapper.address, True,  {"from": accounts[1], "gas_price": price})

	#try to wrap wrapped NFT
	try:
		wrapper.wrap(wNFT, [], accounts[1], {"from": accounts[1], "gas_price": price})
	except ValueError as ve:
		print(ve)

	###
	
	assert original_nft_contract.balanceOf(wrapper.address, original_nft_id) == in_nft_amount
	assert wnft1155.balanceOf(accounts[1], wTokenId) == out_nft_amount

	#try to unwrap by borrower
	try:
		wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[1], "gas_price": price})
	except ValueError as ve:
		print(ve)

	#try to unwrap by other user
	try:
		wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[2], "gas_price": price})
	except ValueError as ve:
		print(ve)

	#unwrap by leasingPool
	wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[0], "gas_price": price})

	assert original_nft_contract.balanceOf(accounts[0], original_nft_id) == in_nft_amount
	assert wnft1155.balanceOf(accounts[1], wTokenId) == 0







