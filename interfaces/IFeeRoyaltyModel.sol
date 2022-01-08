// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;
import "../contracts/LibEnvelopTypes.sol";

interface IFeeRoyaltyModel {
     function getTransfersList(
        ETypes.Fee calldata _fee,
        ETypes.Royalty[] calldata _royalties,
        address _from, 
        address _to
    ) external returns (
      ETypes.AssetItem[] memory assetItems_, 
      address[] memory from_, 
      address[] memory to_
   );
}