import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest1155, makeNFTForTest721
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 4
out_type = 4
in_nft_amount = 3
out_nft_amount = 5
transfer_fee_amount = 100


#checks
def test_transfer(accounts, erc1155mock, erc721mock,  wrapper, dai, weth, wnft1155, niftsy20, whiteLists, techERC20, wrapperChecker, wnft1155_1):

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.setApprovalForAll(wrapper.address, True, {"from": accounts[1]})

    #make 1155 token for wrapping
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapper.address, True, {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})

    token_property = (3, erc1155mock)
    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    
    #################################
    fee = []
    lock = []
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[1])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[1])[1]).find("Original token is not ERC721 and not ERC1155", 0)!= -1

    token_property = (4, erc721mock)
    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[1])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[1])[1]).find("Original token is not ERC721 and not ERC1155", 0)!= -1

    #erc20
    token_property = (4, dai.address)
    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[1])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[1])[1]).find("Original token is not ERC721 and not ERC1155", 0)!= -1

    token_property = (4, erc1155mock.address)
    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[1])[0] == True
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[1])[1]).find("Success", 0)!= -1


    token_property = (3, erc721mock.address)
    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[1])[0] == True
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[1])[1]).find("Success", 0)!= -1

    token_property = (3, erc721mock.address)
    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    #check collateral in wrapping
    collateral = [((3, erc1155mock.address), ORIGINAL_NFT_IDs[1], 0)]
    assert wrapperChecker.checkWrap(wNFT, collateral, accounts[1])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, collateral, accounts[1])[1]).find("Collateral token is not ERC721 and not ERC1155", 0)!= -1

    collateral = [((4, erc721mock.address), ORIGINAL_NFT_IDs[1], in_nft_amount)]
    assert wrapperChecker.checkWrap(wNFT, collateral, accounts[1])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, collateral, accounts[1])[1]).find("Collateral token is not ERC721 and not ERC1155", 0)!= -1

    #erc20
    collateral = [((4, dai.address), ORIGINAL_NFT_IDs[1], in_nft_amount)]
    assert wrapperChecker.checkWrap(wNFT, collateral, accounts[1])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, collateral, accounts[1])[1]).find("Collateral token is not ERC721 and not ERC1155", 0)!= -1
    
    collateral = [((4, erc1155mock), ORIGINAL_NFT_IDs[1], in_nft_amount), ((4, erc721mock), ORIGINAL_NFT_IDs[1], in_nft_amount), ((3, erc721mock), ORIGINAL_NFT_IDs[1], 0)]
    assert wrapperChecker.checkWrap(wNFT, collateral, accounts[1])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, collateral, accounts[1])[1]).find("Collateral token is not ERC721 and not ERC1155", 0)!= -1

    collateral = [((4, erc1155mock), ORIGINAL_NFT_IDs[1], in_nft_amount), ((3, erc721mock), ORIGINAL_NFT_IDs[1], 0)]
    assert wrapperChecker.checkWrap(wNFT, collateral, accounts[1])[0] == True
    assert (wrapperChecker.checkWrap(wNFT, collateral, accounts[1])[1]).find("Success", 0)!= -1

    
    #check collateral in addCollateral
    collateral = [((3, erc1155mock.address), ORIGINAL_NFT_IDs[1], 0)]
    assert wrapperChecker.checkAddCollateral(wnft1155.address, 1, collateral)[0] == False
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, 1, collateral)[1]).find("Collateral token is not ERC721 and not ERC1155", 0)!= -1

    collateral = [((4, erc721mock.address), ORIGINAL_NFT_IDs[1], in_nft_amount)]
    assert wrapperChecker.checkAddCollateral(wnft1155.address, 1, collateral)[0] == False
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, 1, collateral)[1]).find("Collateral token is not ERC721 and not ERC1155", 0)!= -1

    #erc20
    collateral = [((4, dai.address), ORIGINAL_NFT_IDs[1], in_nft_amount)]
    assert wrapperChecker.checkAddCollateral(wnft1155.address, 1, collateral)[0] == False
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, 1, collateral)[1]).find("Collateral token is not ERC721 and not ERC1155", 0)!= -1
    
    collateral = [((4, erc1155mock), ORIGINAL_NFT_IDs[1], in_nft_amount), ((4, erc721mock), ORIGINAL_NFT_IDs[1], in_nft_amount), ((3, erc721mock), ORIGINAL_NFT_IDs[1], 0)]
    assert wrapperChecker.checkAddCollateral(wnft1155.address, 1, collateral)[0] == False
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, 1, collateral)[1]).find("Collateral token is not ERC721 and not ERC1155", 0)!= -1

    collateral = [((4, erc1155mock), ORIGINAL_NFT_IDs[1], in_nft_amount), ((3, erc721mock), ORIGINAL_NFT_IDs[1], 0)]
    assert wrapperChecker.checkAddCollateral(wnft1155.address, 1, collateral)[0] == True
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, 1, collateral)[1]).find("Success", 0)!= -1




