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
    whiteListsForTrustedWrapper.setWLItem((2, weth.address), wl_data, {"from": accounts[0]})
    whiteListsForTrustedWrapper.setWLItem((2, niftsy20.address), wl_data, {"from": accounts[0]})


    token_property = (in_type, erc721mock.address)
    
    for i in range(len(ORIGINAL_NFT_IDs)):
        erc721mock.approve(wrapperTrustedV1, ORIGINAL_NFT_IDs[i], {"from": accounts[0]})
        
    
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

        receiverS.append(accounts[i].address)


    #set wrapper for batchWorker
    saftV1.setTrustedWrapper(wrapperTrustedV1, {"from": accounts[0]})

    #wrap batch without collateral
    tx = saftV1.wrapBatch(inDataS, [], receiverS, {"from": accounts[0]})

    #add collateral using batch
    dai_amount = 0
    weth_amount = 0
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)

    wnftContracts = []
    wnftIDs = []
    for i in range(len(ORIGINAL_NFT_IDs)):
        wnftContracts.append(wnft721.address)
        wnftIDs.append(wrapperTrustedV1.lastWNFTId(out_type)[1] - i)

        dai_amount = dai_amount + Wei(call_amount)
        weth_amount = weth_amount + Wei(2*call_amount)

    logging.info(wnftIDs)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))

    collateralS = [dai_data, weth_data]
    # dai.approve(wrapperTrustedV1.address, dai_amount, {"from": accounts[0]})
    # weth.approve(wrapperTrustedV1.address, weth_amount, {"from": accounts[0]})
    
    dai.approve(saftV1.address, dai_amount, {"from": accounts[0]})
    weth.approve(saftV1.address, weth_amount, {"from": accounts[0]})


    tx = saftV1.addCollateralBatch(wnftContracts, wnftIDs, collateralS, {"from": accounts[0], "value": len(ORIGINAL_NFT_IDs)*eth_amount})

    '''
    #check CollateralAdded events
    for i in range(len(tx.events['CollateralAdded'])):
        assert tx.events['CollateralAdded'][i]['wrappedAddress'] == wnft721.address
        assert tx.events['CollateralAdded'][i]['wrappedId'] in [1,2,3,4,5]
        if tx.events['CollateralAdded'][i]['collateralAddress'] == zero_address:
            assert tx.events['CollateralAdded'][i]['collateralBalance'] == eth_amount
            assert tx.events['CollateralAdded'][i]['assetType'] == 1
        elif tx.events['CollateralAdded'][i]['collateralAddress'] == dai.address:
            assert tx.events['CollateralAdded'][i]['collateralBalance'] == call_amount
            assert tx.events['CollateralAdded'][i]['assetType'] == 2
        elif tx.events['CollateralAdded'][i]['collateralAddress'] == weth.address:
            assert tx.events['CollateralAdded'][i]['collateralBalance'] == 2*call_amount
            assert tx.events['CollateralAdded'][i]['assetType'] == 2
        else:
            assert True == False
        assert tx.events['CollateralAdded'][i]['collateralTokenId'] == 0
    
    for i in range(len(ORIGINAL_NFT_IDs)):
        #check collateral in wnft
        assert wnft721.wnftInfo(i+1)[1][0] == eth_data
        assert wnft721.wnftInfo(i+1)[1][1] == dai_data
        assert wnft721.wnftInfo(i+1)[1][2] == weth_data

    assert dai.balanceOf(wrapperTrustedV1.address) == call_amount*len(ORIGINAL_NFT_IDs)
    assert weth.balanceOf(wrapperTrustedV1.address) == 2*call_amount*len(ORIGINAL_NFT_IDs)
    assert wrapperTrustedV1.balance() == eth_amount*len(ORIGINAL_NFT_IDs)

    
    #try to add collateral (allowed and not allowed tokens)
    with reverts("WL:Some assets are not enabled for collateral"):
        wrapperTrustedV1.addCollateral(wnft721.address, 1, [weth_data], {"from": accounts[0]})

    for i in range(len(ORIGINAL_NFT_IDs)):
        dai.approve(wrapperTrustedV1.address, call_amount, {"from": accounts[0]})
        wrapperTrustedV1.addCollateral(wnft721.address, i+1, [dai_data], {"from": accounts[0]})

    assert dai.balanceOf(wrapperTrustedV1.address) == 2*call_amount * len(ORIGINAL_NFT_IDs)        

    #try to unwrap - failed. Timelock

    with reverts("TimeLock error"):
        wrapperTrustedV1.unWrap(wnft721.address, 1, {"from": accounts[0]})

    chain.sleep(100)
    chain.mine()

    before_balance_acc_dai = dai.balanceOf(accounts[0])
    before_balance_acc_weth = weth.balanceOf(accounts[0])
    before_balance_acc_niftsy = niftsy20.balanceOf(accounts[0])
    before_balance_acc_eth = accounts[0].balance()

    #check balances after UNWRAP
    for i in range(len(ORIGINAL_NFT_IDs)):
        wrapperTrustedV1.unWrap(wnft721.address, i+1, {"from": accounts[0]})
        assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[i]) == accounts[0]

    assert dai.balanceOf(accounts[0]) == before_balance_acc_dai + 2*call_amount * len(ORIGINAL_NFT_IDs)
    assert weth.balanceOf(accounts[0]) == before_balance_acc_weth + 2*call_amount * len(ORIGINAL_NFT_IDs)
    assert niftsy20.balanceOf(accounts[0]) == before_balance_acc_niftsy + (transfer_fee_amount*royalty[1][1]/10000) * (len(ORIGINAL_NFT_IDs)-1)
    assert accounts[0].balance() == before_balance_acc_eth + eth_amount*len(ORIGINAL_NFT_IDs)
    assert dai.balanceOf(wrapperTrustedV1.address) == 0
    assert weth.balanceOf(wrapperTrustedV1.address) == 0
    assert wrapperTrustedV1.balance() == 0'''