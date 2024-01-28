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

```shell
$ forge script script/Counter.s.sol:CounterScript --rpc-url <your_rpc_url> --private-key <your_private_key>
```

### Cast

```shell
$ cast <subcommand>
```

### Help

```shell
$ forge --help
$ anvil --help
$ cast --help
```
