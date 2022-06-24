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
def test_UnitBox(accounts, erc721mock, wrapperRemovable, dai, weth, wnft721, niftsy20, erc1155mock1, erc721mock1, whiteLists):

    with reverts("Ownable: caller is not the owner"):
        wrapperRemovable.setTrustedAddress(accounts[1], True, {"from": accounts[1]})

    wrapperRemovable.setTrustedAddress(accounts[1], True, {"from": accounts[0]})