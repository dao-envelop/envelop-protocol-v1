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
def test_settings(accounts, erc721mock, wrapperTrustedV1, dai, weth, wnft721, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
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
    subscriptionManager.addTarif((subscriptionType, payOption), {"from": accounts[0]})
    assert len(subscriptionManager.getAvailableTariffs()) == 1
   