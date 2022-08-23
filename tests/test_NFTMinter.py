import pytest
import logging
from brownie import Wei, reverts, chain, web3
from makeTestData import makeNFTForTest721
from web3 import Web3
from eth_abi import encode_single
from eth_account.messages import encode_defunct


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
ORIGINAL_NFT_IDs_BATCH = [10,11,12,13]
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

def test_mint(accounts, NFTMinter, MockManager):
    
    tokenId = 1
    tokenUri = 'https://swarm.envelop.is/bzz/'
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

    with reverts("Unexpected signer"):
        NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, signed_message.signature, {"from": accounts[0]})

    NFTMinter.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0]})

    #with reverts("Signature check failed"):
    #    NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, signed_message_wrong.signature, {"from": accounts[0]})

    NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, signed_message.signature, {"from": accounts[0]})

    #use previous data again
    with reverts("ERC721: token already minted"):
        NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, signed_message.signature, {"from": accounts[0]})

def test_subscription(accounts, NFTMinter, MockManager):
    tokenId = 2
    tokenUri = 'https://swarm.envelop.is/bzz/'

    with reverts("Ownable: caller is not the owner"):
        NFTMinter.setSubscriptionManager(MockManager.address, {"from": accounts[1]})

    with reverts("Non zero only"):
        NFTMinter.setSubscriptionManager(zero_address, {"from": accounts[0]})

    NFTMinter.setSubscriptionManager(MockManager.address, {"from": accounts[0]})

    with reverts("Has No Subscription"):
        NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})

    MockManager.setMinter(NFTMinter, accounts[0], True)
    NFTMinter.mintWithURI(accounts[1], tokenId, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    



