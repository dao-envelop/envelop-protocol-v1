from brownie import *
import json

if  web3.eth.chain_id in [4, 5, 97, 11155111]:
    # Testnets
    #private_key='???'
    accounts.load('ttwo');
    #accounts.load('secret2');
elif web3.eth.chain_id in [1,56,137, 42161]:
    accounts.load('envdeployer')



print('Deployer:{}, balance: {} eth'.format(accounts[0],Wei(accounts[0].balance()).to('ether') ))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))


CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io'},
    4:{'explorer_base':'rinkeby.etherscan.io'},
    5:{'explorer_base':'goerli.etherscan.io'},
    56:{
        'explorer_base':'bscscan.com',
        'users_sbt_collection_registry':'0x41d7aeDb4FE67fe00B5a7Bc842f78aCC03927470',
    },
    97:{'explorer_base':'testnet.bscscan.com'},
    137:{
        'explorer_base':'polygonscan.com',
        'users_sbt_collection_registry':'0xed5A643370467De27984A3B92565A02187413604',
    },
    42161:{
        'explorer_base':'arbiscan.io',
        'users_sbt_collection_registry':'0xc4e4Cf661A0B9878588E3fE49eF4e1244894cf81',
    },
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network'},
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },
    11155111:{
        'explorer_base':'sepolia.etherscan.io', 
        'subscription_registry': '0xbdE298FcD625d77C30CB6F1Ad661a6CA4F41aE67',
        'users_sbt_collection_registry':'0x1C6568b1858C05F0229fadE7B01C473436Ab93B1'
    }

}.get(web3.eth.chainId, {
    'explorer_base':'io', 'users_sbt_collection_registry':'0xc4e4Cf661A0B9878588E3fE49eF4e1244894cf81'
})
print(CHAIN)
tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4,5, 137, 42161, 11155111]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

def main():
    wrapper   = WrapperUsersV1.deploy(CHAIN['users_sbt_collection_registry'],tx_params) 
    print("**WrapperUsersV1**")
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wrapper))
    print("\n```python")
    print("wrapper = WrapperUsersV1.at('{}')".format(wrapper.address))
    print("```")
    
    if  web3.eth.chainId in [1,4, 5, 56, 137, 42161, 43114, 11155111]:
        WrapperUsersV1.publish_source(wrapper);



