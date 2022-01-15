// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - main protocol contract
pragma solidity 0.8.10;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";
import "@openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol";
//import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
//import "./TechToken.sol";
//import "../interfaces/IERC20Extended.sol";
import "../interfaces/IFeeRoyaltyModel.sol";
import "../interfaces/IWrapper.sol";
import "../interfaces/IAdvancedWhiteList.sol";
import "./LibEnvelopTypes.sol";
import "../interfaces/IERC721Mintable.sol";
import "../interfaces/IERC1155Mintable.sol";
import "./TokenService.sol";
//import "../interfaces/ITokenService.sol";

// #### Envelop ProtocolV1 Rules
// 15   14   13   12   11   10   9   8   7   6   5   4   3   2   1   0  <= Bit number(dec)
// ------------------------------------------------------------------------------------  
//  1    1    1    1    1    1   1   1   1   1   1   1   1   1   1   1
//  |    |    |    |    |    |   |   |   |   |   |   |   |   |   |   |
//  |    |    |    |    |    |   |   |   |   |   |   |   |   |   |   +-No_Unwrap
//  |    |    |    |    |    |   |   |   |   |   |   |   |   |   +-No_Wrap 
//  |    |    |    |    |    |   |   |   |   |   |   |   |   +-No_Transfer
//  |    |    |    |    |    |   |   |   |   |   |   |   +-No_Collateral
//  |    |    |    |    |    |   |   |   |   |   |   +-reserved_core
//  |    |    |    |    |    |   |   |   |   |   +-reserved_core
//  |    |    |    |    |    |   |   |   |   +-reserved_core  
//  |    |    |    |    |    |   |   |   +-reserved_core
//  |    |    |    |    |    |   |   |
//  |    |    |    |    |    |   |   |
//  +----+----+----+----+----+---+---+
//      for use in extendings
/**
 * @title Non-Fungible Token Wrapper
 * @dev Make  wraping for existing ERC721 & ERC1155 and empty 
 */
contract WrapperBaseV1 is ReentrancyGuard, ERC721Holder, ERC1155Holder, IWrapper, TokenService, Ownable {
    //using SafeERC20 for IERC20Extended;


    uint256 public MAX_COLLATERAL_SLOTS = 20;
    address public protocolTechToken;
    address public protocolWhiteList;
    //address public tokenService;

     
    mapping(address => bool) public trustedOperators;

    // Map from wrapping asset type to wnft contract address and last minted id
    mapping(ETypes.AssetType => ETypes.NFTItem) public lastWNFTId;  
    
    // Map from wrapped token address and id => wNFT record 
    mapping(address => mapping(uint256 => ETypes.WNFT)) public wrappedTokens; //? Private in Production

    //error UnSupportedAsset(ETypes.AssetItem asset);


    modifier onlyTrusted() {
        require (trustedOperators[msg.sender] == true, "Only trusted address");
        _;
    }

    constructor(address _erc20) {
        require(_erc20 != address(0), "ProtocolTechToken cant be zero value");
        protocolTechToken = _erc20;
        trustedOperators[msg.sender] = true;
        IFeeRoyaltyModel(protocolTechToken).registerModel(); 
    }

    
    function wrap(ETypes.INData calldata _inData, ETypes.AssetItem[] calldata _collateral, address _wrappFor) 
        public 
        virtual
        payable 
        nonReentrant 
        returns (ETypes.AssetItem memory) 
    {

        // 0. Check assetIn asset
        require(_checkWrap(_inData,_wrappFor),
            "Wrap check fail"
        );
        // 1. Take users inAsset
        if ( _inData.inAsset.asset.assetType != ETypes.AssetType.NATIVE &&
             _inData.inAsset.asset.assetType != ETypes.AssetType.EMPTY
        ) 
        {
            require(
                _mustTransfered(_inData.inAsset) == _transferSafe(_inData.inAsset, msg.sender, address(this)),
                "Suspicious asset for wrap"
            );
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

        if (_checkAddCollateral(
                lastWNFTId[_inData.outType].contractAddress, 
                lastWNFTId[_inData.outType].tokenId,
                _collateral
            )) 
        {

            _addCollateral(
                lastWNFTId[_inData.outType].contractAddress, 
                lastWNFTId[_inData.outType].tokenId, 
                _collateral
            );

        } 
         
        // Charge Fee Hook 
        // There is No Any Fees in Protocol
        // So this hook can be used in b2b extensions of Envelop Protocol 
        // 0x02 - feeType for WrapFee
        _chargeFees(
            lastWNFTId[_inData.outType].contractAddress, 
            lastWNFTId[_inData.outType].tokenId, 
            msg.sender, 
            address(this), 
            0x02
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

    function wrapUnsafe(ETypes.INData calldata _inData, ETypes.AssetItem[] calldata _collateral, address _wrappFor) 
        public 
        virtual
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


    function addCollateral(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateral
    ) external payable virtual {

        require(
            _checkAddCollateral(
                _wNFTAddress, 
                _wNFTTokenId,
                _collateral
            ),
            "Forbidden add collateral"
        );
        _addCollateral(
            _wNFTAddress, 
            _wNFTTokenId, 
            _collateral
        );
    }

    function addCollateralUnsafe(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateral
    ) 
        external 
        payable 
        virtual 
        onlyTrusted 
    {

        _addCollateral(
            _wNFTAddress, 
            _wNFTTokenId, 
            _collateral
        );
    }

    function unWrap(ETypes.AssetType _wNFTType, address _wNFTAddress, uint256 _wNFTTokenId) external virtual {
        unWrap(_wNFTType,_wNFTAddress, _wNFTTokenId, false);
    }

    function unWrap(ETypes.AssetType _wNFTType, address _wNFTAddress, uint256 _wNFTTokenId, bool _isEmergency) public virtual {
        // 0. Check core protocol logic:
        // - who and what possible to unwrap
        (address burnFor, uint256 burnBalance) = _checkCoreUnwrap(_wNFTType, _wNFTAddress, _wNFTTokenId);
        
        
        // // 1. Check  rules, such as unWrapless
        // require(
        //     _checkUnwrap(_wNFTAddress, _wNFTTokenId),
        //     "UnWrap check fail"

        // );

        // 2. Check  locks = move to _checkUnwrap
        require(
            _checkLocks(_wNFTAddress, _wNFTTokenId)
        );

        // 3. Charge Fee Hook 
        // There is No Any Fees in Protocol
        // So this hook can be used in b2b extensions of Envelop Protocol 
        // 0x03 - feeType for UnWrapFee
        // 
        _chargeFees(_wNFTAddress, _wNFTTokenId, msg.sender, address(this), 0x03);
        uint256 nativeCollateralAmount = _getNativeCollateralBalance(_wNFTAddress, _wNFTTokenId);
        ///////////////////////////////////////////////
        ///  Place for hook                        ////
        ///////////////////////////////////////////////
        // 4. Safe return collateral to appropriate benificiary

        if (!_beforeUnWrapHook(_wNFTAddress, _wNFTTokenId, _isEmergency)) {
            return;
        }
        
        // 5. BurnWNFT
        _burnNFT(
            _wNFTType, 
            _wNFTAddress, 
            burnFor,  // msg.sender, 
            _wNFTTokenId, 
            burnBalance
        );
        
        // 5. Return Original
        if (wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset.asset.assetType != ETypes.AssetType.NATIVE && 
            wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset.asset.assetType != ETypes.AssetType.EMPTY
        ) 
        {

            if (!_isEmergency){
                _transferSafe(
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset,
                    address(this),
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestinition
                );
            } else {
                _transferEmergency (
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset,
                    address(this),
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestinition
                );
            }
        }        
        emit UnWrappedV1(
            _wNFTAddress,
            wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset.asset.contractAddress,
            _wNFTTokenId, 
            wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset.tokenId,
            wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestinition, 
            nativeCollateralAmount,  // TODO Check  GAS
            wrappedTokens[_wNFTAddress][_wNFTTokenId].rules 
        );
    } 

    function chargeFees(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        address _from, 
        address _to,
        bytes1 _feeType
    ) 
        public
        virtual  
        returns (bool) 
    {
        //TODO  only wNFT contract can  execute  this(=charge fee)
        require(msg.sender == _wNFTAddress || msg.sender == address(this), 
            "Only for wNFT or wrapper"
        );
        require( _chargeFees(_wNFTAddress, _wNFTTokenId, _from, _to, _feeType),
            "Fee charge fail"
        );
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

    // function setTokenService(address _serviveAddress) external onlyOwner {
    //     tokenService = _serviveAddress;
    // }

    function setTrustedAddres(address _operator, bool _status) public onlyOwner {
        trustedOperators[_operator] = _status;
    }
    /////////////////////////////////////////////////////////////////////

    //TODO Reafactro with internal getters
    function getERC20CollateralBalance(
        address _wNFTAddress, 
        uint256 _tokenId, 
        address _erc20
    ) public view returns (uint256) 
    {
        for (uint256 i = 0; i < wrappedTokens[_wNFTAddress][_tokenId].collateral.length; i ++) {
            if (wrappedTokens[_wNFTAddress][_tokenId].collateral[i].asset.contractAddress == _erc20 &&
                wrappedTokens[_wNFTAddress][_tokenId].collateral[i].asset.assetType == ETypes.AssetType.ERC20 
                ) {
                return wrappedTokens[_wNFTAddress][_tokenId].collateral[i].amount;
            }
        }
    }

    function getWrappedToken(address _wNFTAddress, uint256 _wNFTTokenId) public view returns (ETypes.WNFT memory) {
        return _getWrappedToken(_wNFTAddress,_wNFTTokenId);

    }

    function getOriginalURI(address _wNFTAddress, uint256 _wNFTTokenId) public view returns(string memory) {
        ETypes.AssetItem memory _wnftInAsset = _getWrappedToken(
                _wNFTAddress, _wNFTTokenId
        ).inAsset;

        if (_wnftInAsset.asset.assetType == ETypes.AssetType.ERC721) {
            return IERC721Metadata(_wnftInAsset.asset.contractAddress).tokenURI(_wnftInAsset.tokenId);
        
        } else if (_wnftInAsset.asset.assetType == ETypes.AssetType.ERC1155) {
            return IERC1155MetadataURI(_wnftInAsset.asset.contractAddress).uri(_wnftInAsset.tokenId);
        
        } else {
            return '';
        } 
    } 
    /////////////////////////////////////////////////////////////////////
    //                    Internals                                    //
    /////////////////////////////////////////////////////////////////////

    // function _mintNFT(
    //     ETypes.AssetType _mint_type, 
    //     address _contract, 
    //     address _mintFor, 
    //     uint256 _tokenId, 
    //     uint256 _outBalance
    // ) 
    //     internal 
    //     virtual
    // {
    //     ITokenService(tokenService).mintNFT(
    //         _mint_type,
    //         _contract,
    //         _mintFor,
    //         _tokenId,
    //         _outBalance

    //     );
    //     // if (_mint_type == ETypes.AssetType.ERC721) {
    //     //     IERC721Mintable(_contract).mint(_mintFor, _tokenId);
    //     // } else if (_mint_type == ETypes.AssetType.ERC1155) {
    //     //     IERC1155Mintable(_contract).mint(_mintFor, _tokenId, _outBalance);
    //     // }
    // }

    // function _burnNFT(
    //     ETypes.AssetType _burn_type, 
    //     address _contract, 
    //     address _burnFor, 
    //     uint256 _tokenId, 
    //     uint256 _balance
    // ) 
    //     internal
    //     virtual 
    // {
    //     ITokenService(tokenService).burnNFT(
    //         _burn_type,
    //         _contract,
    //         _burnFor,
    //         _tokenId,
    //         _balance
    //     );
    //     // if (_burn_type == ETypes.AssetType.ERC721) {
    //     //     IERC721Mintable(_contract).burn(_tokenId);

    //     // } else if (_burn_type == ETypes.AssetType.ERC1155) {
    //     //     IERC1155Mintable(_contract).burn(_burnFor, _tokenId, _balance);
    //     // }
        
    // }

    // function _transfer(
    //     ETypes.AssetItem memory _assetItem,
    //     address _from,
    //     address _to
    // ) internal virtual returns (bool _transfered){
    //     // if (_assetItem.asset.assetType == ETypes.AssetType.NATIVE) {
    //     //     (bool success, ) = _to.call{ value: _assetItem.amount}("");
    //     //     require(success, "transfer failed");
    //     //     _transfered = true; 
    //     // } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC20) {
    //     //     require(IERC20Extended(_assetItem.asset.contractAddress).balanceOf(_from) <= _assetItem.amount, "UPS!!!!");
    //     //     IERC20Extended(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.amount);
    //     //     _transfered = true;
    //     // } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC721) {
    //     //     IERC721Mintable(_assetItem.asset.contractAddress).transferFrom(_from, _to, _assetItem.tokenId);
    //     //     _transfered = true;
    //     // } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC1155) {
    //     //     IERC1155Mintable(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.tokenId, _assetItem.amount, "");
    //     //     _transfered = true;
    //     // } else {
    //     //     revert UnSupportedAsset(_assetItem);
    //     // }
    //     _transfered = ITokenService(tokenService).transfer(
    //         _assetItem,
    //         _from,
    //         _to
    //     );
    //     //return _transfered;
    // }

    // function _transferSafe(
    //     ETypes.AssetItem memory _assetItem,
    //     address _from,
    //     address _to
    // ) internal virtual returns (uint256 _transferedValue){
    //     // uint256 balanceBefore;
    //     // if (_assetItem.asset.assetType == ETypes.AssetType.NATIVE) {
    //     //     balanceBefore = _to.balance;
    //     //     (bool success, ) = _to.call{ value: _assetItem.amount}("");
    //     //     require(success, "transfer failed");
    //     //     _transferedValue = _to.balance - balanceBefore;
        
    //     // } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC20) {
    //     //     balanceBefore = IERC20Extended(_assetItem.asset.contractAddress).balanceOf(_to);
    //     //     if (_from == address(this)){
    //     //         IERC20Extended(_assetItem.asset.contractAddress).safeTransfer(_to, _assetItem.amount);
    //     //     } else {
    //     //         IERC20Extended(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.amount);
    //     //     }    
    //     //     _transferedValue = IERC20Extended(_assetItem.asset.contractAddress).balanceOf(_to) - balanceBefore;
        
    //     // } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC721 &&
    //     //     IERC721Mintable(_assetItem.asset.contractAddress).ownerOf(_assetItem.tokenId) == _from) {
    //     //     balanceBefore = IERC721Mintable(_assetItem.asset.contractAddress).balanceOf(_to); 
    //     //     IERC721Mintable(_assetItem.asset.contractAddress).transferFrom(_from, _to, _assetItem.tokenId);
    //     //     if (IERC721Mintable(_assetItem.asset.contractAddress).ownerOf(_assetItem.tokenId) == _to &&
    //     //         IERC721Mintable(_assetItem.asset.contractAddress).balanceOf(_to) - balanceBefore == 1
    //     //         ) {
    //     //         _transferedValue = 1;
    //     //     }
        
    //     // } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC1155) {
    //     //     balanceBefore = IERC1155Mintable(_assetItem.asset.contractAddress).balanceOf(_to, _assetItem.tokenId);
    //     //     IERC1155Mintable(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.tokenId, _assetItem.amount, "");
    //     //     _transferedValue = IERC1155Mintable(_assetItem.asset.contractAddress).balanceOf(_to, _assetItem.tokenId) - balanceBefore;
        
    //     // } else {
    //     //     revert UnSupportedAsset(_assetItem);
    //     // }
    //     _transferedValue = ITokenService(tokenService).transferSafe(
    //         _assetItem,
    //         _from,
    //         _to
    //     );
    //     return _transferedValue;
    // }

    // This function must never revert. Use it for unwrap in case some 
    // collateral transfers are revert
    // function _transferEmergency(
    //     ETypes.AssetItem memory _assetItem,
    //     address _from,
    //     address _to
    // ) internal virtual returns (uint256 _transferedValue){
        //TODO   think about try catch in transfers
        // uint256 balanceBefore;
        // if (_assetItem.asset.assetType == ETypes.AssetType.NATIVE) {
        //     balanceBefore = _to.balance;
        //     (bool success, ) = _to.call{ value: _assetItem.amount}("");
        //     //require(success, "transfer failed");
        //     _transferedValue = _to.balance - balanceBefore;
        
        // } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC20) {
        //     if (_from == address(this)){
        //         //IERC20Extended(_assetItem.asset.contractAddress).safeTransfer(_to, _assetItem.amount);
        //         (bool success, ) = _assetItem.asset.contractAddress.call(
        //             abi.encodeWithSignature("transfer(address,uint256)", _to, _assetItem.amount)
        //         );
        //     } else {
        //         //IERC20Extended(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.amount);
        //         (bool success, ) = _assetItem.asset.contractAddress.call(
        //             abi.encodeWithSignature("transferFrom(address,address,uint256)", _from,  _to, _assetItem.amount)
        //         );
        //     }    
        //     _transferedValue = _assetItem.amount;
        
        // } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC721) {
        //     //IERC721Mintable(_assetItem.asset.contractAddress).transferFrom(_from, _to, _assetItem.tokenId);
        //     (bool success, ) = _assetItem.asset.contractAddress.call(
        //         abi.encodeWithSignature("transferFrom(address,address,uint256)", _from,  _to, _assetItem.tokenId)
        //     );
        //     _transferedValue = 1;
        
        // } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC1155) {
        //     //IERC1155Mintable(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.tokenId, _assetItem.amount, "");
        //     (bool success, ) = _assetItem.asset.contractAddress.call(
        //         abi.encodeWithSignature("safeTransferFrom(address,address,uint256,uint256,bytes)", _from, _to, _assetItem.tokenId, _assetItem.amount, "")
        //     );
        //     _transferedValue = _assetItem.amount;
        
        // } else {
        //     revert UnSupportedAsset(_assetItem);
        // }
    //     _transferedValue = ITokenService(tokenService).transferEmergency(
    //         _assetItem,
    //         _from,
    //         _to
    //     );
    //     //return _transferedValue;
    // }

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
        
        // Process Native Colleteral
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
       
        // Process Token Colleteral
        for (uint256 i = 0; i <_collateral.length; i ++) {
            if (_collateral[i].asset.assetType != ETypes.AssetType.NATIVE) {
                require(
                    _mustTransfered(_collateral[i]) == _transferSafe(_collateral[i], msg.sender, address(this)),
                    "Suspicious asset for wrap"
                );
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
            //  ERC20 & NATIVE Collateral         ///
            /////////////////////////////////////////
            if (collateralItem.asset.assetType == ETypes.AssetType.ERC20 ||
                 collateralItem.asset.assetType == ETypes.AssetType.NATIVE){

                if (_amnt > 0) {
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[_index].amount += collateralItem.amount;
                } else {
                //So if we are here hence there is NO that _erc20 in collateral yet 
                //We can add more tokens if limit NOT exccedd
                    require(
                        wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length < MAX_COLLATERAL_SLOTS, 
                        "To much tokens in collatteral"
                    );
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.push(collateralItem);
                }
                return;    
            }

            /////////////////////////////////////////
            //  ERC1155 Collateral                ///
            /////////////////////////////////////////
            if (collateralItem.asset.assetType == ETypes.AssetType.ERC1155) {
                if (_amnt> 0) {
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[_index].amount += collateralItem.amount;
                } else {
                    //So if we are here hence there is NO that _erc20 in collateral yet 
                    //We can add more tokens if limit NOT exccedd
                    require(
                        wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length < MAX_COLLATERAL_SLOTS, 
                        "To much tokens in collatteral"
                    );
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.push(collateralItem);
                }
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


    function _chargeFees(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        address _from, 
        address _to,
        bytes1 _feeType
    ) 
        internal
        virtual  
        returns (bool) 
    {
        if (_feeType == 0x00) {// Transfer fee
            for (uint256 i = 0; i < wrappedTokens[_wNFTAddress][_wNFTTokenId].fees.length; i ++){
                /////////////////////////////////////////
                // For Transfer Fee -0x00             ///  
                /////////////////////////////////////////
                if (wrappedTokens[_wNFTAddress][_wNFTTokenId].fees[i].feeType == 0x00){
                   // - get modelAddress.  Default feeModel adddress always live in
                   // protocolTechToken. When white list used it is possible override that model
                   address feeModel = protocolTechToken;
                    if  (protocolWhiteList != address(0)) {
                        feeModel = IAdvancedWhiteList(protocolWhiteList).getWLItem(
                            wrappedTokens[_wNFTAddress][_wNFTTokenId].fees[i].token).transferFeeModel;
                    }

                    // - get transfer list from external model by feetype(with royalties)
                    (ETypes.AssetItem[] memory assetItems, address[] memory from, address[] memory to) =
                        IFeeRoyaltyModel(feeModel).getTransfersList(
                            wrappedTokens[_wNFTAddress][_wNFTTokenId].fees[i],
                            wrappedTokens[_wNFTAddress][_wNFTTokenId].royalties,
                            _from, 
                            _to 
                        );
                    // - execute transfers
                    uint256 actualTransfered;
                    for (uint256 j = 0; j < to.length; j ++){
                        // if transfer receiver(to) = address(this) lets consider
                        // wNFT as receiver. in this case received amount
                        // will be added to collateral
                        if (to[j]== address(this)){
                            _updateCollateralInfo(
                              _wNFTAddress, 
                              _wNFTTokenId, 
                               assetItems[j]
                            ); 
                        }
                        actualTransfered = _transferSafe(assetItems[j], from[j], to[j]);
                        emit EnvelopFee(to[j], _wNFTAddress, _wNFTTokenId, actualTransfered); 
                    }
                }
                //////////////////////////////////////////
            }
            return true;
        }
    }


    /**
     * @dev This hook may be overriden in inheritor contracts for extend
     * base functionality.
     *
     * @param _wNFTAddress -wrapped token address
     * @param _wNFTTokenId -wrapped token id
     * 
     * must returns true for success unwrapping enable 
     */
    function _beforeUnWrapHook(address _wNFTAddress, uint256 _wNFTTokenId, bool _emergency) internal virtual returns (bool){
        uint256 transfered;
        for (uint256 i = 0; i < wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length; i ++) {
            if (wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].asset.assetType != ETypes.AssetType.EMPTY) {
                if (_emergency) {
                    // In case of something is wrong with any collateral (attack)
                    // user can use  this mode  for skip  malicious asset
                    transfered = _transferEmergency(
                        wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i],
                        address(this),
                        wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestinition
                    );
                } else {
                    transfered = _transferSafe(
                        wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i],
                        address(this),
                        wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestinition
                    );
                }

                // we collect info about contracts with not standard behavior
                if (transfered != wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].amount ) {
                    emit SuspiciousFail(
                        _wNFTAddress, 
                        _wNFTTokenId, 
                        wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].asset.contractAddress
                    );
                }

                // mark collateral record as returned
                wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].asset.assetType = ETypes.AssetType.EMPTY;                
            }
            // dont pop due in some case it c can be very costly
            // https://docs.soliditylang.org/en/v0.8.9/types.html#array-members  
            // TODO add check  that wew  are not  in the  end of array 

            // For safe exit in case of low gaslimit
            if (
                gasleft() <= 1_000 &&
                i < wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length - 1
             
                ) 
            {
                emit PartialUnWrapp(_wNFTAddress, _wNFTTokenId, i);
                return false;
            }
        }

        return true;
    }

    ////////////////////////////////////////////////////////////////////////////////////////////

    function _mustTransfered(ETypes.AssetItem calldata _assetForTransfer) internal pure returns(uint256 mustTransfered) {
        // Available for wrap assets must be good transferable (stakable).
        // So for erc721  mustTransfered always be 1
        if (_assetForTransfer.asset.assetType == ETypes.AssetType.ERC721) {
            mustTransfered = 1;
        } else {
            mustTransfered = _assetForTransfer.amount;
        }
        return mustTransfered;
    }
    

    function _getNativeCollateralBalance(
        address _wNFTAddress, 
        uint256 _wNFTTokenId 
    ) public view returns (uint256) 
    {
        (uint256 res, ) = _getCollateralBalanceAndIndex(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetType.NATIVE, 
            address(0), // tokenAddress 
            0           // tokenId
        );
        return res;
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

    function _getWrappedToken(address _wNFTAddress, uint256 _wNFTTokenId) internal view virtual returns (ETypes.WNFT memory) {
        // TODO  extend  this function in future implementation
        // to get info  from  external wNFT storages(old versions)
        return wrappedTokens[_wNFTAddress][_wNFTTokenId];
    } 

    function _checkRule(bytes2 _rule, bytes2 _wNFTrules) internal view returns (bool) {
        return _rule == (_rule & _wNFTrules);
    }

    // 0x00 - TimeLock
    // 0x01 - TransferFeeLock
    function _checkLocks(address _wNFTAddress, uint256 _wNFTTokenId) internal view returns (bool) {
        // Lets check that inAsset
        ETypes.Lock[] memory _locks =  wrappedTokens[_wNFTAddress][_wNFTTokenId].locks; 
        for (uint256 i = 0; i < _locks.length; i ++) {
            // Time Lock check
            if (_locks[i].lockType == 0x00) {
                require(
                    _locks[i].param <= block.timestamp,
                    "TimeLock error"
                );
            }

            // Fee Lock check
            if (_locks[i].lockType == 0x01) {
                // Lets check this lock rule against each fee record
                for (uint256 j = 0; j < wrappedTokens[_wNFTAddress][_wNFTTokenId].fees.length; j ++){
                    // Fee Lock depend  only from Transfer Fee - 0x00
                    if ( wrappedTokens[_wNFTAddress][_wNFTTokenId].fees[j].feeType == 0x00) {
                        (uint256 _bal,) = _getERC20CollateralBalance(
                            _wNFTAddress, 
                            _wNFTTokenId,
                            wrappedTokens[_wNFTAddress][_wNFTTokenId].fees[j].token
                        );
                        require(
                            _locks[i].param <= _bal,
                            "TransferFeeLock error"
                        );
                    }   

                }
                
            }
        }
        return true;
    }


    function _checkWrap(ETypes.INData calldata _inData, address _wrappFor) internal view returns (bool enabled){
        // Lets check that inAsset 
        // 0x0002 - this rule disable wrap already wrappednFT (NO matryoshka)
        enabled = !_checkRule(0x0002, _getWrappedToken(
            _inData.inAsset.asset.contractAddress, 
            _inData.inAsset.tokenId).rules
            ) 
            && _wrappFor != address(this);
        // Check WhiteList Logic
        if  (protocolWhiteList != address(0)) {
            require(
                !IAdvancedWhiteList(protocolWhiteList).getBLItem(_inData.inAsset.asset.contractAddress),
                "WL:Asset disabled for wrap"
            );
            require(
                IAdvancedWhiteList(protocolWhiteList).rulesEnabled(_inData.inAsset.asset.contractAddress, _inData.rules),
                "WL:Some rules are disabled for this asset"
            );

            for (uint256 i = 0; i < _inData.fees.length; i ++){
                require(
                    IAdvancedWhiteList(protocolWhiteList).enabledForFee(
                        _inData.fees[i].token),
                        "WL:Some assets are not enabled for fee"
                    );
            }
        }    
        return enabled;
    }
    
    function _checkAddCollateral(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateral
    ) 
        internal 
        view 
        returns (bool enabled)
    {
        // Lets check wNFT rules 
        // 0x0008 - this rule disable add collateral
        enabled = !_checkRule(0x0008, _getWrappedToken(_wNFTAddress, _wNFTTokenId).rules); 
        
        // Check WhiteList Logic
        if  (protocolWhiteList != address(0)) {
            for (uint256 i = 0; i < _collateral.length; i ++){
                if (_collateral[i].asset.assetType != ETypes.AssetType.EMPTY) {
                    require(
                        IAdvancedWhiteList(protocolWhiteList).enabledForCollateral(
                        _collateral[i].asset.contractAddress),
                        "WL:Some assets are not enabled for collateral"
                    );
                }
            }
        }
        return enabled;
    }

    function _checkCoreUnwrap(ETypes.AssetType _wNFTType, address _wNFTAddress, uint256 _wNFTTokenId) 
        internal 
        view 
        virtual 
        returns (address burnFor, uint256 burnBalance) 
    {
        
        // Lets wNFT rules 
        // 0x0001 - this rule disable unwrap wrappednFT 
        require(!_checkRule(0x0001, _getWrappedToken(_wNFTAddress, _wNFTTokenId).rules),
            "UnWrapp forbidden by author"
        );

        if (_wNFTType == ETypes.AssetType.ERC721) {
            // Only token owner can UnWrap
            burnFor = IERC721Mintable(_wNFTAddress).ownerOf(_wNFTTokenId);
            require(burnFor == msg.sender, 
                'Only owner can unwrap it'
            ); 
            return (burnFor, burnBalance);

        } else if (_wNFTType == ETypes.AssetType.ERC1155) {
            burnBalance = IERC1155Mintable(_wNFTAddress).totalSupply(_wNFTTokenId);
            burnFor = msg.sender;
            require(
                burnBalance ==
                IERC1155Mintable(_wNFTAddress).balanceOf(burnFor, _wNFTTokenId)
                ,'ERC115 unwrap available only for all totalSupply'
            );
            return (burnFor, burnBalance);
            
        } else {
            revert UnSupportedAsset(ETypes.AssetItem(ETypes.Asset(_wNFTType,_wNFTAddress),_wNFTTokenId, 0));
        }
    }

}