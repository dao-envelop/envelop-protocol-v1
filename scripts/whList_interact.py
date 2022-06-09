from brownie import *
import json

#0-0xeC060A763ACf876a0f25D7796497174B834140b5
private_key=''
accounts.add(private_key)
print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))
    
def main():
    print('Deployer account= {}'.format(accounts[0]))
    whList = AdvancedWhiteList.at("0xf59468635261169B809Ab1E0A03ceD0332A2C362")
    techERC20 = TechTokenV1.at('0xE1604b54CaC27970aa67b4e38495F206b59CEe42')
    
    #whList.setBLItem((3, '0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578'), False, {"from": accounts[0]})

    wl_data = (False, True, False, techERC20.address)
    whList.setWLItem((3, '0xdFeB55cBD23c13C4aC3195048824D14787E10732'), wl_data, {"from": accounts[0]})
    whList.setWLItem((4, '0x0ff3a4F7De32588CFfe22A838D5a18A45CD4358a'), wl_data, {"from": accounts[0]})

