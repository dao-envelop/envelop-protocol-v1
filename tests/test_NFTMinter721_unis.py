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
timelockPeriod = 3600*24*30*12 #1 year
ticketValidPeriod = 10  #10 sec
counter = 0
payAmount = 1e18
in_type = 3
out_type = 3
in_nft_amount = 3



def test_mint(accounts, NFTMinterUni, MockManager):
    
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
        NFTMinterUni.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[1]})

    #signer is not in trusted signer's list
    with reverts("Unexpected signer"):
        NFTMinterUni.mintWithURI(accounts[1], tokenId, tokenUri, signed_message.signature, {"from": accounts[0]})

    NFTMinterUni.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0]})

    with reverts("Unexpected signer"):
        NFTMinterUni.mintWithURI(accounts[1], tokenId, tokenUri, signed_message_wrong.signature, {"from": accounts[0]})

    tx = NFTMinterUni.mintWithURI(accounts[1], tokenId, tokenUri, signed_message.signature, {"from": accounts[0]})
    logging.info('gas = {}'.format(tx.gas_used))

    #use previous data again
    with reverts("ERC721: token already minted"):
        NFTMinterUni.mintWithURI(accounts[1], tokenId, tokenUri, signed_message.signature, {"from": accounts[0]})
    assert NFTMinterUni.ownerOf(1) == accounts[1].address

    #use previous signature, new data
    with reverts("Unexpected signer"):
        NFTMinterUni.mintWithURI(accounts[1], tokenId+1, tokenUri, signed_message.signature, {"from": accounts[0]})

def test_subscription(accounts, NFTMinterUni, subscriptionManager, niftsy20, dai, wrapperTrusted2, wnft721ForwrapperTrusted2):
    tokenId = 2
    tokenUri = '2'

    #without using signature, SubscriptionManager is not set
    with reverts("Has No Subscription"):
        NFTMinterUni.mintWithURI(accounts[1], tokenId, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})


    #settings
    subscriptionManager.setAgentStatus(NFTMinterUni.address, True, {"from": accounts[0]})
    subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
    payOption = [(niftsy20.address, payAmount), (dai.address, 2*payAmount)]
    services = [NFTMinterUni.SERVICE_CODE()]
    subscriptionManager.addTarif((subscriptionType, payOption, services), {"from": accounts[0]})

    #buy subscription
    #create allowance
    niftsy20.approve(subscriptionManager.address, payAmount, {"from": accounts[0]})

    #make settings
    subscriptionManager.setMainWrapper(wrapperTrusted2, {"from": accounts[0]})

    if (wrapperTrusted2.lastWNFTId(out_type)[1] == 0):
        wrapperTrusted2.setWNFTId(out_type, wnft721ForwrapperTrusted2.address, 0, {'from':accounts[0]})

    #try to set SubscriptionManager by not owner
    with reverts("Ownable: caller is not the owner"):
        NFTMinterUni.setSubscriptionManager(subscriptionManager.address, {"from": accounts[1]})
    with reverts("Non zero only"):
        NFTMinterUni.setSubscriptionManager(zero_address, {"from": accounts[0]})

    #set subscription manager
    NFTMinterUni.setSubscriptionManager(subscriptionManager.address, {"from": accounts[0]})

    #try to buy when user does not have subscription
    with reverts("Valid ticket not found"):
        NFTMinterUni.mintWithURI(accounts[1], tokenId, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})

    #buy subscription
    tx = subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})

    #check subscription
    assert len(subscriptionManager.getUserTickets(accounts[0])) == 1
    assert niftsy20.balanceOf(wrapperTrusted2) == payAmount

    #check Tiket
    assert subscriptionManager.getUserTickets(accounts[0])[0][0] > chain.time()
    assert subscriptionManager.getUserTickets(accounts[0])[0][1] == counter

    #check subsctription
    assert subscriptionManager.checkUserSubscription(accounts[0], NFTMinterUni.SERVICE_CODE()) == True
    #check agentStatus
    assert subscriptionManager.agentRegistry(NFTMinterUni.address) == True

    #try to use subscription
    NFTMinterUni.mintWithURI(accounts[1], tokenId, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    
    assert NFTMinterUni.ownerOf(2) == accounts[1].address
    logging.info(NFTMinterUni.tokenURI(1))
    
    tokenUri = 'bzz://testuri'
    NFTMinterUni.mintWithURI(accounts[1], tokenId+1, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    
    assert NFTMinterUni.tokenURI(tokenId+1) == tokenUri
    logging.info(
        'Mint for bzz,  tokenUri: {}'.format(
            NFTMinterUni.tokenURI(tokenId+1)
        )
    )

    tokenUri = 'ipfs://testuri'
    NFTMinterUni.mintWithURI(accounts[1], tokenId+2, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    
    assert NFTMinterUni.tokenURI(tokenId+2) == tokenUri
    logging.info(
        'Mint for ipfs,  tokenUri: {}'.format(
            NFTMinterUni.tokenURI(tokenId+2)
        )
    )

    # Mint with special base URL for prefix
    NFTMinterUni.setPrefixURI(Web3.toBytes(text='ipfs'), "https://pinata.com/",{"from": accounts[0]})
    tokenUri = 'ipfs://testuri'
    NFTMinterUni.mintWithURI(accounts[1], tokenId+3, tokenUri, Web3.toBytes(text=''), {"from": accounts[0]})    
    assert NFTMinterUni.tokenURI(tokenId+3) == "https://pinata.com/"+tokenUri
    logging.info(
        'Mint for ipfs,  tokenUri: {}'.format(
            NFTMinterUni.tokenURI(tokenId+3)
        )
    )


