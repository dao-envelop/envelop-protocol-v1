from brownie import *
import json

if  web3.eth.chain_id in [4, 5, 97, 11155111]:
    # Testnets
    #private_key='???'
    #accounts.load('niftsyms');
    accounts.load('secret2');
elif web3.eth.chain_id in [1,56,137]:
    accounts.load('envdeployer')
    
    pass

signers = ['0xf4321B36e42bD79384116545d80873057d633B87', '0xfA293C97653b542A387539D2fAd1c64CAfbDD729']
CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io', },
    4:{'explorer_base':'rinkeby.etherscan.io',},
    5:{'explorer_base':'goerli.etherscan.io',},
    56:{'explorer_base':'bscscan.com', },
    97:{'explorer_base':'testnet.bscscan.com', },
    137:{'explorer_base':'polygonscan.com', },
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network', },
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },

}.get(web3.eth.chainId, {'explorer_base':'io'})
print(CHAIN)
tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4,5, 137]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

def main():
    print('Deployer account= {}'.format(accounts[0]))

    NFTMinter721 = EnvelopUsers721UniStorageEnum.deploy(
        "Envelop UniStorage NFT", 
        "eNFT", 
        'https://api.envelop.is/metadata/',
        100, 
        tx_params
     )

    NFTMinter1155 = EnvelopUsers1155UniStorage.deploy(
        "Envelop UniStorage NFT", 
        "eNFT", 
        'https://api.envelop.is/metadata/',
        100, 
        tx_params
    )
    #NFTMinter721 = EnvelopUsers721UniStorageEnum.at('0x33ec38185f213D6e75ba26F711ba309b8BcD211a')
    #NFTMinter1155 = EnvelopUsers1155UniStorage.at('0xa459d2f635812792Df0F175B2263D4bE15A0D5aa')



    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("NFTMinter721 = EnvelopUsers721UniStorageEnum.at('{}')".format(NFTMinter721.address))
    print("NFTMinter1155 = EnvelopUsers1155UniStorage.at('{}')".format(NFTMinter1155.address))
    
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],NFTMinter721))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],NFTMinter1155))
    
    # set signers
    #for a in signers:
    #    NFTMinter721.setSignerStatus(a, True, tx_params)
    #    NFTMinter1155.setSignerStatus(a, True, tx_params)


    if  web3.eth.chainId in [1,4,5, 56, 137, 43114, 11155111]:
        EnvelopUsers721UniStorageEnum.publish_source(NFTMinter721);
        EnvelopUsers1155UniStorage.publish_source(NFTMinter1155);
    #721
    #NFTMinter = EnvelopUsers721SwarmEnum.at('0x4B44874F117e04462bF005779E5F2D021F1688b8')

    #1155
    #NFTMinter = EnvelopUsers1155Swarm.at('0xB3BF6FE7A484625A9E63b9b9FBe49a54cBf4F9c3')


