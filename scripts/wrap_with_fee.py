from brownie import *
import json
from web3 import Web3
from web3 import exceptions

if  (web3.eth.chainId != 56 
    and web3.eth.chainId != 1 
    and web3.eth.chainId != 137
    and web3.eth.chainId != 43114):
    # Testnets
    private_key='2cdbeadae3122f6b30a67733fd4f0fb6c27ccd85c3c68de97c8ff534c87603c8'
else:
    # Mainnet
    private_key=input('PLease input private key for deployer address..:')
accounts.clear()    
accounts.add(private_key)
zero_address = '0x0000000000000000000000000000000000000000'
print('Tx Sender is:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))


ETH_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x7728cd70b3dD86210e2bd321437F448231B81733', #NIFTSI ERC20
'0x6b175474e89094c44da98b954eedeac495271d0f',  #DAI
'0xdAC17F958D2ee523a2206206994597C13D831ec7',  #USDT
'0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  #USDC
]

ETH_RINKEBY_ERC20_COLLATERAL_TOKENS = [
'0x1E991eA872061103560700683991A6cF88BA0028', #NIFTSI ERC20
'0xc7ad46e0b8a400bb3c915120d284aafba8fc4735',  #DAI
'0xc778417e063141139fce010982780140aa0cd5ab',  #WETH
]

BSC_TESTNET_ERC20_COLLATERAL_TOKENS = [
'0xCEFe82aDEd5e1f8c2610256629d651840601EAa8', #NIFTSI ERC20
]

BSC_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3',  #DAI
'0x55d398326f99059fF775485246999027B3197955',  #USDT
'0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',  #USDC
]

POLYGON_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',  #DAI
'0xc2132D05D31c914a87C6611C10748AEb04B58e8F',  #USDT
'0x2791bca1f2de4661ed88a30c99a7a9449aa84174',  #USDC
'0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619'   #WETH
]

AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS = [
'0xba7deebbfc5fa1100fb055a87773e1e99cd3507a',  #DAI
'0xde3a24028580884448a5397872046a019649b084',  #USDT
]

TRON_MAIN_ERC20_COLLATERAL_TOKENS = [
'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',  #USDT
]



CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io', 'enabled_erc20': ETH_MAIN_ERC20_COLLATERAL_TOKENS},
    4:{
        'explorer_base':'rinkeby.etherscan.io',
        'enabled_erc20': ETH_RINKEBY_ERC20_COLLATERAL_TOKENS,
        'wrapper':   '0x352cbAF36eDD05e6a85A7BFA9f5d91Ef4Ea13F39',
        'wnft721':   '0xdFeB55cBD23c13C4aC3195048824D14787E10732',
        'wnft1155':  '0x0ff3a4F7De32588CFfe22A838D5a18A45CD4358a',
        'techToken': '0xE1604b54CaC27970aa67b4e38495F206b59CEe42',
        'whitelist': '0x0Cbc46647D4529E8f9bbB13c0F2113B1E74c7Aed'
    },
    56:{'explorer_base':'bscscan.com', 'enabled_erc20': BSC_MAIN_ERC20_COLLATERAL_TOKENS},
    97:{
        'explorer_base':'testnet.bscscan.com', 
        'enabled_erc20': BSC_TESTNET_ERC20_COLLATERAL_TOKENS,
    },
    137:{
        'explorer_base':'polygonscan.com', 
        'enabled_erc20': POLYGON_MAIN_ERC20_COLLATERAL_TOKENS,
        'wrapper':   '0x8368f72a85f5b3bC9f41FF9f3a681b09DA0fE21f',
        'wnft721':   '0xd3FDE1C83B144d07878CDa57b66B35176A785e61',
        'wnft1155':  '0x4A80d07a1e8C15069c397cF34c407A627dcb8487',
        'techToken': '0x5076D59fE7D718a120C3f359648Caed26B81C1e1',
        'whitelist': '0x38E08929a82b2F59037301fa92979eAC90090655'
    },
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network', 'enabled_erc20': AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS},
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },

}.get(web3.eth.chainId, {'explorer_base':'io'})
print(CHAIN)
tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4,137]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}
wrapper = WrapperBaseV1.at(CHAIN['wrapper'])
########################################################################
#WRAP_FOR = accounts[0]
WRAP_FOR = '0x3ff6d2E2DF512B281a78FC660087110BE9a6b77b'
TIME_LOCK = 33202802260 #Tue, 26 Feb 3022 16:37:40 GMT
in_type = 3
out_type = 3
transfer_fee_amount_slvr = 3e16
transfer_fee_amount_gold = 1e17
transfer_fee_amount_dmnd = 2e17
transfer_fee_amount = transfer_fee_amount_slvr
BENEFICIARIES_1='0x3ff6d2E2DF512B281a78FC660087110BE9a6b77b'
BENEFICIARIES_2='0x4AC9aB28957aA70d5f28e6e4918bf12D9558B87C'
ORIGINAL = interface.IERC721('0xA5F11D60d96370878140Fba8783d705C41BDe3BE') #slvr
#ORIGINAL = interface.IERC721('0x844A8AE519f9bf28dE9211d16E417A7710a25AA1') #gold
#ORIGINAL = interface.IERC721('0x2d0c8DE67daDC6aCD16DEAc1747A153C030D7fDb') #dmnd
weth = interface.ERC20('0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619')
fee_token = weth
#ids=[x for x in range(30, 181)]
ids=[55, 116, 118, 124, 147, 159, 166]
########################################################################
def main():
    print('Sender account= {}, len(ids)= {}'.format(accounts[0], len(ids)))
    wrapped_done = []
    err_ids = []
    for tokenId in ids:
        in_data = (
            ((in_type, ORIGINAL),tokenId,0), #inAsset
            zero_address, #UnWrapDestinition
            [
              (Web3.toBytes(0x00), transfer_fee_amount, fee_token.address) #(feeType, feeAmount, feeToken)
            ],
            [(Web3.toBytes(0x00), TIME_LOCK)], #(locltype, param)
            [(BENEFICIARIES_1, 5000), (BENEFICIARIES_2, 5000)], # Royalties
            out_type,
            0,
            Web3.toBytes(0x0000) 
        )
        print("Wrapping tokenId {}".format(tokenId))
        try:
            tx =wrapper.wrap(in_data, [], WRAP_FOR, tx_params)
            wrapped_done.append(tx.txid)
        #except exceptions.TransactionError as e:
        except Exception as e:
            err_ids.append(tokenId)
            print(e)
        # except:
        #     raise e
           
    for x in wrapped_done:
        print('https://{}/tx/{}'.format(CHAIN['explorer_base'], x))

    print('Err in tokenIds: {}'.format(err_ids))