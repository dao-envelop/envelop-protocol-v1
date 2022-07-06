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
    nonce = 4  ##increase nonce!!

    techERC20 = TechTokenV1.at('0xf84cb379Cb536732AFc737921B4EF97390db92eD')
    wrapper = TrustedWrapperRemovable.at('0x522aCbA649165FFB287Bd1cdF2dd85429E4dcD49')
    wnft1155 = EnvelopwNFT1155.at('0x03C496376043259284Ca152D91b8d416Fd125b0d')
    wnft721 = EnvelopwNFT721.at('0x3b24709991c7A9D1FCC0743Dc8C607D5fb779e5C')
    whitelist = AdvancedWhiteList.at('0xa3F83E9Cf253EDc4E26e63F050ceB2D41eb27b26')
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
    before_niftsy_balance3 = niftsy20.balanceOf(accounts[3])
    before_usdt_balance3 = usdt.balanceOf(accounts[3])
    
    unitbox.claimAndSwap(wnft721.address, wTokenId, niftsy20.address, {"from": accounts[1], "gas_price": price}) #by investor
    assert niftsy20.balanceOf(accounts[1]) == before_niftsy_balance1 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][0][1]/10000
    assert niftsy20.balanceOf(accounts[2]) == before_niftsy_balance2 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][1][1]/10000
    assert niftsy20.balanceOf(accounts[3]) == before_niftsy_balance3
    assert before_usdt_balance3 < usdt.balanceOf(accounts[3])
    assert niftsy20.balanceOf(unitbox.address) == 0
    print(niftsy20.balanceOf(unitbox.address))
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0

    #add collateral - dai tokens. DAI does not have DEX
    dai.approve(wrapper.address, coll_amount, {"from": accounts[0]})
    wrapper.addCollateral(wnft721.address, wTokenId, [((2, dai.address), 0, coll_amount )], {"from": accounts[0], "gas_price": price})    

    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, dai.address, 0)[0] == coll_amount
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, dai.address, 0)[1] == 1 #index
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[1] == 0 #index
    assert dai.balanceOf(wrapper.address) == coll_amount
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
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, dai.address, 0)[0] == coll_amount
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, dai.address, 0)[1] == 1
    assert dai.balanceOf(wrapper.address) == coll_amount
    print(accounts[2].balance())
    #claim And Swap again collateral niftsy
    before_balance0 = niftsy20.balanceOf(accounts[0])
    before_niftsy_balance1 = niftsy20.balanceOf(accounts[1])
    before_niftsy_balance2 = niftsy20.balanceOf(accounts[2])
    before_niftsy_balance3 = niftsy20.balanceOf(accounts[3])
    before_usdt_balance3 = usdt.balanceOf(accounts[3])
    unitbox.claimAndSwap(wnft721.address, wTokenId, niftsy20.address, {"from": accounts[2], "gas_price": price})  #by scholar
    assert niftsy20.balanceOf(accounts[1]) == before_niftsy_balance1 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][0][1]/10000
    assert niftsy20.balanceOf(accounts[2]) == before_niftsy_balance2 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][1][1]/10000
    assert niftsy20.balanceOf(accounts[3]) == before_niftsy_balance3
    assert before_usdt_balance3 < usdt.balanceOf(accounts[3])
    assert niftsy20.balanceOf(unitbox.address) == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0
    assert dai.balanceOf(wrapper.address) == coll_amount
    assert len(wrapper.getWrappedToken(wnft721.address, wTokenId)[1]) == 2
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[1] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, dai.address, 0)[0] == coll_amount
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, dai.address, 0)[1] == 1


    #try to claim and swap when there are niftsy in collateral in collateral of wnft
    try:
        unitbox.claimAndSwap(wnft721.address, wTokenId, niftsy20.address, {"from": accounts[2]})
    except ValueError as ve:
        print(ve)

    #try to unwrap by not investor and not scholar
    try:
        unitbox.unWrap(wnft721.address, wTokenId, {"from": accounts[3]})
    except ValueError as ve:
        print(ve)

    #try to unwrap when there are erc20 tokens in collateral of wnft
    try:
        unitbox.unWrap(wnft721.address, wTokenId, {"from": accounts[1]}) #by investor
    except ValueError as ve:
        print(ve)


    #claim collateral dai
    before_dai_balance1 = dai.balanceOf(accounts[1])
    before_dai_balance2 = dai.balanceOf(accounts[2])
    before_dai_balanceU = dai.balanceOf(unitbox.address)
    wrapper.removeERC20Collateral(wnft721.address, wTokenId, dai.address, {"from": accounts[1], "gas_price": price}) #by investor
    assert dai.balanceOf(accounts[1]) == before_dai_balance1 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][0][1]/10000
    assert dai.balanceOf(accounts[2]) == before_dai_balance2 + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][1][1]/10000
    assert dai.balanceOf(unitbox.address) == before_dai_balanceU + coll_amount*wrapper.getWrappedToken(wnft721.address, wTokenId)[5][2][1]/10000
    assert dai.balanceOf(wrapper.address) == 0
    assert len(wrapper.getWrappedToken(wnft721.address, wTokenId)[1]) == 2
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[0] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, niftsy20.address, 0)[1] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, dai.address, 0)[0] == 0
    assert wrapper.getCollateralBalanceAndIndex(wnft721.address, wTokenId, 2, dai.address, 0)[1] == 1


    #investor unwraps wnft
    unitbox.unWrap(wnft721.address, wTokenId, {"from": accounts[1], "gas_price": price}) #by investor

    assert erc721mock.ownerOf(erc721mock_nft_id) == accounts[1]

    #try to withdraw dai tokens from unitbox platform by not owner
    try:
        unitbox.withdrawTokens(dai.address, {"from": accounts[1]})
    except ValueError as ve:
        print(ve)

    before_dai_balance0 = dai.balanceOf(accounts[0])
    before_dai_balanceU = dai.balanceOf(unitbox.address)
    unitbox.withdrawTokens(dai.address, {"from": accounts[0], "gas_price": price})

    #check - owner gets all tokens 
    assert dai.balanceOf(unitbox.address) == 0
    assert dai.balanceOf(accounts[0]) == before_dai_balance0 + before_dai_balanceU






   