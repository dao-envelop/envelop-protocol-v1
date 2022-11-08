from brownie import *
import json

accounts.load('secret2')
ORACLE_ADDRESS = '0x8125F522a712F4aD849E6c7312ba8263bEBeEFeD' 

def main():
    print('Deployer account= {}'.format(accounts[0]))

    #NFTMinter = EnvelopUsers721SwarmEnum.deploy("Envelop simple NFT", "eNFT", 'https://swarm.envelop.is/bzz/', {'from':accounts[0], 'gas_price': '60 gwei'})
    #NFTMinter = EnvelopUsers1155Swarm.deploy("Envelop simple NFT", "eNFT", 'https://swarm.envelop.is/bzz/', {'from':accounts[0], 'gas_price': '60 gwei'})

    
    print("----------Deployment artifacts-------------------")
    #print("NFTMinter = EnvelopUsers721SwarmEnum.at('{}')".format(NFTMinter.address))
    #print("NFTMinter = EnvelopUsers1155Swarm.at('{}')".format(NFTMinter.address))

    #NFTMinter.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0], 'gas_price': '60 gwei'})

    NFTMinter = EnvelopUsers721SwarmEnum.at('0x4B44874F117e04462bF005779E5F2D021F1688b8')

    EnvelopUsers721SwarmEnum.publish_source(NFTMinter);
    #EnvelopUsers1155Swarm.publish_source(NFTMinter);
    
    #rinkeby 
    
    #721
    #NFTMinter = EnvelopUsers721SwarmEnum.at('0x4B44874F117e04462bF005779E5F2D021F1688b8')

    #1155
    #NFTMinter = EnvelopUsers1155Swarm.at('0xB3BF6FE7A484625A9E63b9b9FBe49a54cBf4F9c3')


