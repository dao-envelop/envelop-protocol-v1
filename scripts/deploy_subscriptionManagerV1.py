from brownie import *
import json

accounts.load('secret2')
ORACLE_ADDRESS = '0x8125F522a712F4aD849E6c7312ba8263bEBeEFeD' 

print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))


tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4,5]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

def main():

    niftsy20 = TokenMock.at('0x376e8EA664c2E770E1C45ED423F62495cB63392D')
    dai = TokenMock.at('0x50BddB7911CE4248822a60968A32CDF1D683e7AD')

    timelockPeriod = 3600*24*30 #1 month
    ticketValidPeriod = 10  #10 sec
    counter = 0
    payAmount = 1e18

    saftV1 = BatchWorker.at('0x8A93e685c6B9dEE32f91A12d7655CA3B921EF14F')
    subscriptionManager = SubscriptionManagerV1.deploy(tx_params)
    wrapperTrustedV1 =  TrustedWrapper.at('0xD477cB49576DabFA073519EE91cf310319ee958E')

    

    #make settings of contracts
    saftV1.setTrustedWrapper(wrapperTrustedV1.address, tx_params)
    subscriptionManager.setAgentStatus(saftV1.address, True, {"from": accounts[0]})

    #make settings of subscription
    subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
    call_amount = 1e18
    payOption = [(niftsy20.address, payAmount), (dai.address, 2*payAmount)]
    services = [0]
    subscriptionManager.addTarif((subscriptionType, payOption, services), {"from": accounts[0]})

    #make settings of manager
    subscriptionManager.setMainWrapper(wrapperTrustedV1, {"from": accounts[0]})
    saftV1.setSubscriptionManager(subscriptionManager.address, {"from": accounts[0]})


    if  web3.eth.chainId in [1,4,5, 137, 43114]:
        SubscriptionManagerV1.publish_source(subscriptionManager);

    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("subscriptionManager = SubscriptionManagerV1.at('{}')".format(subscriptionManager.address))
    

    #rinkeby 
    '''saftV1 = BatchWorker.at('0x5a5e87171f7bD5639fe2D52d5D62449c3f606e82')
    techERC20 = TechTokenV1.at('0xD0e558D267EfF3CD6F1606e31C1a455647C4D69F')
    wrapperTrustedV1 = TrustedWrapper.at('0x5e6eF1a7cEAf72c73D8673948194d625b787452b')
    wnft1155 = EnvelopwNFT1155.at('0x1b0CFfc3b108Bb6544708dF3be5ea24709455251')
    wnft721 = EnvelopwNFT721.at('0xc1d74221320be821a5BBBD684d2F1F7332daAD65')
    whitelist = AdvancedWhiteList.at('0x6bD6568BB566fFD1d4a32c3AB5c1231621ab4B87')'''

    #goerli
    #subscriptionManager = SubscriptionManagerV1.at('0x0c7A985fe4064A441CEeFBF878b21fba6c55500b')


