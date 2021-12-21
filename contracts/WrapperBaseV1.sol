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

     
    mapping(address => bool) public trustedOperators;

    // Map from wrapping asset type to wnft contract address and last minted id
    mapping(ETypes.AssetType => ETypes.NFTItem) public lastWNFTId;  
    
    // Map from wrapped token address and id => wNFT record 
    mapping(address => mapping(uint256 => ETypes.WNFT)) public wrappedTokens; //? Private in Production

    error UnSupportedAsset(ETypes.AssetItem asset);


    modifier onlyTrusted() {
        require (trustedOperators[msg.sender] == true, "Only trusted address");
        _;
    }

    constructor(address _erc20) {
        require(_erc20 != address(0), "ProtocolTechToken cant be zero value");
        protocolTechToken = _erc20;
        trustedOperators[msg.sender] = true; 
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
        if (  _inData.inAsset.asset.assetType != ETypes.AssetType.NATIVE &&
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

    function wrapUnsafe(ETypes.INData calldata _inData, ETypes.AssetItem[] calldata _collateral, address _wrappFor) 
        public 
        virtual
        payable
        onlyTrusted 
        nonReentrant 
        returns (ETypes.AssetItem memory) 
    {
        // 1. Take users inAsset
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
    ) external payable virtual {
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
        (address burnFor, uint256 burnBalance) = _checkCore(_wNFTType, _wNFTAddress, _wNFTTokenId);
        
        
        // 1. Check  rules, such as unWrapless
        require(
            _checkRules(_wNFTAddress, _wNFTTokenId)
        );

        // 2. Check  locks
        require(
            _checkLocks(_wNFTAddress, _wNFTTokenId)
        );

        // 3. Charge Fee Hook
        require(
            _chargeFees(_wNFTAddress, _wNFTTokenId)
        );
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
        ETypes.AssetItem memory _assetItem,
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
        ETypes.AssetItem memory _assetItem,
        address _from,
        address _to
    ) internal virtual returns (uint256 _transferedValue){
        //TODO   think about try catch in transfers
        uint256 balanceBefore;
        if (_assetItem.asset.assetType == ETypes.AssetType.NATIVE) {
            balanceBefore = _to.balance;
            (bool success, ) = _to.call{ value: _assetItem.amount}("");
            require(success, "transfer failed");
            _transferedValue = _to.balance - balanceBefore;
        
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC20) {
            balanceBefore = IERC20Extended(_assetItem.asset.contractAddress).balanceOf(_to);
            if (_from == address(this)){
                IERC20Extended(_assetItem.asset.contractAddress).safeTransfer(_to, _assetItem.amount);
            } else {
                IERC20Extended(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.amount);
            }    
            _transferedValue = IERC20Extended(_assetItem.asset.contractAddress).balanceOf(_to) - balanceBefore;
        
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC721 &&
            IERC721Mintable(_assetItem.asset.contractAddress).ownerOf(_assetItem.tokenId) == _from) {
            balanceBefore = IERC721Mintable(_assetItem.asset.contractAddress).balanceOf(_to); 
            IERC721Mintable(_assetItem.asset.contractAddress).transferFrom(_from, _to, _assetItem.tokenId);
            if (IERC721Mintable(_assetItem.asset.contractAddress).ownerOf(_assetItem.tokenId) == _to &&
                IERC721Mintable(_assetItem.asset.contractAddress).balanceOf(_to) - balanceBefore == 1
                ) {
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

    // This function must never revert. Use it for unwrap in case some 
    // collateral transfers are revert
    function _transferEmergency(
        ETypes.AssetItem memory _assetItem,
        address _from,
        address _to
    ) internal virtual returns (uint256 _transferedValue){
        //TODO   think about try catch in transfers
        uint256 balanceBefore;
        if (_assetItem.asset.assetType == ETypes.AssetType.NATIVE) {
            balanceBefore = _to.balance;
            (bool success, ) = _to.call{ value: _assetItem.amount}("");
            //require(success, "transfer failed");
            _transferedValue = _to.balance - balanceBefore;
        
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC20) {
            if (_from == address(this)){
                //IERC20Extended(_assetItem.asset.contractAddress).safeTransfer(_to, _assetItem.amount);
                (bool success, ) = _assetItem.asset.contractAddress.call(
                    abi.encodeWithSignature("transfer(address,uint256)", _to, _assetItem.amount)
                );
            } else {
                //IERC20Extended(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.amount);
                (bool success, ) = _assetItem.asset.contractAddress.call(
                    abi.encodeWithSignature("transferFrom(address,address,uint256)", _from,  _to, _assetItem.amount)
                );
            }    
            _transferedValue = _assetItem.amount;
        
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC721) {
            //IERC721Mintable(_assetItem.asset.contractAddress).transferFrom(_from, _to, _assetItem.tokenId);
            (bool success, ) = _assetItem.asset.contractAddress.call(
                abi.encodeWithSignature("transferFrom(address,address,uint256)", _from,  _to, _assetItem.tokenId)
            );
            _transferedValue = 1;
        
        } else if (_assetItem.asset.assetType == ETypes.AssetType.ERC1155) {
            //IERC1155Mintable(_assetItem.asset.contractAddress).safeTransferFrom(_from, _to, _assetItem.tokenId, _assetItem.amount, "");
            (bool success, ) = _assetItem.asset.contractAddress.call(
                abi.encodeWithSignature("safeTransferFrom(address,address,uint256,uint256,bytes)", _from, _to, _assetItem.tokenId, _assetItem.amount, "")
            );
            _transferedValue = _assetItem.amount;
        
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

    function _chargeFees(address _wNFTAddress, uint256 _wNFTTokenId) internal  returns (bool) {
        return true;
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

    function _checkRules(address _wNFTAddress, uint256 _wNFTTokenId) internal view returns (bool) {
        return true;
    }

    function _checkLocks(address _wNFTAddress, uint256 _wNFTTokenId) internal view returns (bool) {
        return true;
    } 

    function _checkWrap(ETypes.INData calldata _inData, address _wrappFor) internal view returns (bool){
        return true;
    }

    function _checkCore(ETypes.AssetType _wNFTType, address _wNFTAddress, uint256 _wNFTTokenId) 
        internal 
        view 
        virtual 
        returns (address burnFor, uint256 burnBalance) 
    {
        if (_wNFTType == ETypes.AssetType.ERC721) {
            // Only token owner or unwraper can UnWrap
            burnFor = IERC721Mintable(_wNFTAddress).ownerOf(_wNFTTokenId);
            require(burnFor == msg.sender, 
                //|| wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestinition == msg.sender,
                'Only owner or unWrapDestinition can unwrap it'
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