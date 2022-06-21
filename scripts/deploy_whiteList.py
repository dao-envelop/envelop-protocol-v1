from brownie import *
import json

private_key=''
accounts.add(private_key)

print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))


tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

def main():
    print('Deployer account= {}'.format(accounts[0]))
    #whiteList = AdvancedWhiteList.deploy(tx_params)
    whiteList = AdvancedWhiteList.at('0xf59468635261169b809ab1e0a03ced0332a2c362')
    techERC20 = TechTokenV1.at('0xE1604b54CaC27970aa67b4e38495F206b59CEe42')

    #wl_data = (False, True, False, techERC20.address)
    #whiteList.setWLItem((3,'0xdFeB55cBD23c13C4aC3195048824D14787E10732'), wl_data, {"from": accounts[0]})
    whiteList.setBLItem((3,'0xe1383d47550b7b3b2ea6c4d327627a0a167f7b4b'), False, {"from": accounts[0]})
    whiteList.setBLItem((4,'0x403cedff16ad12d4ef53b2d8afe55965a1a61bfe'), False, {"from": accounts[0]})
   
    
    

'''

    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("whiteList = AdvancedWhiteList.at('{}')".format(whiteList.address))

    if  web3.eth.chainId in [1,4, 43114]:
        AdvancedWhiteList.publish_source(whiteList);'''

    #rinkeby - 0xf59468635261169B809Ab1E0A03ceD0332A2C362
