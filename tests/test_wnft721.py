import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

# def test_first(pool_repo):
# 	assert pool_repo.getPoolsCount() == '1'


def test_wnft721_mint(accounts, wnft721):
    wnft721.mint(accounts[0], 0, {'from':accounts[0]})
    assert wnft721.balanceOf(accounts[0]) == 1
    logging.info(wnft721.tokenURI(0))

def test_wnft721_transfer(accounts, wnft721):
    wnft721.transferFrom(accounts[0], accounts[1], 0, {'from':accounts[0]})
    assert wnft721.balanceOf(accounts[1]) == 1


def test_wnft721_burn(accounts, wnft721):
    '''with reverts('ERC721Burnable: caller is not owner nor approved'):
        wnft721.burn( 0, {'from':accounts[0]})'''
    wnft721.setApprovalForAll(accounts[0], True, {'from':accounts[1]})
    wnft721.burn(0, {'from':accounts[0]})
    assert wnft721.balanceOf(accounts[1]) == 0

    