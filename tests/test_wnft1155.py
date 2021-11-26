import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

# def test_first(pool_repo):
# 	assert pool_repo.getPoolsCount() == '1'


def test_wnft1155_mint(accounts, wnft1155):
    wnft1155.mint(accounts[0], 0, 1, {'from':accounts[0]})
    assert wnft1155.balanceOf(accounts[0],0) == 1
    logging.info(wnft1155.uri(0))

def test_wnft1155_transfer(accounts, wnft1155):
    wnft1155.safeTransferFrom(accounts[0], accounts[1], 0, 1, '', {'from':accounts[0]})
    assert wnft1155.balanceOf(accounts[1],0) == 1


def test_wnft1155_burn(accounts, wnft1155):
    with reverts('ERC1155: caller is not owner nor approved'):
        wnft1155.burn(accounts[1], 0, 1, {'from':accounts[0]})
    wnft1155.setApprovalForAll(accounts[0], True, {'from':accounts[1]})
    wnft1155.burn(accounts[1], 0, 1,  {'from':accounts[0]})
    assert wnft1155.balanceOf(accounts[1],0) == 0


    