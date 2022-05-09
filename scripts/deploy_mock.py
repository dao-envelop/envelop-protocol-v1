from brownie import *
import json

#0-0xeC060A763ACf876a0f25D7796497174B834140b5
private_key='???'
accounts.add(private_key)
print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))
    
def main():
    print('Deployer account= {}'.format(accounts[0]))
    erc1155 = Token1155Mock.deploy("https://envelop.is/metadata/", {'from':accounts[0]})
    #erc1155 = Token1155Mock.at("0x948f114eB8D40BE607F5589Cb63bF361a859466c")
    
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("erc1155       = Token1155Mock.at('{}')".format(erc1155.address))

    Token1155Mock.publish_source(erc1155)

#rinkeby 0x403cEDfF16ad12d4Ef53b2D8aFe55965a1a61BFE
#okx-main 0x2d65336E7AEc57F52D76a333eD65Ee5e29F7eB25
#bsc-main 0x948f114eB8D40BE607F5589Cb63bF361a859466c
#bsc-test  0x2d65336E7AEc57F52D76a333eD65Ee5e29F7eB25   
#polygon-main 0xD48fdbCf81070547d5a3fB276203b5bf96344b10