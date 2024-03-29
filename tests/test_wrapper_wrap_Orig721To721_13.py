import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest721, makeNFTForTest1155
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3
in_nft_amount = 3
transfer_fee_amount = 100


#transfer with fee without royalty
def test_wrap(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20, whiteLists, techERC20, wrapperChecker):
    
    niftsy20.transfer(accounts[3], 900, {"from": accounts[0]})
    niftsy20.transfer(accounts[1], 100, {"from": accounts[0]})

    niftsy20.approve(wrapper.address, 900, {"from": accounts[3]})
    niftsy20.approve(wrapper.address, 100, {"from": accounts[1]})

    #make 721 token for wrapping
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})

    logging.info("original_link = {}".format(erc721mock.tokenURI(ORIGINAL_NFT_IDs[0])))

    token_property = (in_type, erc721mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)
    
    fee = []
    lock = [(0x00, chain.time() + 300)]
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    logging.info("wrap1*************************")
    wrapper.wrap(wNFT, [((2, niftsy20.address), 0, 100)], accounts[3], {"from": accounts[1]})

    wTokenId1  = wrapper.lastWNFTId(out_type)[1]
    logging.info(wTokenId1)
    wnft721.setApprovalForAll(wrapper.address, True, {"from": accounts[3]})
    

    token_property = (in_type, wnft721.address)
    token_data = (token_property, wTokenId1, 0)
    
    fee = []
    lock = [(0x00, chain.time() + 200)]
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    logging.info("wrap2*************************")
    wrapper.wrap(wNFT, [((2, niftsy20.address), 0, 200)], accounts[3], {"from": accounts[3]})

    wTokenId2  = wrapper.lastWNFTId(out_type)[1]
    logging.info(wTokenId2)
    token_property = (in_type, wnft721.address)
    token_data = (token_property, wTokenId2, 0)
    
    fee = []
    lock = [(0x00, chain.time() + 100)]
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    logging.info("wrap3*************************")
    wrapper.wrap(wNFT, [((2, niftsy20.address), 0, 300)], accounts[3], {"from": accounts[3]})

    wTokenId3  = wrapper.lastWNFTId(out_type)[1]
    logging.info(wTokenId3)
    token_property = (in_type, wnft721.address)
    token_data = (token_property, wTokenId3, 0)
    
    fee = []
    lock = []
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    logging.info("wrap4*************************")
    wrapper.wrap(wNFT, [((2, niftsy20.address), 0, 400)], accounts[3], {"from": accounts[3]})
    wTokenId4 = wrapper.lastWNFTId(out_type)[1]
    logging.info(wTokenId4)

    logging.info("wnft_tokenUri = {}".format(wnft721.tokenURI(wTokenId4)))


    wrapper.unWrap(wnft721.address, wTokenId4, {"from": accounts[3]})
    chain.sleep(110)
    chain.mine()
    wrapper.unWrap(wnft721.address, wTokenId3, {"from": accounts[3]})
    chain.sleep(110)
    chain.mine()
    wrapper.unWrap(wnft721.address, wTokenId2, {"from": accounts[3]})
    chain.sleep(110)
    chain.mine()
    wrapper.unWrap(wnft721.address, wTokenId1, {"from": accounts[3]})

    assert niftsy20.balanceOf(accounts[3]) == 1000
    assert erc721mock.tokenURI(ORIGINAL_NFT_IDs[0]) == wnft721.tokenURI(wTokenId4)

    logging.info(wnft721.tokenURI(wTokenId4))
    with reverts(""):
        logging.info(wnft721.ownerOf(wTokenId4))






    