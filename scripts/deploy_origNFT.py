from brownie import *
import json

accounts.load('secret2')

def main():
    print('Deployer account= {}'.format(accounts[0]))
    tx_params={'from':accounts[0], 'allow_revert': True, 'gas_limit': 10e6}
    #originalNFT = OrigNFT.deploy("Envelop simple NFT", "ENVELOP", 'https://envelop.is/metadata/', tx_params)
    originalNFT = OrigNFT.at("0x69e8B95d034fdd102dE3006F3EbE3B619945242B")
    OrigNFT.publish_source(originalNFT);
    
    
    print("----------Deployment artifacts-------------------")
    print("originalNFT = OrigNFT.at('{}')".format(originalNFT.address))
    
    #ropsten 0x45f75542d555eabd46b03a6995D314704501c7dc 
    #aurora test OrigNFT deployed at: 0x376e8EA664c2E770E1C45ED423F62495cB63392D
    #goerli OrigNFT.at('0x69e8B95d034fdd102dE3006F3EbE3B619945242B')
