import pytest
import logging
from brownie import *
from web3 import Web3
from eth_abi import encode_single
from eth_account.messages import encode_defunct

###wrap, add Collateral, claim and swap through direct swap pair, unwrap

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
    #pancakeswap Niftsy/USDT 0xF21dBE91Af373c0a6d0Ad7099AfeBdF7B777d605

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
    niftsy20 = TokenMock.at('0x7728cd70b3dD86210e2bd321437F448231B81733') #swapable token
    erc721mock = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')
    usdt = TokenMock.at('0x55d398326f99059fF775485246999027B3197955') #tresury token
    busd = TokenMock.at('0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56') #unswapable token

    treasury = '0x2cccf64bf6eed4236b6c6e1395b2fc7de5fed364' #treasury of unitbox platform
    

    #pair in pancacke Niftsy-usdt 0xF21dBE91Af373c0a6d0Ad7099AfeBdF7B777d605 (bsc)
    router = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
    factory = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'
    

    #settings 
    #unitbox.settreasury(accounts[3], {"from": accounts[0],  "gas_price": price})
    #unitbox.setTokenDex(niftsy20.address, (1, router, True), {"from": accounts[0], "gas_price": price})
    #unitbox.setDexForChain((router, factory, '0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6', usdt.address), {"from": accounts[0], "gas_price": price} )
    #unitbox.setSignerState(ORACLE_ADDRESS, True, {'from':accounts[0], "gas_price": price})
    #unitbox.setWrapRule('0x0006', {"from": accounts[0], "gas_price": price})

    #wl_data = (False, True, False, techERC20.address)
    #whitelist.setWLItem((2, busd), wl_data, {"from": accounts[0], "gas_price": price})
    #wrapper.setTrustedAddress(unitbox.address, True, {"from": accounts[0], "gas_price": price})
    
    
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

    #add collateral - niftsy. Niftsy has DEX
    niftsy20.approve(wrapper.address, coll_amount, {"from": accounts[0], "gas_price": price})

    wrapper.addCollateral(wnft721.address, wTokenId, [((2, niftsy20.address), 0, coll_amount )], {"from": accounts[0], "gas_price": price})
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == coll_amount
    
    
    #claim And Swap collateral niftsy
    before_niftsy_balance1 = niftsy20.balanceOf(accounts[1])
    before_niftsy_balance2 = niftsy20.balanceOf(accounts[2])
    before_niftsy_treasury = niftsy20.balanceOf(treasury)
    before_usdt_treasury = usdt.balanceOf(treasury)
    print(before_niftsy_balance1)
    
    unitbox.claimAndSwap(wnft721.address, wTokenId, niftsy20.address, {"from": accounts[1], "gas_price": price}) #by investor
    assert niftsy20.balanceOf(accounts[1]) == before_niftsy_balance1 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][0][1]/10000
    assert niftsy20.balanceOf(accounts[2]) == before_niftsy_balance2 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][1][1]/10000
    assert niftsy20.balanceOf(treasury) == before_niftsy_treasury
    assert before_usdt_treasury < usdt.balanceOf(treasury)
    assert niftsy20.balanceOf(unitbox.address) == 0
    print(niftsy20.balanceOf(unitbox.address))
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0
    
    
    #add collateral - busd tokens. busd does not have DEX
    busd.approve(wrapper.address, coll_amount, {"from": accounts[0], "gas_price": price})
    wrapper.addCollateral(wnft721.address, wTokenId, [((2, busd.address), 0, coll_amount )], {"from": accounts[0], "gas_price": price})    

    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, busd.address, 0)[0] == coll_amount
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, busd.address, 0)[1] == 1 #index
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[1] == 0 #index
    assert busd.balanceOf(wrapper.address) == coll_amount
    assert niftsy20.balanceOf(unitbox.address) == 0
    assert len(wrapper.getWrappedToken(wnft721.address, wTokenId)[1]) == 2

    
    #add collateral - niftsy tokens again
    niftsy20.approve(wrapper.address, coll_amount, {"from": accounts[0]})
    before_niftsy_balanceW = niftsy20.balanceOf(wrapper.address)
    wrapper.addCollateral(wnft721.address, wTokenId, [((2, niftsy20.address), 0, coll_amount )], {"from": accounts[0], "gas_price": price})
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == coll_amount
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[1] == 0
    assert niftsy20.balanceOf(unitbox.address) == 0
    assert niftsy20.balanceOf(wrapper.address) == before_niftsy_balanceW + coll_amount
    assert len(wrapper.getWrappedToken(wnft721.address, wTokenId)[1]) == 2
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, busd.address, 0)[0] == coll_amount
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, busd.address, 0)[1] == 1
    assert busd.balanceOf(wrapper.address) == coll_amount
    print(accounts[2].balance())

    #claim And Swap again collateral niftsy
    before_balance0 = niftsy20.balanceOf(accounts[0])
    before_niftsy_balance1 = niftsy20.balanceOf(accounts[1])
    before_niftsy_balance2 = niftsy20.balanceOf(accounts[2])
    before_niftsy_treasury = niftsy20.balanceOf(treasury)
    before_usdt_treasury = usdt.balanceOf(treasury)
    unitbox.claimAndSwap(wnft721.address, wTokenId, niftsy20.address, {"from": accounts[2], "gas_price": price})  #by scholar
    assert niftsy20.balanceOf(accounts[1]) == before_niftsy_balance1 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][0][1]/10000
    assert niftsy20.balanceOf(accounts[2]) == before_niftsy_balance2 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][1][1]/10000
    assert niftsy20.balanceOf(accounts[3]) == before_niftsy_treasury
    assert before_usdt_treasury < usdt.balanceOf(treasury)
    assert niftsy20.balanceOf(unitbox.address) == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0
    assert busd.balanceOf(wrapper.address) == coll_amount
    assert len(wrapper.getWrappedToken(wnft721.address, wTokenId)[1]) == 2
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[1] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, busd.address, 0)[0] == coll_amount
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, busd.address, 0)[1] == 1


    #try to claim and swap when there are not niftsy in collateral of wnft
    try:
        unitbox.claimAndSwap(wnft721.address, wTokenId, niftsy20.address, {"from": accounts[2]})
    except ValueError as ve:
        print(ve)

    #try to unwrap by not investor and not scholar
    try:
        unitbox.unWrap(wnft721.address, wTokenId, {"from": accounts[3]})
    except ValueError as ve:
        print(ve)

    #try to unwrap when there are any erc20 tokens in collateral of wnft
    try:
        unitbox.unWrap(wnft721.address, wTokenId, {"from": accounts[1]}) #by investor
    except ValueError as ve:
        print(ve)

    
    #claim collateral busd
    before_busd_balance1 = busd.balanceOf(accounts[1])
    before_busd_balance2 = busd.balanceOf(accounts[2])
    before_busd_balanceU = busd.balanceOf(unitbox.address)
    wrapper.removeERC20Collateral(wnft721.address, wTokenId, busd.address, {"from": accounts[1], "gas_price": price}) #by investor
    assert busd.balanceOf(accounts[1]) == before_busd_balance1 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][0][1]/10000
    assert busd.balanceOf(accounts[2]) == before_busd_balance2 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][1][1]/10000
    assert busd.balanceOf(unitbox.address) == before_busd_balanceU + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][2][1]/10000
    assert busd.balanceOf(wrapper.address) == 0
    assert len(wrapper.getWrappedToken(wnft721.address, wTokenId)[1]) == 2
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[1] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, busd.address, 0)[0] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, busd.address, 0)[1] == 1

    
    #investor unwraps wnft
    unitbox.unWrap(wnft721.address, wTokenId, {"from": accounts[1], "gas_price": price}) #by investor

    assert erc721mock.ownerOf(erc721mock_nft_id) == accounts[1]

    #try to withdraw busd tokens from unitbox platform by not owner
    try:
        unitbox.withdrawTokens(busd.address, {"from": accounts[1]})
    except ValueError as ve:
        print(ve)

    '''before_busd_balance0 = busd.balanceOf(accounts[0])
    before_busd_balanceU = busd.balanceOf(unitbox.address)
    unitbox.withdrawTokens(busd.address, {"from": accounts[0], "gas_price": price})

    #check - owner gets all tokens 
    assert busd.balanceOf(unitbox.address) == 0
    assert busd.balanceOf(accounts[0]) == before_busd_balance0 + before_busd_balanceU'''






   
