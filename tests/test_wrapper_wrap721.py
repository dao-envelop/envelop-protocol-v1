import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
START_NATIVE_COLLATERAL = '1 ether'
ADD_NATIVE_COLLATERAL = '2 ether'
ERC20_COLLATERAL_AMOUNT = 2e17;
TRANSFER_FEE = 2e18
ROAYLTY_PERCENT = 10
UNWRAP_FEE_THRESHOLD = 6e18
protokolFee = 10
chargeFeeAfter = 10
royaltyBeneficiary = '0xbd7e5fb7525ed8583893ce1b1f93e21cc0cf02f6'
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18

def test_simple_wrap(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20):
	#make test data
	makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
	weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})


	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
	weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

	wrapper.setWNFTId(3, wnft721.address, 0, {'from':accounts[0]})
	wrapper.setWhiteList(dai.address, {'from':accounts[0]})
	wrapper.setWhiteList(weth.address, {'from':accounts[0]})
	wnft721.setMinter(wrapper.address, {"from": accounts[0]})

	erc721_property = (3, erc721mock.address)
	dai_property = (2, dai.address)
	weth_property = (2, weth.address)
	eth_property = (1, zero_address)

	erc721_data = (erc721_property, str(ORIGINAL_NFT_IDs[0]), '1')
	dai_data = (dai_property, '0', str(Wei(call_amount)))
	weth_data = (weth_property, '0', str(Wei(2*call_amount)))
	eth_data = (eth_property, '0', str(Wei("4 ether")))

	fee = [('1', str(Wei(1e18)), niftsy20.address)]
	lock = [('1',str(chain.time() + 10)), ('1', str(chain.time() + 20))]
	royalty = [(accounts[1], '100'), (accounts[2], '200')]

	wNFT = ( erc721_data,
		accounts[2],
		fee,
		lock,
		royalty,
		'3',
		'0',
		'0'
		)
	logging.info('d = {}'.format(dai_data))
	logging.info('balance = {}'.format(dai.balanceOf(accounts[1])))
	wrapper.wrap(wNFT, [dai_data, weth_data, eth_data], accounts[3], {"from": accounts[1], "value": "4 ether"})
	
	#[dai_data, weth_data, eth_data]
	#, "value": "4 ether"

	'''
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId'], [ORIGINAL_NFT_IDs[1]], accounts[1], niftsy20)
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == 2 * protokolFee
	assert wrapper.lastWrappedNFTId() == 2
	checkWrappedNFT(wrapper, 
		wrapper.lastWrappedNFTId(), 
		erc721mock.address, 
		ORIGINAL_NFT_IDs[1], 
		START_NATIVE_COLLATERAL, 
		0,  
		unwrapAfter, 
		TRANSFER_FEE, 
		royaltyBeneficiary, 
		ROAYLTY_PERCENT, 
		UNWRAP_FEE_THRESHOLD)

	logging.info('wrapper.tokenURI(wrapper.lastWrappedNFTId()) = {}'.format(wrapper.tokenURI(wrapper.lastWrappedNFTId())))
	logging.info('wrapper.getWrappedToken(wrapper.lastWrappedNFTId()) = {}'.format(wrapper.getWrappedToken(wrapper.lastWrappedNFTId())))
	'''