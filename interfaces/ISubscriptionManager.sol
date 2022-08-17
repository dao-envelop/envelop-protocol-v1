// SPDX-License-Identifier: MIT

pragma solidity 0.8.16;


interface ISubscriptionManager   {

    function isValidMinter(
        address _contractAddress, 
        address _minter
    ) external view returns (bool);
}