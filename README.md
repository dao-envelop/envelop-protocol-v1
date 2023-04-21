![GitHub last commit](https://img.shields.io/github/last-commit/dao-envelop/envelop-protocol-v1)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/dao-envelop/envelop-protocol-v1)
## Envelop Protocol V1 smart contracts  
This version of the protocol is currently being systematically developed. 
The main vector of improvements is related to updating versions 
of dependencies (Solidity and OpenZeppelin)

### Deployment info  
This version has many deployments in different chains. Please follow the docs:  
https://docs.envelop.is/tech/smart-contracts/deployment-addresses  

### Audit  
[2023 April, Envelop Core Smart Contracts audit](./audit/20230420_iber_envelop_audit_rev2.pdf)

### Tests
We use Brownie as main framework for developing and unit testing. For run tests
first please [install it](https://eth-brownie.readthedocs.io/en/stable/install.html)

```bash
brownie pm install OpenZeppelin/openzeppelin-contracts@4.7.2
brownie test
```