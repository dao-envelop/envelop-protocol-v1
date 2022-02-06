import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest1155, makeNFTForTest1155
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


#transfer with fee without royalty
def test_transfer(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20, erc1155mock1, whiteLists, techERC20, wrapperChecker):
    
    #make 1155 token for wrapping
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapper.address, True, {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})

    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    
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

    with reverts("ERC1155: caller is not owner nor approved"):
        wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[3]})

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount+1)

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    with reverts("ERC1155: insufficient balance for transfer"):
        wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

    erc1155mock.safeTransferFrom(accounts[1], accounts[4], ORIGINAL_NFT_IDs[0], 1, "", {"from": accounts[1]})

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

    with reverts("ERC1155: insufficient balance for transfer"):
        wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})