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

in_type = 3
out_type = 3
in_nft_amount = 3
subscriptionId = 0



#send in wrapping time more or less eth than in collateral's array
def test_settings(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
    
    #set agent
    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.setAgentStatus(saftV1.address, True, {"from": accounts[1]})

    subscriptionManager.setAgentStatus(saftV1.address, True, {"from": accounts[0]})

    subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
    payOption = [(niftsy20.address, payAmount), (dai.address, 2*payAmount)]
    services = [0]

    #add tariff
    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.addTarif((subscriptionType, payOption, services), {"from": accounts[1]})

    #without payMethods
    with reverts("No payment method"):
        subscriptionManager.addTarif((subscriptionType, [], services), {"from": accounts[0]})

    subscriptionManager.addTarif((subscriptionType, payOption, services), {"from": accounts[0]})
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
    
    #make settings
    subscriptionManager.setMainWrapper(wrapperTrustedV1, {"from": accounts[0]})
    saftV1.setTrustedWrapper(wrapperTrustedV1, {"from": accounts[0]})
    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapperTrustedV1.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperTrustedV1.address, {"from": accounts[0]})
    saftV1.setSubscriptionManager(subscriptionManager.address, {"from": accounts[0]})

    #buy subscription
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

    #check subsctription
    assert subscriptionManager.checkUserSubscription(accounts[0], 0) == True
    #check agentStatus
    assert subscriptionManager.agentRegistry(saftV1.address) == True

    ############################################################ WRAP wNFT by subscription ################################################
def test_wrapBath(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
    global ORIGINAL_NFT_IDs
    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.transferFrom(accounts[1], accounts[0], ORIGINAL_NFT_IDs[0], {"from": accounts[1]} )

    #add whiteList
    wrapperTrustedV1.setWhiteList(whiteListsForTrustedWrapper.address, {"from": accounts[0]})

    #add tokens in whiteList (dai and niftsy). Weth is NOT in whiteList. But it is able to be added by wrapBatch
    wl_data = (True, True, False, techERC20ForSaftV1.address)
    whiteListsForTrustedWrapper.setWLItem((2, dai.address), wl_data, {"from": accounts[0]})
    whiteListsForTrustedWrapper.setWLItem((2, niftsy20.address), wl_data, {"from": accounts[0]})


    token_property = (in_type, erc721mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)

    for i in range(len(ORIGINAL_NFT_IDs)):
        erc721mock.approve(wrapperTrustedV1, ORIGINAL_NFT_IDs[i], {"from": accounts[0]})
        
    dai_amount = 0
    weth_amount = 0
    inDataS = []
    receiverS = []
    fee = [('0x00', transfer_fee_amount, niftsy20.address)]
    lock = [('0x0', chain.time() + 100)]
    royalty = [(accounts[9].address, 2000), (wrapperTrustedV1.address, 8000)]
    for i in range(len(ORIGINAL_NFT_IDs)):

        token_data = (token_property, ORIGINAL_NFT_IDs[i], 0)

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

        dai_amount = dai_amount + Wei(call_amount)
        weth_amount = weth_amount + Wei(2*call_amount)

        receiverS.append(accounts[i].address)

    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = ((1, zero_address), 0, 1e18)
    collateralS = [eth_data, dai_data, weth_data]
    dai.approve(wrapperTrustedV1.address, dai_amount, {"from": accounts[0]})
    weth.approve(wrapperTrustedV1.address, weth_amount, {"from": accounts[0]})

    #wrap batch
    tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[0], "value": len(ORIGINAL_NFT_IDs)*eth_amount})

    chain.sleep(20)
    chain.mine()

    ##################################### Subscription is expired ######################################
    ORIGINAL_NFT_IDs = [55555]

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.transferFrom(accounts[1], accounts[0], ORIGINAL_NFT_IDs[0], {"from": accounts[1]} )

    for i in range(len(ORIGINAL_NFT_IDs)):
        erc721mock.approve(wrapperTrustedV1, ORIGINAL_NFT_IDs[i], {"from": accounts[0]})

    dai_amount = 0
    weth_amount = 0
    inDataS = []
    receiverS = []


    for i in range(len(ORIGINAL_NFT_IDs)):

        token_data = (token_property, ORIGINAL_NFT_IDs[i], 0)

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

        dai_amount = dai_amount + Wei(call_amount)
        weth_amount = weth_amount + Wei(2*call_amount)

        receiverS.append(accounts[i].address)

    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = ((1, zero_address), 0, 1e18)
    collateralS = [eth_data, dai_data, weth_data]
    dai.approve(wrapperTrustedV1.address, dai_amount, {"from": accounts[0]})
    weth.approve(wrapperTrustedV1.address, weth_amount, {"from": accounts[0]})

    logging.info(subscriptionManager.checkUserSubscription(accounts[0], 0))
    logging.info(subscriptionManager.getUserTickets(accounts[0]))
    logging.info(chain.time())
    logging.info(saftV1.subscriptionManager())
    logging.info(subscriptionManager.address)
    #logging.info(saftV1.check(accounts[0], 0))


    #wrap batch
    tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[0], "value": len(ORIGINAL_NFT_IDs)*eth_amount})