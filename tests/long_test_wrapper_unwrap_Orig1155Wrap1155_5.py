import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155

zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"

def test_unwrap(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20, erc1155mock1, erc721mock1):
    #make wrap NFT with empty
    in_type = 4
    out_type = 4
    in_nft_amount = 3
    out_nft_amount = 5
    coll_amount = 2

    ORIGINAL_NFT_IDs = []
    i=1
    while i<251:
        ORIGINAL_NFT_IDs.append(i)
        i+=1



    #wrap ERC1155 token. Contract of token change the balance for reciever. Token id 0
    erc1155mock.mint(accounts[1], 0, in_nft_amount, {"from": accounts[1]})
    erc1155mock.setApprovalForAll(wrapper.address, True, {"from": accounts[1]})

    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

    #make 721 for collateral - normal token
    makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
    erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})
    i = 1
    while i < 126:
        erc721mock1.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[i], {"from": accounts[0]})
        erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[i], {"from": accounts[1]})
        #logging.info(i)
        i += 1

    #make 1155 for collateral - normal token
    makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock1.setApprovalForAll(wrapper.address,True, {"from": accounts[1]})

    i = 1
    while i < 126:
        erc1155mock1.safeTransferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[i], in_nft_amount, "", {"from": accounts[0]})
        #logging.info(i)
        i += 1

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})

    token_property = (in_type, erc1155mock)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    erc721_property = (3, erc721mock1.address)
    erc1155_property = (4, erc1155mock1.address)

    token_data = (token_property, 0, coll_amount)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))

    collateral = []
    collateral.append(dai_data)
    collateral.append(weth_data)

    i = 0
    while i < 10:
        collateral.append((erc721_property, ORIGINAL_NFT_IDs[i], 0))
        i += 1
        #logging.info(i)

    i = 0
    while i < 10:
        collateral.append((erc1155_property, ORIGINAL_NFT_IDs[i], in_nft_amount))
        i += 1
        #logging.info(i)


    fee = []
    lock = []
    royalty = []

    wNFT = (token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )

    
    wrapper.wrap(wNFT, collateral, accounts[3], {"from": accounts[1]})
    #logging.info (collateral)
    wTokenId = wrapper.lastWNFTId(out_type)[1]

    i= 10
    while i< 90:
        wrapper.addCollateral(wnft1155.address, wTokenId, [(erc721_property, ORIGINAL_NFT_IDs[i], 0)], {"from": accounts[1]})
        wrapper.addCollateral(wnft1155.address, wTokenId, [(erc1155_property, ORIGINAL_NFT_IDs[i], in_nft_amount)], {"from": accounts[1]})
        logging.info(i)
        i +=1

    logging.info("finish of addCollateral")

    tx= wrapper.unWrap(out_type, wnft1155.address, wTokenId, {"from": accounts[3]})
    #logging.info(tx.events['PartialUnWrapp'])
