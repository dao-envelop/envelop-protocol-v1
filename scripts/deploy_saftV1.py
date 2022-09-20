from brownie import *
import json

accounts.load('secret2')
ORACLE_ADDRESS = '0x8125F522a712F4aD849E6c7312ba8263bEBeEFeD' 

print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))

ETH_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x7728cd70b3dD86210e2bd321437F448231B81733', #NIFTSI ERC20
'0x6b175474e89094c44da98b954eedeac495271d0f',  #DAI
'0xdAC17F958D2ee523a2206206994597C13D831ec7',  #USDT
'0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  #USDC
]

ETH_RINKEBY_ERC20_COLLATERAL_TOKENS = [
'0x3125B3b583D576d86dBD38431C937F957B94B47d', #NIFTSI ERC20
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
]

POLYGON_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',  #DAI
'0xc2132D05D31c914a87C6611C10748AEb04B58e8F',  #USDT
'0x2791bca1f2de4661ed88a30c99a7a9449aa84174',  #USDC
'0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619'   #WETH
]

AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS = [
'0xba7deebbfc5fa1100fb055a87773e1e99cd3507a',  #DAI
'0xde3a24028580884448a5397872046a019649b084',  #USDT
]

TRON_MAIN_ERC20_COLLATERAL_TOKENS = [
'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',  #USDT
]

CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io', 'enabled_erc20': ETH_MAIN_ERC20_COLLATERAL_TOKENS},
    4:{'explorer_base':'rinkeby.etherscan.io','enabled_erc20': ETH_RINKEBY_ERC20_COLLATERAL_TOKENS},
    56:{'explorer_base':'bscscan.com', 'enabled_erc20': BSC_MAIN_ERC20_COLLATERAL_TOKENS},
    97:{'explorer_base':'testnet.bscscan.com', 'enabled_erc20': BSC_TESTNET_ERC20_COLLATERAL_TOKENS},
    137:{'explorer_base':'polygonscan.com', 'enabled_erc20': POLYGON_MAIN_ERC20_COLLATERAL_TOKENS},
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network', 'enabled_erc20': AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS},
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },

}.get(web3.eth.chainId, {'explorer_base':'io'})
print(CHAIN)

tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

def main():

    saftV1 = BatchWorker.deploy(tx_params)
    techERC20 = TechTokenV1.deploy(tx_params)
    whitelist = AdvancedWhiteList.deploy(tx_params)
    wrapperTrustedV1 = TrustedWrapper.deploy(techERC20.address, saftV1.address, tx_params)

    wnft1155 = EnvelopwNFT1155.deploy(
        'ENVELOP 1155 wNFT Collection', 
        'wNFT', 
        'https://api.envelop.is/metadata/',
        tx_params
    )
    
    wnft721 = EnvelopwNFT721.deploy(
        'ENVELOP 721 wNFT Collection', 
        'wNFT', 
        'https://api.envelop.is/metadata/',
        tx_params
    )

    #make settings of contracts
    wnft1155.setMinterStatus(wrapperTrustedV1.address, tx_params)
    wnft721.setMinter(wrapperTrustedV1.address, tx_params)
    wrapperTrustedV1.setWNFTId(3, wnft721.address, 1, tx_params)
    wrapperTrustedV1.setWNFTId(4, wnft1155.address,1, tx_params)
    wrapperTrustedV1.setWhiteList(whitelist.address, tx_params)
    saftV1.setTrustedWrapper(wrapperTrustedV1.address, tx_params)


    if  web3.eth.chainId in [1,4, 137, 43114]:
        TechTokenV1.publish_source(techERC20);
        BatchWorker.publish_source(saftV1);
        EnvelopwNFT1155.publish_source(wnft1155);
        EnvelopwNFT721.publish_source(wnft721);
        AdvancedWhiteList.publish_source(whitelist);
        TrustedWrapper.publish_source(wrapperTrustedV1);

    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("techERC20 = TechTokenV1.at('{}')".format(techERC20.address))
    print("saftV1 = BatchWorker.at('{}')".format(saftV1.address))
    print("wrapperTrustedV1 = TrustedWrapper.at('{}')".format(wrapperTrustedV1.address))
    print("wnft1155 = EnvelopwNFT1155.at('{}')".format(wnft1155.address))
    print("wnft721 = EnvelopwNFT721.at('{}')".format(wnft721.address))
    print("whitelist = AdvancedWhiteList.at('{}')".format(whitelist.address))

    if len(CHAIN.get('enabled_erc20', [])) > 0:
        print('Enabling collateral...')
        for erc in CHAIN.get('enabled_erc20', []):
            whitelist.setWLItem((2,erc), (True, True, True, techERC20) ,tx_params)


    #rinkeby 
    '''saftV1 = BatchWorker.at('0x5a5e87171f7bD5639fe2D52d5D62449c3f606e82')
    techERC20 = TechTokenV1.at('0xD0e558D267EfF3CD6F1606e31C1a455647C4D69F')
    wrapperTrustedV1 = TrustedWrapper.at('0x5e6eF1a7cEAf72c73D8673948194d625b787452b')
    wnft1155 = EnvelopwNFT1155.at('0x1b0CFfc3b108Bb6544708dF3be5ea24709455251')
    wnft721 = EnvelopwNFT721.at('0xc1d74221320be821a5BBBD684d2F1F7332daAD65')
    whitelist = AdvancedWhiteList.at('0x6bD6568BB566fFD1d4a32c3AB5c1231621ab4B87')'''


