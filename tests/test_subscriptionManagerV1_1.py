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

#first we will buy subscription with ticketValidPeriod, wrap, then we will buy subscription with counters = 1, wrap, then will try to wrap again (expect revert) 
#one tariff, we will change settings of tariff 

def test_settings(accounts, erc721mock, wrapperTrustedV1, dai, weth, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, subscriptionManager):
    
    #set agent (smart contract for which somebody will buy subscription)
    subscriptionManager.setAgentStatus(saftV1.address, True, {"from": accounts[0]})

    subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
    payOption = [(niftsy20.address, payAmount), (dai.address, 2*payAmount)]
    services = [0]

    #add tariff
    subscriptionManager.addTarif((subscriptionType, payOption, services), {"from": accounts[0]})
    assert len(subscriptionManager.getAvailableTariffs()) == 1

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
    assert subscriptionManager.getUserTickets(accounts[0])[0][1] == 0
    assert subscriptionManager.getUserTickets(accounts[0])[0][0] > 0
    
    ############################################################ WRAP wNFT by subscription (ticketValidPeriod) ################################################
def test_wrapBatch_ticketValidPeriod(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, subscriptionManager):
    
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
    wnft_count = wnft721ForwrapperTrustedV1.balanceOf(accounts[0])
    tx = saftV1.wrapBatch(inDataS, [], receiverS, {"from": accounts[0]})
    assert wnft721ForwrapperTrustedV1.balanceOf(accounts[0]) == wnft_count + 4

#edit tariff - add counter , without ticketValidPeriod
def test_settings1(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, subscriptionManager):
    
    #edit tariff
    subscriptionManager.editTarif(0, timelockPeriod, 0, 1, True, {"from": accounts[0]})

    #buy subscription with counter
    #create allowance
    niftsy20.approve(subscriptionManager.address, payAmount, {"from": accounts[0]})

    #call buySubscription
    wnft_count = wnft721ForwrapperTrustedV1.balanceOf(accounts[0])
    with reverts("Only one valid ticket at time"):
        tx = subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})
    chain.sleep(ticketValidPeriod+1)
    chain.mine()
    tx = subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})
    assert wnft721ForwrapperTrustedV1.balanceOf(accounts[0]) == wnft_count + 1

    #check tickets
    assert subscriptionManager.getUserTickets(accounts[0])[0][1] == 1
    assert subscriptionManager.getUserTickets(accounts[0])[0][0] > 0

############################################################ WRAP wNFT by subscription (counter) ################################################
def test_wrapBatch_counter(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, subscriptionManager):
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
    wnft_count = wnft721ForwrapperTrustedV1.balanceOf(accounts[0])
    tx = saftV1.wrapBatch(inDataS, [], receiverS, {"from": accounts[0]})
    assert wnft721ForwrapperTrustedV1.balanceOf(accounts[0]) == wnft_count + 4

    #try wrap when counter=0
    wnft_count = wnft721ForwrapperTrustedV1.balanceOf(accounts[0])
    with reverts("Valid ticket not found"):
        tx = saftV1.wrapBatch(inDataS, [], receiverS, {"from": accounts[0]})
    #check counter in ticket
    assert subscriptionManager.getUserTickets(accounts[0])[0][1] == 0