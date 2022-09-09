from brownie import *
import json

accounts.load('secret2')
ORACLE_ADDRESS = '0x8125F522a712F4aD849E6c7312ba8263bEBeEFeD' 

def main():
    print('Deployer account= {}'.format(accounts[0]))

    NFTMinter = EnvelopUsers721Swarm.deploy("Envelop simple NFT", "eNFT", 'https://swarm.envelop.is/bzz/', {'from':accounts[0], 'gas_price': '60 gwei'})
    
    
    print("----------Deployment artifacts-------------------")
    print("NFTMinter = EnvelopUsers721Swarm.at('{}')".format(NFTMinter.address))

    NFTMinter.setSignerStatus(ORACLE_ADDRESS, True, {'from':accounts[0], 'gas_price': '60 gwei'})

    EnvelopUsers721Swarm.publish_source(NFTMinter);
    
    #rinkeby 
    #NFTMinter = EnvelopUsers721Swarm.at('0x7a97Ce5C07f5aF52fe8f857290d76cEe5b53c4BD')


