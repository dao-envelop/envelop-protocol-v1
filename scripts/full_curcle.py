import logging
import time
from brownie import *
LOGGER = logging.getLogger(__name__)


#0-0x989FA3062bc4329B2E3c5907c48Ea48a38437fB7
private_key='721fd469cc7604dcc6ab618e4055822216d977cd14deeae23e6e452c82da9ae9'
accounts.add(private_key)


def main():
	wrapperRent     = WrapperForRent.at('0x8904Ef7b93f6aAcbaF66E7Fe61616a92bC73Cfdd')
	wnft1155         = EnvelopwNFT1155.at('0x5bF8D8E84Ae2Ee9514bA37B18cfe1b868992ee6f')
	original_nft_contract = Bunny.at('0xa3a6e26032c01eac3557207dbfae45d305625ecd')
	in_type = 3
	out_type = 4
	out_nft_amount = 5
	
	original_nft_id = 59

	original_nft_contract.approve(wrapperRent.address, original_nft_id, {"from": accounts[0], "gas_price": price})


	'''token_property = (in_type, erc1155mock)
	token_data = (token_property, ORIGINAL_NFT_IDs[0], coll_amount)
	
	fee = []
	lock = []
	royalty = []

	wNFT = ( token_data,
	accounts[2], #leasingPool
	fee,
	lock,
	royalty,
	out_type,
	out_nft_amount,
	Web3.toBytes(0x000F)
	)
	logging.info('{}'.format(Web3.toBytes(0x000F)))

	wrapperRent.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
	wTokenId = wrapperRent.lastWNFTId(out_type)[1]
	wnft_pretty_print(wrapperRent, wnft1155, wTokenId)
	assert erc1155mock.balanceOf(wrapperRent.address, ORIGINAL_NFT_IDs[0]) == coll_amount
	assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount


	#refuse to transfer
	with reverts("Trasfer was disabled by author"):
	 	wnft1155.safeTransferFrom(accounts[3], accounts[9], wTokenId, 1, '', {"from": accounts[3]})

	#refuse to deposit collateral
	with reverts("Forbidden add collateral"):
		wrapperRent.addCollateral(wnft1155.address, wTokenId, [], {"from": accounts[1], "value": "1 ether"})

	#refuse to wrap wNFT
	wnft1155.setApprovalForAll(wrapperRent, True, {"from": accounts[3]})

	token_property = (in_type, wnft1155)
	token_data = (token_property, wTokenId, coll_amount)
	
	fee = []
	lock = []
	royalty = []

	wNFT = ( token_data,
	accounts[2], #leasingPool
	fee,
	lock,
	royalty,
	out_type,
	out_nft_amount,
	'0'
	)
	
	
	#refuse to wrap again
	with reverts("Wrap check fail"):
		wrapperRent.wrap(wNFT, [], accounts[4], {"from": accounts[3]})

	#refuse unwrap by owner
	with reverts("Only unWrapDestinition can unwrap forbidden wnft"):
		wrapperRent.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]})

	#unwrap by UnwrapDestinition
	wrapperRent.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[2]})


	print('*******************************************************************************************')
	print('****************************************USERDATA in fundHiSTAKING**************************')
	print('*******************************************************************************************')'''







