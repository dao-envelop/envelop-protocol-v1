import pytest
import logging
from brownie import Wei, reverts, chain, web3
from makeTestData import makeNFTForTest721
from web3 import Web3
from eth_abi import encode_single
from eth_account.messages import encode_defunct


LOGGER = logging.getLogger(__name__)

ORACLE_ADDRESS = '0x8125F522a712F4aD849E6c7312ba8263bEBeEFeD' 
ORACLE_PRIVATE_KEY = '0x222ead82a51f24a79887aae17052718249295530f8153c73bf1f257a9ca664af'
zero_address = '0x0000000000000000000000000000000000000000'


def test_mint(accounts, NFTMinter, MockManager):
    
    tokenId = 1
    tokenUri = 'b72f05424ee87a65cb7c94b432d3b5b553bbb82f7b0fe34e8a3ad161b1b05ca5/'
    #Message for sign
    encoded_msg = encode_single(
         '(address,uint256,string)',
         ( accounts[0].address, 
           Web3.toInt(tokenId) ,
           tokenUri
         )
    )

    encoded_msg_wrong = encode_single(
         '(address,uint256,string)',
         ( accounts[0].address, 
           Web3.toInt(tokenId+1) ,
           tokenUri
         )
    )

    hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    hashed_msg_wrong = Web3.solidityKeccak(['bytes32'], [encoded_msg_wrong])
    ## Block Above has too complicated param for encode in web3py
    ## So  use helper from contract
    
    logging.info('hashed_msg = {}'.format(hashed_msg))
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)
    message_wrong = encode_defunct(primitive=hashed_msg_wrong)

    logging.info('message = {}'.format(message))
    signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)
    signed_message_wrong = web3.eth.account.sign_message(message_wrong, private_key=ORACLE_PRIVATE_KEY)

    logging.info('sign_message is {}'.format(signed_message))
    logging.info('sign_message is {}'.format(signed_message_wrong))
    
    ####################################
    with reverts("Ownable: caller is not the owner"):
        NFTMinter.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[1]})

    #signer is not in trusted signer's list
    with reverts("Unexpected signer"):
        NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, signed_message.signature, {"from": accounts[0]})

    NFTMinter.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0]})

    with reverts("Unexpected signer"):
        NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, signed_message_wrong.signature, {"from": accounts[0]})

    tx = NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, signed_message.signature, {"from": accounts[0]})
    logging.info('gas = {}'.format(tx.gas_used))

    #use previous data again
    with reverts("ERC721: token already minted"):
        NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, signed_message.signature, {"from": accounts[0]})
    assert NFTMinter.ownerOf(1) == accounts[1].address

    #use previous signature, new data
    with reverts("Unexpected signer"):
        NFTMinter.mintWithURI(accounts[1], tokenId+1, tokenUri, signed_message.signature, {"from": accounts[0]})

'''def test_subscription(accounts, NFTMinter, MockManager):
    tokenId = 2
    tokenUri = '2'

    #without using signature, SubscriptionManager is not set
    with reverts(""):
        NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})

    #try to set SubscriptionManager by not owner
    with reverts("Ownable: caller is not the owner"):
        NFTMinter.setSubscriptionManager(MockManager.address, {"from": accounts[1]})

    with reverts("Non zero only"):
        NFTMinter.setSubscriptionManager(zero_address, {"from": accounts[0]})

    #set SubscriptionManager
    NFTMinter.setSubscriptionManager(MockManager.address, {"from": accounts[0]})


    with reverts("Has No Subscription"):
        NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})

    MockManager.setMinter(NFTMinter, accounts[0], True)
    NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    
    assert NFTMinter.ownerOf(2) == accounts[1].address

    logging.info(NFTMinter.tokenURI(1))'''

def test_batch(accounts, NFTMinter):
    #with signature
    _to = [accounts[1].address, accounts[2].address]
    _tokenId = [3, 4]
    _tokenURI = ['3', '4']
    _signature = []

    for i in range(2):
        encoded_msg = encode_single(
            '(address,uint256,string)',
            ( accounts[0].address, 
            Web3.toInt(_tokenId[i]) ,
            _tokenURI[i]
            )
        )

        hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
        logging.info('hashed_msg = {}'.format(hashed_msg))
        # Ether style signature
        message = encode_defunct(primitive=hashed_msg)
        logging.info('message = {}'.format(message))
        signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)
        
        logging.info('sign_message is {}'.format(signed_message))

        _signature.append(signed_message.signature)
           
    NFTMinter.mintWithURIBatch(_to, _tokenId, _tokenURI, _signature)

    assert NFTMinter.ownerOf(3) == accounts[1].address

    #without signature - using subscription
    '''
    _to = [accounts[3].address, accounts[4].address]
    _tokenId = [5, 6]
    _tokenURI = ['5', '6']
    _signature = [Web3.toBytes(text=''), Web3.toBytes(text='')] #empty
           
    NFTMinter.mintWithURIBatch(_to, _tokenId, _tokenURI, _signature)

    assert NFTMinter.ownerOf(5) == accounts[3].address'''




