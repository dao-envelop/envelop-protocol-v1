from brownie import *
import json

accounts.load('secret2')

def main():
    print('Deployer account= {}'.format(accounts[0]))
    originalNFT = OrigNFT.deploy("Envelop simple NFT", "ENVELOP", 'https://envelop.is/metadata/', {'from':accounts[0], 'gas_price': '60 gwei', 'gas_limit': 1e8, 'allow_revert': True})
    
    
    print("----------Deployment artifacts-------------------")
    print("originalNFT = OrigNFT.at('{}')".format(originalNFT.address))
    
    #ropsten 0x45f75542d555eabd46b03a6995D314704501c7dc

