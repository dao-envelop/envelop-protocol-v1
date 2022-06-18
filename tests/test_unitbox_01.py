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

def test_wrap(accounts, erc721mock, unitbox, wrapperRemovable, wnft721):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

    erc721mock.approve(wrapperRemovable.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
    wrapperRemovable.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperRemovable.address, {"from": accounts[0]})

    erc721_property = (in_type, erc721mock.address)
    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 1)
    royalty=[
        (accounts[1], 4000), # Maker
        (accounts[2], 5000), # Taker
        (unitbox.address, 1000) # Treasure proxy
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
        0x0000
    )

    # Message for sign
    # encoded_msg = encode_single(
    #     '(address,uint256,(address,uint16)[],address,uint256)',
    #     ( Web3.toChecksumAddress(erc721mock.address), 
    #       Web3.toInt(ORIGINAL_NFT_IDs[0]),
    #       royalty, 
    #       Web3.toChecksumAddress(accounts[0].address), 
    #       Web3.toInt(0)
    #     )
    # )
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
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)
    signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)
    logging.info('sign_message is {}'.format(signed_message))
    ####################################
    unitbox.setSignerState(ORACLE_ADDRESS, True, {'from':accounts[0]})
    wrapperRemovable.setTrustedAddress(unitbox, True, {'from':accounts[0]})

    unitbox.wrapForRent(inData, 0, signed_message.signature, {"from": accounts[0]})
    wTokenId = wrapperRemovable.lastWNFTId(out_type)[1]
    wNFT = wrapperRemovable.getWrappedToken(wnft721, wTokenId)   
    wnft_pretty_print(wrapperRemovable, wnft721, wTokenId)
    #checks
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperRemovable.address
    assert wnft721.ownerOf(wrapperRemovable.lastWNFTId(out_type)[1]) == accounts[2].address
    assert wnft721.totalSupply() == 1

 
    


    #wrapper.unWrap(3, wnft721, wTokenId, {'from': accounts[3]})
        
# def test_freeze(accounts, erc721mock, wrapper, wnft721, keeper, spawner721mock):
#     wTokenId = wrapper.lastWNFTId(out_type)[1]
#     wnft721.setApprovalForAll(keeper, True, {'from': accounts[3]})
#     hashed_secret = keeper.getHashed(secret)
#     keeper.setSpawnerContract(web3.eth.chain_id,(spawner721mock, 22),{'from': accounts[0]})
#     tx = keeper.freeze((wnft721, wTokenId), web3.eth.chain_id, hashed_secret,{'from': accounts[3]})
#     logging.info('Freeze event:{}'.format(tx.events['NewFreeze']))
#     #logging.info('Debug event:{}'.format(tx.events['Debug']))
#     encoded_msg = encode_single(
#         '(bytes32,address,uint256)',
#          (hashed_secret, tx.events['NewFreeze']['spawnerContract'], tx.events['NewFreeze']['spawnedTokenId'])
#     )
#     hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
#     logging.info('frozenItems[{}] = {}'.format(
#         Web3.toBytes(hashed_msg).hex(), 
#         keeper.frozenItems(Web3.toBytes(hashed_msg))
#     ))
#     logging.info('tx.hash={}'.format(tx.txid))
#     global freeze_tx
#     freeze_tx = tx.txid
#     #assert keeper
#     assert wnft721.balanceOf(keeper) == 1
#     assert wnft721.ownerOf(wTokenId) == keeper.address
#     assert keeper.frozenItems(Web3.toBytes(hashed_msg))[1] == wTokenId

# def test_spawn(accounts, keeper, spawner721mock):
#     # get tx datails from Oracle
#     tx = chain.get_transaction(freeze_tx)
#     logging.info('\ntx: {} \nsender: {}\n logs:{}'.format(tx.txid, tx.sender, tx.logs))
#     logging.info('Freeze event from Oracle:{}'.format(tx.events['NewFreeze']))
#     # Lets prepare  signed  message
#     encoded_msg = encode_single(
#         '(address,uint256,address,uint256)',
#         ( Web3.toChecksumAddress(accounts[3].address), 
#           Web3.toInt(web3.eth.chain_id), 
#           Web3.toChecksumAddress(tx.events['NewFreeze']['spawnerContract']), 
#           Web3.toInt(tx.events['NewFreeze']['spawnedTokenId'])
#         )
#     )
#     hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
#     # Ether style signature
#     message = encode_defunct(primitive=hashed_msg)
#     signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)
#     logging.info('sign_message is {}'.format(signed_message))

#     spawner721mock.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0]})
#     # logging.info('debug msg:{}'.format(
#     #     spawner721.debug(Web3.toInt(tx.events['NewFreeze']['spawnedTokenId']), accounts[3])
#     # ))
#     # logging.info('debug msg no ether:{}'.format(
#     #     spawner721.debug1(Web3.toInt(tx.events['NewFreeze']['spawnedTokenId']), accounts[3])
#     # ))
#     # logging.info('debug chainid:{}'.format(
#     #     spawner721.debugNet()
#     # ))
#     spawntx = spawner721mock.mint(
#         Web3.toInt(tx.events['NewFreeze']['spawnedTokenId']), 
#         #signed_message.messageHash, 
#         signed_message.signature,
#         {'from':accounts[3]}
#     )
#     global spawned_token_id
#     assert spawner721mock.ownerOf(tx.events['NewFreeze']['spawnedTokenId']) == accounts[3]
#     spawned_token_id = tx.events['NewFreeze']['spawnedTokenId']

# def test_reclaim(accounts, erc721mock, wrapper, wnft721, keeper, spawner721mock):
#     spawner721mock.transferFrom(accounts[3], accounts[4], spawned_token_id, {'from':accounts[3]})
#     tx = chain.get_transaction(freeze_tx)
#     tx_burn = spawner721mock.burn(spawned_token_id, {'from':accounts[4]})
    
#     # Lets prepare  signed  message
#     encoded_msg = encode_single(
#         '(address,address,uint256)',
#         ( Web3.toChecksumAddress(accounts[4].address), 
#           Web3.toChecksumAddress(tx.events['NewFreeze']['spawnerContract']), 
#           Web3.toInt(tx.events['NewFreeze']['spawnedTokenId'])
#         )
#     )
#     hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
#     # Ether style signature
#     message = encode_defunct(primitive=hashed_msg)
#     signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)
#     logging.info('sign_message is {}'.format(signed_message))
#     keeper.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0]})
#     logging.info('Check wnft by proof({}): {}'.format(
#         keeper.getHashed(secret),
#         keeper.checkWNFTByProof(
#             keeper.getHashed(secret),
#             Web3.toChecksumAddress(tx.events['NewFreeze']['spawnerContract']), 
#             Web3.toInt(tx.events['NewFreeze']['spawnedTokenId'])
#         )
        
#     ))

#     tx_unfreez = keeper.unFreeze(
#         secret,
#         Web3.toChecksumAddress(tx.events['NewFreeze']['spawnerContract']), 
#         Web3.toInt(tx.events['NewFreeze']['spawnedTokenId']),
#         #signed_message.messageHash, 
#         signed_message.signature,
#         {'from':accounts[4]}

#     )
#     logging.info('tx_unfreez events {}'.format(tx_unfreez.events))
#     wTokenId = wrapper.lastWNFTId(out_type)[1]
#     assert wnft721.ownerOf(wTokenId) == accounts[4]




