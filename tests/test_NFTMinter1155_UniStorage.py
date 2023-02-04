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
timelockPeriod = 3600*24*30*12 #1 year
ticketValidPeriod = 10  #10 sec
counter = 0
payAmount = 1e18

in_type = 3
out_type = 3



def test_mint(accounts, NFTMinter1155Uni, MockManager):
    
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
        NFTMinter1155Uni.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[1]})

    with reverts("Unexpected signer"):
        NFTMinter1155Uni.mintWithURI(accounts[1], tokenId, amount, tokenUri, signed_message.signature, {"from": accounts[0]})

    NFTMinter1155Uni.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0]})

    #wrong signature
    with reverts("Unexpected signer"):
        NFTMinter1155Uni.mintWithURI(accounts[1], tokenId, amount, tokenUri, signed_message_wrong.signature, {"from": accounts[0]})

    tx = NFTMinter1155Uni.mintWithURI(accounts[1], tokenId, amount, tokenUri, signed_message.signature, {"from": accounts[0]})
    logging.info('gas = {}'.format(tx.gas_used))

    #use previous data again
    with reverts("This id already minted"):
        NFTMinter1155Uni.mintWithURI(accounts[1], tokenId, amount, tokenUri, signed_message.signature, {"from": accounts[0]})

    with reverts("Unexpected signer"):
        NFTMinter1155Uni.mintWithURI(accounts[1], tokenId+1, amount, tokenUri, signed_message.signature, {"from": accounts[0]})
    assert NFTMinter1155Uni.totalSupply(tokenId) == amount
    assert NFTMinter1155Uni.balanceOf(accounts[1], tokenId) == amount

    logging.info('uri = {}'.format(NFTMinter1155Uni.uri(1)))
    #assert NFTMinter1155Uni.uri(1) == baseUrl+tokenUri

def test_subscription(accounts, NFTMinter1155Uni, subscriptionManager, niftsy20, dai, wrapperTrustedV1, wnft721):
    tokenId = 2
    tokenUri = '2'
    amount = 3

    #without using signature, SubscriptionManager is not set
    with reverts("Has No Subscription"):
        NFTMinter1155Uni.mintWithURI(accounts[1], tokenId, amount, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})   

    #settings
    subscriptionManager.setAgentStatus(NFTMinter1155Uni.address, True, {"from": accounts[0]})
    subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
    payOption = [(niftsy20.address, payAmount), (dai.address, 2*payAmount)]
    services = [NFTMinter1155Uni.SERVICE_CODE()]
    subscriptionManager.addTarif((subscriptionType, payOption, services), {"from": accounts[0]})

    #buy subscription
    #create allowance
    niftsy20.approve(subscriptionManager.address, payAmount, {"from": accounts[0]})

    #make settings
    subscriptionManager.setMainWrapper(wrapperTrustedV1, {"from": accounts[0]})

    if (wrapperTrustedV1.lastWNFTId(out_type)[1] == 0):
        wrapperTrustedV1.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperTrustedV1.address, {"from": accounts[0]})

    #try to set SubscriptionManager by not owner
    with reverts("Ownable: caller is not the owner"):
        NFTMinter1155Uni.setSubscriptionManager(subscriptionManager.address, {"from": accounts[1]})
    with reverts("Non zero only"):
        NFTMinter1155Uni.setSubscriptionManager(zero_address, {"from": accounts[0]})

    #set subscription manager
    NFTMinter1155Uni.setSubscriptionManager(subscriptionManager.address, {"from": accounts[0]})

    #try to buy when user does not have subscription
    with reverts("Valid ticket not found"):
        NFTMinter1155Uni.mintWithURI(accounts[1], tokenId, amount, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})

    #buy subscription
    tx = subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})

    #check subscription
    assert len(subscriptionManager.getUserTickets(accounts[0])) == 1
    assert niftsy20.balanceOf(wrapperTrustedV1) == payAmount

    #check Tiket
    assert subscriptionManager.getUserTickets(accounts[0])[0][0] > chain.time()
    assert subscriptionManager.getUserTickets(accounts[0])[0][1] == counter

    #check subsctription
    assert subscriptionManager.checkUserSubscription(accounts[0], NFTMinter1155Uni.SERVICE_CODE()) == True
    #check agentStatus
    assert subscriptionManager.agentRegistry(NFTMinter1155Uni.address) == True

    #try to use subscription
    NFTMinter1155Uni.mintWithURI(accounts[1], tokenId, amount, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    
    logging.info('uri = {}'.format(NFTMinter1155Uni.uri(tokenId)))
    assert NFTMinter1155Uni.totalSupply(tokenId) == amount
    assert NFTMinter1155Uni.balanceOf(accounts[1], tokenId) == amount
    tokenId += 3
    
    tokenUri = 'bzz://12345678'
    NFTMinter1155Uni.mintWithURI(accounts[1], tokenId, amount, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    
    logging.info('uri = {}'.format(NFTMinter1155Uni.uri(tokenId)))
    assert NFTMinter1155Uni.uri(tokenId) == tokenUri
    tokenId += 3

    tokenUri = 'ipfs://12345678'
    NFTMinter1155Uni.mintWithURI(accounts[1], tokenId, amount, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    
    logging.info('uri = {}'.format(NFTMinter1155Uni.uri(tokenId)))
    assert NFTMinter1155Uni.uri(tokenId) == tokenUri
    tokenId += 3

    okenUri = 'ipfs://12345678'
    NFTMinter1155Uni.setPrefixURI(Web3.toBytes(text='ipfs'), "https://pinata.com/",{"from": accounts[0]})
    NFTMinter1155Uni.mintWithURI(accounts[1], tokenId, amount, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    
    logging.info('uri = {}'.format(NFTMinter1155Uni.uri(tokenId)))
    assert NFTMinter1155Uni.uri(tokenId) == "https://pinata.com/"+tokenUri
    tokenId += 3


def test_setBaseURI(accounts, NFTMinter1155Uni):
    with reverts("Ownable: caller is not the owner"):
        NFTMinter1155Uni.setBaseURI('1', {"from": accounts[1]})
    NFTMinter1155Uni.setBaseURI('https:\\\\envelop.is\\', {"from": accounts[0]})



