import pytest
import logging
from brownie import chain, Wei
LOGGER = logging.getLogger(__name__)

zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "4 ether"


def makeNFTForTest721(accounts, erc721mock, original_nft_ids):
    [erc721mock.mint(x, {'from':accounts[0]})  for x in original_nft_ids]
    erc721mock.transferFrom(accounts[0], accounts[1], original_nft_ids[0], {'from':accounts[0]})

def makeNFTForTest1155(accounts, erc1155mock, original_nft_ids, amount):
    [erc1155mock.mint(accounts[0], x, amount, {'from':accounts[0]})  for x in original_nft_ids]
    erc1155mock.safeTransferFrom(accounts[0], accounts[1], original_nft_ids[0], amount, "", {'from':accounts[0]})

def makeFromERC1155ToERC1155(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20, ORIGINAL_NFT_ID, in_nft_amount, out_nft_amount, wrappFor):
    in_type = 4
    out_type = 4

    erc1155mock.setApprovalForAll(wrapper.address,True, {'from':accounts[1]})
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})
    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

    wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})

    erc1155_property = (in_type, erc1155mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    eth_property = (1, zero_address)

    erc1155_data = (erc1155_property, ORIGINAL_NFT_ID, in_nft_amount)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = (eth_property, 0, Wei(eth_amount))

    fee = [('0x0', Wei(1e18), niftsy20.address)]
    lock = [('0x0', chain.time() + 10), ('0x0', chain.time() + 20)]
    royalty = [(accounts[1], 100), (accounts[2], 200)]

    wNFT = ( erc1155_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    wrapper.wrap(wNFT, [dai_data, weth_data, eth_data], wrappFor, {"from": accounts[1], "value": eth_amount})
    return wrapper.lastWNFTId(out_type)[1]

def makeFromERC721ToERC721(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, ORIGINAL_NFT_ID, wrappFor):
    in_type = 3
    out_type = 3

    erc721mock.setApprovalForAll(wrapper.address, True, {'from':accounts[1]})
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

    wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

    erc721_property = (in_type, erc721mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    eth_property = (1, zero_address)

    erc721_data = (erc721_property, ORIGINAL_NFT_ID, 1)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = (eth_property, 0, Wei(eth_amount))

    fee = [('0x0', Wei(1e18), niftsy20.address)]
    lock = [('0x0', chain.time() + 10), ('0x0', chain.time() + 20)]
    royalty = [(accounts[1], 100), (accounts[2], 200)]

    wNFT = ( erc721_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    assert erc721mock.ownerOf(ORIGINAL_NFT_ID) == accounts[1]
    assert erc721mock.isApprovedForAll(accounts[1], wrapper.address) == True


    wrapper.wrap(wNFT, [dai_data, weth_data, eth_data], wrappFor, {"from": accounts[1], "value": eth_amount})
    return wrapper.lastWNFTId(out_type)[1]