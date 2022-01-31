import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest1155
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

    #make 1155 token for wrapping
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapper.address, True, {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})

    
   #################################
    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)

    fee = []
    lock = []
    royalty = []
    wNFT = ( token_data,
        zero_address,
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )

    wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    
    #check collateral for wrap
    assert wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((2, niftsy20.address), 0, 0)])[0] == False
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((2, niftsy20.address), 0, 0)])[1]).find("ERC20 collateral has incorrect settings", 0)!= -1

    assert wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((2, zero_address), 0, 1)])[0] == False
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((2, zero_address), 0, 1)])[1]).find("ERC20 collateral has incorrect settings", 0)!= -1

    assert wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((2, niftsy20.address), 0, 1)])[0] == True
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((2, niftsy20.address), 0, 1)])[1]).find("Success", 0)!= -1

    assert wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((3, zero_address), 0, 1)])[0] == False
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((3, zero_address), 0, 1)])[1]).find("ERC721 collateral has incorrect settings", 0)!= -1

    assert wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((3, erc721mock.address), 0, 1)])[0] == True
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((3, erc721mock.address), 0, 1)])[1]).find("Success", 0)!= -1

    assert wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), 0, 1)])[0] == False
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), 0, 1)])[1]).find("ERC1155 collateral has incorrect settings", 0)!= -1

    assert wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((4, zero_address), 1, 1)])[0] == False
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((4, zero_address), 1, 1)])[1]).find("ERC1155 collateral has incorrect settings", 0)!= -1

    assert wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), 1, 0)])[0] == False
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), 1, 0)])[1]).find("ERC1155 collateral has incorrect settings", 0)!= -1

    assert wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), 1, 1)])[0] == True
    assert (wrapperChecker.checkAddCollateral(wnft1155.address, wTokenId, [((4, erc1155mock.address), 1, 1)])[1]).find("Success", 0)!= -1

    
    