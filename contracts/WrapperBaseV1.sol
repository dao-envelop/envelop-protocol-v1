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
    uint256 constant public MAX_FEE_THRESHOLD_PERCENT = 1; //percent from project token totalSupply

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

    function wrap(ETypes.WNFT calldata _inData, address _wrappFor) 
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
        // 3. Process Colleteral
        uint256 nativeDeclared;
        for (uint256 i = 0; i < _inData.collateral.length; i ++) {
            if (_inData.collateral[i].asset.assetType != ETypes.AssetType.NATIVE) {
                _transfer(_inData.collateral[i], msg.sender, address(this));
            } else if (_inData.collateral[i].asset.assetType == ETypes.AssetType.NATIVE) {
                require(msg.value >= _inData.collateral[i].amount, "Insufficient funds for native collateral");
                nativeDeclared += _inData.collateral[i].amount;
            }    
        }
        require(msg.value == nativeDeclared, "Need pass correct native value in wrap params");

        // 4. Safe wNFT info
        _saveWNFTinfo(
            lastWNFTId[_inData.outType].contractAddress, 
            lastWNFTId[_inData.outType].tokenId,
            _inData
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

    function wrapSafe(ETypes.WNFT calldata _inData, address _wrappFor) public returns (ETypes.AssetItem memory) {
        //TODO many Checks
        return wrap(_inData, _wrappFor);
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

    function _saveWNFTinfo(address wNFTAddress, uint256 tokenId, ETypes.WNFT calldata _inData) internal virtual {
        wrappedTokens[wNFTAddress][tokenId] = _inData;

    }

}