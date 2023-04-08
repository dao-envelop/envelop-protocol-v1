import pytest
import logging
from brownie import *
from web3 import Web3
from eth_abi import encode_single
from eth_account.messages import encode_defunct

###wrap, add Collateral, remove collateral, manual swap through not direct swap pair, unwrap

#0-0x5992Fe461F81C8E0aFFA95b831E50e9b3854BA0E  - //address which create wnft and add collateral
accounts.load('secret2')

#1-0xf315B9006C20913D6D8498BDf657E778d4Ddf2c4  Secret1 - investor
accounts.load('secret1')

#2-0x110fa9c41cb43c08ad98391dfb52a9a0713d9613  exo - scholar
accounts.load('exo')

#3 - 0x0Bc721C6eEf62C6A756A98d169f65294306f20b4  -  additinal  address for  tests
accounts.load('user_swap')

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
    #cross swap

    
    zero_address = '0x0000000000000000000000000000000000000000'
    call_amount = 1e18
    eth_amount = "1 ether"
    in_type = 3
    out_type = 3
    ORACLE_ADDRESS = '0x8125F522a712F4aD849E6c7312ba8263bEBeEFeD' 
    ORACLE_PRIVATE_KEY = '0x222ead82a51f24a79887aae17052718249295530f8153c73bf1f257a9ca664af'
    coll_amount = 1e18
    price = "50 gwei"
    nonce = 1  ##increase nonce!!

    #bsc
    techERC20 = TechTokenV1.at('0xe2842fBB5931E3Fb282deb96aAd0efD3013426A8')
    wrapper = TrustedWrapperRemovable.at('0x1f34b6c342941F8b40b2cd15C54FeccA1Ec15D22')
    wnft1155 = EnvelopwNFT1155.at('0x89B4F87699d760BCB864e23891F608a6D825c1AC')
    wnft721 = EnvelopwNFT721.at('0x92D7eD06d39d34Fec9476EEB20FeC8E70D02d8a9')
    whitelist = AdvancedWhiteList.at('0xFA01246F58F0FFdd25650b59d81504eF277b6343')
    unitbox = UnitBoxPlatform.at('0x30dFB8c1FE622D8C6e4c8DbaacFa4826E6EBAb58')
    niftsy = TokenMock.at('0x7728cd70b3dD86210e2bd321437F448231B81733') #swapable token
    erc721mock = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')
    usdt = TokenMock.at('0x55d398326f99059fF775485246999027B3197955') #tresury token
    busd = TokenMock.at('0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56')
    
    treasury = '0x2cccf64bf6eed4236b6c6e1395b2fc7de5fed364' #treasury of unitbox platform
    

    #pair in pancacke Niftsy-usdt 0xF21dBE91Af373c0a6d0Ad7099AfeBdF7B777d605 (bsc)
    router = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
    factory = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'

    #unitbox.settreasury(accounts[3], {"from": accounts[0],  "gas_price": price})
    #unitbox.setTokenDex(niftsy.address, (1, unitbox.dexForChain()[0], True), {"from": accounts[0], "gas_price": price})
    #unitbox.setDexForChain((unitbox.UniswapV2Router02(), unitbox.UniswapV2Factory(), '0xc778417E063141139Fce010982780140Aa0cD5Ab', usdt.address), {"from": accounts[0], "gas_price": price} )
    #unitbox.setSignerState(ORACLE_ADDRESS, True, {'from':accounts[0], "gas_price": price})

    #wl_data = (False, True, False, techERC20.address)
    #whitelist.setWLItem((2, niftsy.address), wl_data, {"from": accounts[0], "gas_price": price})

    
    #mint original nft erc721
    erc721mock.mint(accounts[1], {"from": accounts[1], "gas_price": price})
    erc721mock_nft_id = erc721mock.lastNFTId()
    #make allowance to use original NFT
    erc721mock.approve(wrapper.address, erc721mock_nft_id,  {"from": accounts[1], "gas_price": price})
   

    erc721_property = (in_type, erc721mock.address)
    erc721_data = (erc721_property, erc721mock_nft_id, 0)
    royalty=[
        (accounts[1], 4000), # investor
        (accounts[2], 5000), # scolar
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

    hashed_msg = unitbox.prepareMessage(
        Web3.toChecksumAddress(erc721mock.address), 
        Web3.toInt(erc721mock_nft_id),
        royalty, 
        Web3.toChecksumAddress(accounts[0].address), 
        Web3.toInt(nonce)    #change nonce every time!!!
    )
    print('hashed_msg = {}'.format(hashed_msg))
    # Ether style signature
    message = encode_defunct(primitive=hashed_msg)
    print('message = {}'.format(message))
    signed_message = web3.eth.account.sign_message(message, private_key=ORACLE_PRIVATE_KEY)
    print('sign_message is {}'.format(signed_message))
    ####################################
    

    #try to wrap with bad nonce
    try:
        unitbox.wrapForRent(inData, 0, signed_message.signature, {"from": accounts[0], "gas_price": price})    
    except ValueError as ve:
        print(ve)
    
    #wrap
    tx = unitbox.wrapForRent(inData, nonce, signed_message.signature, {"from": accounts[0], "gas_price": price})
    wTokenId = wrapper.lastWNFTId(out_type)[1]
    wNFT = wrapper.getWrappedToken(wnft721, wTokenId)   
    print(wTokenId)

    wnft_pretty_print(wrapper, wnft721, wTokenId)
    
    #checks
    assert erc721mock.ownerOf(erc721mock_nft_id) == wrapper.address
    assert wnft721.ownerOf(wTokenId) == accounts[2].address # owner of wnft is scholar

    #add collateral - niftsy. niftsy has DEX
    niftsy.approve(wrapper.address, coll_amount, {"from": accounts[0], "gas_price": price})

    wrapper.addCollateral(wnft721.address, wTokenId, [((2, niftsy.address), 0, coll_amount )], {"from": accounts[0], "gas_price": price})
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy.address, 0)[0] == coll_amount

    #claim collateral niftsy
    before_niftsy_balance1 = niftsy.balanceOf(accounts[1])
    before_niftsy_balance2 = niftsy.balanceOf(accounts[2])
    before_niftsy_treasury = niftsy.balanceOf(treasury)
    before_usdt_treasury = usdt.balanceOf(treasury)
    wrapper.removeERC20Collateral(wnft721.address, wTokenId, niftsy.address, {"from": accounts[1], "gas_price": price}) #by investor

    assert niftsy.balanceOf(accounts[1]) == before_niftsy_balance1 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][0][1]/10000
    assert niftsy.balanceOf(accounts[2]) == before_niftsy_balance2 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][1][1]/10000
    assert niftsy.balanceOf(unitbox.address) == before_niftsy_treasury + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][2][1]/10000
    assert before_usdt_treasury == usdt.balanceOf(treasury)
    assert niftsy.balanceOf(wrapper.address) == 0
    print(niftsy.balanceOf(unitbox.address))
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy.address, 0)[0] == 0

    #swap
    before_niftsy_treasury = niftsy.balanceOf(treasury)
    before_usdt_treasury = usdt.balanceOf(treasury)
    unitbox.swapMeWithPath(niftsy.address, [niftsy.address, busd, unitbox.dexForChain()[2], usdt.address], {"from": accounts[0], "gas_price": price})

    assert niftsy.balanceOf(unitbox.address) == 0
    assert before_usdt_treasury < usdt.balanceOf(treasury)

    unitbox.unWrap(wnft721.address, wTokenId, {"from": accounts[2]}) #by scholar

    assert erc721mock.ownerOf(erc721mock_nft_id) == accounts[1]



