// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. 

import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/ITrustedWrapper.sol";
import "../interfaces/ISubscriptionManager.sol";



pragma solidity 0.8.16;

contract BatchWorker is Ownable {

    ITrustedWrapper public trustedWrapper;
    ISubscriptionManager public subscriptionManager;


    function wrapBatch(
        ETypes.INData[] calldata _inDataS, 
        ETypes.AssetItem[] calldata _collateralERC20,
        address[] memory _receivers
    ) public payable {
        require(_inDataS.length == _receivers.length, "Array params must have equal length");
        // make wNFTs
        for (uint256 i = 0; i < _inDataS.length; i++) {
            // wrap
            trustedWrapper.wrapUnsafe{value: (msg.value / _receivers.length)}(
                _inDataS[i],
                _collateralERC20,
                _receivers[i]
            );
            
            // Transfer original NFTs  to wrapper
            if (_inDataS[i].inAsset.asset.assetType == ETypes.AssetType.ERC721 ||
                _inDataS[i].inAsset.asset.assetType == ETypes.AssetType.ERC1155 ) 
            {
                trustedWrapper.transferIn(
                    _inDataS[i].inAsset, 
                    msg.sender, 
                    address(trustedWrapper)
                );
            }
        }

        // TODO Transfer ERC20 & Native collateral
        ETypes.AssetItem memory totalERC20Collateral;
        uint256 totalNativeAmount;
        for (uint256 i = 0; i < _collateralERC20.length; i ++) {

            if (_collateralERC20[i].asset.assetType == ETypes.AssetType.ERC20) {
            
                totalERC20Collateral.asset.assetType = _collateralERC20[i].asset.assetType;
                totalERC20Collateral.asset.contractAddress = _collateralERC20[i].asset.contractAddress; 
                totalERC20Collateral.tokenId = _collateralERC20[i].tokenId;
                // We need construct totalERC20Collateral due make one transfer
                // instead of maked wNFT counts
                totalERC20Collateral.amount = _collateralERC20[i].amount * _receivers.length;
                
                uint256 amountTransfered = trustedWrapper.transferIn(
                   totalERC20Collateral, 
                    msg.sender, 
                    address(trustedWrapper)
                );
                
            }

            if (_collateralERC20[i].asset.assetType == ETypes.AssetType.NATIVE) {
                    totalNativeAmount += _collateralERC20[i].amount * _receivers.length;    
                } 
        }

        require(totalNativeAmount == msg.value,  "Native amount check failed");
    }


    function addCollateralBatch(
        address[] calldata _wNFTAddress, 
        uint256[] calldata _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateral
    ) public payable {
        require(_wNFTAddress.length == _wNFTTokenId.length, "Array params must have equal length");
        for (uint256 i = 0; i < _wNFTAddress.length; i ++){
            trustedWrapper.addCollateral{value: (msg.value / _wNFTAddress.length)}(
                _wNFTAddress[i],
                _wNFTTokenId[i],
                _collateral
            );
        }
    }

    ////////////////////////////////////////
    //     Admin functions               ///
    ////////////////////////////////////////
    function setTrustedWrapper(address _wrapper) public onlyOwner {
        trustedWrapper = ITrustedWrapper(_wrapper);
        require(trustedWrapper.trustedOperator() == address(this), "Only for exact wrapper");
    }

    function setSubscriptionManager(address _manager) external onlyOwner {
        require(_manager != address(0),'Non zero only');
        subscriptionManager = ISubscriptionManager(_manager);
    }
}