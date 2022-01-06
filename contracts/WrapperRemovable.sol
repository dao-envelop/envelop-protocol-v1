// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - main protocol contract
pragma solidity 0.8.10;

import "./WrapperBaseV1.sol";

contract WrapperRemovable is WrapperBaseV1 {
    
    constructor(address _erc20) WrapperBaseV1(_erc20){

    }

    // In wraperbase implementation this function will work only
    // for white list collateral with special flag.  Anybode able
    // call this function but receiver always be one
    function removeCollateral(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem calldata _collateralItem,
        address _receiver
    ) external virtual {
        require(
            (wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestinition != address(0) 
            && wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestinition != address(this)),
            "Undefined receiver"
        );
        _removeCollateralItem(
            _wNFTAddress, 
            _wNFTTokenId,
            _collateralItem, 
            wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestinition
        );
    } 

    /////////////////////////////////////////////////////////////////////
    //                    Internals                                    //
    /////////////////////////////////////////////////////////////////////
    function _removeCollateralItem(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem calldata _collateralItem,
        address _receiver
    ) internal virtual {
        // Check WhiteList Logic
        if  (protocolWhiteList != address(0)) {
            if (_collateralItem.asset.assetType != ETypes.AssetType.NATIVE) {
                require(
                    IAdvancedWhiteList(protocolWhiteList).getWLItem(
                    _collateralItem.asset.contractAddress
                    ).enabledRemoveFromCollateral,
                    "WL:Asset Not enabled for remove"
                );

            }
        }
        // we need know index in collateral array
        (uint256 _amnt, uint256 _index) = _getCollateralBalanceAndIndex(
                _wNFTAddress, 
                _wNFTTokenId,
                _collateralItem.asset.assetType, 
                _collateralItem.asset.contractAddress,
                _collateralItem.tokenId
        );

        // Only this assets can be removed
        if ((_collateralItem.asset.assetType == ETypes.AssetType.ERC1155)
           || (_collateralItem.asset.assetType == ETypes.AssetType.ERC721) 
           || (_collateralItem.asset.assetType == ETypes.AssetType.ERC20)
        ) 
        {
            wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[_index].amount -= _collateralItem.amount;
            // case full remove 
            if (wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[_index].amount == 0) {
                wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[_index].asset.assetType = ETypes.AssetType.EMPTY;
            }
        }
        require(
            _mustTransfered(_collateralItem) == _transferSafe(_collateralItem, address(this), _receiver),
            "Suspicious asset for wrap or collateral"
        );
    } 
}