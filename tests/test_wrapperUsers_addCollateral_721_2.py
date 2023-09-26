import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721
from web3 import Web3


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222, 33333]
zero_address = '0x0000000000000000000000000000000000000000'
in_nft_amount = 3 
out_nft_amount = 5
coll_amount = 2
amount = 100
in_type = 3
out_type = 3




def test_call_factory(accounts, usersSBTRegistry, wrapperUsers, wnft721SBT, wnft1155SBT):
    usersSBTRegistry.addImplementation((3,wnft721SBT), {'from': accounts[0]})
    usersSBTRegistry.addImplementation((4,wnft1155SBT), {'from': accounts[0]})
    usersSBTRegistry.deployNewCollection(
        wnft721SBT, 
        accounts[0],'', '', '', wrapperUsers, {'from': accounts[0]}
    )

    logging.info(usersSBTRegistry.getUsersCollections(accounts[0]))
    assert len(usersSBTRegistry.getUsersCollections(accounts[0])) == 1


def test_addColl(accounts, erc721mock, wrapperUsers, dai, weth, wnft721SBT, niftsy20, erc721mock1, erc1155mock1):
    #make test data
    erc721mock.mint(ORIGINAL_NFT_IDs[0], {"from": accounts[0]})
    erc721mock.mint(ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    erc721mock.mint(ORIGINAL_NFT_IDs[2], {"from": accounts[0]})
    erc721mock.mint(ORIGINAL_NFT_IDs[3], {"from": accounts[0]})
    
    #make wrap NFT 721
    erc721_property = (in_type, erc721mock.address)

    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 0)
    erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[0], {"from": accounts[0]} )

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
        Web3.toBytes(0x0004)  #rules - No Transfer
        )

    tx = wrapperUsers.wrapIn(wNFT, [], accounts[3], wnft721SBT,  {"from": accounts[0]})
    wTokenId = tx.return_value[1]

    #PREPARE DATA
    #make 721 for collateral
    erc721mock1.mint(ORIGINAL_NFT_IDs[0], {"from": accounts[0]})
    erc721mock1.mint(ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    erc721mock1.mint(ORIGINAL_NFT_IDs[2], {"from": accounts[0]})
    erc721mock1.mint(ORIGINAL_NFT_IDs[3], {"from": accounts[0]})

    erc721mock1.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[0], {"from": accounts[0]} )
    erc721mock1.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[1], {"from": accounts[0]} )

    #make 1155 for collateral
    erc1155mock1.mintBatch(
        accounts[0], 
        ORIGINAL_NFT_IDs,
        [coll_amount,coll_amount,coll_amount,coll_amount],
        '',
        {"from": accounts[0]})

    erc1155mock1.setApprovalForAll(wrapperUsers.address,True, {"from": accounts[0]})
    

    #make erc20 for collateral
    dai.approve(wrapperUsers.address, amount, {"from": accounts[0]})
    weth.approve(wrapperUsers.address, 10*amount, {"from": accounts[0]})

    #add collateral
    wrapperUsers.addCollateral(wnft721SBT.address, wTokenId, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0),
            ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount),
            ((2, dai.address), 0, amount),
            ((3, erc721mock1.address), ORIGINAL_NFT_IDs[1], 0),
            ((2, weth.address), 0, 10*amount),
            ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[1], coll_amount-1),
            ], {'from': accounts[0], "value": "1 ether"})

    #1
    collateral = wrapperUsers.getWrappedToken(wnft721SBT, wTokenId)[1]
    assert wrapperUsers.balance() == "1 ether"
    assert erc1155mock1.balanceOf(wrapperUsers.address, ORIGINAL_NFT_IDs[0]) == coll_amount
    assert erc1155mock1.balanceOf(wrapperUsers.address, ORIGINAL_NFT_IDs[1]) == coll_amount - 1
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapperUsers.address
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapperUsers.address
    assert dai.balanceOf(wrapperUsers.address) == amount
    assert weth.balanceOf(wrapperUsers.address) == 10*amount
    assert collateral[0] == ((1, zero_address), 0, Wei("1 ether"))
    assert collateral[1] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[0], 0)
    assert collateral[2] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[0], coll_amount)
    assert collateral[3] ==  ((2, dai.address), 0, amount)
    assert collateral[4] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[1], 0)
    assert collateral[5] == ((2, weth.address), 0, 10*amount)
    assert collateral[6] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[1], coll_amount-1)

    #########################################################################

    #make wrap NFT 721
    #make wrap NFT 721
    erc721_property = (in_type, erc721mock.address)

    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[1], 0)
    erc721mock.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[1], {"from": accounts[0]} )

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
        Web3.toBytes(0x0004)  #rules - No Transfer
        )

    tx = wrapperUsers.wrapIn(wNFT, [], accounts[3], wnft721SBT,  {"from": accounts[0]})
    wTokenId1 = tx.return_value[1]

    #PREPARE DATA
    #make 721 for collateral
    erc721mock1.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[2], {"from": accounts[0]} )
    erc721mock1.approve(wrapperUsers.address, ORIGINAL_NFT_IDs[3], {"from": accounts[0]} )

    #make erc20 for collateral
    dai.approve(wrapperUsers.address, 2*amount, {"from": accounts[0]})
    weth.approve(wrapperUsers.address, 7*amount, {"from": accounts[0]})

    #add collateral
    wrapperUsers.addCollateral(wnft721SBT.address, wTokenId1, [((3, erc721mock1.address), ORIGINAL_NFT_IDs[2], 0),
            ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[2], coll_amount),
            ((2, dai.address), 0, 2*amount),
            ((3, erc721mock1.address), ORIGINAL_NFT_IDs[3], 0),
            ((2, weth.address), 0, 7*amount),
            ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[3], coll_amount),
            ], {'from': accounts[0], "value": "0.1 ether"})


    #2
    collateral1 = wrapperUsers.getWrappedToken(wnft721SBT, wTokenId1)[1]
    assert wrapperUsers.balance() == "1.1 ether"
    assert erc1155mock1.balanceOf(wrapperUsers.address, ORIGINAL_NFT_IDs[2]) == coll_amount
    assert erc1155mock1.balanceOf(wrapperUsers.address, ORIGINAL_NFT_IDs[3]) == coll_amount
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[2]) == wrapperUsers.address
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[3]) == wrapperUsers.address
    assert dai.balanceOf(wrapperUsers.address) == 3*amount
    assert weth.balanceOf(wrapperUsers.address) == 17*amount
    assert collateral1[0] == ((1, zero_address), 0, Wei("0.1 ether"))
    assert collateral1[1] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[2], 0)
    assert collateral1[2] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[2], coll_amount)
    assert collateral1[3] == ((2, dai.address), 0, 2*amount)
    assert collateral1[4] == ((3, erc721mock1.address), ORIGINAL_NFT_IDs[3], 0)
    assert collateral1[5] == ((2, weth.address), 0, 7*amount)
    assert collateral1[6] == ((4, erc1155mock1.address), ORIGINAL_NFT_IDs[3], coll_amount)


    contract_eth_balance = wrapperUsers.balance()
    before_dai_balance =  wrapperUsers.getCollateralBalanceAndIndex(wnft721SBT.address, wTokenId, 2, dai, 0)[0]+wrapperUsers.getCollateralBalanceAndIndex(wnft721SBT.address, wTokenId1, 2, dai, 0)[0]
    before_weth_balance =  wrapperUsers.getCollateralBalanceAndIndex(wnft721SBT.address, wTokenId, 2, weth, 0)[0]+wrapperUsers.getCollateralBalanceAndIndex(wnft721SBT.address, wTokenId1, 2, weth, 0)[0]
    before_acc_balance = accounts[3].balance()

    wrapperUsers.unWrap(3, wnft721SBT.address, wTokenId, {"from": accounts[3]})
    wrapperUsers.unWrap(3, wnft721SBT.address, wTokenId1, {"from": accounts[3]})

    #checks
    assert wrapperUsers.balance() == 0
    assert accounts[3].balance() == before_acc_balance + contract_eth_balance
    assert dai.balanceOf(wrapperUsers) == 0
    assert weth.balanceOf(wrapperUsers) == 0
    assert dai.balanceOf(accounts[3]) == before_dai_balance
    assert weth.balanceOf(accounts[3]) == before_weth_balance
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3]
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[3]
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[2]) == accounts[3]
    assert erc721mock1.ownerOf(ORIGINAL_NFT_IDs[3]) == accounts[3]
    assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[0]) == coll_amount
    assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[1]) == coll_amount - 1
    assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[2]) == coll_amount
    assert erc1155mock1.balanceOf(accounts[3], ORIGINAL_NFT_IDs[3]) == coll_amount
    assert wnft721SBT.totalSupply() == 0
    