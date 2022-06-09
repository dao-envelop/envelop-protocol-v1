// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. 

import "./WrapperBaseV1.sol";

pragma solidity 0.8.11;

contract TrustedWrapperRemovable is WrapperBaseV1{

	mapping(address => bool) public trustedOperators;

    event CollateralRemoved(
        address indexed wrappedAddress,
        uint256 indexed wrappedId,
        uint8   assetType,
        address collateralAddress,
        uint256 collateralTokenId,
        uint256 collateralBalance
    );

    constructor (address _erc20)
    WrapperBaseV1(_erc20) 
    {
    	trustedOperators[msg.sender] = true;
    } 

	modifier onlyTrusted() {
        require (trustedOperators[msg.sender] == true, "Only trusted address");
        _;
    }

    function setTrustedAddres(address _operator, bool _status) public onlyOwner {
        trustedOperators[_operator] = _status;
    }

    function wrap(
        ETypes.INData calldata _inData, 
        ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor
    ) 
        public 
        override
        payable
        onlyTrusted 
        nonReentrant 
        returns (ETypes.AssetItem memory) 
    {
        // 1. Take users inAsset
        if ( _inData.inAsset.asset.assetType != ETypes.AssetType.NATIVE &&
             _inData.inAsset.asset.assetType != ETypes.AssetType.EMPTY
            )
        { 
            _transfer(_inData.inAsset, msg.sender, address(this));
        }
        // 2. Mint wNFT
        _mintNFT(
            _inData.outType,     // what will be minted instead of wrapping asset
            lastWNFTId[_inData.outType].contractAddress, // wNFT contract address
            _wrappFor,                                   // wNFT receiver (1st owner) 
            lastWNFTId[_inData.outType].tokenId + 1,        
            _inData.outBalance                           // wNFT tokenId
        );
        lastWNFTId[_inData.outType].tokenId += 1;  //Save just minted id 


        // 4. Safe wNFT info
        _saveWNFTinfo(
            lastWNFTId[_inData.outType].contractAddress, 
            lastWNFTId[_inData.outType].tokenId,
            _inData
        );

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
        address _collateralAddress,
        address _amount
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
            (uint256 removeBalance, ) = getCollateralBalanceAndIndex(
                _wNFTAddress, 
                _wNFTTokenId,
                ETypes.AssetType(2), 
                _to,
                0
            );
           // - get modelAddress.  Default feeModel adddress always live in
           // protocolTechToken. When white list used it is possible override that model.
           // default model always  must be set  as protocolTechToken
           address feeModel = protocolTechToken;
            if  (protocolWhiteList != address(0)) {
                feeModel = IAdvancedWhiteList(protocolWhiteList).getWLItem(
                    _to
                ).transferFeeModel;
            }


            // - get transfer list from external model by feetype(with royalties)
            (ETypes.AssetItem[] memory assetItems, 
             address[] memory from, 
             address[] memory to
            ) =
                IFeeRoyaltyModel(feeModel).getTransfersList(
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
            // - execute transfers
            uint256 actualTransfered;
            for (uint256 j = 0; j < to.length; j ++){
                actualTransfered = _transferSafe(assetItems[j], from[j], to[j]);
                emit CollateralRemoved(
                    _wNFTAddress,
                    _wNFTTokenId,
                    2,
                    _to,
                    0,
                    removeBalance
                );
            }
            return true; 

        } else {
            return super._chargeFees(_wNFTAddress, _wNFTTokenId, _from, _to, _feeType);
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
        onlyTrusted  
        returns (address burnFor, uint256 burnBalance) 
    {
        for (uint256 i = 0; i < wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length; i ++) {
            require(wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[1].amount == 0);
        }
        super._checkCoreUnwrap(_wNFTType, _wNFTAddress, _wNFTTokenId);
        
    }
}