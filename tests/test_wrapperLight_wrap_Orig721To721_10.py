import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

def test_unwrap(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20, erc1155mock1, erc721mock1):
    #make wrap NFT with empty
    in_type = 3
    out_type = 3
    in_nft_amount = 3

    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})
    niftsy20.transfer(accounts[1], 3*call_amount, {"from": accounts[0]})

    dai.approve(wrapperLight.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapperLight.address, 2*call_amount, {'from':accounts[1]})

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

     #make 721 for collateral - normal token
    makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
    erc721mock1.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    #make 1155 for collateral - normal token
    makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock1.setApprovalForAll(wrapperLight.address,True, {"from": accounts[1]})

    if (wrapperLight.lastWNFTId(out_type)[1] == 0):
        wrapperLight.setWNFTId(out_type, wnft721ForWrapperLightV1.address, 0, {'from':accounts[0]})

    token_property = (in_type, erc721mock)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    niftsy20_property = (2, niftsy20.address)
    eth_property = (1, zero_address)
    erc721_property = (3, erc721mock1.address)
    erc1155_property = (4, erc1155mock1.address)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    niftsy20_data = (niftsy20_property, 0, Wei(3*call_amount))
    eth_data = (eth_property, 0, Wei(eth_amount))
    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 0)
    erc1155_data = (erc1155_property, ORIGINAL_NFT_IDs[0], in_nft_amount)

    fee = []
    lock = [('0x0', chain.time() + 100), ('0x0', chain.time() + 200)]
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    with reverts("ERC20: insufficient allowance"):
        wrapperLight.wrap(wNFT, [niftsy20_data, dai_data, weth_data, erc721_data, erc1155_data], accounts[3], {"from": accounts[1], "value": eth_amount})
    with reverts("ERC20: insufficient allowance"):
        wrapperLight.wrap(wNFT, [ dai_data, weth_data, niftsy20_data, erc721_data, erc1155_data], accounts[3], {"from": accounts[1], "value": eth_amount})
    with reverts("ERC20: insufficient allowance"):
        wrapperLight.wrap(wNFT, [ dai_data, weth_data, erc721_data, erc1155_data, niftsy20_data], accounts[3], {"from": accounts[1], "value": eth_amount})
    

    niftsy20.approve(wrapperLight.address, 3*call_amount, {'from':accounts[1]})
    wrapperLight.wrap(wNFT, [ dai_data, weth_data, erc721_data, erc1155_data, niftsy20_data], accounts[3], {"from": accounts[1], "value": eth_amount})
    wTokenId = wrapperLight.lastWNFTId(out_type)[1]

    assert dai.balanceOf(wrapperLight.address) == call_amount
    assert weth.balanceOf(wrapperLight.address) == 2*call_amount
    assert niftsy20.balanceOf(wrapperLight.address) == 3*call_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
    assert erc1155mock1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert wrapperLight.balance() == eth_amount
    assert wnft721ForWrapperLightV1.ownerOf(wTokenId) == accounts[3]