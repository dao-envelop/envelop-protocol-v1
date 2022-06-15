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
def test_UnitBox(accounts, erc721mock, wrapperRemovable, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1, whiteLists, techERC20, wrapperChecker):

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapperRemovable.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapperRemovable.lastWNFTId(out_type)[1] == 0):
        wrapperRemovable.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapperRemovable.address, {"from": accounts[0]})

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    
    fee = []
    lock = []
    royalty = [(accounts[1], 4000), (accounts[2], 6000)]

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

    # owner of original nft tries to wrap it
    with reverts('Only trusted address'):
        wrapperRemovable.wrap(wNFT, [], accounts[2], {"from": accounts[1]})

    #trusted address tries to wrap original nft of account[1]
    with reverts('Only trusted address'):
        wrapperRemovable.wrap(wNFT, [], accounts[2], {"from": accounts[1]})
    wrapperRemovable.wrap(wNFT, [], accounts[2], {"from": accounts[0]})

    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperRemovable.address
    wTokenId = wrapperRemovable.lastWNFTId(out_type)[1]

    #add collateral

    niftsy20.approve(wrapperRemovable.address, coll_amount, {"from": accounts[0]})

    wrapperRemovable.addCollateral(wnft721.address, wTokenId, [((2, niftsy20.address), 0, coll_amount )], {"from": accounts[0]})
    assert wrapperRemovable.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == coll_amount

    assert niftsy20.balanceOf(accounts[1]) == 0
    assert niftsy20.balanceOf(accounts[2]) == 0
    wrapperRemovable.removeERC20Collateral(wnft721.address, wTokenId, niftsy20.address, {"from": accounts[1]}) 
    assert niftsy20.balanceOf(accounts[1]) + niftsy20.balanceOf(accounts[2]) == coll_amount
    

    

    #address _wNFTAddress, 
    #    uint256 _wNFTTokenId,
    #    address _collateralAddress,
    #    address _amount
        
    







    #account[0] - platform
    #account[1] - investor
    #account[2] - scolar



    