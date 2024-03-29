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
in_type = 4
out_type = 4
in_nft_amount = 3
out_nft_amount = 5
transfer_fee_amount = 1


#transfer with fee without royalty
def test_transfer(accounts, erc1155mock, wrapper, wnft1155, whiteLists, techERC20, erc721mock):

    #make 1155 token for wrapping
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapper.address,True,  {"from": accounts[1]})

    #make 721 token for transfer fee
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)
    erc721mock.transferFrom(accounts[0], accounts[3], ORIGINAL_NFT_IDs[1], {"from": accounts[0]})
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {"from": accounts[3]})


    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})

    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    
    fee = [(Web3.toBytes(0x00), transfer_fee_amount, erc721mock.address)]
    lock = []
    royalty = [(wrapper.address, 10000)]

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )


    #switch on white list
    wrapper.setWhiteList(whiteLists.address, {"from": accounts[0]})

    #transferFee flag is switched on
    wl_data = (True, False, False, techERC20.address)
    whiteLists.setWLItem((3, erc721mock.address), wl_data, {"from": accounts[0]})

    tx = wrapper.wrap(wNFT, [], accounts[3], {"from": accounts[1]})

    assert erc1155mock.balanceOf(wrapper.address, ORIGINAL_NFT_IDs[0]) == in_nft_amount

    wTokenId = wrapper.lastWNFTId(out_type)[1]


    #fee is erc721 token. It is absurd, but we check the case
    with reverts("ERC721: invalid token ID"):
        wnft1155.safeTransferFrom(accounts[3], accounts[2], wTokenId, out_nft_amount, "",  {"from": accounts[3]})