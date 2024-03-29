// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. 

import "../../WrapperBaseV1.sol";
import "../../../interfaces/IWrapperRemovable.sol";

pragma solidity 0.8.21;

/// @title TrustedWrapperRemovable  contract in Envelop PrtocolV1 
/// @author Envelop Team
/// @notice Special Partners GameFi case
/// @dev  Use with UnitBoxPlatform
contract TrustedWrapperRemovable is WrapperBaseV1, IWrapperRemovable {

    mapping(address => bool) public trustedOperators;

    constructor (address _erc20)
    WrapperBaseV1(_erc20) 
    {
    	trustedOperators[msg.sender] = true;
    } 

	modifier onlyTrusted() {
        require (trustedOperators[msg.sender] == true, "Only trusted address");
        _;
    }

    function setTrustedAddress(address _operator, bool _status) public onlyOwner {
        trustedOperators[_operator] = _status;
    }

    function wrap(
        ETypes.INData      calldata _inData, 
        ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor
    ) 
        public 
        override(WrapperBaseV1, IWrapper)
        payable
        onlyTrusted 
        nonReentrant 
        returns (ETypes.AssetItem memory) 
    {
        
        require(_inData.unWrapDestination != address(0), "Must define in this implementation");
        // 1. take original    
        _transfer(_inData.inAsset, _inData.unWrapDestination, address(this));

        // 2. Mint wNFT
        _mintNFT(
            _inData.outType,     // what will be minted instead of wrapping asset
            lastWNFTId[_inData.outType].contractAddress, // wNFT contract address
            _wrappFor,                                   // wNFT receiver (1st owner) 
            lastWNFTId[_inData.outType].tokenId + 1,        
            _inData.outBalance                           // wNFT tokenId
        );
        lastWNFTId[_inData.outType].tokenId += 1;        //Save just minted id 


        // 4. Safe wNFT info
        _saveWNFTinfo(
            lastWNFTId[_inData.outType].contractAddress, 
            lastWNFTId[_inData.outType].tokenId,
            _inData
        );
        
        // 5. Add collateral
        _addCollateral(
            lastWNFTId[_inData.outType].contractAddress, 
            lastWNFTId[_inData.outType].tokenId, 
            _collateral
        );

        emit WrappedV1(
            _inData.inAsset.asset.contractAddress,        // inAssetAddress
            lastWNFTId[_inData.outType].contractAddress,  // outAssetAddress
            _inData.inAsset.tokenId,                      // inAssetTokenId 
            lastWNFTId[_inData.outType].tokenId,          // outTokenId 
            _wrappFor,                                    // wnftFirstOwner
            msg.value,                                    // nativeCollateralAmount
            _inData.rules                                 // rules
        );
        return ETypes.AssetItem(
            ETypes.Asset(_inData.outType, lastWNFTId[_inData.outType].contractAddress),
            lastWNFTId[_inData.outType].tokenId,
            _inData.outBalance
        );
    }


    function removeERC20Collateral(
        address _wNFTAddress, 
        uint256 _wNFTTokenId,
        address _collateralAddress
    ) 
        public
        nonReentrant 
    {
        require(_chargeFees(
            _wNFTAddress, 
            _wNFTTokenId, 
            address(this),      // this mean that transfers will be from collateral vault 
            _collateralAddress, // erc20 collateral address
            0x04                // this fee type implement remove collateral mechanics
            ), "Remove fail"
        );
    }

    
    /**
     * @dev Function implement remove collateral logic 
     * based on fee & royalties functionality 
     *
     * @param _wNFTAddress address of wNFT contract
     * @param _wNFTTokenId id of wNFT 
     * @param _from source address of token transfers (vault for removeable)   
     * @param _to asset address for remove
     * @param _feeType == 0x04 - remove collateral mechanics
     * @return true when remove have been done
     */
    function _chargeFees(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        address _from, 
        address _to,
        bytes1 _feeType
    ) 
        internal
        override  
        returns (bool) 
    {
        // _feeType == 0x04 - remove collateral mechanics
        if (_feeType == 0x04) {
            (uint256 removeBalance, uint256 removeIndex) = getCollateralBalanceAndIndex(
                _wNFTAddress, 
                _wNFTTokenId,
                ETypes.AssetType(2), 
                _to,
                0
            );
            if (removeBalance == 0) {
                return false;
            }

            (ETypes.AssetItem[] memory assetItems, 
             address[] memory from, 
             address[] memory to
            ) =
                // This implementation works only with native model from protocolTechToken
                IFeeRoyaltyModel(protocolTechToken).getTransfersList(
                    //erc20ItemForRemove,
                    ETypes.Fee({
                      feeType: 0x04,        // it can be used in FeeRoyalty model
                      param: removeBalance, // balance for remove
                      token: _to            // token for remove
                    }),
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].royalties,
                    _from, 
                    _to 
                );
            // Update collateral:  decrease value in collateral record
             wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[removeIndex].amount 
                    -= removeBalance;
            emit CollateralRemoved(
                _wNFTAddress,
                _wNFTTokenId,
                2,
                _to,
                0,
                removeBalance
            );    
            // - execute transfers
            for (uint256 j = 0; j < to.length; j ++){
                _transferSafe(assetItems[j], from[j], to[j]);
            }
            return true; 

        } else {
            return super._chargeFees(_wNFTAddress, _wNFTTokenId, _from, _to, _feeType);
        }
    }

    function _saveWNFTinfo(
        address wNFTAddress, 
        uint256 tokenId, 
        ETypes.INData calldata _inData
    ) internal override 
    {
        wrappedTokens[wNFTAddress][tokenId].inAsset = _inData.inAsset;
        // We will use _inData.unWrapDestination  ONLY for RENT implementation
        wrappedTokens[wNFTAddress][tokenId].unWrapDestination = _inData.unWrapDestination;
        wrappedTokens[wNFTAddress][tokenId].rules = _inData.rules;
        
        // Copying of type struct ETypes.Fee memory[] 
        // memory to storage not yet supported.
        for (uint256 i = 0; i < _inData.fees.length; i ++) {
            wrappedTokens[wNFTAddress][tokenId].fees.push(_inData.fees[i]);            
        }

        for (uint256 i = 0; i < _inData.locks.length; i ++) {
            wrappedTokens[wNFTAddress][tokenId].locks.push(_inData.locks[i]);            
        }

        for (uint256 i = 0; i < _inData.royalties.length; i ++) {
            wrappedTokens[wNFTAddress][tokenId].royalties.push(_inData.royalties[i]);            
        }

    }

    function _checkCoreUnwrap(
        ETypes.AssetType _wNFTType, 
        address _wNFTAddress, 
        uint256 _wNFTTokenId
    ) 
        internal 
        view 
        override
        onlyTrusted  // for platform operator
        returns (address burnFor, uint256 burnBalance) 
    {
        for (uint256 i = 0; i < wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length; i ++) {
            if (wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].asset.assetType 
                == ETypes.AssetType.ERC20
            ) 
            {
                require(
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].amount == 0, 
                    'Need remove collateral before unwrap'
                );
            }
        }

        // Lets check wNFT rules 
        // 0x0001 - this rule disable unwrap wrappednFT 
        require(!_checkRule(0x0001, getWrappedToken(_wNFTAddress, _wNFTTokenId).rules),
            "UnWrapp forbidden by author"
        );

        if (_wNFTType == ETypes.AssetType.ERC721) {
            // Only token owner can UnWrap
            burnFor = IERC721Mintable(_wNFTAddress).ownerOf(_wNFTTokenId);
            // require(burnFor == msg.sender, 
            //     'Only owner can unwrap it'
            // ); 

        } else if (_wNFTType == ETypes.AssetType.ERC1155) {
            burnBalance = IERC1155Mintable(_wNFTAddress).totalSupply(_wNFTTokenId);
            burnFor = wrappedTokens[_wNFTAddress][_wNFTTokenId].royalties[1].beneficiary;
            require(
                burnBalance ==
                IERC1155Mintable(_wNFTAddress).balanceOf(burnFor, _wNFTTokenId)
                ,'ERC115 unwrap available only for all totalSupply'
            );
            
        } else {
            revert UnSupportedAsset(ETypes.AssetItem(ETypes.Asset(_wNFTType,_wNFTAddress),_wNFTTokenId, 0));
        }
        
    }
}