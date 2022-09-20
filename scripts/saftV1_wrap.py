import pytest
import logging
from brownie import *
LOGGER = logging.getLogger(__name__)
from web3 import Web3

accounts.load('secret2')

ORIGINAL_NFT_IDs = []
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = 1e10
transfer_fee_amount = 100

def main():
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3

    saftV1 = BatchWorker.at('0x5a5e87171f7bD5639fe2D52d5D62449c3f606e82')
    techERC20 = TechTokenV1.at('0xD0e558D267EfF3CD6F1606e31C1a455647C4D69F')
    wrapperTrustedV1 = TrustedWrapper.at('0x5e6eF1a7cEAf72c73D8673948194d625b787452b')
    wnft1155 = EnvelopwNFT1155.at('0x1b0CFfc3b108Bb6544708dF3be5ea24709455251')
    wnft721 = EnvelopwNFT721.at('0xc1d74221320be821a5BBBD684d2F1F7332daAD65')
    whitelist = AdvancedWhiteList.at('0x6bD6568BB566fFD1d4a32c3AB5c1231621ab4B87')
    niftsy20 = Niftsy.at('0x3125B3b583D576d86dBD38431C937F957B94B47d')
    origNFT = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')

    if web3.eth.chainId in  [1,4]:
        tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

    ORIGINAL_NFT_IDs = [266, 267, 268, 269, 270]
    
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



    