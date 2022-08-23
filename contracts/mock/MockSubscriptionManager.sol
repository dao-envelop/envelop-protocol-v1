// SPDX-License-Identifier: MIT
// ENVELOP protocol for NFT. Mintable User NFT Collection
pragma solidity 0.8.16;

contract MockSubscriptionManager {

    mapping(address => mapping(address => bool)) public minters;

    constructor() {}

    function setMinter(address _contract, address _minter, bool _status) external {
        minters[_contract][_minter] = _status;
    }

    function isValidMinter(address _contract, address _minter) external view returns (bool) {
        return minters[_contract][_minter];
    }
}