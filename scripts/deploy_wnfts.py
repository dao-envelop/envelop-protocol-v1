from brownie import *
import json

if  web3.eth.chain_id in [4, 5, 97]:
    # Testnets
    #private_key='???'
    accounts.load('tone');
elif web3.eth.chain_id in [1,56,137, 42161]:
    accounts.load('envdeployer')



print('Deployer:{}, balance: {} eth'.format(accounts[0],Wei(accounts[0].balance()).to('ether') ))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))


CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io', 
       #'enabled_erc20': ETH_MAIN_ERC20_COLLATERAL_TOKENS,
       'niftsy': '0x7728cd70b3dD86210e2bd321437F448231B81733',
       'techERC20':'0x41FF1Dbe71cD32AF87E1eC88dcA8C12045cd0CA9',
       'wl':'0xF99796325c62984092B81778E4B4526daA7DE752',
       'wrapper':'0x2C72097760B3f0E781C9499dD94486E46DFD664C'
    },
    4:{'explorer_base':'rinkeby.etherscan.io',
        #'enabled_erc20': ETH_RINKEBY_ERC20_COLLATERAL_TOKENS,
        'niftsy': '0x3125B3b583D576d86dBD38431C937F957B94B47d'
    },
    5:{'explorer_base':'goerli.etherscan.io',
       #'enabled_erc20': ETH_GOERLI_ERC20_COLLATERAL_TOKENS,
       'niftsy': '0x376e8EA664c2E770E1C45ED423F62495cB63392D'
    },
    56:{'explorer_base':'bscscan.com', 
        #'enabled_erc20': BSC_MAIN_ERC20_COLLATERAL_TOKENS,
        'niftsy': '',
        'techERC20':'0x7716Bf599131aCC5169d8F2369375632B56Cef7D',
        'wl':'0x0fE8B380723cc75d75D49a9e3D8811A8E114246D',
        'wrapper':'0x0a18Abe3030C9E766329b9b9A05d2D9bD03C4F8F'
    },
    97:{'explorer_base':'testnet.bscscan.com', 
        #'enabled_erc20': BSC_TESTNET_ERC20_COLLATERAL_TOKENS
    },
    137:{'explorer_base':'polygonscan.com', 
         #'enabled_erc20': POLYGON_MAIN_ERC20_COLLATERAL_TOKENS,
         'niftsy': '',
         'techERC20':'0x70D06cD502BC51fa7C805677c6ecB7e43cddE439',
         'wl':'0x1A9DF09bb68ED345fFAAf515991C098cCA3B2BB9',
         'wrapper':'0x018Ab23bae3eD9Ec598B1239f37B998fEDB75af3'
    },
    80001:{'explorer_base':'mumbai.polygonscan.com', 
    },  
    43114:{'explorer_base':'cchain.explorer.avax.network', 
           #'enabled_erc20': AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS
    },
    43113:{'explorer_base':'cchain.explorer.avax-test.network', 
    },

}.get(web3.eth.chainId, {'explorer_base':'io','niftsy': '',
         'techERC20':'0x70D06cD502BC51fa7C805677c6ecB7e43cddE439',
         'wl':'0x70D06cD502BC51fa7C805677c6ecB7e43cddE439',
         'wrapper':'0x018Ab23bae3eD9Ec598B1239f37B998fEDB75af3'}
)
print(CHAIN)
tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4,5, 137]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

def main():
    #techERC20 = TechTokenV1.deploy(tx_params)
    #techERC20 = TechTokenV1.at('0x7e4Be057C70657C71dEc4716A2fD23BEad0Ad4Eb')
   # wrapper   = WrapperBaseV1.deploy(techERC20.address,tx_params) 
    wrapper = WrapperBaseV1.at(CHAIN['wrapper'])
    wnft1155 = EnvelopwNFT1155.deploy(
        'ENVELOP 1155 wNFT Collection', 
        'wNFT', 
        'https://api.envelop.is/metadata/',
        wrapper.address,
        tx_params
    )
    
    wnft721 = EnvelopwNFT721.deploy(
        'ENVELOP 721 wNFT Collection', 
        'wNFT', 
        'https://api.envelop.is/metadata/',
        wrapper.address,
        tx_params
    )

    whitelist = AdvancedWhiteList.at(CHAIN['wl'])
    #wnft1155 = EnvelopwNFT1155.at('0xf294ab4B27f27cC619E2EfF2db5077A7D995A1FC')
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    #print("techERC20 = TechTokenV1.at('{}')".format(techERC20.address))
    #print("wrapper = WrapperBaseV1.at('{}')".format(wrapper.address))
    print("wnft1155 = EnvelopwNFT1155.at('{}')".format(wnft1155.address))
    print("wnft721 = EnvelopwNFT721.at('{}')".format(wnft721.address))
    #print("whitelist = AdvancedWhiteList.at('{}')".format(whitelist.address))
    
    #print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],techERC20))
    #print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wrapper))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wnft1155))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wnft721))
    #print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],whitelist))
    #Init
    #techERC20.addMinter(wrapper.address, {'from': accounts[0]})
    wrapper.setWNFTId(3, wnft721.address, 1, tx_params)
    wrapper.setWNFTId(4, wnft1155.address,1, tx_params)
    wrapper.setWhiteList(whitelist.address, tx_params)
    
    
    



    

    if  web3.eth.chainId in [1,4, 5, 137, 42161, 43114]:
        #TechTokenV1.publish_source(techERC20);
       # WrapperBaseV1.publish_source(wrapper);
        EnvelopwNFT1155.publish_source(wnft1155);
        EnvelopwNFT721.publish_source(wnft721);
        #AdvancedWhiteList.publish_source(whitelist);

