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
def test_settings(accounts, erc721mock, wrapperTrustedV1, dai, weth, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
    
    #set agent
    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.setAgentStatus(saftV1.address, True, {"from": accounts[1]})

    #set agent (smart contract for which somebody will buy subscription)
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
    if (wrapperTrustedV1.lastWNFTId(out_type)[1] == 0):
        wrapperTrustedV1.setWNFTId(out_type, wnft721ForwrapperTrustedV1.address, 0, {'from':accounts[0]})
    
    with reverts("Ownable: caller is not the owner"):
        saftV1.setSubscriptionManager(subscriptionManager.address, {"from": accounts[1]})
    saftV1.setSubscriptionManager(subscriptionManager.address, {"from": accounts[0]})

    #buy subscription
    tx = subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})

    assert len(subscriptionManager.getUserTickets(accounts[0])) == 1
    assert niftsy20.balanceOf(wrapperTrustedV1) == payAmount

    wTokenId = tx.events['WrappedV1']['outTokenId']

    #check wNFT
    assert wnft721ForwrapperTrustedV1.ownerOf(wTokenId) == accounts[0]
    assert wnft721ForwrapperTrustedV1.wnftInfo(wTokenId)[0] == ((0, zero_address), 0, 0) 
    assert wnft721ForwrapperTrustedV1.wnftInfo(wTokenId)[1][0] == ((2, niftsy20.address), 0, int(payAmount))
    assert wnft721ForwrapperTrustedV1.wnftInfo(wTokenId)[2] == zero_address
    assert wnft721ForwrapperTrustedV1.wnftInfo(wTokenId)[3] == []
    assert wnft721ForwrapperTrustedV1.wnftInfo(wTokenId)[4][0][1] > chain.time() + ticketValidPeriod
    assert wnft721ForwrapperTrustedV1.wnftInfo(wTokenId)[5] == []
    assert wnft721ForwrapperTrustedV1.wnftInfo(wTokenId)[6] == '0x0000'

    #check Tiket
    assert subscriptionManager.getUserTickets(accounts[0])[0][0] > chain.time()
    assert subscriptionManager.getUserTickets(accounts[0])[0][1] == counter

    #check subsctription
    assert subscriptionManager.checkUserSubscription(accounts[0], 0) == True
    #check agentStatus
    assert subscriptionManager.agentRegistry(saftV1.address) == True

    ############################################################ WRAP wNFT by subscription ################################################
def test_wrapBatch(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
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

    #wrap batch with expired subscription
    with reverts("Valid ticket not found"):
        tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[0], "value": len(ORIGINAL_NFT_IDs)*eth_amount})

#without subscription (there is not valid ticket of subscription)
def test_wrap_without_subscription(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):

    inDataS = []
    receiverS = []
    wNFT = ( ((0, zero_address), 0,0),
            zero_address,
            [],
            [],
            [],
            out_type,
            0,
            Web3.toBytes(0x0000)
            )
    receiverS.append(accounts[2])
    collateralS = []
    with reverts("Valid ticket not found"):
        tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[2]})

def test_buySubscription(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
    
    #try to buy nonexist subscription
    with reverts("Index out of range"):
        subscriptionManager.buySubscription(1,0, accounts[0], {"from": accounts[0]})    

    #try to buy paying by nonexist method
    with reverts("Index out of range"):
        subscriptionManager.buySubscription(0,2, accounts[0], {"from": accounts[0]})

    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.editTarif(0, 100, 100, 0, False, {"from": accounts[1]})

    #tariff is switched off. Try to buy subscription
    subscriptionManager.editTarif(0, 100, 100, 0, False, {"from": accounts[0]})
    with reverts("This subscription not available"):
        subscriptionManager.buySubscription(0, 1, accounts[0], {"from": accounts[0]})

    #tariff is switched on. Payment method is with zero amount token
    subscriptionManager.editTarif(0, 100, 100, 0, True, {"from": accounts[0]})
    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.addTarifPayOption(0, weth, 0, {"from": accounts[1]})
    subscriptionManager.addTarifPayOption(0, weth, 0, {"from": accounts[0]})
    with reverts("This Payment option not available"):
        subscriptionManager.buySubscription(0, 2, accounts[0], {"from": accounts[0]})
    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.editTarifPayOption(0,2, weth, payAmount, {"from": accounts[1]})
    
    #buy subscription by weth
    subscriptionManager.editTarifPayOption(0,2, weth, payAmount, {"from": accounts[0]})
    weth.approve(subscriptionManager.address, payAmount, {"from": accounts[0]})
    wl_data = (True, True, False, techERC20ForSaftV1.address)
    whiteListsForTrustedWrapper.setWLItem((2, weth.address), wl_data, {"from": accounts[0]})
    subscriptionManager.buySubscription(0, 2, accounts[0], {"from": accounts[0]})

    #try to call checkAndFixUserSubscription и fixUserSubscription from not agent
    with reverts('Unknown agent'):
        subscriptionManager.checkAndFixUserSubscription(accounts[0], 0, {"from": accounts[1]})
    with reverts('Unknown agent'):
        subscriptionManager.fixUserSubscription(accounts[0], 0, {"from": accounts[1]})
    #add account in agent list
    subscriptionManager.setAgentStatus(accounts[1], True, {"from": accounts[0]})
    subscriptionManager.checkAndFixUserSubscription(accounts[0], 0, {"from": accounts[1]})
    subscriptionManager.fixUserSubscription(accounts[0], 0, {"from": accounts[1]})


    #try to buy subscription when there is valid subscription
    niftsy20.approve(subscriptionManager.address, payAmount, {"from": accounts[0]})
    with reverts("Only one valid ticket at time"):
        subscriptionManager.buySubscription(0, 0, accounts[0], {"from": accounts[0]})

    #try to add service to tarif
    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.addServiceToTarif(0, 1, {"from": accounts[1]})
    subscriptionManager.addServiceToTarif(0, 1, {"from": accounts[0]})

    #try to remove service from tarif
    with reverts("Ownable: caller is not the owner"):
        subscriptionManager.removeServiceFromTarif(0, 1, {"from": accounts[1]})
    subscriptionManager.removeServiceFromTarif(0, 1, {"from": accounts[0]})

def test_buySubscription_for_other_user(accounts, erc721mock, wrapperTrustedV1, dai, weth, wrapper, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1, subscriptionManager):
    assert wnft721ForwrapperTrustedV1.balanceOf(accounts[9]) == 0
    #create allowance
    niftsy20.transfer(accounts[9], payAmount, {"from": accounts[0]})
    niftsy20.approve(subscriptionManager.address, payAmount, {"from": accounts[9]})
    #buy subscription
    tx = subscriptionManager.buySubscription(0,0, accounts[1], {"from": accounts[9]})
    assert subscriptionManager.getUserTickets(accounts[1])[0][0] > 0
    assert wnft721ForwrapperTrustedV1.balanceOf(accounts[9]) == 1
    assert subscriptionManager.getUserTickets(accounts[9])[0][0] == 0



    #++смена контракта подписки у враппера - со своими тарифами - останется ли билет, будет ли действовать  setPreviousManager - 3 контракта сменить
    #++смена контракта подписки у враппера - со своими тарифами - останется ли билет, будет ли действовать  setPreviousManager - 3 контракта сменить - не было подписок ни в одном контракте!!
    #++попытаться купить сначала подписку по времени, а потом подписку по количеству попыток
    #++попытатьcя завернуть, когда подписку купил на другую услугу
    #++добавить несколько тарифов, купить разными счетами разные
    #++одна услуга в нескольких тарифах, купил оба тарифа, пытаюсь завернуть
    #++для услуги продали тариф, потом выключили услугу в контракте подписок. Пытаемся завернуть
    #++тысяча тарифов заведено. Купили один. Проверить доступные билеты
    #++сделать тест, где билет получает третье лицо - не msg.sender
    #++попытаться вызвать checkAndFixUserSubscription и fixUserSubscription не из под агента

    


        
