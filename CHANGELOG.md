
# CHANGELOG

All notable changes to this project are documented in this file.

This changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## [Unreleased]
- Full tests  for WrapperUsersV1

## [1.3.0](https://github.com/dao-envelop/envelop-protocol-v1/tree/1.3.0) - 2023-11-20
### Added
- Upgrade solidity version up to 0.8.21
- Open Zeppelin dependencies upgrade to 4.9.3
- New contract WrapperUsersV1 for use with SBT factory

### Fixed
- 

## [1.2.0](https://github.com/dao-envelop/envelop-protocol-v1/tree/1.2.0) - 2023-05-16
### Added
- Fresh audit report added 
- Upgrade solidity version up to 0.8.19
- Open Zeppelin dependencies upgrade to 4.8.3

### Fixed
- Auditor issues resolving
- Remove owner and setMinter from wnft contracts. move this featere to constructor. 
Update fixtures and deploy_main scrypt
- Files structure refactor
- Update unit tests and some deployment scripts
### Deprecated
- Some contracts are marked as depricated

## [1.1.0](https://github.com/dao-envelop/envelop-protocol-v1/tree/1.1.0) - 2023-03-17
### Added
- SAFT with subscription (only wrap-and-lock payment method)
- Contracts for users mint with swarm and ipfs uri support.

### Fixed
- Minor bug fixes
