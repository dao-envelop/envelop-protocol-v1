import pytest
import logging
from brownie import chain, Wei
LOGGER = logging.getLogger(__name__)

zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"


def makeNFTForTest721(accounts, erc721mock, original_nft_ids):
    [erc721mock.mint(x, {'from':accounts[0]})  for x in original_nft_ids]
    erc721mock.transferFrom(accounts[0], accounts[1], original_nft_ids[0], {'from':accounts[0]})

def makeNFTForTest1155(accounts, erc1155mock, original_nft_ids, amount):
    [erc1155mock.mint(accounts[0], x, amount, {'from':accounts[0]})  for x in original_nft_ids]
    erc1155mock.safeTransferFrom(accounts[0], accounts[1], original_nft_ids[0], amount, "", {'from':accounts[0]})

################################## make wNFT WITH COLLATERAL ##################################
def makeFromERC1155ToERC1155(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20, ORIGINAL_NFT_ID, in_nft_amount, out_nft_amount, wrappFor):
    #make wrap NFT with determined collateral
    in_type = 4
    out_type = 4

    erc1155mock.setApprovalForAll(wrapper.address,True, {'from':accounts[1]})
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})
    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})

    erc1155_property = (in_type, erc1155mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    eth_property = (1, zero_address)

    erc1155_data = (erc1155_property, ORIGINAL_NFT_ID, in_nft_amount)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = (eth_property, 0, Wei(eth_amount))

    fee = []
    lock = []
    royalty = []

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
    #make wrap NFT with determined collateral
    in_type = 3
    out_type = 3

    erc721mock.setApprovalForAll(wrapper.address, True, {'from':accounts[1]})
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
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

    fee = []
    lock = []
    royalty = []

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

def makeFromERC721ToERC1155(accounts, erc721mock, wrapper, dai, weth, wnft1155, niftsy20, ORIGINAL_NFT_ID, out_nft_amount, wrappFor, check_mode):
    #make wrap NFT with determined collateral
    in_type = 3
    out_type = 4

    erc721mock.setApprovalForAll(wrapper.address, True, {'from':accounts[1]})
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})

    erc721_property = (in_type, erc721mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    eth_property = (1, zero_address)

    erc721_data = (erc721_property, ORIGINAL_NFT_ID, 1)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = (eth_property, 0, Wei(eth_amount))

    fee = []
    lock = []
    royalty = []

    wNFT = ( erc721_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    wrapper.wrap(wNFT, [dai_data, weth_data, eth_data], wrappFor, {"from": accounts[1], "value": eth_amount})

    #checks
    if (check_mode == True):
        assert wrapper.balance() == eth_amount
        assert dai.balanceOf(wrapper) == call_amount
        assert weth.balanceOf(wrapper) == 2*call_amount
        assert erc721mock.ownerOf(ORIGINAL_NFT_ID) == wrapper.address
        assert wnft1155.balanceOf(accounts[3].address,wrapper.lastWNFTId(out_type)[1]) == out_nft_amount
        assert wnft1155.totalSupply(wrapper.lastWNFTId(out_type)[1]) == out_nft_amount

        wTokenId = wrapper.lastWNFTId(out_type)[1]
        wNFT = wrapper.getWrappedToken(wnft1155, wTokenId)
        #logging.info(wNFT)
        assert wNFT[0] == erc721_data
        assert wNFT[1] == [eth_data, dai_data, weth_data]
        assert wNFT[2] == accounts[2]
        assert wNFT[3] == fee
        assert wNFT[4] == lock
        assert wNFT[5] == royalty
        assert wNFT[6] == '0x0' 

    return wrapper.lastWNFTId(out_type)[1]

def makeFromERC1155ToERC721(accounts, erc1155mock, wrapper, dai, weth, wnft721, niftsy20, ORIGINAL_NFT_ID, in_nft_amount, wrappFor, check_mode):
    #make wrap NFT with determined collateral
    in_type = 4
    out_type = 3

    erc1155mock.setApprovalForAll(wrapper.address,True, {'from':accounts[1]})
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

    erc1155_property = (in_type, erc1155mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    eth_property = (1, zero_address)

    erc1155_data = (erc1155_property, ORIGINAL_NFT_ID, in_nft_amount)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = (eth_property, 0, Wei(eth_amount))

    fee = []
    lock = []
    royalty = []

    wNFT = ( erc1155_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    wrapper.wrap(wNFT, [dai_data, weth_data, eth_data], wrappFor, {"from": accounts[1], "value": eth_amount})

    #checks
    if (check_mode == True):
        assert wrapper.balance() == eth_amount
        assert dai.balanceOf(wrapper) == call_amount
        assert weth.balanceOf(wrapper) == 2*call_amount
        assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_ID) == in_nft_amount
        assert wnft721.ownerOf(wrapper.lastWNFTId(out_type)[1]) == accounts[3].address
        assert wnft721.totalSupply() == 1

        wTokenId = wrapper.lastWNFTId(out_type)[1]
        wNFT = wrapper.getWrappedToken(wnft721, wTokenId)
        #logging.info(wNFT)
        assert wNFT[0] == erc1155_data
        assert wNFT[1] == [eth_data, dai_data, weth_data]
        assert wNFT[2] == accounts[2]
        assert wNFT[3] == fee
        assert wNFT[4] == lock
        assert wNFT[5] == royalty
        assert wNFT[6] == '0x0' 

    return wrapper.lastWNFTId(out_type)[1]

################################## make wNFT WITHOUT COLLATERAL ##################################
def makeFromERC1155ToERC1155WithoutCollateral(accounts, erc1155mock, wrapper, wnft1155, niftsy20, ORIGINAL_NFT_ID, in_nft_amount, out_nft_amount, wrappFor):
    in_type = 4
    out_type = 4

    erc1155mock.setApprovalForAll(wrapper.address,True, {'from':accounts[1]})

    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})

    erc1155_property = (in_type, erc1155mock.address)

    erc1155_data = (erc1155_property, ORIGINAL_NFT_ID, in_nft_amount)
    
    fee = []
    lock = []
    royalty = []

    wNFT = ( erc1155_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    wrapper.wrap(wNFT, [], wrappFor, {"from": accounts[1]})
    return wrapper.lastWNFTId(out_type)[1]

def makeFromERC721ToERC721WithoutCollateral(accounts, erc721mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_ID, wrappFor):
    in_type = 3
    out_type = 3

    erc721mock.setApprovalForAll(wrapper.address, True, {'from':accounts[1]})
    
    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

    erc721_property = (in_type, erc721mock.address)
    
    erc721_data = (erc721_property, ORIGINAL_NFT_ID, 1)

    fee = []
    lock = []
    royalty = []

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


    wrapper.wrap(wNFT, [], wrappFor, {"from": accounts[1]})
    return wrapper.lastWNFTId(out_type)[1]

def makeFromERC721ToERC1155WithoutCollateral(accounts, erc721mock, wrapper, wnft1155, niftsy20, ORIGINAL_NFT_ID, out_nft_amount, wrappFor, check_mode):
    #make wrap NFT with determined collateral
    in_type = 3
    out_type = 4

    erc721mock.setApprovalForAll(wrapper.address, True, {'from':accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})

    erc721_property = (in_type, erc721mock.address)

    erc721_data = (erc721_property, ORIGINAL_NFT_ID, 1)

    fee = []
    lock = []
    royalty = []

    wNFT = ( erc721_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    wrapper.wrap(wNFT, [], wrappFor, {"from": accounts[1]})

    #checks
    if (check_mode == True):
        assert erc721mock.ownerOf(ORIGINAL_NFT_ID) == wrapper.address
        assert wnft1155.balanceOf(accounts[3].address,wrapper.lastWNFTId(out_type)[1]) == out_nft_amount
        assert wnft1155.totalSupply(wrapper.lastWNFTId(out_type)[1]) == out_nft_amount

        wTokenId = wrapper.lastWNFTId(out_type)[1]
        wNFT = wrapper.getWrappedToken(wnft1155, wTokenId)
        #logging.info(wNFT)
        assert wNFT[0] == erc721_data
        assert wNFT[1] == []
        assert wNFT[2] == accounts[2]
        assert wNFT[3] == fee
        assert wNFT[4] == lock
        assert wNFT[5] == royalty
        assert wNFT[6] == '0x0' 

    return wrapper.lastWNFTId(out_type)[1]

def makeFromERC1155ToERC721WithoutCollateral(accounts, erc1155mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_ID, in_nft_amount, wrappFor, check_mode):
    #make wrap NFT with determined collateral
    in_type = 4
    out_type = 3

    erc1155mock.setApprovalForAll(wrapper.address,True, {'from':accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

    erc1155_property = (in_type, erc1155mock.address)

    erc1155_data = (erc1155_property, ORIGINAL_NFT_ID, in_nft_amount)

    fee = []
    lock = []
    royalty = []

    wNFT = ( erc1155_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    wrapper.wrap(wNFT, [], wrappFor, {"from": accounts[1]})

    #checks
    if (check_mode == True):
        assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_ID) == in_nft_amount
        assert wnft721.ownerOf(wrapper.lastWNFTId(out_type)[1]) == accounts[3].address
        assert wnft721.totalSupply() == 1

        wTokenId = wrapper.lastWNFTId(out_type)[1]
        wNFT = wrapper.getWrappedToken(wnft721, wTokenId)
        #logging.info(wNFT)
        assert wNFT[0] == erc1155_data
        assert wNFT[1] == []
        assert wNFT[2] == accounts[2]
        assert wNFT[3] == fee
        assert wNFT[4] == lock
        assert wNFT[5] == royalty
        assert wNFT[6] == '0x0' 

    return wrapper.lastWNFTId(out_type)[1]