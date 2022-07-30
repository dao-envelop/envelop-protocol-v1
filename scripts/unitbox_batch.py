import pytest
import logging
from brownie import *
from web3 import Web3
from eth_abi import encode_single
from eth_account.messages import encode_defunct

###wrap, add Collateral, claim and swap through direct swap pair, unwrap

###before
# add trustedSigner status for msg.sender for wrap in unitboxPlatform
# check trustedOperator in TrustedWrapperRemovable == UnitBoxPlatform
# add tokens in whitelist of TrustedWrapperRemovable
# make Token Dex settings
# make DexForChain settings
# add tresury

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
    ORACLE_ADDRESS = '0x8125F522a712F4aD849E6c7312ba8263bEBeEFeD' 
    ORACLE_PRIVATE_KEY = '0x222ead82a51f24a79887aae17052718249295530f8153c73bf1f257a9ca664af'
    coll_amount = 1e18
    price = "50 gwei"
    nonce = 10  ##increase nonce!!

    techERC20 = TechTokenV1.at('0xf84cb379Cb536732AFc737921B4EF97390db92eD')
    wrapper = TrustedWrapperRemovable.at('0x522aCbA649165FFB287Bd1cdF2dd85429E4dcD49')
    wnft1155 = EnvelopwNFT1155.at('0x03C496376043259284Ca152D91b8d416Fd125b0d')
    wnft721 = EnvelopwNFT721.at('0x3b24709991c7A9D1FCC0743Dc8C607D5fb779e5C')
    whitelist = AdvancedWhiteList.at('0x9b0cE975003DBEef2f2fE7860C5362C1dc79A469')
    unitbox = UnitBoxPlatform.at('0x5a2407832A211E6899e279BbfD3060D3d207EFa7')
    erc721mock = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')
    niftsy20 = Niftsy.at('0x3125B3b583D576d86dBD38431C937F957B94B47d') #swapable token
    usdt = TokenMock.at('0x876F77e05C77A37d6Dd2d46DFC76D8BC54Be293F') #tresury token
    dai = TokenMock.at('0xafB8D77EE821275ff7E12464edafe3C8b6A37725') #unswapable token

    #unitbox.settreasury(accounts[3], {"from": accounts[0],  "gas_price": price})
    #unitbox.setTokenDex(niftsy20.address, (1, unitbox.dexForChain()[0], True), {"from": accounts[0], "gas_price": price})
    #unitbox.setDexForChain((unitbox.UniswapV2Router02(), unitbox.UniswapV2Factory(), '0xc778417E063141139Fce010982780140Aa0cD5Ab', usdt.address), {"from": accounts[0], "gas_price": price} )
    #unitbox.setSignerState(ORACLE_ADDRESS, True, {'from':accounts[0], "gas_price": price})

    #wl_data = (False, True, False, techERC20.address)
    #whitelist.setWLItem((2, dai.address), wl_data, {"from": accounts[0], "gas_price": price})

    inDataS = []
    nonceS = []
    signatureS = []
    token_idS = []
    i = 0
    while i<5:
        print(i)
        erc721mock.mint(accounts[1], {"from": accounts[1], "gas_price": price})
        token_idS.append(erc721mock.lastNFTId())
        erc721mock.approve(wrapper.address, token_idS[i],  {"from": accounts[1], "gas_price": price})
        erc721_property = (in_type, erc721mock.address)
        erc721_data = (erc721_property, token_idS[i], 0)
        royalty=[
            (accounts[1].address, 4000), # Maker
            (accounts[2].address, 5000), # Taker
            (unitbox.address, 1000) # Treasure proxy
        ]
        fee = []
        lock = []
        inData = (erc721_data,
            accounts[1],
            fee,
            lock,
            royalty,
            out_type,
            0,
            0x0006
        )
        inDataS.append(inData)
        nonceS.append(nonce + i)
        hashed_msg = unitbox.prepareMessage(
            Web3.toChecksumAddress(erc721mock.address), 
            Web3.toInt(token_idS[i]),
            royalty, 
            Web3.toChecksumAddress(accounts[0].address), 
            Web3.toInt(nonce + i)
        )
        print('hashed_msg = {}'.format(hashed_msg))
        # Ether style signature
        message = encode_defunct(primitive=hashed_msg)
        print('message = {}'.format(message))
        signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)
        print('sign_message is {}'.format(signed_message))
        signatureS.append(signed_message.signature)
        print('ownerOf[{}] = {}'.format(token_idS[i], erc721mock.ownerOf(token_idS[i]))) 
        i = i + 1

    print('inDataS = {}'.format(inDataS))
    print('nonceS = {}'.format(nonceS))
    print('token_idS = {}'.format(token_idS))
    print('signatureS = {}'.format(signatureS))
    print('accounts[0] = {}'.format(accounts[0].address))
    print('accounts[1] = {}'.format(accounts[1].address))


    tx = unitbox.wrapBatch(inDataS, nonceS, signatureS, {"from": accounts[0]})
    print('tx.events.WrappedV1 = {}'.format(tx.events['WrappedV1']))

    
    