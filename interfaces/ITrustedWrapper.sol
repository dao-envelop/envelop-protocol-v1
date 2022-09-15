// SPDX-License-Identifier: MIT

pragma solidity 0.8.16;

import "./IWrapper.sol";

interface ITrustedWrapper is IWrapper  {

    function trustedOperator() external view returns(address);    
    
    function wrapUnsafe(
        ETypes.INData calldata _inData, 
        ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor
    ) 
        external
        payable
        returns (ETypes.AssetItem memory); 

    function transferIn(
        ETypes.AssetItem memory _assetItem,
        address _from,
        address _to
    ) 
        external  
    returns (uint256 _transferedValue);
   
}