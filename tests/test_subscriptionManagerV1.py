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
ticketValidPeriod = 3600*24*30  #1 month
counter = 0
payAmount = 1e18



#send in wrapping time more or less eth than in collateral's array
def test_settings(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3
    subscriptionId = 0

    #set agent
    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.setAgentStatus(saftV1.address, subscriptionId, True, {"from": accounts[1]})

    subscriptionManager.setAgentStatus(saftV1.address, subscriptionId, True, {"from": accounts[0]})

    subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
    payOption = [(niftsy20.address, payAmount), (dai.address, 2*payAmount)]

    #add tariff
    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.addTarif((subscriptionType, payOption), {"from": accounts[1]})

    #without payMethods
    with reverts("No payment method"):
        subscriptionManager.addTarif((subscriptionType, []), {"from": accounts[0]})

    subscriptionManager.addTarif((subscriptionType, payOption), {"from": accounts[0]})
    assert len(subscriptionManager.getAvailableTariffs()) == 1

    #buy subscription

    #doesn't have mainWrapper
    with reverts("ERC20: insufficient allowance"):
        subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})

    #create allowance
    niftsy20.approve(subscriptionManager.address, payAmount, {"from": accounts[0]})
    with reverts("ERC20: approve to the zero address"):
        subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})

    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.setMainWrapper(wrapperTrustedV1.address, {"from": accounts[1]})
    
    #settings
    subscriptionManager.setMainWrapper(wrapperTrustedV1, {"from": accounts[0]})
    #saftV1.setTrustedWrapper(wrapperTrustedV1, {"from": accounts[0]})
    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapperTrustedV1.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperTrustedV1.address, {"from": accounts[0]})

    tx = subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})

    assert len(subscriptionManager.getUserTickets(accounts[0])) == 1
    assert niftsy20.balanceOf(wrapperTrustedV1) == payAmount

    wTokenId = tx.events['WrappedV1']['outTokenId']

    #check wNFT
    assert wnft721.ownerOf(wTokenId) == accounts[0]
    assert wnft721.wnftInfo(wTokenId)[0] == ((0, zero_address), 0, 0) 
    assert wnft721.wnftInfo(wTokenId)[1][0] == ((2, niftsy20.address), 0, int(payAmount))
    assert wnft721.wnftInfo(wTokenId)[2] == zero_address
    assert wnft721.wnftInfo(wTokenId)[3] == []
    assert wnft721.wnftInfo(wTokenId)[4][0][1] > chain.time() + ticketValidPeriod
    assert wnft721.wnftInfo(wTokenId)[5] == []
    assert wnft721.wnftInfo(wTokenId)[6] == '0x0000'

    #check Tiket
    assert subscriptionManager.getUserTickets(accounts[0])[0][0] > chain.time()
    assert subscriptionManager.getUserTickets(accounts[0])[0][1] == counter






   