// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;
import "../contracts/LibEnvelopTypes.sol";

interface IFeeRoyaltyModel {
    
    function registerModel() external;
    
    function getTransfersList(
        ETypes.Fee calldata _fee,
        ETypes.Royalty[] calldata _royalties,
        address _from, 
        address _to
    ) external view returns (
      ETypes.AssetItem[] memory, 
      address[] memory, 
      address[] memory
   );
}