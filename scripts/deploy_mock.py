from brownie import *
import json


private_key='721fd469cc7604dcc6ab618e4055822216d977cd14deeae23e6e452c82da9ae9'
accounts.add(private_key)
print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))
    
def main():
    print('Deployer account= {}'.format(accounts[0]))
    erc1155 = Token1155Mock.deploy("https://maxsiz.github.io/", {'from':accounts[0]})
    
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("erc1155       = Token1155Mock.at('{}')".format(erc1155.address))

    if  web3.eth.chainId in [1,4, 56, 97]:
        Token1155Mock.publish_source(erc1155)