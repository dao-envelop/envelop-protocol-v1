// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - main protocol contract
pragma solidity 0.8.10;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";
import "@openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
//import "./TechToken.sol";
import "../interfaces/IERC20Extended.sol";
import "../interfaces/IFeeRoyaltyCharger.sol";
import "../interfaces/IWrapper.sol";
import "./LibEnvelopTypes.sol";
import "../interfaces/IERC721Mintable.sol";
import "../interfaces/IERC1155Mintable.sol";


/**
 * @title Non-Fungible Token Wrapper
 * @dev Make  wraping for existing ERC721 & ERC1155 and empty 
 */
contract WrapperBaseV1 is ReentrancyGuard, ERC721Holder, ERC1155Holder,/*IFeeRoyaltyCharger,*/ IWrapper, Ownable {
    using SafeERC20 for IERC20Extended;



    uint256 constant public MAX_ROYALTY_PERCENT = 5000;
    uint256 constant public MAX_TIME_TO_UNWRAP = 365 days;
    //uint256 constant public MAX_FEE_THRESHOLD_PERCENT = 1; //percent from project token totalSupply

    uint256 public MAX_COLLATERAL_SLOTS = 20;
    address public protocolTechToken;
    address public protocolWhiteList;
    address public transferProxy;


    // Map from wrapping asset type to wnft contract address and last minted id
    mapping(ETypes.AssetType => ETypes.NFTItem) public lastWNFTId;  
    
    // Map from wrapped token address and id => wNFT record 
    mapping(address => mapping(uint256 => ETypes.WNFT)) public wrappedTokens; //? Private in Production

    error UnSupportedAsset(ETypes.AssetItem asset);
    constructor(address _erc20) {
        require(_erc20 != address(0), "ProtocolTechToken cant be zero value");
        protocolTechToken = _erc20; 
    }

    function wrap(ETypes.INData calldata _inData, ETypes.AssetItem[] calldata _collateral, address _wrappFor) 
        public 
        virtual
        payable 
        nonReentrant 
        returns (ETypes.AssetItem memory) 
    {
        // 1. Take users inAsset
        //_takeUnderlineAssetForWrap(_inData.inAsset),
        _transfer(_inData.inAsset, msg.sender, address(this));
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
        return ETypes.AssetItem(ETypes.Asset(ETypes.AssetType(0), address(0)),0,0);
    }

    function wrapSafe(
        ETypes.INData calldata _inData, 
        ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor
    ) public returns (ETypes.AssetItem memory) {
        //TODO many Checks
        return wrap(_inData, _collateral, _wrappFor);
    }

    function addCollateral(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateral
    ) external virtual {
        _addCollateral(
            _wNFTAddress, 
            _wNFTTokenId, 
            _collateral
        );
    } 

    function unWrap(address _wNFTAddress, uint256 _wNFTTokenId) external virtual {

    } 
    /////////////////////////////////////////////////////////////////////
    //                    Admin functions                              //
    /////////////////////////////////////////////////////////////////////
    function setWNFTId(
        ETypes.AssetType  _assetOutType, 
        address _wnftContract, 
        uint256 _tokenId
    ) external onlyOwner {
        require(_wnftContract != address(0), "No zero address");
        lastWNFTId[_assetOutType] = ETypes.NFTItem(_wnftContract, _tokenId);
    }

    function setWhiteList(address _wlAddress) external onlyOwner {
        protocolWhiteList = _wlAddress;
    }

    function setTransferProxy(address _proxyAddress) external onlyOwner {
        transferProxy = _proxyAddress;
    }
    /////////////////////////////////////////////////////////////////////

    //TODO Reafactro with internal getters
    function getERC20CollateralBalance(
        address _wNFTAddress, 
        uint256 _tokenId, 
        address _erc20
    ) public view returns (uint256) 
    {
        //ERC20Collateral[] memory e = erc20Collateral[_wrappedId];
        for (uint256 i = 0; i < wrappedTokens[_wNFTAddress][_tokenId].collateral.length; i ++) {
            if (wrappedTokens[_wNFTAddress][_tokenId].collateral[i].asset.contractAddress == _erc20 &&
                wrappedTokens[_wNFTAddress][_tokenId].collateral[i].asset.assetType == ETypes.AssetType.ERC20 
                ) {
                return wrappedTokens[_wNFTAddress][_tokenId].collateral[i].amount;
            }
        }
    }

    function getWrappedToken(address _wNFTAddress, uint256 _wNFTTokenId) public view returns (ETypes.WNFT memory) {
        return wrappedTokens[_wNFTAddress][_wNFTTokenId];

    } 
    /////////////////////////////////////////////////////////////////////
    //                    Internals                                    //
    /////////////////////////////////////////////////////////////////////

    function _mintNFT(
        ETypes.AssetType _mint_type, 
        address _contract, 
        address _mintFor, 
        uint256 _tokenId, 
        uint256 _outBalance
    ) 
        internal 
        virtual
    {
        if (_mint_type == ETypes.AssetType.ERC721) {
            IERC721Mintable(_contract).mint(_mintFor, _tokenId);
        } else if (_mint_type == ETypes.AssetType.ERC1155) {
            IERC1155Mintable(_contract).mint(_mintFor, _tokenId, _outBalance);
        }
    }

    function _burnNFT(
        ETypes.AssetType _burn_type, 
        address _contract, 
        address _burnFor, 
        uint256 _tokenId, 
        uint256 _balance
    ) 
        internal
        virtual 
    {
        if (_burn_type == ETypes.AssetType.ERC721) {
            IERC721Mintable(_contract).burn(_tokenId);

        } else if (_burn_type == ETypes.AssetType.ERC1155) {
            IERC1155Mintable(_contract).burn(_burnFor, _tokenId, _balance);
        }
        
    }

    function _transfer(
        ETypes.AssetItem calldata _assetItem,
        address _from,
        address _to
    ) internal virtual returns (bool _transfered){
        if (_assetItem.asset.assetType == ETypes.AssetType.NATIVE) {
            (bool success, ) = _to.call{ value: _assetItem.amount}("");
            require(success, "transfer failed");
            _transfered = true; 
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC20) {
            require(IERC20Extended(_assetItem.asset.contractAddress).balanceOf(_from) <= _assetItem.amount, "UPS!!!!");
            IERC20Extended(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.amount);
            _transfered = true;
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC721) {
            IERC721Mintable(_assetItem.asset.contractAddress).transferFrom(_from, _to, _assetItem.tokenId);
            _transfered = true;
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC1155) {
            IERC1155Mintable(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.tokenId, _assetItem.amount, "");
            _transfered = true;
        } else {
            revert UnSupportedAsset(_assetItem);
        }
        return _transfered;
    }

    function _transferSafe(
        ETypes.AssetItem calldata _assetItem,
        address _from,
        address _to
    ) internal virtual returns (uint256 _transferedValue){
        uint256 balanceBefore;
        if (_assetItem.asset.assetType == ETypes.AssetType.NATIVE) {
            balanceBefore = _to.balance;
            (bool success, ) = _to.call{ value: _assetItem.amount}("");
            require(success, "transfer failed");
            _transferedValue = _to.balance - balanceBefore;
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC20) {
            balanceBefore = IERC20Extended(_assetItem.asset.contractAddress).balanceOf(_to);
            IERC20Extended(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.amount);
            _transferedValue = IERC20Extended(_assetItem.asset.contractAddress).balanceOf(_to) - balanceBefore;
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC721) {
            IERC721Mintable(_assetItem.asset.contractAddress).transferFrom(_from, _to, _assetItem.tokenId);
            if (IERC721Mintable(_assetItem.asset.contractAddress).ownerOf(_assetItem.tokenId) == _to) {
                _transferedValue = 1;
            }
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC1155) {
            balanceBefore = IERC1155Mintable(_assetItem.asset.contractAddress).balanceOf(_to, _assetItem.tokenId);
            IERC1155Mintable(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.tokenId, _assetItem.amount, "");
            _transferedValue = IERC1155Mintable(_assetItem.asset.contractAddress).balanceOf(_to, _assetItem.tokenId) - balanceBefore;
        } else {
            revert UnSupportedAsset(_assetItem);
        }
        return _transferedValue;
    }

    function _saveWNFTinfo(
        address wNFTAddress, 
        uint256 tokenId, 
        ETypes.INData calldata _inData
        //ETypes.AssetItem[] calldata _collateral
    ) internal virtual 
    {
        wrappedTokens[wNFTAddress][tokenId].inAsset = _inData.inAsset;
        wrappedTokens[wNFTAddress][tokenId].unWrapDestinition = _inData.unWrapDestinition;
        wrappedTokens[wNFTAddress][tokenId].rules = _inData.rules;
        
        // Copying of type struct ETypes.Fee memory[] memory to storage not yet supported.
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

    function _addCollateral(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateral
    ) internal virtual 
    {
        // 3. Process Native Colleteral
        if (msg.value > 0) {
            _updateCollateralInfo(
                _wNFTAddress, 
                _wNFTTokenId,
                ETypes.AssetItem(
                    ETypes.Asset(ETypes.AssetType.NATIVE, address(0)),
                    0,
                    msg.value
                )
            );
            emit CollateralAdded(
                    _wNFTAddress, 
                    _wNFTTokenId, 
                    uint8(ETypes.AssetType.NATIVE),
                    address(0),
                    0,
                    msg.value
                );
        }
       
        // 4. Process Token Colleteral
        for (uint256 i = 0; i <_collateral.length; i ++) {
            if (_collateral[i].asset.assetType != ETypes.AssetType.NATIVE) {
                _transfer(_collateral[i], msg.sender, address(this));
                _updateCollateralInfo(
                    _wNFTAddress, 
                    _wNFTTokenId,
                    _collateral[i]
                );
                emit CollateralAdded(
                    _wNFTAddress, 
                    _wNFTTokenId, 
                    uint8(_collateral[i].asset.assetType),
                    _collateral[i].asset.contractAddress,
                    _collateral[i].tokenId,
                    _collateral[i].amount
                );
            }
        }
    }

    function _updateCollateralInfo(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem memory collateralItem
    ) internal virtual 
    {
        if (wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length == 0) {
            // Just add first record in empty collateral storage
            wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.push(collateralItem);
        } else {
            // Collateral storage is not empty
            (uint256 _amnt, uint256 _index) = _getCollateralBalanceAndIndex(
                _wNFTAddress, 
                _wNFTTokenId,
                collateralItem.asset.assetType, 
                //ETypes.AssetType.ERC20,
                collateralItem.asset.contractAddress,
                collateralItem.tokenId
            );
            /////////////////////////////////////////
            //  ERC20 Collateral                  ///
            /////////////////////////////////////////
            if (collateralItem.asset.assetType == ETypes.AssetType.ERC20 && _amnt> 0) {
                wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[_index].amount += collateralItem.amount;
            } else {
                //So if we are here hence there is NO that _erc20 in collateral yet 
                //We can add more tokens if limit NOT exccedd
                require(
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length < MAX_COLLATERAL_SLOTS, 
                    "To much tokens in collatteral"
                );
                wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.push(collateralItem);
                return;
            }


            /////////////////////////////////////////
            //  ERC1155 Collateral                ///
            /////////////////////////////////////////
            if (collateralItem.asset.assetType == ETypes.AssetType.ERC1155 && _amnt> 0) {
                wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[_index].amount += collateralItem.amount;
            } else {
                //So if we are here hence there is NO that _erc20 in collateral yet 
                //We can add more tokens if limit NOT exccedd
                require(
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length < MAX_COLLATERAL_SLOTS, 
                    "To much tokens in collatteral"
                );
                wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.push(collateralItem);
                return;
            }

            /////////////////////////////////////////
            //  ERC721 Collateral                 ///
            /////////////////////////////////////////
            if (collateralItem.asset.assetType == ETypes.AssetType.ERC721 ) {
                require(
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length < MAX_COLLATERAL_SLOTS, 
                    "To much  tokens in collatteral"
                );
                wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.push(collateralItem);
                return;
            }
        }
    }



    function _getERC20CollateralBalance(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        address _erc20
    ) public view returns (uint256, uint256) 
    {
        return _getCollateralBalanceAndIndex(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetType.ERC20, 
            _erc20,
            0
        );
    }

    function _getERC1155CollateralBalance(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        address _erc1155,
        uint256 _tokenId
    ) internal view returns (uint256, uint256) 
    {
        return _getCollateralBalanceAndIndex(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetType.ERC1155, 
            _erc1155,
            _tokenId
        ); 
    }

    function _getCollateralBalanceAndIndex(
        address _wNFTAddress, 
        uint256 _wNFTTokenId,
        ETypes.AssetType _collateralType, 
        address _erc,
        uint256 _tokenId
    ) internal view returns (uint256, uint256) 
    {
        //ERC20Collateral[] memory e = erc20Collateral[_wrappedId];
        for (uint256 i = 0; i < wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length; i ++) {
            if (wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].asset.contractAddress == _erc &&
                wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].tokenId == _tokenId &&
                wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].asset.assetType == _collateralType 
            ) 
            {
                return (wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].amount, i);
            }
        }
    }

    function _getWNFTCollateralCount(
        address _wNFTAddress, 
        uint256 _wNFTTokenId,
        ETypes.AssetType _collateralType
    ) internal view returns (uint256) 
    {
        if (_collateralType == ETypes.AssetType.EMPTY) {
            return wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length;
        } else {
            uint256 n;
            for (uint256 i = 0; i < wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length; i ++) {
                if (
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].asset.assetType == _collateralType 
                ) 
                {
                    n ++;
                }
            }   
            return n;    
        }

    }


}