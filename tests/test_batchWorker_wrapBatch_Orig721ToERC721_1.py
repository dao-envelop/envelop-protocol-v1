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


#send in wrapping time more or less eth than in collateral's array
def test_wrap(accounts, erc721mock, wrapperTrustedV1, dai, weth, wnft721, niftsy20, saftV1, whiteListsForTrustedWrapper, techERC20ForSaftV1):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3


    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.transferFrom(accounts[1], accounts[0], ORIGINAL_NFT_IDs[0], {"from": accounts[1]} )
    

    if (wrapperTrustedV1.lastWNFTId(out_type)[1] == 0):
        wrapperTrustedV1.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperTrustedV1.address, {"from": accounts[0]})

    #add whiteList
    wrapperTrustedV1.setWhiteList(whiteListsForTrustedWrapper.address, {"from": accounts[0]})

    #add tokens in whiteList (dai and niftsy). Weth is NOT in whiteList
    wl_data = (True, True, False, techERC20ForSaftV1.address)
    whiteListsForTrustedWrapper.setWLItem((2, dai.address), wl_data, {"from": accounts[0]})
    whiteListsForTrustedWrapper.setWLItem((2, niftsy20.address), wl_data, {"from": accounts[0]})


    token_property = (in_type, erc721mock.address)

    for i in range(5):
        erc721mock.approve(wrapperTrustedV1, ORIGINAL_NFT_IDs[i], {"from": accounts[0]})
        

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

        receiverS.append(accounts[i].address)

    eth_data = ((1, zero_address), 0, 1e18)
    collateralS = [eth_data]

    #set wrapper for batchWorker
    saftV1.setTrustedWrapper(wrapperTrustedV1, {"from": accounts[0]})

    #wrap batch
    with reverts("Native amount check failed"):
        tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[0], "value": (len(ORIGINAL_NFT_IDs)+1)*eth_amount})

    with reverts("Native amount check failed"):
        tx = saftV1.wrapBatch(inDataS, collateralS, receiverS, {"from": accounts[0], "value": (len(ORIGINAL_NFT_IDs)-1)*eth_amount})
    

