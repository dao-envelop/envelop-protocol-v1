import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateralLight, makeNFTForTest1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5
coll_amount = 2
amount = 100

def test_addColl(accounts, erc721mock, wrapperLight, dai, weth, wnft721ForWrapperLightV1, niftsy20, erc721mock1, erc1155mock1, wrapperCheckerLightV1):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    
    #make wrap NFT 721
    wTokenId = makeFromERC721ToERC721WithoutCollateralLight(accounts, erc721mock, wrapperLight, wnft721ForWrapperLightV1, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])

    #PREPARE DATA
    #make 721 for collateral
    makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
    erc721mock1.approve(wrapperLight.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]} )
    erc721mock1.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {"from": accounts[0]} )
    erc721mock1.approve(wrapperLight.address, ORIGINAL_NFT_IDs[1], {"from": accounts[1]} )

    #make 1155 for collateral
    makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock1.setApprovalForAll(wrapperLight.address,True, {"from": accounts[1]})
    erc1155mock1.safeTransferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], in_nft_amount, "",{"from": accounts[0]})

    #make erc20 for collateral
    dai.transfer(accounts[1], amount, {"from": accounts[0]})
    dai.approve(wrapperLight.address, amount, {"from": accounts[1]})
    weth.transfer(accounts[1], 10*amount, {"from": accounts[0]})
    weth.approve(wrapperLight.address, 10*amount, {"from": accounts[1]})

    #add collateral
    wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0),
            ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount),
            ((2, dai.address), 0, amount),
            ((3, erc721mock1.address), ORIGINAL_NFT_IDs[1], 0),
            ((2, weth.address), 0, 10*amount),
            ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[1], coll_amount-1),
            ], {'from': accounts[1], "value": "1 ether"})

    collateral = wrapperLight.getWrappedToken(wnft721ForWrapperLightV1, wTokenId)[1]

    assert wrapperLight.balance() == "1 ether"
    assert erc1155mock1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[0]) == coll_amount
    assert erc1155mock1.balanceOf(wrapperLight.address, ORIGINAL_NFT_IDs[1]) == coll_amount - 1
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperLight.address
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapperLight.address
    assert dai.balanceOf(wrapperLight.address) == amount
    assert weth.balanceOf(wrapperLight.address) == 10*amount
    assert collateral[0] == ((1, zero_address), 0, Wei("1 ether"))
    assert collateral[1] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
    assert collateral[2] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)
    assert collateral[3] ==  ((2, dai.address), 0, amount)
    assert collateral[4] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[1], 0)
    assert collateral[5] == ((2, weth.address), 0, 10*amount)
    assert collateral[6] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[1], coll_amount-1)

    #check 
    assert wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, dai.address)[0] == amount
    assert wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, weth.address)[0] == 10*amount
    assert wrapperCheckerLightV1.getNativeCollateralBalance(wnft721ForWrapperLightV1.address, wTokenId) == "1 ether"
    assert wrapperCheckerLightV1.getERC1155CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, erc1155mock1.address, ORIGINAL_NFT_IDs[1])[0] == coll_amount-1 



    contract_eth_balance = wrapperLight.balance()
    before_dai_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, dai.address)[0]
    before_weth_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, weth.address)[0]
    before_eth_balance = wrapperCheckerLightV1.getERC20CollateralBalance(wnft721ForWrapperLightV1.address, wTokenId, zero_address)[0]
    before_acc_balance = accounts[3].balance()

    wrapperLight.unWrap(3, wnft721ForWrapperLightV1.address, wTokenId, {"from": accounts[3]})

    #checks
    assert wrapperLight.balance() == 0
    assert accounts[3].balance() == before_acc_balance + contract_eth_balance
    assert dai.balanceOf(wrapperLight) == 0
    assert weth.balanceOf(wrapperLight) == 0
    assert dai.balanceOf(accounts[3]) == before_dai_balance
    assert weth.balanceOf(accounts[3]) == before_weth_balance
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[3]
    assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == coll_amount
    assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[1]) == coll_amount - 1
    assert wnft721ForWrapperLightV1.totalSupply() == 0

    with reverts("wNFT not exists"):
        wrapperLight.addCollateral(wnft721ForWrapperLightV1.address, wTokenId, [], {'from': accounts[1], "value": "0.01 ether"})

    assert wrapperLight.balance() == 0
    