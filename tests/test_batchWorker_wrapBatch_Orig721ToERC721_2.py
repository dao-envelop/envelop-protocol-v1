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

#reverts due to bad collateral data
def test_wrap(accounts, erc721mock, wrapperTrustedV1, dai, weth, wnft721ForwrapperTrustedV1, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3


    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    #erc721mock.transferFrom(accounts[1], accounts[0], ORIGINAL_NFT_IDs[0], {"from": accounts[1]} )
    for i in range(4):
        erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[i+1], {"from": accounts[0]} )
    

    if (wrapperTrustedV1.lastWNFTId(out_type)[1] == 0):
        wrapperTrustedV1.setWNFTId(out_type, wnft721ForwrapperTrustedV1.address, 0, {'from':accounts[0]})

    #add whiteList
    wrapperTrustedV1.setWhiteList(whiteListsForTrustedWrapper.address, {"from": accounts[0]})

    #add tokens in whiteList (dai and niftsy). Weth is NOT in whiteList
    wl_data = (True, True, False, techERC20ForSaftV1.address)
    whiteListsForTrustedWrapper.setWLItem((2, dai.address), wl_data, {"from": accounts[0]})
    whiteListsForTrustedWrapper.setWLItem((2, niftsy20.address), wl_data, {"from": accounts[0]})


    token_property = (in_type, erc721mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)

    for i in range(5):
        erc721mock.approve(wrapperTrustedV1, ORIGINAL_NFT_IDs[i], {"from": accounts[1]})
        
    dai_amount = 0
    weth_amount = 0
    inDataS = []
    receiverS = []
    fee = [('0x00', transfer_fee_amount, niftsy20.address)]
    lock = [('0x0', chain.time() + 100)]
    royalty = [(accounts[9].address, 2000), (wrapperTrustedV1.address, 8000)]
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

        dai_amount = dai_amount + Wei(call_amount)
        weth_amount = weth_amount + Wei(2*call_amount)

        receiverS.append(accounts[i].address)

    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = ((1, zero_address), 0, 1e18)
    collateralS = [eth_data, dai_data, weth_data]
    dai.approve(wrapperTrustedV1.address, dai_amount, {"from": accounts[1]})
    weth.approve(wrapperTrustedV1.address, weth_amount, {"from": accounts[1]})

    #set wrapper for batchWorker
    saftV1.setTrustedWrapper(wrapperTrustedV1, {"from": accounts[0]})

    #wrap batch
    with reverts("ERC20: transfer amount exceeds balance"):
        tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[1], "value": len(ORIGINAL_NFT_IDs)*eth_amount})

    #decrease allowance
    dai.approve(wrapperTrustedV1.address, 0, {"from": accounts[1]})
    weth.approve(wrapperTrustedV1.address, 0, {"from": accounts[1]})
    
    with reverts("ERC20: insufficient allowance"):
        tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[1], "value": len(ORIGINAL_NFT_IDs)*eth_amount})

    #does not own original tokens
    with reverts(''):
        tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[0], "value": len(ORIGINAL_NFT_IDs)*eth_amount})

    collateralS = [((1, zero_address), 0, 2)]
    with reverts("Native amount check failed"):
        tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[1], "value": '9 wei'})

    with reverts("Native amount check failed"):
        tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[1], "value": '11 wei'})

    collateralS = [((1, zero_address), 0, 11)]
    tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[1], "value": '55 wei'})

