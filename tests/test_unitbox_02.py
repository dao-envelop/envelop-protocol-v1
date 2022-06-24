import pytest
import logging
from brownie import Wei, reverts, chain, web3
from makeTestData import makeNFTForTest721
from web3 import Web3
from eth_abi import encode_single
from eth_account.messages import encode_defunct


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3
secret = 7777777
ORACLE_ADDRESS = '0x8125F522a712F4aD849E6c7312ba8263bEBeEFeD' 
ORACLE_PRIVATE_KEY = '0x222ead82a51f24a79887aae17052718249295530f8153c73bf1f257a9ca664af'
coll_amount = 1e18


def wnft_pretty_print(_wrapper, _wnft721, _wTokenId):
    logging.info(
        '\n=========wNFT=============\nwNFT:{0},{1}\nInAsset: {2}\nCollrecords:\n{3}\nunWrapDestination: {4}'
        '\nFees: {5} \nLocks: {6} \nRoyalty: {7} \nrules: {8}({9:0>16b}) \n=========================='.format(
        _wnft721, _wTokenId,
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[0],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[1],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[2],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[3],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[4],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[5],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[6],
        Web3.toInt(_wrapper.getWrappedToken(_wnft721, _wTokenId)[6]),
        
    ))

def test_wrap(accounts, erc721mock, unitbox, wrapperRemovable, wnft721, whiteLists, niftsy20, techERC20, dai):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

    erc721mock.approve(wrapperRemovable.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
    wrapperRemovable.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperRemovable.address, {"from": accounts[0]})

    erc721_property = (in_type, erc721mock.address)
    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 1)
    royalty=[
        (accounts[1], 4000), # Maker
        (accounts[2], 5000) #, # Taker
        #(unitbox.address, 1000) # Treasure proxy
    ]

    fee = []
    lock = []

    inData = (erc721_data,
        accounts[1],
        fee,
        lock,
        royalty,
        out_type,
        0,
        0x0006
    )

    #hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    ## Block Above has too complicated param for encode in web3py
    ## So  use helper from contract
    hashed_msg = unitbox.prepareMessage(
        Web3.toChecksumAddress(erc721mock.address), 
        Web3.toInt(ORIGINAL_NFT_IDs[0]),
        royalty, 
        Web3.toChecksumAddress(accounts[0].address), 
        Web3.toInt(0)
    )

    logging.info('hashed_msg = {}'.format(hashed_msg))
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)

    logging.info('message = {}'.format(message))
    signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)

    logging.info('sign_message is {}'.format(signed_message))
    ####################################
    unitbox.setSignerState(ORACLE_ADDRESS, True, {'from':accounts[0]})
    wrapperRemovable.setTrustedAddress(unitbox, True, {'from':accounts[0]})

    with reverts("No beneficiaries"):
        unitbox.wrapForRent(inData, 0, signed_message.signature, {"from": accounts[0]})

    royalty=[
        (accounts[1], 4000), # Maker
        (accounts[2], 5000), #, # Taker
        (accounts[3], 1000) # Treasure proxy
    ]

    inData = (erc721_data,
        accounts[1],
        fee,
        lock,
        royalty,
        out_type,
        0,
        0x0006
    )

    #hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    ## Block Above has too complicated param for encode in web3py
    ## So  use helper from contract
    hashed_msg = unitbox.prepareMessage(
        Web3.toChecksumAddress(erc721mock.address), 
        Web3.toInt(ORIGINAL_NFT_IDs[0]),
        royalty, 
        Web3.toChecksumAddress(accounts[0].address), 
        Web3.toInt(0)
    )

    logging.info('hashed_msg = {}'.format(hashed_msg))
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)

    logging.info('message = {}'.format(message))
    signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)

    logging.info('sign_message is {}'.format(signed_message))

    with reverts("Last record in royalties always this contract"):
        unitbox.wrapForRent(inData, 0, signed_message.signature, {"from": accounts[0]})

    royalty=[
        (accounts[1], 4000), # Maker
        (accounts[2], 5000), #, # Taker
        (unitbox.address, 1000) # Treasure proxy
    ]

    inData = (erc721_data,
        accounts[1],
        fee,
        lock,
        royalty,
        out_type,
        0,
        0x0006
    )

    #hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    ## Block Above has too complicated param for encode in web3py
    ## So  use helper from contract
    hashed_msg = unitbox.prepareMessage(
        Web3.toChecksumAddress(erc721mock.address), 
        Web3.toInt(ORIGINAL_NFT_IDs[0]),
        royalty, 
        Web3.toChecksumAddress(accounts[0].address), 
        Web3.toInt(0)
    )

    logging.info('hashed_msg = {}'.format(hashed_msg))
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)

    logging.info('message = {}'.format(message))
    signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)

    logging.info('sign_message is {}'.format(signed_message))

    unitbox.wrapForRent(inData, 0, signed_message.signature, {"from": accounts[0]})

    wTokenId = wrapperRemovable.lastWNFTId(out_type)[1]
    wNFT = wrapperRemovable.getWrappedToken(wnft721, wTokenId)   
    wnft_pretty_print(wrapperRemovable, wnft721, wTokenId)
    #checks
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperRemovable.address
    assert wnft721.ownerOf(wrapperRemovable.lastWNFTId(out_type)[1]) == accounts[2].address
    assert wnft721.totalSupply() == 1

    
    #investor unwraps wnft
    before_eth_balance1 = accounts[1].balance()
    before_eth_balanceW = wrapperRemovable.balance()

    #nothing in collateral
    unitbox.unWrap(wnft721.address, wTokenId, {"from": accounts[2]})  #by scholar
    assert wrapperRemovable.balance() == 0
    assert accounts[1].balance() == before_eth_balance1 + before_eth_balanceW

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[1]

    