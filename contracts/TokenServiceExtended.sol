// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - main protocol contract
pragma solidity 0.8.21;

import "./TokenService.sol";
import "../interfaces/IUsersSBT.sol";

/// @title Envelop PrtocolV1  helper service for manage ERC(20, 721, 115) getters
/// @author Envelop Team
/// @notice Just as dependence for main wrapper contract
abstract contract TokenServiceExtended is TokenService {
	
    event EnvelopRulesChanged(
        address indexed wrappedAddress,
        uint256 indexed wrappedId,
        bytes2 newRules
    );
    
    function _balanceOf(
        ETypes.AssetItem memory _assetItem,
        address _holder
    ) internal view virtual returns (uint256 _balance){
        if (_assetItem.asset.assetType == ETypes.AssetType.NATIVE) {
            _balance = _holder.balance;
        
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC20) {
            _balance = IERC20Extended(_assetItem.asset.contractAddress).balanceOf(_holder);
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC721) {
            _balance = IERC721Mintable(_assetItem.asset.contractAddress).balanceOf(_holder); 
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC1155) {
            _balance = IERC1155Mintable(_assetItem.asset.contractAddress).balanceOf(_holder, _assetItem.tokenId);
        } else {
            revert UnSupportedAsset(_assetItem);
        }
    }

    function _ownerOf(
        ETypes.AssetItem memory _assetItem
    ) internal view virtual returns (address _owner){
        if (_assetItem.asset.assetType == ETypes.AssetType.NATIVE) {
            _owner = address(0);
        
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC20) {
            _owner = address(0);
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC721) {
            _owner = IERC721Mintable(_assetItem.asset.contractAddress).ownerOf(_assetItem.tokenId); 
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC1155) {
            _owner = address(0);
        } else {
            revert UnSupportedAsset(_assetItem);
        }
    }

    function _mintWNFTWithRules(
        ETypes.AssetType _mint_type, 
        address _contract, 
        address _mintFor, 
        uint256 _outBalance,
        bytes2 _rules
    ) 
        internal 
        virtual
        returns(uint256 tokenId)
    {
        if (_mint_type == ETypes.AssetType.ERC721) {
            tokenId = IUsersSBT(_contract).mintWithRules(_mintFor, _rules);
        } else if (_mint_type == ETypes.AssetType.ERC1155) {
            tokenId = IUsersSBT(_contract).mintWithRules(_mintFor, _outBalance, _rules);
        }else {
            revert UnSupportedAsset(
                ETypes.AssetItem(
                    ETypes.Asset(_mint_type, _contract),
                    tokenId, _outBalance
                )
            );
        }
    }

    function _updateRules(
        address _contract,
        uint256 _tokenId, 
        bytes2 _rules
    )
        internal
        virtual
        returns(bool changed)
    {
        changed = IUsersSBT(_contract).updateRules(_tokenId, _rules);
        if (changed){
            emit EnvelopRulesChanged(_contract, _tokenId, _rules);
        }
    }
}