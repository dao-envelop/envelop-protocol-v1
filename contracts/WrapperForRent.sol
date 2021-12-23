// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - main protocol contract
pragma solidity 0.8.10;

import "./WrapperBaseV1.sol";

contract WrapperForRent is WrapperBaseV1 {
    

    // mapping from wNFT to wNFT Holder(tenant).
    // we need this map because there is no single owner in ERC1155
    // and for unwrap we need know who  hold  wNFT 
	mapping(address => mapping(uint256 => address)) public rentersOf;

	constructor(address _erc20) WrapperBaseV1(_erc20){

	}

	function wrap(ETypes.INData calldata _inData, ETypes.AssetItem[] calldata _collateral, address _wrappFor) 
        public 
        override
        payable 
        returns (ETypes.AssetItem memory) 
    {
        ETypes.AssetItem memory wNFT_= super.wrap(_inData, _collateral, _wrappFor);
        rentersOf[wNFT_.asset.contractAddress][wNFT_.tokenId] = _wrappFor;  
    	return wNFT_;

    }

    /////////////////////////////////////////////////////////////////////
    //                    Internals                                    //
    /////////////////////////////////////////////////////////////////////
    function _checkUnwrap(address _wNFTAddress, uint256 _wNFTTokenId) internal view override returns (bool enabled){
        // Lets wNFT rules 
        // ETypes.WNFT memory _w = _getWrappedToken(
        //     _wNFTAddress,
        //     _wNFTTokenId 
        // );
        // 0x0001 - this rule disable unwrap wrappednFT 
        if (_getWrappedToken(_wNFTAddress, _wNFTTokenId).unWrapDestinition != msg.sender) {
            enabled = !_checkRule(0x0001, _getWrappedToken(_wNFTAddress, _wNFTTokenId).rules);
        } else {
        	enabled = true;
        }
        return enabled;
    }


 
    function _checkCore(ETypes.AssetType _wNFTType, address _wNFTAddress, uint256 _wNFTTokenId) 
        internal 
        view 
        override 
        returns (address burnFor, uint256 burnBalance) 
    {
        if (_wNFTType == ETypes.AssetType.ERC721) {
            // Only token owner or unwraper can UnWrap
            burnFor = IERC721Mintable(_wNFTAddress).ownerOf(_wNFTTokenId);
            require(_getWrappedToken(_wNFTAddress, _wNFTTokenId).unWrapDestinition == msg.sender,
                'Only unWrapDestinition can unwrap it'
            ); 
            return (burnFor, burnBalance);

        } else if (_wNFTType == ETypes.AssetType.ERC1155) {
            burnBalance = IERC1155Mintable(_wNFTAddress).totalSupply(_wNFTTokenId);
            burnFor = rentersOf[_wNFTAddress][_wNFTTokenId];
            require(
                burnBalance ==
                IERC1155Mintable(_wNFTAddress).balanceOf(burnFor, _wNFTTokenId)
                ,'ERC115 unwrap available only for all totalSupply'
            );
            // Only token owner or unwraper can UnWrap
            require(_getWrappedToken(_wNFTAddress, _wNFTTokenId).unWrapDestinition == msg.sender,
                'Only unWrapDestinition can unwrap it'
            );

            return (burnFor, burnBalance);
            
        } else {
            revert UnSupportedAsset(ETypes.AssetItem(ETypes.Asset(_wNFTType,_wNFTAddress),_wNFTTokenId, 0));
        }
    }

}