from brownie import *
import json

if  web3.eth.chain_id in [4, 5, 97]:
    # Testnets
    #private_key='???'
    accounts.load('tzero');
elif web3.eth.chain_id in [1,56,137]:
    accounts.load('envdeployer')
    
    pass
#else:
    #my local ganache
    # Mainnet
    #private_key=input('PLease input private key for deployer address..:')
#accounts.clear()    
#accounts.add(private_key)



print('Deployer:{}, balance: {} eth'.format(accounts[0],Wei(accounts[0].balance()).to('ether') ))
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

ETH_GOERLI_ERC20_COLLATERAL_TOKENS = [
'0x376e8EA664c2E770E1C45ED423F62495cB63392D', #NIFTSI ERC20
'0x11fE4B6AE13d2a6055C8D9cF65c55bac32B5d844'  #DAI
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

ORACLE_SIGNERS = [
    '0xf4321b36e42bd79384116545d80873057d633b87',
    '0xfa293c97653b542a387539d2fad1c64cafbdd729'
]



CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io', 'enabled_erc20': ETH_MAIN_ERC20_COLLATERAL_TOKENS},
    4:{'explorer_base':'rinkeby.etherscan.io','enabled_erc20': ETH_RINKEBY_ERC20_COLLATERAL_TOKENS},
    5:{'explorer_base':'goerli.etherscan.io','enabled_erc20': ETH_GOERLI_ERC20_COLLATERAL_TOKENS},
    56:{'explorer_base':'bscscan.com', 'enabled_erc20': BSC_MAIN_ERC20_COLLATERAL_TOKENS},
    97:{'explorer_base':'testnet.bscscan.com', 'enabled_erc20': BSC_TESTNET_ERC20_COLLATERAL_TOKENS},
    137:{'explorer_base':'polygonscan.com', 'enabled_erc20': POLYGON_MAIN_ERC20_COLLATERAL_TOKENS},
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network', 'enabled_erc20': AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS},
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },

}.get(web3.eth.chainId, {'explorer_base':'io'})
print(CHAIN)
tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4,5]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

def main():
    print('Deployer account= {}'.format(accounts[0]))
    mint1155 = EnvelopUsers1155Swarm.deploy(
        "Envelop Users NFT 1155", 
        "eNFT", 'https://swarm.envelop.is/bzz/', 
        100,
        tx_params
    )
    mint721 = EnvelopUsers721SwarmEnum.deploy(
        "Envelop Users NFT 721", 
        "eNFT", 'https://swarm.envelop.is/bzz/',
        100, 
        tx_params
    )

    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("mint721 = EnvelopUsers721SwarmEnum.at('{}')".format(mint721.address))
    print("mint1155 = EnvelopUsers1155Swarm.at('{}')".format(mint1155.address))
    
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],mint721))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],mint1155))

    for s in ORACLE_SIGNERS:
        mint721.setSignerStatus(s, True, tx_params)
        mint1155.setSignerStatus(s, True, tx_params)

    if  web3.eth.chainId in [1,4, 5, 56, 137, 43114]:
        EnvelopUsers721SwarmEnum.publish_source(mint721);
        EnvelopUsers1155Swarm.publish_source(mint1155);

    
