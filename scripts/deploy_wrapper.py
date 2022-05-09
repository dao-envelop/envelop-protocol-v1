from brownie import *
import json

#0-0xeC060A763ACf876a0f25D7796497174B834140b5
private_key='???'
accounts.add(private_key)
print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))
    
def main():
    print('Deployer account= {}'.format(accounts[0]))
    wrapper = WrapperBaseV1.at("0xB22e29afF453Fb1d72503044cAbECd6be1136A7d")
    
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("wrapper       = WrapperBaseV1.at('{}')".format(wrapper.address))

    WrapperBaseV1.publish_source(wrapper)