import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest721
from web3 import Web3
from eth_abi import encode_single
from eth_account.messages import encode_defunct


LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 3
out_type = 3
secret = 7777777


def wnft_pretty_print(_wrapper, _wnft721, _wTokenId):
    logging.info(
        '\n=========wNFT=============\nwNFT:{0},{1}\nInAsset: {2}\nCollrecords:\n{3}\nunWrapDestination: {4}'
        '\nFees: {5} \nLocks: {6} \nRoyalty: {7} \nrules: {8}({9:0>16b}) \n=========================='.format(
        _wnft721, _wTokenId,
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[0],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[1],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[2],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[3],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[4],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[5],
        _wrapper.getWrappedToken(_wnft721, _wTokenId)[6],
        Web3.toInt(_wrapper.getWrappedToken(_wnft721, _wTokenId)[6]),
        
    ))

def test_simple_wrap(accounts, erc721mock, wrapper, dai, weth, wnft721, niftsy20):
    #make test data
    makeNFTForTest721(accounts, erc721mock, ORIGINAL_NFT_IDs)

    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
    dai.transfer(accounts[1], call_amount, {"from": accounts[0]})
    weth.transfer(accounts[1], 2*call_amount, {"from": accounts[0]})

    dai.approve(wrapper.address, call_amount, {'from':accounts[1]})
    weth.approve(wrapper.address, 2*call_amount, {'from':accounts[1]})

    wrapper.setWNFTId(out_type, wnft721.address, 0, {'from':accounts[0]})
    wnft721.setMinter(wrapper.address, {"from": accounts[0]})

    erc721_property = (in_type, erc721mock.address)
    dai_property = (2, dai.address)
    weth_property = (2, weth.address)
    eth_property = (1, zero_address)

    erc721_data = (erc721_property, ORIGINAL_NFT_IDs[0], 1)
    dai_data = (dai_property, 0, Wei(call_amount))
    weth_data = (weth_property, 0, Wei(2*call_amount))
    eth_data = (eth_property, 0, Wei(eth_amount))

    fee = []
    lock = [('0x0', chain.time() + 10), ('0x0', chain.time() + 20)]
    royalty = []

    wNFT = ( erc721_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
        )

    wrapper.wrap(wNFT, [dai_data, weth_data, eth_data], accounts[3], {"from": accounts[1], "value": eth_amount})
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    wNFT = wrapper.getWrappedToken(wnft721, wTokenId)   
    wnft_pretty_print(wrapper, wnft721, wTokenId)
    #checks
    assert wrapper.balance() == eth_amount
    assert dai.balanceOf(wrapper) == call_amount
    assert weth.balanceOf(wrapper) == 2*call_amount
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address
    assert wnft721.ownerOf(wrapper.lastWNFTId(out_type)[1]) == accounts[3].address
    assert wnft721.totalSupply() == 1

    #logging.info(wNFT)
    assert wNFT[0] == erc721_data
    assert wNFT[1] == [eth_data, dai_data, weth_data]
    assert wNFT[2] == zero_address
    assert wNFT[3] == fee
    assert wNFT[4] == lock
    assert wNFT[5] == royalty
    assert wNFT[6] == '0x0' 
    
    with reverts("TimeLock error"):
        wrapper.unWrap(3, wnft721, wTokenId, {'from': accounts[3]})

    chain.sleep(250)
    chain.mine()

    #wrapper.unWrap(3, wnft721, wTokenId, {'from': accounts[3]})
        
def test_freeze(accounts, erc721mock, wrapper, wnft721, keeper, spawner721):
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    wnft721.setApprovalForAll(keeper, True, {'from': accounts[3]})
    hashed_secret = keeper.getHashed(secret)
    keeper.setSpawnerContract(4,(spawner721, 22),{'from': accounts[0]})
    tx = keeper.freeze((wnft721, wTokenId), 4, hashed_secret,{'from': accounts[3]})
    logging.info('Freeze event:{}'.format(tx.events['NewFreeze']))
    #logging.info('Debug event:{}'.format(tx.events['Debug']))
    encoded_msg = encode_single(
        '(bytes32,address,uint256)',
         (hashed_secret, tx.events['NewFreeze']['spawnerContract'], tx.events['NewFreeze']['spawnedTokenId'])
    )
    hashed_msg = Web3.solidityKeccak(['bytes32'], [encoded_msg])
    logging.info('frozenItems[{}] = {}'.format(
        Web3.toBytes(hashed_msg).hex(), 
        keeper.frozenItems(Web3.toBytes(hashed_msg))
    ))
    logging.info('tx.hash={}'.format(tx.txid))
    global freeze_tx
    freeze_tx = tx.txid
    #assert keeper
    assert wnft721.balanceOf(keeper) == 1
    assert wnft721.ownerOf(wTokenId) == keeper.address
    assert keeper.frozenItems(Web3.toBytes(hashed_msg))[1] == wTokenId

def test_spawn(accounts, keeper, spawner721):
    # get tx datails from Oracle
    tx = chain.get_transaction(freeze_tx)
    logging.info('\ntx: {} \nsender: {}\n logs:{}'.format(tx.txid, tx.sender, tx.logs))
    logging.info('Freeze event:{}'.format(tx.events['NewFreeze']))
