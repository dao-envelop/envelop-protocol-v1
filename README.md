# Envelop Protocol V1
![GitHub last commit](https://img.shields.io/github/last-commit/dao-envelop/envelop-protocol-v1)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/dao-envelop/envelop-protocol-v1)
## Envelop Protocol V1 smart contracts  
This version of the protocol is currently being systematically developed. 
The main vector of improvements is related to updating versions 
of dependencies (Solidity and OpenZeppelin)

## License
All code provided with  `SPDX-License-Identifier: MIT`

## Deployment info  
This version has many deployments in different chains. Please follow the docs:  
https://docs.envelop.is/tech/smart-contracts/deployment-addresses  

## Audit  
[2023 April, Envelop Core Smart Contracts audit](./audit/20230420_iber_envelop_audit_rev2.pdf)

## brownie-eth dev environment
### Tests
We use Brownie as main framework for developing and unit testing. For run tests
first please [install it](https://eth-brownie.readthedocs.io/en/stable/install.html)

```bash
brownie pm install OpenZeppelin/openzeppelin-contracts@4.9.3
brownie test
```

## Foundry  dev environment

**Foundry is a blazing fast, portable and modular toolkit for Ethereum application development written in Rust.**

Foundry consists of:

-   **Forge**: Ethereum testing framework (like Truffle, Hardhat and DappTools).
-   **Cast**: Swiss army knife for interacting with EVM smart contracts, sending transactions and getting chain data.
-   **Anvil**: Local Ethereum node, akin to Ganache, Hardhat Network.
-   **Chisel**: Fast, utilitarian, and verbose solidity REPL.

## Documentation

https://book.getfoundry.sh/

## Usage

### Build

```shell
$ forge build
```

### Test

```shell
$ forge test
```

### Format

```shell
$ forge fmt
```

### Gas Snapshots

```shell
$ forge snapshot
```

### Anvil

```shell
$ anvil
```

### Deploy 
#### Ethereum Mainet
```shell
$ forge script script/DeployWrapperUserBatch.s.sol:DeployScript --rpc-url mainnet  --account envdeployer --sender 0xE1a8F0a249A87FDB9D8B912E11B198a2709D6d9B  --etherscan-api-key $ETHERSCAN_TOKEN  --broadcast  --verify
```
#### Sepolia
```shell
$ forge script script/Deploy-main-index.s.sol:DeployMain --rpc-url sepolia  --account ttwo --sender 0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3 --broadcast --verify  --etherscan-api-key $ETHERSCAN_TOKEN
```

#### Blast Sepolia
```shell
$ forge script script/Deploy-main.s.sol:DeployMain --rpc-url blast_sepolia  --account ttwo --sender 0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3 --broadcast
```
#### Verify
```shell
$ forge verify-contract 0xA37a57EC4ED5A3784A3Dce7c456dbDC9E4a73577  ./contracts/TechTokenV1.sol:TechTokenV1 --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/168587773/etherscan' --etherscan-api-key "verifyContract" --num-of-optimizations 200 --compiler-version 0.8.21 

$ forge verify-contract 0xdf4e8278D8D050E667D9ECe9AC2346a73236eD33  ./contracts/WrapperBaseV1.sol:WrapperBaseV1 --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/168587773/etherscan' --etherscan-api-key "verifyContract" --num-of-optimizations 200 --compiler-version 0.8.21 --constructor-args $(cast abi-encode "constructor(address)" 0xA37a57EC4ED5A3784A3Dce7c456dbDC9E4a73577)

$ forge verify-contract 0x953D1FE8761cCFCBCb05F8dc76937E158919cB9a  ./contracts/EnvelopwNFT721.sol:EnvelopwNFT721 --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/168587773/etherscan' --etherscan-api-key "verifyContract" --num-of-optimizations 200 --compiler-version 0.8.21 --constructor-args $(cast abi-encode "constructor(string name_, string symbol_, string _baseurl, address wrapper)" 'ENVELOP 721 wNFT Collection' 'wNFT' 'https://api.envelop.is/metadata/' 0xdf4e8278D8D050E667D9ECe9AC2346a73236eD33)

$ forge verify-contract  0x645B343ae714Bf3E548A24D4E46AD6D1D19E3933 ./contracts/EnvelopwNFT1155.sol:EnvelopwNFT1155 --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/168587773/etherscan' --etherscan-api-key "verifyContract" --num-of-optimizations 200 --compiler-version 0.8.21 --constructor-args $(cast abi-encode "constructor(string name_, string symbol_, string _baseurl, address wrapper)" 'ENVELOP 1155 wNFT Collection' 'wNFT' 'https://api.envelop.is/metadata/' 0xdf4e8278D8D050E667D9ECe9AC2346a73236eD33)

$ forge verify-contract 0x6A37E369b615C4244B0D3d092a45a8D2B092e6f9  ./contracts/AdvancedWhiteList.sol:AdvancedWhiteList --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/168587773/etherscan' --etherscan-api-key "verifyContract" --num-of-optimizations 200 --compiler-version 0.8.21 

```
#### Blast Mainnet
```shell
$ forge script script/Deploy-main-blast.s.sol:DeployMainBlast --rpc-url blast_mainnet  --account envdeployer --sender 0xE1a8F0a249A87FDB9D8B912E11B198a2709D6d9B  --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --priority-gas-price 300000 --broadcast  --verify
$ #Index Wrapper  contracts set
$ forge script script/Deploy-main-blast-forindex.s.sol:DeployMainBlast --rpc-url blast_mainnet  --account envdeployer --sender 0xE1a8F0a249A87FDB9D8B912E11B198a2709D6d9B  --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --priority-gas-price 300000 --broadcast  --verify

$ forge script script/DeployWrapperUserBatch.s.sol:DeployScript --rpc-url blast_mainnet  --account envdeployer --sender 0xE1a8F0a249A87FDB9D8B912E11B198a2709D6d9B  --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --priority-gas-price 300000 --broadcast  --verify
```

#### Verify
```shell
$ forge verify-contract 0x6004efe4C11f98C05bF27B900Db18258B5f87652  ./contracts/TechTokenV1.sol:TechTokenV1 --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --num-of-optimizations 200 --compiler-version 0.8.21 

$ forge verify-contract 0xd3807CE2F215DC42ca4bfA616B16C20b0B195128  ./contracts/WrapperBaseV1BlastPoints.sol:WrapperBaseV1BlastPoints --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --num-of-optimizations 200 --compiler-version 0.8.21 --constructor-args $(cast abi-encode "constructor(address, address)" 0x6004efe4C11f98C05bF27B900Db18258B5f87652 0x303cD2A927D9Cb6F5CE03b88a4e3E2528baEDF40)


$ forge verify-contract 0x765886A9f388ca58092Bba5b6191b1e57e0950Bf  ./contracts/EnvelopwNFT721.sol:EnvelopwNFT721 --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --num-of-optimizations 200 --compiler-version 0.8.21 --constructor-args $(cast abi-encode "constructor(string name_, string symbol_, string _baseurl, address wrapper)" 'ENVELOP 721 wNFT Collection' 'wNFT' 'https://api.envelop.is/metadata/' 0xd3807CE2F215DC42ca4bfA616B16C20b0B195128)

$ forge verify-contract  0xbd2D353821CdEdC7C74632669Ea592aff61150d7 ./contracts/EnvelopwNFT1155.sol:EnvelopwNFT1155 --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --num-of-optimizations 200 --compiler-version 0.8.21 --constructor-args $(cast abi-encode "constructor(string name_, string symbol_, string _baseurl, address wrapper)" 'ENVELOP 1155 wNFT Collection' 'wNFT' 'https://api.envelop.is/metadata/' 0xd3807CE2F215DC42ca4bfA616B16C20b0B195128)

$ forge verify-contract 0xe91BF43105b9F307A591E827CC27BebC308B3F01  ./contracts/AdvancedWhiteList.sol:AdvancedWhiteList --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --num-of-optimizations 200 --compiler-version 0.8.21 

$ forge verify-contract 0x77714B0B51D64Ad3dB8c7FBeBb7f367f869bc6B8  ./contracts/OriginalNFT.sol:OrigNFT --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --num-of-optimizations 200 --compiler-version 0.8.21 --constructor-args $(cast abi-encode "constructor(string name_, string symbol_, string _baseurl)" 'ENVELOP 721 Default Collection' 'ENVELOP' 'https://api.envelop.is/metadata/')
```
#### Arbitrum
```shell
$ #Index Wrapper  contracts set
$ forge script script/Deploy-main-index.s.sol:DeployMain --rpc-url arbitrum  --account envdeployer --sender 0xE1a8F0a249A87FDB9D8B912E11B198a2709D6d9B  --etherscan-api-key $ARBISCAN_TOKEN  --broadcast  --verify

$ forge script script/DeployWrapperUserBatch.s.sol:DeployScript --rpc-url arbitrum  --account envdeployer --sender 0xE1a8F0a249A87FDB9D8B912E11B198a2709D6d9B  --etherscan-api-key $ARBISCAN_TOKEN  --broadcast  --verify


```
#### Polygon
```shell
$ forge script script/DeployWrapperUserBatch.s.sol:DeployScript --rpc-url polygon  --account envdeployer --sender 0xE1a8F0a249A87FDB9D8B912E11B198a2709D6d9B   --etherscan-api-key $POLYGONSCAN_TOKEN  --broadcast  --verify
```


### Cast

```shell
$ #set whilte list
$ cast send 0xd3807CE2F215DC42ca4bfA616B16C20b0B195128 "setWhiteList(address)" "0xe91BF43105b9F307A591E827CC27BebC308B3F01" --rpc-url blast_mainnet  --account envdeployer 

$ cast send 0xd3807CE2F215DC42ca4bfA616B16C20b0B195128 "setWhiteList(address)" "0x0000000000000000000000000000000000000000" --rpc-url blast_mainnet  --account envdeployer 
```

### Help

```shell
$ forge --help
$ anvil --help
$ cast --help
```
### Add forge to existing Brownie project
```shell
$ forge init --force
$ forge install OpenZeppelin/openzeppelin-contracts@v4.9.3
$ forge buld
```
### First build
```shell
git clone git@gitlab.com:envelop/mintnft/mintfactory.git
git submodule update --init --recursive
```