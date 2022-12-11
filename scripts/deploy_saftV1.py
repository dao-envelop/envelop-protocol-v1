from brownie import *
import json

if  web3.eth.chain_id in [4, 5, 97]:
    # Testnets
    #private_key='???'
    accounts.load('tzero');
elif web3.eth.chain_id in [1,56,137]:
    accounts.load('envdeployer')
    
    pass


print('Deployer:{}, balance: {} eth'.format(accounts[0],Wei(accounts[0].balance()).to('ether')))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))

CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io', 
       #'enabled_erc20': ETH_MAIN_ERC20_COLLATERAL_TOKENS,
       'niftsy': '0x7728cd70b3dD86210e2bd321437F448231B81733'
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
        'niftsy': '0x7728cd70b3dD86210e2bd321437F448231B81733'
    },
    97:{'explorer_base':'testnet.bscscan.com', 
        #'enabled_erc20': BSC_TESTNET_ERC20_COLLATERAL_TOKENS
    },
    137:{'explorer_base':'polygonscan.com', 
         #'enabled_erc20': POLYGON_MAIN_ERC20_COLLATERAL_TOKENS,
         'niftsy': '0x432cdbC749FD96AA35e1dC27765b23fDCc8F5cf1'
    },
    80001:{'explorer_base':'mumbai.polygonscan.com', 
    },  
    43114:{'explorer_base':'cchain.explorer.avax.network', 
           #'enabled_erc20': AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS
    },
    43113:{'explorer_base':'cchain.explorer.avax-test.network', 
    },

}.get(web3.eth.chainId, {'explorer_base':'io'})
print(CHAIN)

tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4,5]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

def main():
    # START TARIF
    FREEZ_AMOUNT = 1e18
    timelockPeriod = 3600 #1 hour
    ticketValidPeriod = 1000  #1000 sec
    counter = 0
    #
       

    saftV1 = BatchWorker.deploy(0, tx_params)
    subscriptionManager = SubscriptionManagerV1.deploy(tx_params)
    techERC20 = TechTokenV1.deploy(tx_params)
    wrapperTrustedV1 = TrustedWrapper.deploy(
        techERC20.address, 
        saftV1.address, 
        tx_params
    )

    wnft1155 = EnvelopwNFT1155.deploy(
        'ENVELOP 1155 wNFT SAFT V1 Collection', 
        'swNFT', 
        'https://api.envelop.is/metadata/',
        tx_params
    )
    
    wnft721 = EnvelopwNFT721.deploy(
        'ENVELOP 721 wNFT SAFT V1 Collection', 
        'swNFT', 
        'https://api.envelop.is/metadata/',
        tx_params
    )

     # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("techERC20 = TechTokenV1.at('{}')".format(techERC20.address))
    print("saftV1 = BatchWorker.at('{}')".format(saftV1.address))
    print("subscriptionManager = SubscriptionManagerV1.at('{}')".format(subscriptionManager.address))
    print("wrapperTrustedV1 = TrustedWrapper.at('{}')".format(wrapperTrustedV1.address))
    print("wnft1155 = EnvelopwNFT1155.at('{}')".format(wnft1155.address))
    print("wnft721 = EnvelopwNFT721.at('{}')".format(wnft721.address))

    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],techERC20.address))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],saftV1.address))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],subscriptionManager.address))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wrapperTrustedV1.address))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wnft1155.address))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wnft721.address))


    #make settings of contracts
    wnft1155.setMinterStatus(wrapperTrustedV1.address, tx_params)
    wnft721.setMinter(wrapperTrustedV1.address, tx_params)
    wrapperTrustedV1.setWNFTId(3, wnft721.address, 1, tx_params)
    wrapperTrustedV1.setWNFTId(4, wnft1155.address,1, tx_params)
    #wrapperTrustedV1.setWhiteList(whitelist.address, tx_params)
    saftV1.setTrustedWrapper(wrapperTrustedV1.address, tx_params)
    subscriptionManager.setAgentStatus(saftV1.address, True, tx_params)

    #make settings of subscription -- add tarif
    if  CHAIN.get('niftsy', None) is not None:
        subscriptionType = (timelockPeriod, ticketValidPeriod, counter, True)
        payOption = [(CHAIN.get('niftsy', None), FREEZ_AMOUNT)]
        services = [0]
        subscriptionManager.addTarif(
            (subscriptionType, payOption, services), 
            tx_params
        )

    #make settings of manager
    subscriptionManager.setMainWrapper(wrapperTrustedV1, tx_params)
    saftV1.setSubscriptionManager(subscriptionManager.address, tx_params)




    if  web3.eth.chainId in [1,4,5, 137, 43114]:
        TechTokenV1.publish_source(techERC20);
        BatchWorker.publish_source(saftV1);
        EnvelopwNFT1155.publish_source(wnft1155);
        EnvelopwNFT721.publish_source(wnft721);
        TrustedWrapper.publish_source(wrapperTrustedV1);
        SubscriptionManagerV1.publish_source(subscriptionManager);
