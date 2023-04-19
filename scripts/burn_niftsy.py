from brownie import *
import json

if  web3.eth.chain_id in [4, 5, 97, 1313161555]:
    # Testnets
    #private_key='???'
    accounts.load('ttwo');
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



CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io'},
    4:{'explorer_base':'rinkeby.etherscan.io'},
    56:{
        'explorer_base':'bscscan.com', 
        'uswp_router': '0x10ed43c718714eb63d5aa57b78b54704e256024e',
        'uswp_factory': '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73',
        'in_asset_address':   '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56', # busd
        'niftsy_address': '0x7728cd70b3dD86210e2bd321437F448231B81733'

    },
    97:{'explorer_base':'testnet.bscscan.com', },
    137:{
        'explorer_base':'polygonscan.com', 
        'uswp_router': '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
        'uswp_factory': '0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32',
        'in_asset_address':   '0x2791bca1f2de4661ed88a30c99a7a9449aa84174', # usdc
        'niftsy_address': '0x432cdbC749FD96AA35e1dC27765b23fDCc8F5cf1'
    },
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network'},
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },
    1313161555:{'explorer_base':'testnet.aurorascan.dev', },
    1313161554:{'explorer_base':'aurorascan.dev', },

}.get(web3.eth.chainId, {'explorer_base':'io'})
print(CHAIN)
tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4, 5, 137]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

eee_address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
def main():
    niftsy = interface.ERC20(CHAIN['niftsy_address'])
    for a in accounts:
        tx_params['from'] = a
        burn_amount = niftsy.balanceOf(a)
        tx= niftsy.transfer(eee_address, burn_amount, tx_params)
        print('https://{}/tx/{} \n{}'.format(
            CHAIN['explorer_base'],
            tx.txid, 
            Wei(burn_amount).to('ether')
        ))
    

