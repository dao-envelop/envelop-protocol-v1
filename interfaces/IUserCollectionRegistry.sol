// SPDX-License-Identifier: MIT

pragma solidity 0.8.21;
import "../contracts/LibEnvelopTypes.sol";

interface IUserCollectionRegistry {


    function getUsersCollections(address _user) 
        external 
        view 
        returns(ETypes.Asset[] memory);

    function isWrapEnabled(address _ticketContract, address _eventContract)
        external 
        view 
        returns(bool enabled); 

    function isRulesUpdateEnabled(address _eventContract)
        external 
        view 
        returns(bytes2 rules); 
   
}
