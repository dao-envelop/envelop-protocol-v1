import pytest
import logging
from brownie import *
LOGGER = logging.getLogger(__name__)
from web3 import Web3

accounts.load('secret2')

ORIGINAL_NFT_IDs = []
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = 1e8
transfer_fee_amount = 100
timelockPeriod = 3600*24*30 #1 month
ticketValidPeriod = 100  #100 sec
counter = 0
payAmount = 1e18

def main():
    #make wrap NFT with empty
    #account has subscription
    in_type = 3
    out_type = 3
    in_nft_amount = 3

    niftsy20 = TokenMock.at('0x376e8EA664c2E770E1C45ED423F62495cB63392D')
    origNFT = OrigNFT.at('0x69e8B95d034fdd102dE3006F3EbE3B619945242B')
    techERC20 = TechTokenV1.at('0x2b2ca6527aeb9ec416A909Ff9b6938E08eF0a45e')
    saftV1 = BatchWorker.at('0x8A93e685c6B9dEE32f91A12d7655CA3B921EF14F')
    subscriptionManager = SubscriptionManagerV1.at('0xAAA599Bf7AAeAEA2F0ef89dd9fE345187e61A650')
    wrapperTrustedV1 = TrustedWrapper.at('0xD477cB49576DabFA073519EE91cf310319ee958E')
    wnft1155 = EnvelopwNFT1155.at('0xA35769AeBE8b0F13c653F45c82667dAED078F8db')
    wnft721 = EnvelopwNFT721.at('0x3B47910b3aAbED960B1773dFE1DE299D51655720')
    whitelist = AdvancedWhiteList.at('0x37624e622e0931be99E4494F423eAA68F6FB72C1')


    if web3.eth.chainId in  [1,4,5]:
        tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

    #ORIGINAL_NFT_IDs = [266, 267, 268, 269, 270]

    #create allowance for subscription
    niftsy20.approve(subscriptionManager.address, payAmount, {"from": accounts[0]})

    #buy subscription
    tx = subscriptionManager.buySubscription(0,0, accounts[0], {"from": accounts[0]})
    
    #mint orig nft
    for i in range(5):
        tx = origNFT.mint(accounts[0], tx_params)
        ORIGINAL_NFT_IDs.append(tx.events['Transfer']['tokenId'])
        origNFT.approve(wrapperTrustedV1, tx.events['Transfer']['tokenId'], tx_params)

    print(ORIGINAL_NFT_IDs)

    token_property = (in_type, origNFT.address)
    niftsy_property = (2, niftsy20.address)
        
    niftsy_amount = 0
    inDataS = []
    receiverS = ['0x5992Fe461F81C8E0aFFA95b831E50e9b3854BA0E', 
                    '0xa11103Da33d2865C3B70947811b1436ea6Bb32eF', 
                    '0xbD7E5fB7525ED8583893ce1B1f93E21CC0cf02F6',
                    '0x989FA3062bc4329B2E3c5907c48Ea48a38437fB7',
                    '0xd7924834C7896f60c6b4F9ba7d98a36FE3c7af0f']
                    
    fee = [('0x00', transfer_fee_amount, niftsy20.address)]
    lock = [('0x0', chain.time() + 100)]
    royalty = [('0xABB923e03E1E354B4f1Ac7cBee37A4cC9D2519f1', 2000), (wrapperTrustedV1.address, 8000)]
    for i in range(5):

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

        niftsy_amount = niftsy_amount + Wei(call_amount)

    niftsy_data = (niftsy_property, 0, Wei(call_amount))
    eth_data = ((1, zero_address), 0, eth_amount)
    collateralS = [eth_data, niftsy_data]

    niftsy20.approve(wrapperTrustedV1.address, niftsy_amount, {"from": accounts[0]})
    
    #wrap batch
    tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[0], "value": len(ORIGINAL_NFT_IDs)*eth_amount, 'gas_price': "60 gwei"})
    
    print(tx.events)



    