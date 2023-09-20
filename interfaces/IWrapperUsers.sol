// SPDX-License-Identifier: MIT

pragma solidity 0.8.21;

import "./IWrapper.sol";

interface IWrapperUsers is IWrapper  {

    function wrapIn(
        ETypes.INData calldata _inData, 
        ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor,
        address _wrappIn
    ) 
        external
        payable
        returns (ETypes.AssetItem memory); 

   
}