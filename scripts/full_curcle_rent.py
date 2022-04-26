import logging
import time
from brownie import *
from web3 import Web3
LOGGER = logging.getLogger(__name__)


#0-0xa11103Da33d2865C3B70947811b1436ea6Bb32eF  - leasingPool
private_key='c4f373082110065841b63c9e005710309756f78bc7b09dbf2a242442173b1ddc'
accounts.add(private_key)

#1-0xbD7E5fB7525ED8583893ce1B1f93E21CC0cf02F6 
private_key='96ee5dfa63f4091fcfbf01725a883cb6d66a5990d67374ae3217be3bb0e70516'
accounts.add(private_key)

#2-0x989FA3062bc4329B2E3c5907c48Ea48a38437fB7 
private_key='721fd469cc7604dcc6ab618e4055822216d977cd14deeae23e6e452c82da9ae9'
accounts.add(private_key)




def main():
	wrapper     = WrapperForRent.at('0x446EC4c1793B664Bb4f42b956DdD147362Ef4AB4')
	wnft1155         = EnvelopwNFT1155.at('0x0E3b3E63c4e1f37629930bf904A76Fd812f81b83')
	original_nft_contract = Token1155Mock.at('0x948f114eB8D40BE607F5589Cb63bF361a859466c')
	in_type = 4
	out_type = 4
	in_nft_amount = 5
	out_nft_amount = 5 
	
	original_nft_id = 1 #increase number +1 to mint new original NFT 
	price = "10 gwei"

	#original_nft_contract.mint(accounts[0], original_nft_id, in_nft_amount, {"from": accounts[0], "gas_price": price})
	
	#make allowance to use original NFT
	#original_nft_contract.setApprovalForAll(wrapper.address, True,  {"from": accounts[0], "gas_price": price})

	
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
		Web3.toBytes(0x000E)
	)
	
	#wrap NFT
	#wrapper.wrap(wNFT, [], accounts[1], {"from": accounts[0],'gas_price': price})
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







