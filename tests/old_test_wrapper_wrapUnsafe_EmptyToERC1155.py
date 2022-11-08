import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

def test_unwrap(accounts, erc1155mock, wrapperTrusted, dai, weth, wnft1155, niftsy20, erc1155mock1, erc721mock1):
    #make wrap NFT with empty
    
    in_type = 0
    out_type = 4
    in_nft_amount = 3
    out_nft_amount = 5

    dai.approve(wrapperTrusted.address, call_amount, {'from':accounts[0]})
    weth.approve(wrapperTrusted.address, 2*call_amount, {'from':accounts[0]})

     #make 721 for collateral - normal token
    makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
    erc721mock1.transferFrom(accounts[1], accounts[0], ORIGINAL_NFT_IDs[0], {"from": accounts[1]})
    erc721mock1.approve(wrapperTrusted.address, ORIGINAL_NFT_IDs[0], {"from": accounts[0]})

    #make 1155 for collateral - normal token
    makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock1.setApprovalForAll(wrapperTrusted.address,True, {"from": accounts[0]})

    if (wrapperTrusted.lastWNFTId(out_type)[1] == 0):
        wrapperTrusted.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
    wnft1155.setMinterStatus(wrapperTrusted.address, {"from": accounts[0]})

    empty_property = (in_type, zero_address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    eth_property = (1, zero_address)
    erc721_property = (3, erc721mock1.address)
    erc1155_property = (4, erc1155mock1.address)

    empty_data = (empty_property, 0, 0)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = (eth_property, 0, Wei(eth_amount))
    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 0)
    erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], in_nft_amount)

    fee = []
    lock = [('0x0', chain.time() + 100), ('0x0', chain.time() + 200)]
    royalty = []

    wNFT = ( empty_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    with reverts("Only trusted address"):
        wrapperTrusted.wrapUnsafe(wNFT, [dai_data, weth_data, erc721_data, erc1155_data], accounts[3], {"from": accounts[1], "value": eth_amount})

    wrapperTrusted.wrapUnsafe(wNFT, [dai_data, weth_data, erc721_data, erc1155_data], accounts[3], {"from": accounts[0], "value": eth_amount})

    wTokenId = wrapperTrusted.lastWNFTId(out_type)[1]

    assert dai.balanceOf(wrapperTrusted.address) == call_amount
    assert weth.balanceOf(wrapperTrusted.address) == 2*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperTrusted.address
    assert erc1155mock1.balanceOf(wrapperTrusted.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert wrapperTrusted.balance() == eth_amount
    assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount


    '''
    eth_contract_balance = wrapperTrusted.balance()
    eth_acc_balance = accounts[3].balance()

    with reverts("TimeLock error"):
        wrapperTrusted.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]} )

    chain.sleep(250)
    chain.mine()

    wrapperTrusted.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]} )

    assert dai.balanceOf(accounts[3]) == call_amount
    assert weth.balanceOf(accounts[3]) == 2*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
    assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert wrapperTrusted.balance() == 0
    assert wnft1155.balanceOf(accounts[3], wTokenId) == 0
    assert accounts[3].balance() == eth_acc_balance + eth_contract_balance

    logging.info(wTokenId)


    ####################################################################again wrap and unwrap#################################################3
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapperTrusted.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapperTrusted.address, 2*call_amount, {'from':accounts[1]})

     #make 721 for collateral - normal token
    erc721mock1.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    erc721mock1.approve(wrapperTrusted.address, ORIGINAL_NFT_IDs[1], {"from": accounts[1]})

    #make 1155 for collateral - normal token
    erc1155mock1.safeTransferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], in_nft_amount, "", {"from": accounts[0]})

    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[1], 0)
    erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[1], in_nft_amount)
    lock = [('0x0', chain.time() + 100), ('0x0', chain.time() + 200)]

    wNFT = ( empty_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    wrapperTrusted.wrapUnsafe(wNFT, [dai_data, weth_data, erc721_data, erc1155_data], accounts[3], {"from": accounts[0], "value": eth_amount})
    wTokenId = wrapperTrusted.lastWNFTId(out_type)[1]
    logging.info(wTokenId)

    assert dai.balanceOf(wrapperTrusted.address) == call_amount
    assert weth.balanceOf(wrapperTrusted.address) == 2*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapperTrusted.address
    assert erc1155mock1.balanceOf(wrapperTrusted.address, ORIGINAL_NFT_IDs[1]) == in_nft_amount
    assert wrapperTrusted.balance() == eth_amount
    assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount



    eth_contract_balance = wrapperTrusted.balance()
    eth_acc_balance = accounts[3].balance()

    wnft1155.safeTransferFrom(accounts[3], accounts[4], wTokenId, 1, "", {"from": accounts[3]} )

    with reverts("ERC115 unwrap available only for all totalSupply"):
        wrapperTrusted.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]} )

    wnft1155.safeTransferFrom(accounts[4], accounts[3], wTokenId, 1, "", {"from": accounts[4]} )



    with reverts("TimeLock error"):
        wrapperTrusted.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]} )

    chain.sleep(250)
    chain.mine()
    
    wrapperTrusted.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]} )    

    assert dai.balanceOf(accounts[3]) == 2*call_amount
    assert weth.balanceOf(accounts[3]) == 4*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[3]
    assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[1]) == in_nft_amount
    assert wrapperTrusted.balance() == 0
    assert wnft1155.balanceOf(accounts[3], wTokenId) == 0
    assert accounts[3].balance() == eth_acc_balance + eth_contract_balance'''


