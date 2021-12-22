import pytest
import logging
from brownie import chain, Wei
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "4 ether"

def test_unwrap(accounts, erc1155mock, wrapper, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1):
    #make wrap NFT with empty
    in_type = 0
    out_type = 3
    in_nft_amount = 3

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
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

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

    fee = [('0x0', Wei(1e18), niftsy20.address)]
    lock = [('0x0', chain.time() + 100), ('0x0', chain.time() + 200)]
    royalty = [(accounts[1], 100), (accounts[2], 200)]

    wNFT = ( empty_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    wrapper.wrap(wNFT, [dai_data, weth_data, erc721_data, erc1155_data], accounts[3], {"from": accounts[1], "value": eth_amount})
    wTokenId = wrapper.lastWNFTId(out_type)[1]

    assert dai.balanceOf(wrapper.address) == call_amount
    assert weth.balanceOf(wrapper.address) == 2*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
    assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert wrapper.balance() == eth_amount
    assert wnft721.ownerOf(wTokenId) == accounts[3]



    eth_contract_balance = wrapper.balance()
    eth_acc_balance = accounts[2].balance()

    wrapper.unWrap(out_type, wnft721.address, wTokenId, {"from": accounts[3]} )

    assert dai.balanceOf(accounts[2]) == call_amount
    assert weth.balanceOf(accounts[2]) == 2*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[2]
    assert erc1155mock1.balanceOf(accounts[2], ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert wrapper.balance() == 0
    assert wnft721.balanceOf(accounts[3]) == 0
    assert accounts[2].balance() == eth_acc_balance + eth_contract_balance

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

    wNFT = ( empty_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
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
    assert wnft721.ownerOf(wTokenId) == accounts[3]



    eth_contract_balance = wrapper.balance()
    eth_acc_balance = accounts[2].balance()


    wrapper.unWrap(out_type, wnft721.address, wTokenId, {"from": accounts[3]} )

    assert dai.balanceOf(accounts[2]) == 2*call_amount
    assert weth.balanceOf(accounts[2]) == 4*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[2]
    assert erc1155mock1.balanceOf(accounts[2], ORIGINAL_NFT_IDs[1]) == in_nft_amount
    assert wrapper.balance() == 0
    assert wnft721.balanceOf(accounts[3]) == 0
    assert accounts[2].balance() == eth_acc_balance + eth_contract_balance


