// SPDX-License-Identifier: MIT

pragma solidity 0.8.21;
import "../contracts/LibEnvelopTypes.sol";

interface IUserCollectionRegistry {


    function getUsersCollections(address _user) 
        external 
        view 
        returns(ETypes.Asset[] memory);
   
}