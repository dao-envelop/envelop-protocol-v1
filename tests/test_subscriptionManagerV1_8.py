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
ticketValidPeriod = 10  #10 sec
counter = 0
payAmount = 1e18
batch = 4

in_type = 3
out_type = 3
in_nft_amount = 3
subscriptionId = 0

#two tariff. one service. one subscriptionManagers - buy one subscription!!
def test_settings(accounts, erc721mock, wrapperTrustedV1, dai, weth, wnft721, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
    
    #set agent
    subscriptionManager.setAgentStatus(saftV1, True, {"from": accounts[0]}) 

    subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
    payOption = [(niftsy20.address, payAmount), (dai.address, 2*payAmount)]
    #service 0 is not included in tariff. Only service
    services = [0]

    #add tariff
    subscriptionManager.addTarif((subscriptionType, payOption, [0]), {"from": accounts[0]})
    subscriptionManager.addTarif((subscriptionType, [(niftsy20.address, 3*payAmount)], [0]), {"from": accounts[0]})


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

    logging.info(subscriptionManager.checkUserSubscription(accounts[0], 0))

    chain.sleep(2*ticketValidPeriod)
    chain.mine()


    logging.info(subscriptionManager.checkUserSubscription(accounts[0], 0))

    #buy subscription with ticketValidPeriod
    #create allowance
    niftsy20.approve(subscriptionManager.address, 3*payAmount, {"from": accounts[0]})
    #call buySubscription
    tx = subscriptionManager.buySubscription(1,0, accounts[0], {"from": accounts[0]})

    logging.info(subscriptionManager.checkUserSubscription(accounts[0], 0))

