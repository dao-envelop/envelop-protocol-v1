import pytest
import requests
import logging
import time
from brownie import *
from hashlib import sha256

accounts.load('secret2')

def wnft_pretty_print(_wrapper, _wnft721, _wTokenId):
    print(
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

def main():
    #UniswapPairV2 Niftsy/USDT 0x8783e4c466d2f90c1f1235409d352923ff8f1791

    zero_address = '0x0000000000000000000000000000000000000000'
    call_amount = 1e18
    eth_amount = "1 ether"
    in_type = 3
    out_type = 3
    coll_amount = 1e18
    price = "50 gwei"

    wrapper = WrapperBaseV1.at('0x7d4CBE4FD761206d0B06F91BE846FEbE9B7b9fec')
    wnft721 = EnvelopwNFT721.at('0x25aD94A06c7DBfc985F0848d1d8E457270FCcfca')
    erc721mock = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')

    
    #mint original nft erc721
    erc721mock.mint(accounts[0], {"from": accounts[0], "gas_price": price})
    erc721mock_nft_id = erc721mock.lastNFTId()
    #make allowance to use original NFT
    erc721mock.approve(wrapper.address, erc721mock_nft_id,  {"from": accounts[0], "gas_price": price})
   

    erc721_property = (in_type, erc721mock.address)
    erc721_data = (erc721_property, erc721mock_nft_id, 0)
    royalty=[]
    fee = []
    lock = []

    inData = (erc721_data,
        accounts[0],
        fee,
        lock,
        royalty,
        out_type,
        0,
        0x0000
    )

    #wrap
    tx = wrapper.wrap(inData, [], accounts[0], {"from": accounts[0], "gas_price": price}) 
    wTokenId = tx.events['WrappedV1']['outTokenId']
    #wTokenId = wrapper.lastWNFTId(3)[1]
    wNFT = wrapper.getWrappedToken(wnft721, wTokenId)   
    print(wTokenId)

    wnft_pretty_print(wrapper, wnft721, wTokenId)
    #checks

    time.sleep(120)

    baseUrl='https://stage.api.envelop.is/'
    app_name='bunnybank24.com'
    app_id='7110613d8b66a507e083491007dc0d72fcd8a5f97b3c138d92d3817e21586a74'
    app_key='b14130564aaa38f203ca6fe3d9ed294d92b0ce26ac7b8fae8c25c164ecd71c07'
    key_active=300
    now = now = int(time.time())
    timeBlock = str(int(now / int(key_active)))
    auth = app_id + '.' + sha256(f'{app_name}{app_key}{timeBlock}'.encode('utf-8')).hexdigest()
    print(auth)

    response = requests.get('https://stage.api.envelop.is/'+'discover/721/'+str(4)+'/'+str(wnft721.address)+'/'+str(wTokenId), headers = {'Content-Type': 'application/json', 'Authorization': auth})
    print(response.json())

    assert len(response.json())>0
    assert response.status_code == 200

    