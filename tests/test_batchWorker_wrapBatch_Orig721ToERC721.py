import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222, 33333, 44444]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
transfer_fee_amount = 100

def test_wrap(accounts, erc721mock, wrapperTrustedV1, dai, weth, wnft721, niftsy20, saftV1):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3

    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapperTrustedV1.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapperTrustedV1.address, 2*call_amount, {'from':accounts[1]})

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.transferFrom(accounts[1], accounts[0], ORIGINAL_NFT_IDs[0], {"from": accounts[1]} )
    

    if (wrapperTrustedV1.lastWNFTId(out_type)[1] == 0):
        wrapperTrustedV1.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperTrustedV1.address, {"from": accounts[0]})

    token_property = (in_type, erc721mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)

    for i in range(5):
        erc721mock.approve(wrapperTrustedV1, ORIGINAL_NFT_IDs[i], {"from": accounts[0]})
        
    dai_amount = 0
    weth_amount = 0
    inDataS = []
    receiverS = []
    for i in range(5):

        token_data = (token_property, ORIGINAL_NFT_IDs[i], 0)
        dai_data = (dai_property, 0, Wei(call_amount))
        weth_data = (weth_property, 0, Wei(2*call_amount))
        
        
        fee = [] #[(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
        lock = [] #[('0x0', chain.time() + 100)]
        royalty = [] #[(accounts[9].address, 2000), (wrapperTrustedV1.address, 8000)]

        wNFT = ( token_data,
            zero_address,
            fee,
            lock,
            royalty,
            out_type,
            0,
            '0'
            )
        inDataS.append(wNFT)
        logging.info(inDataS)

        dai_amount = + Wei(call_amount)
        weth_amount = + Wei(2*call_amount)

        receiverS.append(accounts[i])
        logging.info(receiverS)


    collateralS = [((1, zero_address), 0, 1e18)]
    #collateralS = [dai_data, weth_data]
    dai.approve(wrapperTrustedV1.address, dai_amount, {"from": accounts[0]})
    weth.approve(wrapperTrustedV1.address, weth_amount, {"from": accounts[0]})

    #set wrapper for batchWorker
    saftV1.setTrustedWrapper(wrapperTrustedV1, {"from": accounts[0]})
    tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[0], "value": "1 ether"})
    logging.info(inDataS)
    logging.info(collateralS)
    logging.info(receiverS)
    
    
    #wrapperTrustedV1.wrapUnsafe(wNFT, collateralS, accounts[0], {"from": accounts[0], "value": "1 ether"})

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperTrustedV1.address

    wTokenId = wrapperTrustedV1.lastWNFTId(out_type)[1]
    logging.info(wTokenId)

    #assert dai.balanceOf(wrapperTrustedV1.address) == call_amount
    #assert weth.balanceOf(wrapperTrustedV1.address) == 2*call_amount
    #assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperTrustedV1.address
    #assert wrapperTrustedV1.balance() == eth_amount
    assert wnft721.ownerOf(1) == accounts[0]

    #wrapperTrustedV1.transferIn(((1, zero_address), 0, 1e18), accounts[0], wrapperTrustedV1.address, {"from": accounts[0], "value": "1 ether"})
    
    logging.info(saftV1.balance())
    logging.info(wrapperTrustedV1.balance())
    logging.info(accounts[0].balance())

    