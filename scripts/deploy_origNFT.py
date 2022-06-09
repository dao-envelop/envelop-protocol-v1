from brownie import *
import json

#private_key='???'
#0-0xE71978b1696a972b1a8f724A4eBDB906d9dA0885
private_key=''
accounts.add(private_key)

def main():
    print('Deployer account= {}'.format(accounts[0]))
    originalNFT = OrigNFT.deploy("Envelop simple NFT", "ENVELOP", 'https://envelop.is/metadata/', {'from':accounts[0], 'gas_price': '60 gwei'})
    
    
    print("----------Deployment artifacts-------------------")
    print("originalNFT = OrigNFT.at('{}')".format(originalNFT.address))

