from brownie import *
import json
import pytest
import logging
from web3 import Web3
from eth_abi import encode_single
from eth_account.messages import encode_defunct

accounts.load('secret2')
accounts.load('secret1')
ORACLE_ADDRESS = '0x8125F522a712F4aD849E6c7312ba8263bEBeEFeD' 
ORACLE_PRIVATE_KEY = '0x222ead82a51f24a79887aae17052718249295530f8153c73bf1f257a9ca664af'

def main():
    '''NFTMinter = EnvelopUsers721Swarm.at('0x7a97Ce5C07f5aF52fe8f857290d76cEe5b53c4BD')
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

    hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)
    
    signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)

    tx = NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, signed_message.signature, {"from": accounts[0], 'gas_price': '60 gwei'})'''

    NFTMinter = EnvelopUsers1155Swarm.at('0xB3BF6FE7A484625A9E63b9b9FBe49a54cBf4F9c3')
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

    hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)
    
    signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)

    tx = NFTMinter.mintWithURI(accounts[1], tokenId, amount, tokenUri, signed_message.signature, {"from": accounts[0], 'gas_price': '60 gwei'})
   


