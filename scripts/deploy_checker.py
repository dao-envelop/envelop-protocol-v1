from brownie import *
import json

if  (web3.eth.chainId != 56 
    and web3.eth.chainId != 1 
    and web3.eth.chainId != 137
    and web3.eth.chainId != 43114):
    # Testnets
    private_key='???'
else:
    # Mainnet
    private_key=input('PLease input private key for deployer address..:')
accounts.add(private_key)

print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))


tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

def main():
    print('Deployer account= {}'.format(accounts[0]))
    checker = WrapperChecker.deploy('0x352cbAF36eDD05e6a85A7BFA9f5d91Ef4Ea13F39', tx_params)
   
    
    



    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("checker = WrapperChecker.at('{}')".format(checker.address))

    if  web3.eth.chainId in [1,4, 43114]:
        WrapperChecker.publish_source(checker);

    #rinkeby - 0x058B7b0fE9D1204E462EDbB01A85f2E57E8A5b7E
