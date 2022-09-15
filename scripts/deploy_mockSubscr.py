from brownie import *
import json

accounts.load('secret2')
ORACLE_ADDRESS = '0x8125F522a712F4aD849E6c7312ba8263bEBeEFeD' 

def main():
    print('Deployer account= {}'.format(accounts[0]))

    #mock = MockSubscriptionManager.deploy({'from':accounts[0], 'gas_price': '60 gwei'})
    
    mock = MockSubscriptionManager.at('0x42Ae36Da67b35A7fC42c623e8ffDDd5b6223368E')
    
    print("----------Deployment artifacts-------------------")
    print("mock = MockSubscriptionManager.at('{}')".format(mock.address))

    #MockSubscriptionManager.publish_source(mock);

    NFTMinter721 = EnvelopUsers721SwarmEnum.at('0xc0C01d695B03c6A3A87c8cEd8Da0BD18be85eaf6')
    NFTMinter721.setSubscriptionManager(mock.address, {'from':accounts[0], 'gas_price': '60 gwei'})

    NFTMinter1155 = EnvelopUsers1155Swarm.at('0xB3BF6FE7A484625A9E63b9b9FBe49a54cBf4F9c3')
    NFTMinter1155.setSubscriptionManager(mock.address, {'from':accounts[0], 'gas_price': '60 gwei'})

    mock.setMinter(NFTMinter1155, '0xa11103Da33d2865C3B70947811b1436ea6Bb32eF', True, {'from':accounts[0], 'gas_price': '60 gwei'})
    mock.setMinter(NFTMinter721, '0xa11103Da33d2865C3B70947811b1436ea6Bb32eF', True, {'from':accounts[0], 'gas_price': '60 gwei'})

    #rinkeby
    #mock = MockSubscriptionManager.at('0x42Ae36Da67b35A7fC42c623e8ffDDd5b6223368E')


