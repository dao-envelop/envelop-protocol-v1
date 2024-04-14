// SPDX-License-Identifier: MIT

pragma solidity 0.8.21;

import "./IWrapperUsers.sol";

interface IWrapperUsersV1Batch is IWrapperUsers  {

    function wrapBatch(
        ETypes.INData[] calldata _inDataS, 
        ETypes.AssetItem[] memory _collateralERC20,
        address[] memory _receivers,
        address _wrappIn
    ) external payable;

    function addCollateralBatch(
        address[] calldata _wNFTAddress, 
        uint256[] calldata _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateralERC20
    ) external payable;
   
}