import logging
import time
from brownie import *
from web3 import Web3
LOGGER = logging.getLogger(__name__)


#0-0x5992Fe461F81C8E0aFFA95b831E50e9b3854BA0E  - leasingPool
private_key=''
accounts.add(private_key)

#1-0xa11103Da33d2865C3B70947811b1436ea6Bb32eF 
private_key=''
accounts.add(private_key)

#2-0x989FA3062bc4329B2E3c5907c48Ea48a38437fB7 
private_key=''
accounts.add(private_key)


#tech 0x8368f72a85f5b3bc9f41ff9f3a681b09da0fe21f

def main():
	techERC20 = TechTokenV1.at('0xDD2C613E4C06127f7c69fA4A941BDde50fc4A9b1')
	wrapper = WrapperForRent.at('0x13c38357360f2A674FC49F8035DB9CeD8963B96C')
	wnft721 = EnvelopwNFT721.at('0x1fBa8e7237C2Eef4104406a230bB562Bf66be162')
	wnft1155 = EnvelopwNFT1155.at('0x34Ed6Af28AfA2e42e31C2604FD25D0Fe8B200910')

	original_nft_contract = Token1155Mock.at('0x403cEDfF16ad12d4Ef53b2D8aFe55965a1a61BFE')
	origNFT = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')

	#wnft721
	in_type = 3
	out_type = 3
	
	
	price = "50 gwei"

	#origNFT.mint(accounts[0], {"from": accounts[0], "gas_price": price})
	original_nft_id = origNFT.lastNFTId()
	
	#make allowance to use original NFT
	origNFT.approve(wrapper.address, original_nft_id,  {"from": accounts[0], "gas_price": price})

	
	token_property = (in_type, origNFT)
	token_data = (token_property, original_nft_id, 0)
	
	fee = []
	lock = [('0x00', chain.time()+300)]
	royalty = []

	wNFT = ( token_data,
		accounts[0], #owner of original nft
		fee,
		lock,
		royalty,
		out_type,
		0,
		Web3.toBytes(0x000E)
	)
	
	#wrap NFT
	wrapper.wrap(wNFT, [], accounts[1], {"from": accounts[0],'gas_price': price})
	wTokenId = wrapper.lastWNFTId(out_type)[1]
	print(wTokenId)


	assert wnft721.ownerOf(wTokenId) == accounts[1]
	assert origNFT.ownerOf(original_nft_id) == wrapper.address

	#try to transfer wrapped NFT
	try:
		wnft721.transferFrom(accounts[1], accounts[0], wTokenId, {"from": accounts[1], "gas_price": price})
	except ValueError as ve:
		print(ve)

	#try to deposit collateral
	try:
		wrapper.addCollateral(wnft721.address, wTokenId, [], {"from": accounts[1], "value": 0.1, "gas_price": price})
	except ValueError as ve:
		print(ve)
	
	#####
	token_property = (in_type, wnft721)
	token_data = (token_property, wTokenId, 0)
	
	fee = []
	lock = []
	royalty = []

	wNFT = ( token_data,
	accounts[0], #leasingPool
	fee,
	lock,
	royalty,
	out_type,
	0,
	'0'
	)

	wnft721.approve(wrapper.address, wTokenId,  {"from": accounts[1], "gas_price": price})

	#try to wrap wrapped NFT
	try:
		wrapper.wrap(wNFT, [], accounts[1], {"from": accounts[1], "gas_price": price})
	except ValueError as ve:
		print(ve)

	###
	
	assert origNFT.ownerOf(original_nft_id) == wrapper.address
	assert wnft721.ownerOf(wTokenId) == accounts[1]

	#try to unwrap by borrower
	try:
		wrapper.unWrap(out_type, wnft721.address, wTokenId, {"from": accounts[1], "gas_price": price})
	except ValueError as ve:
		print(ve)

	#try to unwrap by other user
	try:
		wrapper.unWrap(out_type, wnft721.address, wTokenId, {"from": accounts[2], "gas_price": price})
	except ValueError as ve:
		print(ve)

	#unwrap by leasingPool
	wrapper.unWrap(out_type, wnft721.address, wTokenId, {"from": accounts[0], "gas_price": price})

	assert origNFT.ownerOf(original_nft_id) == accounts[0]
	

	'''in_type = 4
	out_type = 4
	in_nft_amount = 1
	out_nft_amount = 1 
	
	original_nft_id = 7 #increase number +1 to mint new original NFT 
	price = "50 gwei"

	original_nft_contract.mint(accounts[0], original_nft_id, in_nft_amount, {"from": accounts[0], "gas_price": price})
	
	#make allowance to use original NFT
	original_nft_contract.setApprovalForAll(wrapper.address, True,  {"from": accounts[0], "gas_price": price})

	
	token_property = (in_type, original_nft_contract)
	token_data = (token_property, original_nft_id, in_nft_amount)
	
	fee = []
	lock = [('0x00', chain.time()+300)]
	royalty = []

	wNFT = ( token_data,
		accounts[0], #owner of original nft
		fee,
		lock,
		royalty,
		out_type,
		out_nft_amount,
		Web3.toBytes(0x000E)
	)
	
	#wrap NFT
	wrapper.wrap(wNFT, [], accounts[1], {"from": accounts[0],'gas_price': price})
	wTokenId = wrapper.lastWNFTId(out_type)[1]
	print(wTokenId)


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
	assert wnft1155.balanceOf(accounts[1], wTokenId) == 0'''







