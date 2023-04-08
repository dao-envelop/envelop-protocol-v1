from brownie import *
import json
import time


if  web3.eth.chain_id in [4, 5, 97]:
    # Testnets
    #private_key='???'
    accounts.load('ttwo');
elif web3.eth.chain_id in [1,56,137, 42161]:
    accounts.load('env_unitbox')


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

ETH_ROPSTEN_ERC20_COLLATERAL_TOKENS = [
(2,'0x376e8EA664c2E770E1C45ED423F62495cB63392D'), #NIFTSI ERC20
(2,'0xad6d458402f60fd3bd25163575031acdce07538d'),  #DAI
(2,'0xc778417E063141139Fce010982780140Aa0cD5Ab')  #WETH
]

ETH_GOERLI_ERC20_COLLATERAL_TOKENS = [
(2,'0x376e8EA664c2E770E1C45ED423F62495cB63392D'), #NIFTSI ERC20
(2,'0x11fE4B6AE13d2a6055C8D9cF65c55bac32B5d844'),  #DAI
(2,'0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6')  #WETH
]

BSC_TESTNET_ERC20_COLLATERAL_TOKENS = [
'0xCEFe82aDEd5e1f8c2610256629d651840601EAa8', #NIFTSI ERC20
]

BSC_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x7728cd70b3dD86210e2bd321437F448231B81733', #NIFTSI ERC20
'0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3',  #DAI
'0x55d398326f99059fF775485246999027B3197955',  #USDT
'0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',  #USDC
'0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
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
    3:{'explorer_base':'ropsten.etherscan.io','enabled_erc20': ETH_ROPSTEN_ERC20_COLLATERAL_TOKENS},
    4:{'explorer_base':'rinkeby.etherscan.io','enabled_erc20': ETH_RINKEBY_ERC20_COLLATERAL_TOKENS},
    5:{'explorer_base':'goerli.etherscan.io','enabled_erc20': ETH_GOERLI_ERC20_COLLATERAL_TOKENS},
    56:{'explorer_base':'bscscan.com', 'enabled_erc20': BSC_MAIN_ERC20_COLLATERAL_TOKENS},
    65:{'explorer_base': 'www.oklink.com/okc-test',},
    66:{'explorer_base': 'www.oklink.com/okc',},
    97:{'explorer_base':'testnet.bscscan.com', 'enabled_erc20': BSC_TESTNET_ERC20_COLLATERAL_TOKENS},
    137:{'explorer_base':'polygonscan.com', 'enabled_erc20': POLYGON_MAIN_ERC20_COLLATERAL_TOKENS},
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network', 'enabled_erc20': AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS},
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },

}.get(web3.eth.chainId, {'explorer_base':'io'})
print(CHAIN)
tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,3,4,5]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}
elif web3.eth.chainId in  [65, 66]:    
    tx_params={'from':accounts[0], 'allow_revert': True}

def main():
    print('Deployer account= {}'.format(accounts[0]))
    techERC20 = TechTokenV1.deploy(tx_params)
    #techERC20 = TechTokenV1.at('')
    wrapper   = TrustedWrapperRemovable.deploy(techERC20.address,tx_params) 
    #time.sleep(5)
    #wrapper = TrustedWrapperRemovable.at('')
    wnft1155 = EnvelopwNFT1155.deploy(
        'UNITBOX & ENVELOP 1155 wNFT Collection', 
        'wNFT', 
        'https://api.envelop.is/metadata/',
        tx_params                           
    )
    #time.sleep(5)
    #wnft1155 = EnvelopwNFT1155.at('')
    
    wnft721 = EnvelopwNFT721.deploy(
        'UNITBOX & ENVELOP 721 wNFT Collection', 
        'wNFT', 
        'https://api.envelop.is/metadata/',
        tx_params
    )
    #time.sleep(5)
    #wnft721 = EnvelopwNFT721.at('')

    whitelist = AdvancedWhiteList.deploy(tx_params)
    #whitelist = AdvancedWhiteList.at('')
    unitbox = UnitBoxPlatform.deploy(wrapper, tx_params);
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("techERC20 = TechTokenV1.at('{}')".format(techERC20.address))
    print("wrapper = TrustedWrapperRemovable.at('{}')".format(wrapper.address))
    print("wnft1155 = EnvelopwNFT1155.at('{}')".format(wnft1155.address))
    print("wnft721 = EnvelopwNFT721.at('{}')".format(wnft721.address))
    print("whitelist = AdvancedWhiteList.at('{}')".format(whitelist.address))
    print("unitbox = UnitBoxPlatform.at('{}')".format(unitbox.address))
    
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],techERC20))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wrapper))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wnft1155))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wnft721))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],whitelist))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],unitbox))

    #Init
    wnft1155.setMinterStatus(wrapper.address, tx_params)
    wnft721.setMinter(wrapper.address, tx_params)
    wrapper.setWNFTId(3, wnft721.address, 1, tx_params)
    wrapper.setWNFTId(4, wnft1155.address,1, tx_params)
    wrapper.setWhiteList(whitelist.address, tx_params)
    wrapper.setTrustedAddress(unitbox.address, True, tx_params)


    

    if  web3.eth.chainId in [1,5, 56, 137, 43114]:
        TechTokenV1.publish_source(techERC20);
        TrustedWrapperRemovable.publish_source(wrapper);
        EnvelopwNFT1155.publish_source(wnft1155);
        EnvelopwNFT721.publish_source(wnft721);
        AdvancedWhiteList.publish_source(whitelist);
        UnitBoxPlatform.publish_source(unitbox);

    #if len(CHAIN.get('enabled_erc20', [])) > 0:
    print('Enabling collateral...')
    for erc in CHAIN.get('enabled_erc20', []):
        whitelist.setWLItem((2, erc), (True, True, True, techERC20) ,tx_params)
    
    #TODO set tresure and collateral status
#for unitbox
#ropsten
#techERC20 = TechTokenV1.at('0x3AEe8a578021E5082cd00634B55af984A0D8D386')
#wrapper = TrustedWrapperRemovable.at('0x56Ea9ccf5892D3F543FE707735E6b1A10BC91ede')
#wnft1155 = EnvelopwNFT1155.at('0xDb359A2d2C3B9928e61B03CebB4810d5E36e7cFe')
#wnft721 = EnvelopwNFT721.at('0xdA9FA61DD368e6FF8011a1e861FD34119e67689d')
#whitelist = AdvancedWhiteList.at('0x1FF12bC583D6579e4fbe032735E84BEA29532483')
#unitbox = UnitBoxPlatform.at('0x0db1ebcF530E9ac80fF5C711C8038b3826553D36')
#https://ropsten.etherscan.io/address/0x3AEe8a578021E5082cd00634B55af984A0D8D386#code
#https://ropsten.etherscan.io/address/0x56Ea9ccf5892D3F543FE707735E6b1A10BC91ede#code
#https://ropsten.etherscan.io/address/0xDb359A2d2C3B9928e61B03CebB4810d5E36e7cFe#code
#https://ropsten.etherscan.io/address/0xdA9FA61DD368e6FF8011a1e861FD34119e67689d#code
#https://ropsten.etherscan.io/address/0x1FF12bC583D6579e4fbe032735E84BEA29532483#code
#https://ropsten.etherscan.io/address/0x0db1ebcF530E9ac80fF5C711C8038b3826553D36#code

#goerli

#techERC20 = TechTokenV1.at('0x4aCd4B8e758260d2688101b2670fE22B39D6D616')
#wrapper = TrustedWrapperRemovable.at('0xAd8027f4bB7e585Eb868D47AeB693e12cFEEDC8D')
#wnft1155 = EnvelopwNFT1155.at('0x227a9c496E1DeC8C88E18C93A63Ca42B988f38d2')
#wnft721 = EnvelopwNFT721.at('0xA9D984B954fBB83D68d7F3e16fbF02F1999fB4ed')
#whitelist = AdvancedWhiteList.at('0x3AEe8a578021E5082cd00634B55af984A0D8D386')
#unitbox = UnitBoxPlatform.at('0x56Ea9ccf5892D3F543FE707735E6b1A10BC91ede')

