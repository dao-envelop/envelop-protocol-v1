// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Batch Worker 

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/ITrustedWrapper.sol";
import "../interfaces/ISubscriptionManager.sol";
import "../interfaces/IERC20Extended.sol";



pragma solidity 0.8.16;

contract BatchWorker is Ownable {
    using SafeERC20 for IERC20Extended;

    ITrustedWrapper public trustedWrapper;
    ISubscriptionManager public subscriptionManager;


    function wrapBatch(
        ETypes.INData[] calldata _inDataS, 
        ETypes.AssetItem[] calldata _collateralERC20,
        address[] memory _receivers
    ) public payable {
        _checkAndFixSubscription(msg.sender, 1);
        if (address(subscriptionManager) != address(0)){
            require(
                ISubscriptionManager(subscriptionManager).checkAndFixUserSubscription(
                    msg.sender,
                    1  // 1 - simple saftNFT subscription
                ),
                "Has No Subscription"
            );
        }
        
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
                    msg.sender
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
                    msg.sender
                );
                require(amountTransfered == totalERC20Collateral.amount, "Check transfer ERC20 amount fail");
                
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
        ETypes.AssetItem[] calldata _collateralERC20
    ) public payable {
        _checkAndFixSubscription(msg.sender, 1);
        require(_wNFTAddress.length == _wNFTTokenId.length, "Array params must have equal length");
        
        for (uint256 i = 0; i < _collateralERC20.length; i ++) {
            if (_collateralERC20[i].asset.assetType == ETypes.AssetType.ERC20) {
                // 1. Transfer all erc20 tokens to BatchWorker        
                IERC20Extended(_collateralERC20[i].asset.contractAddress).safeTransferFrom(
                    msg.sender,
                    address(this),
                    _collateralERC20[i].amount * _wNFTAddress.length
                );
                // 2. approve for spending to wrapper
                IERC20Extended(_collateralERC20[i].asset.contractAddress).safeIncreaseAllowance(
                    address(trustedWrapper),
                    _collateralERC20[i].amount * _wNFTAddress.length
                );
            }
        }

            

        for (uint256 i = 0; i < _wNFTAddress.length; i ++){
            trustedWrapper.addCollateral{value: (msg.value / _wNFTAddress.length)}(
                _wNFTAddress[i],
                _wNFTTokenId[i],
                _collateralERC20
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
    /////////////////////////////////////////

    // 1 - simple saftNFT subscription
    function _checkAndFixSubscription(address _user, uint256 _subscriptionType) internal {
        if (address(subscriptionManager) != address(0)){
            require(
                ISubscriptionManager(subscriptionManager).checkAndFixUserSubscription(
                    _user,
                    _subscriptionType  
                ),
                "Has No Subscription"
            );
        }
    }   
}