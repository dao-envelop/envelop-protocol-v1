from brownie import *
import json

if  web3.eth.chain_id in [4, 5, 97, 1313161555]:
    # Testnets
    #private_key='???'
    accounts.load('tzero');
elif web3.eth.chain_id in [1,56,137, 1313161554]:
    accounts.load('env_amm1')
    accounts.load('env_amm2')
    accounts.load('env_amm3')
    
    pass
#else:
    #my local ganache
    # Mainnet
    #private_key=input('PLease input private key for deployer address..:')
#accounts.clear()    
#accounts.add(private_key)



print('mm:{}'.format(accounts))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))

ETH_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x7728cd70b3dD86210e2bd321437F448231B81733', #NIFTSI ERC20
'0x6b175474e89094c44da98b954eedeac495271d0f',  #DAI
'0xdAC17F958D2ee523a2206206994597C13D831ec7',  #USDT
'0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  #USDC
]

ETH_RINKEBY_ERC20_COLLATERAL_TOKENS = [
'0x1E991eA872061103560700683991A6cF88BA0028', #NIFTSI ERC20
'0xc7ad46e0b8a400bb3c915120d284aafba8fc4735',  #DAI
'0xc778417e063141139fce010982780140aa0cd5ab',  #WETH
]

BSC_TESTNET_ERC20_COLLATERAL_TOKENS = [
'0xCEFe82aDEd5e1f8c2610256629d651840601EAa8', #NIFTSI ERC20
]

BSC_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3',  #DAI
'0x55d398326f99059fF775485246999027B3197955',  #USDT
'0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',  #USDC
'0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',  #BUSD
'0x7728cd70b3dD86210e2bd321437F448231B81733'   #NIFTSY
]

POLYGON_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',  #DAI
'0xc2132D05D31c914a87C6611C10748AEb04B58e8F',  #USDT
'0x2791bca1f2de4661ed88a30c99a7a9449aa84174',  #USDC
'0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',  #WETH
'0x432cdbC749FD96AA35e1dC27765b23fDCc8F5cf1' # NIFTSY
]

AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS = [
'0xba7deebbfc5fa1100fb055a87773e1e99cd3507a',  #DAI
'0xde3a24028580884448a5397872046a019649b084',  #USDT
]

TRON_MAIN_ERC20_COLLATERAL_TOKENS = [
'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',  #USDT
]

AURORA_MAIN_ERC20_TOKENS = [
'0x4988a896b1227218e4A686fdE5EabdcAbd91571f' #USDT
]

AURORA_TEST_ERC20_TOKENS = [
'0x20e30c7c1295FCD1A78528078b83aaf16C5CE032', #NIFTSY MOCK
'0x9e70345a1b3D2D55FB29be4aDbd2A6E38eE57D83'  #WETH
]



CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io', 'enabled_erc20': ETH_MAIN_ERC20_COLLATERAL_TOKENS},
    4:{'explorer_base':'rinkeby.etherscan.io','enabled_erc20': ETH_RINKEBY_ERC20_COLLATERAL_TOKENS},
    56:{
        'explorer_base':'bscscan.com', 
        'enabled_erc20': BSC_MAIN_ERC20_COLLATERAL_TOKENS,
        'uswp_router': '0x10ed43c718714eb63d5aa57b78b54704e256024e',
        'uswp_factory': '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73',
        'in_asset_address':   '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56', # busd
        'niftsy_address': '0x7728cd70b3dD86210e2bd321437F448231B81733'

    },
    97:{'explorer_base':'testnet.bscscan.com', 'enabled_erc20': BSC_TESTNET_ERC20_COLLATERAL_TOKENS},
    137:{
        'explorer_base':'polygonscan.com', 
        'enabled_erc20': POLYGON_MAIN_ERC20_COLLATERAL_TOKENS,
        'uswp_router': '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
        'uswp_factory': '0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32',
        #'in_asset_address':   '0x2791bca1f2de4661ed88a30c99a7a9449aa84174', # usdc
        'in_asset_address':   '0xc2132D05D31c914a87C6611C10748AEb04B58e8F', # usdt
        'niftsy_address': '0x432cdbC749FD96AA35e1dC27765b23fDCc8F5cf1'
    },
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network', 'enabled_erc20': AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS},
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },
    1313161555:{'explorer_base':'testnet.aurorascan.dev', },
    1313161554:{'explorer_base':'aurorascan.dev', },

}.get(web3.eth.chainId, {'explorer_base':'io'})
print(CHAIN)
tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4, 5, 137]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}
# elif web3.eth.chainId in  [1313161555, 1313161554]:    
#     tx_params={'from':accounts[0], 'allow_revert': True, 'gas_limit': 10e7}
BUY_AMOUNT_USD = 1
def main():
    inasset = interface.ERC20(CHAIN['in_asset_address'])
    niftsy = interface.ERC20(CHAIN['niftsy_address'])
    path = [CHAIN['in_asset_address'],CHAIN['niftsy_address']]
    router = interface.IUniswapV2Router02(CHAIN['uswp_router'])
    factory = interface.IUniswapV2Factory(CHAIN['uswp_factory'])
    pair = factory.getPair(CHAIN['in_asset_address'],CHAIN['niftsy_address'])
    for a in accounts:
        tx_params = {'from':a}
        if web3.eth.chainId in  [1,4, 5, 137]:
            tx_params={'from':a, 'priority_fee': chain.priority_fee}
        if inasset.allowance(router, a) < BUY_AMOUNT_USD * 10 ** inasset.decimals():
            inasset.approve(router, BUY_AMOUNT_USD * 10 ** inasset.decimals(), tx_params)
            router.swapExactTokensForTokens(
                BUY_AMOUNT_USD * 10 ** inasset.decimals(), 
                0, path, a, chain.time() + 360, tx_params
        )
    

