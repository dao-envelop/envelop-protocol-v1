// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. 
pragma solidity 0.8.11;

import "../contracts/LibEnvelopTypes.sol";


interface IWrapperChecker {

	
	function checkWrap(
        ETypes.INData calldata _inData, 
        //ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor
    ) 
        external returns (bool);
}