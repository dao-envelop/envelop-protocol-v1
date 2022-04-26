from brownie import *
import json

#0-0xa11103Da33d2865C3B70947811b1436ea6Bb32eF
private_key='c4f373082110065841b63c9e005710309756f78bc7b09dbf2a242442173b1ddc'
accounts.add(private_key)
print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))
    
def main():
    print('Deployer account= {}'.format(accounts[0]))
    #erc1155 = Token1155Mock.deploy("https://envelop.is/metadata/", {'from':accounts[0]})
    erc1155 = Token1155Mock.at("0x948f114eB8D40BE607F5589Cb63bF361a859466c")
    
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("erc1155       = Token1155Mock.at('{}')".format(erc1155.address))

    if  web3.eth.chainId in [1,4, 56, 97]:
        Token1155Mock.publish_source(erc1155)

#rinkeby 0x403cEDfF16ad12d4Ef53b2D8aFe55965a1a61BFE
#okx-main 0x2d65336E7AEc57F52D76a333eD65Ee5e29F7eB25
#bsc-main 0x948f114eB8D40BE607F5589Cb63bF361a859466c