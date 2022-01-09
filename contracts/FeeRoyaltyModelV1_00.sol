// SPDX-License-Identifier: MIT
// Envelop Protocol Fee Model
pragma solidity 0.8.10;

import "../contracts/LibEnvelopTypes.sol";
import "../interfaces/IFeeRoyaltyModel.sol";

contract FeeRoyaltyModelV1_00 is IFeeRoyaltyModel {

    uint256 constant public ROYALTY_PERCENT_BASE = 10000;
    address public wrapper;

    function registerModel() external {
        require(wrapper == address(0), 'Already registered');
        wrapper = msg.sender;
    }

    function getTransfersList(
        ETypes.Fee calldata _fee,
        ETypes.Royalty[] calldata _royalties,
        address _from, 
        address _to
    ) external view returns (
      ETypes.AssetItem[] memory, 
      address[] memory, 
      address[] memory
    )
    {
        ETypes.AssetItem[] memory assetItems_ = new ETypes.AssetItem[](_royalties.length);
        address[] memory from_ = new address[](_royalties.length); 
        address[] memory   to_ = new address[](_royalties.length);
        for (uint256 i = 0; i < _royalties.length; i ++) {
            assetItems_[i] = ETypes.AssetItem({
                asset: ETypes.Asset({assetType: ETypes.AssetType.ERC20, contractAddress: _fee.token}),
                tokenId: 0,
                amount: _fee.param * _royalties[i].percent / ROYALTY_PERCENT_BASE
            });
            from_[i] = _from;
            to_[i] = _royalties[i].beneficiary;
        }
    }
}
