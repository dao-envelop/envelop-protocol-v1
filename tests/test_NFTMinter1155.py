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
baseUrl = 'https://swarm.envelop.is/bzz/'



def test_mint(accounts, NFTMinter1155, MockManager):
    
    tokenId = 1
    tokenUri = 'b72f05424ee87a65cb7c94b432d3b5b553bbb82f7b0fe34e8a3ad161b1b05ca5/'
    amount = 3
    #Message for sign
    encoded_msg = encode_single(
         '(address,uint256,string,uint256)',
         ( accounts[0].address, 
           Web3.toInt(tokenId) ,
           tokenUri,
           Web3.toInt(amount)
         )
    )

    encoded_msg_wrong = encode_single(
         '(address,uint256,string,uint256)',
         ( accounts[0].address, 
           Web3.toInt(tokenId+1) ,
           tokenUri,
           Web3.toInt(amount)
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
        NFTMinter1155.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[1]})

    with reverts("Unexpected signer"):
        NFTMinter1155.mintWithURI(accounts[1], tokenId, amount, tokenUri, signed_message.signature, {"from": accounts[0]})

    NFTMinter1155.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0]})

    #with reverts("Signature check failed"):
    #    NFTMinter1155.mintWithURI(accounts[1], tokenId, tokenUri, signed_message_wrong.signature, {"from": accounts[0]})

    tx = NFTMinter1155.mintWithURI(accounts[1], tokenId, amount, tokenUri, signed_message.signature, {"from": accounts[0]})
    logging.info('gas = {}'.format(tx.gas_used))

    #use previous data again
    with reverts("This id already minted"):
        NFTMinter1155.mintWithURI(accounts[1], tokenId, amount, tokenUri, signed_message.signature, {"from": accounts[0]})
    assert NFTMinter1155.totalSupply(tokenId) == amount
    assert NFTMinter1155.balanceOf(accounts[1], tokenId) == amount

    logging.info('uri = {}'.format(NFTMinter1155.uri(1)))
    assert NFTMinter1155.uri(1) == baseUrl+tokenUri

def test_subscription(accounts, NFTMinter1155, MockManager):
    tokenId = 2
    tokenUri = '2'
    amount = 3

    with reverts("Ownable: caller is not the owner"):
        NFTMinter1155.setSubscriptionManager(MockManager.address, {"from": accounts[1]})

    with reverts("Non zero only"):
        NFTMinter1155.setSubscriptionManager(zero_address, {"from": accounts[0]})

    NFTMinter1155.setSubscriptionManager(MockManager.address, {"from": accounts[0]})

    with reverts("Has No Subscription"):
        NFTMinter1155.mintWithURI(accounts[1], tokenId, amount, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})

    MockManager.setMinter(NFTMinter1155, accounts[0], True)
    NFTMinter1155.mintWithURI(accounts[1], tokenId, amount, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    
    assert NFTMinter1155.totalSupply(tokenId) == amount
    assert NFTMinter1155.balanceOf(accounts[1], tokenId) == amount


def test_batch(accounts, NFTMinter1155):
    #with signature
    _to = [accounts[1].address, accounts[2].address]
    _tokenId = [3, 4]
    _amount = [4,4]
    _tokenURI = ['3', '4']
    _signature = []

    for i in range(2):
        encoded_msg = encode_single(
            '(address,uint256,string,uint256)',
            ( accounts[0].address, 
            Web3.toInt(_tokenId[i]),
            _tokenURI[i],
            Web3.toInt(_amount[i])
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
           
    NFTMinter1155.mintWithURIBatch(_to, _tokenId, _amount, _tokenURI, _signature)

    assert NFTMinter1155.totalSupply(_tokenId[0]) == _amount[0]
    assert NFTMinter1155.balanceOf(_to[0], _tokenId[0]) == _amount[0]

    #without signature

    _to = [accounts[3].address, accounts[4].address]
    _tokenId = [5, 6]
    _tokenURI = ['5', '6']
    _amount = [4,4]
    _signature = [Web3.toBytes(text=''), Web3.toBytes(text='')]
           
    NFTMinter1155.mintWithURIBatch(_to, _tokenId, _amount, _tokenURI, _signature)

    assert NFTMinter1155.totalSupply(_tokenId[0]) == _amount[0]
    assert NFTMinter1155.balanceOf(_to[0], _tokenId[0]) == _amount[0]
    assert NFTMinter1155.exists(_tokenId[0]) == True

def test_setBaseURI(accounts, NFTMinter1155):
    with reverts("Ownable: caller is not the owner"):
        NFTMinter1155.setBaseURI('1', {"from": accounts[1]})
    NFTMinter1155.setBaseURI('https:\\\\envelop.is\\', {"from": accounts[0]})



