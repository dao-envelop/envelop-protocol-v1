import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
coll_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3
in_nft_amount = 3
transfer_fee_amount = 100


#transfer with fee without royalty
def test_UnitBox(accounts, erc721mock, erc1155mock, wrapperRemovable, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1, whiteLists, techERC20, wrapperChecker):

    with reverts("Ownable: caller is not the owner"):
        wrapperRemovable.setTrustedAddress(accounts[1], True, {"from": accounts[1]})

    wrapperRemovable.setTrustedAddress(accounts[1], True, {"from": accounts[0]})

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    #make 1155 tokens
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc721mock.approve(wrapperRemovable.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapperRemovable.lastWNFTId(out_type)[1] == 0):
        wrapperRemovable.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperRemovable.address, {"from": accounts[0]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    
    fee = []
    lock = []
    royalty = [(accounts[1], 4250), (accounts[2], 4250), (accounts[3], 1500)]

    wNFT = ( token_data,
        accounts[1],
        fee,
        lock,
        royalty,
        out_type,
        0,
        Web3.toBytes(0x0006)
        )


    #switch on white list
    wrapperRemovable.setWhiteList(whiteLists.address, {"from": accounts[0]})
    
    wl_data = (False, True, False, techERC20.address)
    whiteLists.setWLItem((2, niftsy20.address), wl_data, {"from": accounts[0]})
    whiteLists.setWLItem((2, dai.address), wl_data, {"from": accounts[0]})
    whiteLists.setWLItem((3, erc721mock.address), wl_data, {"from": accounts[0]})
    whiteLists.setWLItem((4, erc1155mock.address), wl_data, {"from": accounts[0]})

    wrapperRemovable.wrap(wNFT, [], accounts[2], {"from": accounts[0]})

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperRemovable.address
    wTokenId = wrapperRemovable.lastWNFTId(out_type)[1]

    #add collateral

    niftsy20.approve(wrapperRemovable.address, coll_amount, {"from": accounts[0]})

    wrapperRemovable.addCollateral(wnft721.address, wTokenId, [((2, niftsy20.address), 0, 0 )], {"from": accounts[0], "value": "1 ether"})
    assert wrapperRemovable.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0


    wrapperRemovable.addCollateral(wnft721.address, wTokenId, [((2, niftsy20.address), 0, 0 )], {"from": accounts[0]})

    #try to remove ether
    logging.info(wrapperRemovable.getWrappedToken(wnft721.address, wTokenId)[1])
    with reverts("Remove fail"):
        wrapperRemovable.removeERC20Collateral(wnft721.address, wTokenId, zero_address, {"from": accounts[1]}) 

    dai.approve(wrapperRemovable.address, coll_amount, {"from": accounts[0]})
    wrapperRemovable.addCollateral(wnft721.address, wTokenId, [((2, dai.address), 0, coll_amount )], {"from": accounts[0]})

    #logging.info(wrapperRemovable.getWrappedToken(wnft721.address, wTokenId)[1])
    #try to remove niftsy when amount is 0
    with reverts("Remove fail"):
        wrapperRemovable.removeERC20Collateral(wnft721.address, wTokenId, niftsy20.address, {"from": accounts[1]}) 

    #try to remove collateral for nonexists wnft
    with reverts("Remove fail"):
        wrapperRemovable.removeERC20Collateral(wnft721.address, wTokenId+1, dai.address, {"from": accounts[1]}) 

    #remove dai tokens
    wrapperRemovable.removeERC20Collateral(wnft721.address, wTokenId, dai.address, {"from": accounts[1]}) 
    #logging.info(wrapperRemovable.getWrappedToken(wnft721.address, wTokenId)[1])

    #add erc721 in collateral with amount
    erc721mock.approve(wrapperRemovable.address, ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    wrapperRemovable.addCollateral(wnft721.address, wTokenId, [((3, erc721mock.address), ORIGINAL_NFT_IDs[1], 0 )], {"from": accounts[0]})

    #add erc1155 in collateral
    erc1155mock.setApprovalForAll(wrapperRemovable.address,True, {"from": accounts[1]}) 
    wrapperRemovable.addCollateral(wnft721.address, wTokenId, [((4, erc1155mock.address), ORIGINAL_NFT_IDs[0], in_nft_amount)], {"from": accounts[1]})

    #try to remove erc1155 from collateral
    with reverts("Remove fail"):
        wrapperRemovable.removeERC20Collateral(wnft721.address, wTokenId, erc1155mock.address, {"from": accounts[1]}) 

    #try to remove erc721 from collateral
    with reverts("Remove fail"):
        wrapperRemovable.removeERC20Collateral(wnft721.address, wTokenId, erc721mock.address, {"from": accounts[1]}) 

    logging.info(wrapperRemovable.getWrappedToken(wnft721.address, wTokenId)[1])

    #try to add niftsy with type "empty"
    niftsy20.approve(wrapperRemovable.address, coll_amount, {"from": accounts[0]})
    with reverts(""):
        wrapperRemovable.addCollateral(wnft721.address, wTokenId, [((0, niftsy20.address), 0, coll_amount )], {"from": accounts[0]})

    before_balance_ether1 = accounts[1].balance()

    wrapperRemovable.unWrap(out_type, wnft721.address, wTokenId, {"from": accounts[0]})

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[1]
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[1]
    assert erc1155mock.balanceOf(accounts[1], ORIGINAL_NFT_IDs[0]) == in_nft_amount
    assert accounts[1].balance() == before_balance_ether1 + 1e18


    



    