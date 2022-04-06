from brownie import *
import json


private_key='???'
accounts.add(private_key)
print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))
    
def main():
    print('Deployer account= {}'.format(accounts[0]))
    erc721 = Token721Mock.deploy("Token721Mock for tests", "TKM", {'from':accounts[0]})
    
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("erc721       = Token721Mock.at('{}')".format(erc721.address))

    if  web3.eth.chainId in [1,4, 56, 97, 137]:
        Token721Mock.publish_source(erc721)