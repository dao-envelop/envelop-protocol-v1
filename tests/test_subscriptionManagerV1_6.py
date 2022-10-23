import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222, 33333, 44444]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = 1e18
transfer_fee_amount = 100
timelockPeriod = 3600*24*30*12 #1 year
ticketValidPeriod = 300  #5 min
counter = 0
payAmount = 1e18
batch = 4

in_type = 3
out_type = 3
in_nft_amount = 3
subscriptionId = 0

#several tariffs for one service. Buy both tariff by several accounts. Try to wrap
def test_settings(accounts, erc721mock, wrapperTrustedV1, dai, weth, wnft721, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
    
    #set agent
    subscriptionManager.setAgentStatus(saftV1, True, {"from": accounts[0]}) 

    subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
    payOption = [(niftsy20.address, payAmount), (dai.address, 2*payAmount)]
    #service 0 is not included in tariff. Only service
    services = [0]

    #add tariff
    for i in range(1000):
        subscriptionManager.addTarif((subscriptionType, payOption, services), {"from": accounts[0]})
        logging.info(i)
    assert len(subscriptionManager.getAvailableTariffs()) == 1000

    #buy subscription with ticketValidPeriod
    #create allowance
    niftsy20.approve(subscriptionManager.address, payAmount, {"from": accounts[0]})
    subscriptionManager.setMainWrapper(wrapperTrustedV1, {"from": accounts[0]})
    saftV1.setTrustedWrapper(wrapperTrustedV1, {"from": accounts[0]})
    if (wrapperTrustedV1.lastWNFTId(out_type)[1] == 0):
        wrapperTrustedV1.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperTrustedV1.address, {"from": accounts[0]})
    
    saftV1.setSubscriptionManager(subscriptionManager.address, {"from": accounts[0]})

    #call buySubscription
    tx = subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})
    assert wnft721.balanceOf(accounts[0]) == 1
    #check tickets
    logging.info(subscriptionManager.getUserTickets(accounts[0]))
    assert subscriptionManager.getUserTickets(accounts[0])[0][1] == 0
    assert subscriptionManager.getUserTickets(accounts[0])[0][0] > 0
    assert len(subscriptionManager.getUserTickets(accounts[0])) == 1000

def test_wrapBatch(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
    
    #wrap empty
    token_property = (0, zero_address)
    token_data = (token_property, 0, 0)
    inDataS = []
    receiverS = []
    fee = []
    lock = []
    royalty = []
    for i in range(batch):

        wNFT = ( token_data,
            zero_address,
            fee,
            lock,
            royalty,
            out_type,
            0,
            Web3.toBytes(0x0000)
            )
        inDataS.append(wNFT)

        #all wnft for accounts[0]
        receiverS.append(accounts[0].address)

    #wrap batch
    tx = saftV1.wrapBatch(inDataS, [], receiverS, {"from": accounts[0]})

    #check tickets
    assert subscriptionManager.getUserTickets(accounts[0])[0][1] == 0
    assert subscriptionManager.getUserTickets(accounts[0])[0][0] > 0
