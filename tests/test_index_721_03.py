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

def test_simple_wrap(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

    wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

    erc721_property = (in_type, erc721mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    eth_property = (1, zero_address)

    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 1)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = (eth_property, 0, Wei(eth_amount))

    fee = []
    lock = [('0x0', chain.time() + 10), ('0x0', chain.time() + 20)]
    royalty = []

    wNFT = ( erc721_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    wrapper.wrap(wNFT, [dai_data, weth_data, eth_data], accounts[3], {"from": accounts[1], "value": eth_amount})
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    wNFT = wrapper.getWrappedToken(wnft721, wTokenId)   
    wnft_pretty_print(wrapper, wnft721, wTokenId)
    #checks
    assert wrapper.balance() == eth_amount
    assert dai.balanceOf(wrapper) == call_amount
    assert weth.balanceOf(wrapper) == 2*call_amount
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
    assert wnft721.ownerOf(wrapper.lastWNFTId(out_type)[1]) == accounts[3].address
    assert wnft721.totalSupply() == 1

    #logging.info(wNFT)
    assert wNFT[0] == erc721_data
    assert wNFT[1] == [eth_data, dai_data, weth_data]
    assert wNFT[2] == zero_address
    assert wNFT[3] == fee
    assert wNFT[4] == lock
    assert wNFT[5] == royalty
    assert wNFT[6] == '0x0' 
    
    with reverts("TimeLock error"):
        wrapper.unWrap(3, wnft721, wTokenId, {'from': accounts[3]})

    chain.sleep(250)
    chain.mine()
        
def test_full(accounts, erc721mock, wrapper, wnft721, keeper, spawner721mock):
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    wnft721.setApprovalForAll(keeper, True, {'from': accounts[3]})
    hashed_secret = keeper.getHashed(secret)
    keeper.setSpawnerContract(web3.eth.chain_id,(spawner721mock, 22),{'from': accounts[0]})

    tx = keeper.freeze((wnft721, wTokenId), web3.eth.chain_id, hashed_secret,{'from': accounts[3]})
    
    logging.info('Freeze event:{}'.format(tx.events['NewFreeze']))
    #logging.info('Debug event:{}'.format(tx.events['Debug']))
    encoded_msg = encode_single(
        '(bytes32,address,uint256)',
         (hashed_secret, tx.events['NewFreeze']['spawnerContract'], tx.events['NewFreeze']['spawnedTokenId'])
    )
    hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    logging.info('frozenItems[{}] = {}'.format(
        Web3.toBytes(hashed_msg).hex(), 
        keeper.frozenItems(Web3.toBytes(hashed_msg))
    ))
    logging.info('tx.hash={}'.format(tx.txid))

    freeze_tx1 = tx.txid
    #assert keeper
    assert wnft721.balanceOf(keeper) == 1
    assert wnft721.ownerOf(wTokenId) == keeper.address
    assert keeper.frozenItems(Web3.toBytes(hashed_msg))[1] == wTokenId


    # get tx datails from Oracle
    tx = chain.get_transaction(freeze_tx1)
    logging.info('\ntx: {} \nsender: {}\n logs:{}'.format(tx.txid, tx.sender, tx.logs))
    logging.info('Freeze event from Oracle:{}'.format(tx.events['NewFreeze']))
    # Lets prepare  signed  message for mint nft key
    encoded_msg = encode_single(
        '(address,uint256,address,uint256)',
        ( Web3.toChecksumAddress(accounts[3].address), 
          Web3.toInt(web3.eth.chain_id), 
          Web3.toChecksumAddress(tx.events['NewFreeze']['spawnerContract']), 
          Web3.toInt(tx.events['NewFreeze']['spawnedTokenId'])
        )
    )
    hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)
    
    #CREATE signed_message
    signed_message_after_freeze1 = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)
    logging.info('signed_message_after_freeze1 is {}'.format(signed_message_after_freeze1))

    spawner721mock.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0]})

    #mint nft key first time
    spawntx1 = spawner721mock.mint(
        Web3.toInt(tx.events['NewFreeze']['spawnedTokenId']), 
        #signed_message.messageHash, 
        signed_message_after_freeze1.signature,
        {'from':accounts[3]}
    )

    assert spawner721mock.ownerOf(tx.events['NewFreeze']['spawnedTokenId']) == accounts[3]
    spawned_token_id1 = tx.events['NewFreeze']['spawnedTokenId']

    logging.info('spawned_token_id1 = {}'.format(spawned_token_id1))


    #tx = chain.get_transaction(freeze_tx1)

   
    tx_burn1 = spawner721mock.burn(spawned_token_id1, {'from':accounts[3]})

    # Lets prepare  signed  message to unfreeze wNFT - for account 3. Acc3 will take unfrozen WNFT
    encoded_msg = encode_single(
        '(address,address,uint256)',
        ( Web3.toChecksumAddress(accounts[3].address), 
          Web3.toChecksumAddress(spawner721mock.address), 
          Web3.toInt(spawned_token_id1)
        )
    )
    hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)
    signed_message_after_burn1 = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)
    logging.info('signed_message_after_burn1 is {}'.format(signed_message_after_burn1))
    keeper.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0]})
    logging.info('Check wnft by proof({}): {}'.format(
        keeper.getHashed(secret),
        keeper.checkWNFTByProof(
            keeper.getHashed(secret),
            Web3.toChecksumAddress(spawner721mock.address), 
            Web3.toInt(spawned_token_id1)
        )
        
    ))

    tx_unfreez1 = keeper.unFreeze(
        secret,
        Web3.toChecksumAddress(spawner721mock.address), 
        Web3.toInt(spawned_token_id1),
        #signed_message.messageHash, 
        signed_message_after_burn1.signature,
        {'from':accounts[3]}

    )
    logging.info('tx_unfreez events {}'.format(tx_unfreez1.events))
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    #check - wnft is owned by acc3
    assert wnft721.ownerOf(wTokenId) == accounts[3]


    #freeze same wNFT again

    wnft721.setApprovalForAll(keeper, True, {'from': accounts[3]})
    hashed_secret = keeper.getHashed(secret)

    tx = keeper.freeze((wnft721, wTokenId), web3.eth.chain_id, hashed_secret,{'from': accounts[3]})
    logging.info('Freeze event:{}'.format(tx.events['NewFreeze']))
    #logging.info('Debug event:{}'.format(tx.events['Debug']))
    encoded_msg = encode_single(
        '(bytes32,address,uint256)',
         (hashed_secret, tx.events['NewFreeze']['spawnerContract'], tx.events['NewFreeze']['spawnedTokenId'])
    )
    hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    logging.info('frozenItems[{}] = {}'.format(
        Web3.toBytes(hashed_msg).hex(), 
        keeper.frozenItems(Web3.toBytes(hashed_msg))
    ))
    logging.info('tx.hash={}'.format(tx.txid))
    freeze_tx2 = tx.txid
    #assert keeper
    assert wnft721.balanceOf(keeper) == 1
    assert wnft721.ownerOf(wTokenId) == keeper.address
    assert keeper.frozenItems(Web3.toBytes(hashed_msg))[1] == wTokenId


    # get tx datails from Oracle for second frozen transaction
    tx = chain.get_transaction(freeze_tx2)
    logging.info('\ntx: {} \nsender: {}\n logs:{}'.format(tx.txid, tx.sender, tx.logs))
    logging.info('Freeze event from Oracle:{}'.format(tx.events['NewFreeze']))
    # Lets prepare  signed  message for second minting of the nft key
    encoded_msg = encode_single(
        '(address,uint256,address,uint256)',
        ( Web3.toChecksumAddress(accounts[3].address), 
          Web3.toInt(web3.eth.chain_id), 
          Web3.toChecksumAddress(tx.events['NewFreeze']['spawnerContract']), 
          Web3.toInt(tx.events['NewFreeze']['spawnedTokenId'])
        )
    )
    hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)
    
    #CREATE signed_message
    signed_message_after_freeze2 = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)
    logging.info('signed_message_after_freeze2 is {}'.format(signed_message_after_freeze2))

    #mint nft key second time - token id is new!!
    spawntx2 = spawner721mock.mint(
        Web3.toInt(tx.events['NewFreeze']['spawnedTokenId']), 
        #signed_message.messageHash, 
        signed_message_after_freeze2.signature,
        {'from':accounts[3]}
    )

    assert spawner721mock.ownerOf(tx.events['NewFreeze']['spawnedTokenId']) == accounts[3]
    spawned_token_id2 = tx.events['NewFreeze']['spawnedTokenId']
    logging.info('spawned_token_id2 = {}'.format(spawned_token_id2))

   
    tx_burn2 = spawner721mock.burn(spawned_token_id2, {'from':accounts[3]})

    #try to unfreeze using signature of the previous unfreezing
    with reverts("Unexpected signer"):
        tx_unfreez = keeper.unFreeze(
            secret,
            Web3.toChecksumAddress(spawner721mock.address), 
            Web3.toInt(spawned_token_id2),
            #signed_message.messageHash, 
            signed_message_after_burn1.signature,
            {'from':accounts[3]}
        )
