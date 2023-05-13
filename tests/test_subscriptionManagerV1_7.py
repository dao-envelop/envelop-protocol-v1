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

#one tariff. one service. several subscriptionManagers - new and old!!
def test_settings(accounts, erc721mock, wrapperTrustedV1, dai, weth, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, subscriptionManager):
    
    #set agent
    subscriptionManager.setAgentStatus(saftV1, True, {"from": accounts[0]}) 

    subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
    payOption = [(niftsy20.address, payAmount), (dai.address, 2*payAmount)]
    #service 0 is not included in tariff. Only service
    services = [0]

    #add tariff
    subscriptionManager.addTarif((subscriptionType, payOption, [0]), {"from": accounts[0]})


    #buy subscription with ticketValidPeriod
    #create allowance
    niftsy20.approve(subscriptionManager.address, payAmount, {"from": accounts[0]})
    subscriptionManager.setMainWrapper(wrapperTrustedV1, {"from": accounts[0]})
    saftV1.setTrustedWrapper(wrapperTrustedV1, {"from": accounts[0]})
    if (wrapperTrustedV1.lastWNFTId(out_type)[1] == 0):
        wrapperTrustedV1.setWNFTId(out_type, wnft721ForwrapperTrustedV1.address, 0, {'from':accounts[0]})
    
    saftV1.setSubscriptionManager(subscriptionManager.address, {"from": accounts[0]})

    #call buySubscription
    tx = subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})
    assert wnft721ForwrapperTrustedV1.balanceOf(accounts[0]) == 1
    #check tickets
    logging.info(subscriptionManager.getUserTickets(accounts[0]))
    assert subscriptionManager.getUserTickets(accounts[0])[0][1] == 0
    assert subscriptionManager.getUserTickets(accounts[0])[0][0] > 0


def test_wrapBatch(accounts, SubscriptionManagerV1, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, subscriptionManager):


    #change subscriptionManager
    subscriptionManager1 = accounts[0].deploy(SubscriptionManagerV1)
    subscriptionManager2 = accounts[0].deploy(SubscriptionManagerV1)
    with reverts("Ownable: caller is not the owner"):
        subscriptionManager2.setPreviousManager(subscriptionManager1, {"from": accounts[1]})
    
    subscriptionManager2.setPreviousManager(subscriptionManager1, {"from": accounts[0]})
    subscriptionManager1.setPreviousManager(subscriptionManager, {"from": accounts[0]})
    
    saftV1.setSubscriptionManager(subscriptionManager2.address, {"from": accounts[0]})

    #settings
    subscriptionManager2.setAgentStatus(saftV1.address, True, {"from": accounts[0]})
    subscriptionManager1.setAgentStatus(subscriptionManager2.address, True, {"from": accounts[0]})
    subscriptionManager.setAgentStatus(subscriptionManager1.address, True, {"from": accounts[0]})
    subscriptionManager2.setMainWrapper(wrapperTrustedV1, {"from": accounts[0]})


    #check subscriptionManager in saftV1
    assert saftV1.subscriptionManager() == subscriptionManager2.address

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
    assert subscriptionManager.getUserTickets(accounts[0])[0][1]== 0
    assert subscriptionManager.getUserTickets(accounts[0])[0][0] >0

    #try to use service when user does not have subscription not in any subscriptionManager
    with reverts("Valid ticket not found"):
        tx = saftV1.wrapBatch(inDataS, [], receiverS, {"from": accounts[1]})

    #buy subscription in last subscriptionManager
    ##
    #set agent
    subscriptionManager2.setAgentStatus(saftV1, True, {"from": accounts[0]}) 

    subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
    payOption = [(niftsy20.address, payAmount/2), (dai.address, 2*payAmount)]
    #service 0 is not included in tariff. Only service
    services = [0]

    #add tariff for subscriptionManager2
    subscriptionManager2.addTarif((subscriptionType, payOption, [0]), {"from": accounts[0]})
    niftsy20.transfer(accounts[1], payAmount/2, {"from": accounts[0]})
    niftsy20.approve(subscriptionManager2.address, payAmount/2, {"from": accounts[1]})

    #call buySubscription
    tx = subscriptionManager2.buySubscription(0,0, accounts[1], {"from": accounts[1]})


    #try to use service when user has subscription in last subscriptionManager
    tx = saftV1.wrapBatch(inDataS, [], receiverS, {"from": accounts[1]})