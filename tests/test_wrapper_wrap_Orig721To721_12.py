import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721, makeFromERC721ToERC721WithoutCollateral, makeNFTForTest1155


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222, 33333]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5
coll_amount = 2
amount = 100

def test_addColl(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, erc721mock1, erc1155mock1, wrapperChecker):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    
    #make wrap NFT 721
    wTokenId = makeFromERC721ToERC721WithoutCollateral(accounts, erc721mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_IDs[0], accounts[3])

    #PREPARE DATA
    #make 721 for collateral
    makeNFTForTest721(accounts, erc721mock1, ORIGINAL_NFT_IDs)
    erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]} )
    erc721mock1.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {"from": accounts[0]} )
    erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {"from": accounts[1]} )

    #make 1155 for collateral
    makeNFTForTest1155(accounts, erc1155mock1, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock1.setApprovalForAll(wrapper.address,True, {"from": accounts[1]})
    erc1155mock1.safeTransferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], in_nft_amount, "",{"from": accounts[0]})

    #make erc20 for collateral
    dai.transfer(accounts[1], amount, {"from": accounts[0]})
    dai.approve(wrapper.address, amount, {"from": accounts[1]})
    weth.transfer(accounts[1], 10*amount, {"from": accounts[0]})
    weth.approve(wrapper.address, 10*amount, {"from": accounts[1]})

    #add collateral
    wrapper.addCollateral(wnft721.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0),
            ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount),
            ((2, dai.address), 0, amount),
            ((3, erc721mock1.address), ORIGINAL_NFT_IDs[1], 0),
            ((2, weth.address), 0, 10*amount),
            ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[1], coll_amount-1),
            ], {'from': accounts[1], "value": "1 ether"})

    #1
    collateral = wrapper.getWrappedToken(wnft721, wTokenId)[1]
    assert wrapper.balance() == "1 ether"
    assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == coll_amount
    assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[1]) == coll_amount - 1
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapper.address
    assert dai.balanceOf(wrapper.address) == amount
    assert weth.balanceOf(wrapper.address) == 10*amount
    assert collateral[0] == ((1, zero_address), 0, Wei("1 ether"))
    assert collateral[1] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
    assert collateral[2] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)
    assert collateral[3] ==  ((2, dai.address), 0, amount)
    assert collateral[4] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[1], 0)
    assert collateral[5] == ((2, weth.address), 0, 10*amount)
    assert collateral[6] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[1], coll_amount-1)

    #check 
    assert wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId, dai.address)[0] == amount
    assert wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId, weth.address)[0] == 10*amount
    assert wrapperChecker.getNativeCollateralBalance(wnft721.address, wTokenId) == "1 ether"
    assert wrapperChecker.getERC1155CollateralBalance(wnft721.address, wTokenId, erc1155mock1.address, ORIGINAL_NFT_IDs[1])[0] == coll_amount-1

    #########################################################################

    #make wrap NFT 721
    erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    wTokenId1 = makeFromERC721ToERC721WithoutCollateral(accounts, erc721mock, wrapper, wnft721, niftsy20, ORIGINAL_NFT_IDs[1], accounts[3])

    #PREPARE DATA
    #make 721 for collateral
    erc721mock1.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[2], {"from": accounts[0]} )
    erc721mock1.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[3], {"from": accounts[0]} )
    erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[2], {"from": accounts[1]} )
    erc721mock1.approve(wrapper.address, ORIGINAL_NFT_IDs[3], {"from": accounts[1]} )

    #make 1155 for collateral
    erc1155mock1.safeTransferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[2], in_nft_amount, "",{"from": accounts[0]})
    erc1155mock1.safeTransferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[3], in_nft_amount, "",{"from": accounts[0]})

    #make erc20 for collateral
    dai.transfer(accounts[1], 2*amount, {"from": accounts[0]})
    dai.approve(wrapper.address, 2*amount, {"from": accounts[1]})
    weth.transfer(accounts[1], 7*amount, {"from": accounts[0]})
    weth.approve(wrapper.address, 7*amount, {"from": accounts[1]})

    #add collateral
    wrapper.addCollateral(wnft721.address, wTokenId1, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[2], 0),
            ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[2], coll_amount),
            ((2, dai.address), 0, 2*amount),
            ((3, erc721mock1.address), ORIGINAL_NFT_IDs[3], 0),
            ((2, weth.address), 0, 7*amount),
            ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[3], coll_amount),
            ], {'from': accounts[1], "value": "0.1 ether"})


    #2
    collateral1 = wrapper.getWrappedToken(wnft721, wTokenId1)[1]
    assert wrapper.balance() == "1.1 ether"
    assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[2]) == coll_amount
    assert erc1155mock1.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[3]) == coll_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[2]) == wrapper.address
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[3]) == wrapper.address
    assert dai.balanceOf(wrapper.address) == 3*amount
    assert weth.balanceOf(wrapper.address) == 17*amount
    assert collateral1[0] == ((1, zero_address), 0, Wei("0.1 ether"))
    assert collateral1[1] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[2], 0)
    assert collateral1[2] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[2], coll_amount)
    assert collateral1[3] == ((2, dai.address), 0, 2*amount)
    assert collateral1[4] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[3], 0)
    assert collateral1[5] == ((2, weth.address), 0, 7*amount)
    assert collateral1[6] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[3], coll_amount)

    #check 
    assert wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId1, dai.address)[0] == 2*amount
    assert wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId1, weth.address)[0] == 7*amount
    assert wrapperChecker.getNativeCollateralBalance(wnft721.address, wTokenId1) == "0.1 ether"
    assert wrapperChecker.getERC1155CollateralBalance(wnft721.address, wTokenId1, erc1155mock1.address, ORIGINAL_NFT_IDs[2])[0] == coll_amount 



    contract_eth_balance = wrapper.balance()
    before_dai_balance = wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId, dai.address)[0]+wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId1, dai.address)[0]
    before_weth_balance = wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId, weth.address)[0]+wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId1, weth.address)[0]
    before_eth_balance = wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId, zero_address)[0]+wrapperChecker.getERC20CollateralBalance(wnft721.address, wTokenId1, zero_address)[0]
    before_acc_balance = accounts[2].balance()

    wrapper.unWrap(3, wnft721.address, wTokenId, {"from": accounts[3]})
    wrapper.unWrap(3, wnft721.address, wTokenId1, {"from": accounts[3]})

    #checks
    assert wrapper.balance() == 0
    assert accounts[2].balance() == before_acc_balance + contract_eth_balance
    assert dai.balanceOf(wrapper) == 0
    assert weth.balanceOf(wrapper) == 0
    assert dai.balanceOf(accounts[2]) == before_dai_balance
    assert weth.balanceOf(accounts[2]) == before_weth_balance
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[2]
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[2]
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[2]) == accounts[2]
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[3]) == accounts[2]
    assert erc1155mock1.balanceOf(accounts[2], ORIGINAL_NFT_IDs[0]) == coll_amount
    assert erc1155mock1.balanceOf(accounts[2], ORIGINAL_NFT_IDs[1]) == coll_amount - 1
    assert erc1155mock1.balanceOf(accounts[2], ORIGINAL_NFT_IDs[2]) == coll_amount
    assert erc1155mock1.balanceOf(accounts[2], ORIGINAL_NFT_IDs[3]) == coll_amount
    assert wnft721.totalSupply() == 0
    