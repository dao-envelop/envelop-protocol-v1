import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
transfer_fee_amount = 100

def test_unwrap(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20, erc1155mock1, erc721mock1):
    #make wrap NFT with empty
    in_type = 0
    out_type = 4
    in_nft_amount = 3
    out_nft_amount = 5

    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

     #make 721 for collateral - normal token
    makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
    erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    #make 1155 for collateral - normal token
    makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock1.setApprovalForAll(wrapper.address,True, {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})

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

    fee = [(Web3.toBytes(0x00), transfer_fee_amount, niftsy20.address)]
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

    wrapper.wrap(wNFT, [dai_data, weth_data, erc721_data, erc1155_data], accounts[3], {"from": accounts[1], "value": eth_amount})
    wTokenId = wrapper.lastWNFTId(out_type)[1]

    assert dai.balanceOf(wrapper.address) == call_amount
    assert weth.balanceOf(wrapper.address) == 2*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
    assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert wrapper.balance() == eth_amount
    assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount

    with reverts("ERC20: insufficient allowance"):
        wnft1155.safeTransferFrom(accounts[3], accounts[2], wTokenId,  out_nft_amount, "", {"from": accounts[3]})

    niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[3]})

    with reverts("ERC20: transfer amount exceeds balance"):
        wnft1155.safeTransferFrom(accounts[3], accounts[2], wTokenId, out_nft_amount, "", {"from": accounts[3]})

    niftsy20.transfer(accounts[3], transfer_fee_amount, {"from": accounts[0]})
    

    eth_contract_balance = wrapper.balance()
    eth_acc_balance = accounts[3].balance()

    with reverts("TimeLock error"):
        wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]} )

    chain.sleep(250)
    chain.mine()

    wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]} )

    assert dai.balanceOf(accounts[3]) == call_amount
    assert weth.balanceOf(accounts[3]) == 2*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
    assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert wrapper.balance() == 0
    assert wnft1155.balanceOf(accounts[3], wTokenId) == 0
    assert accounts[3].balance() == eth_acc_balance + eth_contract_balance

    logging.info(wTokenId)


    ####################################################################again wrap and unwrap#################################################3
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

     #make 721 for collateral - normal token
    erc721mock1.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {"from": accounts[1]})

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

    wrapper.wrap(wNFT, [dai_data, weth_data, erc721_data, erc1155_data], accounts[3], {"from": accounts[1], "value": eth_amount})
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    logging.info(wTokenId)

    assert dai.balanceOf(wrapper.address) == call_amount
    assert weth.balanceOf(wrapper.address) == 2*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapper.address
    assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[1]) == in_nft_amount
    assert wrapper.balance() == eth_amount
    assert wnft1155.balanceOf(accounts[3], wTokenId) == out_nft_amount



    eth_contract_balance = wrapper.balance()
    eth_acc_balance = accounts[3].balance()

    wnft1155.safeTransferFrom(accounts[3], accounts[4], wTokenId, 1, "", {"from": accounts[3]} )

    with reverts("ERC115 unwrap available only for all totalSupply"):
        wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]} )


    niftsy20.approve(wrapper.address, transfer_fee_amount, {"from": accounts[4]})
    niftsy20.transfer(accounts[4], transfer_fee_amount, {"from": accounts[0]})
    wnft1155.safeTransferFrom(accounts[4], accounts[3], wTokenId, 1, "", {"from": accounts[4]} )



    with reverts("TimeLock error"):
        wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]} )

    chain.sleep(250)
    chain.mine()
    
    wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]} )    

    assert dai.balanceOf(accounts[3]) == 2*call_amount
    assert weth.balanceOf(accounts[3]) == 4*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[3]
    assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[1]) == in_nft_amount
    assert wrapper.balance() == 0
    assert wnft1155.balanceOf(accounts[3], wTokenId) == 0
    assert accounts[3].balance() == eth_acc_balance + eth_contract_balance


