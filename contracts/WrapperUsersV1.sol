// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - for users SBT collections
pragma solidity 0.8.21;

//import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";
import "@openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./TokenServiceExtended.sol";
import "../interfaces/IWrapperUsers.sol";
import "../interfaces/IUserCollectionRegistry.sol";


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
contract WrapperUsersV1 is 
    ReentrancyGuard, 
    ERC721Holder, 
    ERC1155Holder, 
    IWrapperUsers, 
    TokenServiceExtended
{

    uint256 public MAX_COLLATERAL_SLOTS = 25;
    address constant public protocolTechToken = address(0);  // Just for backward interface compatibility
    address constant public protocolWhiteList = address(0);  // Just for backward interface compatibility

    address immutable public usersCollectionRegistry;

    // Map from wrapping asset type to wnft contract address and last minted id
    //mapping(ETypes.AssetType => ETypes.NFTItem) public lastWNFTId;  
    
    // Map from wNFT address to it's type (721, 1155)
    //mapping(address => ETypes.AssetType) public wnftTypes;

    // Map from wrapped token address and id => wNFT record 
    mapping(address => mapping(uint256 => ETypes.WNFT)) internal wrappedTokens; 

    constructor(address _usersWNFTRegistry) {
        require(_usersWNFTRegistry != address(0), "Only for non zero registry");
        usersCollectionRegistry = _usersWNFTRegistry;
    }

    function wrap(
        ETypes.INData calldata _inData, 
        ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor
    ) 
        public 
        virtual
        payable 
        returns (ETypes.AssetItem memory) 
    {
      // Just for backward interface compatibility        
    }

    function wrapIn(
        ETypes.INData calldata _inData, 
        ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor,
        address _wrappIn
    )
        public 
        virtual
        payable 
        nonReentrant 
        returns (ETypes.AssetItem memory) 
    {

        // 0. Check assetIn asset
        require(_checkWrap(_inData, _wrappFor, _wrappIn),
            "Wrap check fail"
        );
        
        
        // 2. Mint wNFT
        //lastWNFTId[_inData.outType].tokenId += 1;  //Save just will minted id 
        uint256 wnftId = _mintWNFTWithRules(
            _inData.outType,     // what will be minted instead of wrapping asset
            _wrappIn, // wNFT contract address
            _wrappFor,                                   // wNFT receiver (1st owner) 
            _inData.outBalance,                           // wNFT tokenId
            _inData.rules
        );
        
        // 3. Safe wNFT info
        _saveWNFTinfo(
            _wrappIn, 
            wnftId,
            _inData
        );

        // 1. Take users inAsset
        if ( _inData.inAsset.asset.assetType != ETypes.AssetType.NATIVE &&
             _inData.inAsset.asset.assetType != ETypes.AssetType.EMPTY
        ) 
        {
            require(
                _mustTransfered(_inData.inAsset) == _transferSafe(
                    _inData.inAsset, 
                    msg.sender, 
                    address(this)
                ),
                "Suspicious asset for wrap"
            );
        }

        addCollateral(
            _wrappIn, 
            wnftId,
            _collateral
        ); 
         
        // Charge Fee Hook 
        // There is No Any Fees in Protocol
        // So this hook can be used in b2b extensions of Envelop Protocol 
        // 0x02 - feeType for WrapFee
        // _chargeFees(
        //     lastWNFTId[_inData.outType].contractAddress, 
        //     lastWNFTId[_inData.outType].tokenId, 
        //     msg.sender, 
        //     address(this), 
        //     0x02
        // );
        

        emit WrappedV1(
            _inData.inAsset.asset.contractAddress,        // inAssetAddress
            _wrappIn,                                     // outAssetAddress
            _inData.inAsset.tokenId,                      // inAssetTokenId 
            wnftId,                                       // outTokenId 
            _wrappFor,                                    // wnftFirstOwner
            msg.value,                                    // nativeCollateralAmount
            _inData.rules                                 // rules
        );

        return ETypes.AssetItem(
            ETypes.Asset(_inData.outType, _wrappIn),
            wnftId,
            _inData.outBalance
        );
    }

    function addCollateral(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateral
    ) public payable virtual  {
        if (_collateral.length > 0 || msg.value > 0) {
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
    }

    

    function unWrap(address _wNFTAddress, uint256 _wNFTTokenId) external virtual {

        unWrap(_getNFTType(_wNFTAddress, _wNFTTokenId), _wNFTAddress, _wNFTTokenId, false);
    }

    function unWrap(
        ETypes.AssetType _wNFTType, 
        address _wNFTAddress, 
        uint256 _wNFTTokenId
    ) external virtual  {
        unWrap(_wNFTType, _wNFTAddress, _wNFTTokenId, false);
    }

    function unWrap(
        ETypes.AssetType _wNFTType, 
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        bool _isEmergency
    ) public virtual nonReentrant{
        // 1. Check core protocol logic:
        // - who and what possible to unwrap
        (address burnFor, uint256 burnBalance) = _checkCoreUnwrap(_wNFTType, _wNFTAddress, _wNFTTokenId);

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
        
        (uint256 nativeCollateralAmount, ) = getCollateralBalanceAndIndex(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetType.NATIVE,
            address(0),
            0
        );
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
        
        ETypes.WNFT memory w = getWrappedToken(_wNFTAddress, _wNFTTokenId);
        emit UnWrappedV1(
            _wNFTAddress,
            w.inAsset.asset.contractAddress,
            //wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset.asset.contractAddress,
            _wNFTTokenId, 
            w.inAsset.tokenId,
            //wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset.tokenId,
            w.unWrapDestination, 
            //wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestination, 
            nativeCollateralAmount,  // TODO Check  GAS
            w.rules
            //wrappedTokens[_wNFTAddress][_wNFTTokenId].rules 
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
        returns (bool charged) 
    {
        //TODO  only wNFT contract can  execute  this(=charge fee)
        // require(msg.sender == _wNFTAddress || msg.sender == address(this), 
        //     "Only for wNFT or wrapper"
        // );
        // require(_chargeFees(_wNFTAddress, _wNFTTokenId, _from, _to, _feeType),
        //     "Fee charge fail"
        // );
        charged = true;
    }
    /////////////////////////////////////////////////////////////////////
    //                    Admin functions                              //
    /////////////////////////////////////////////////////////////////////
    
    /////////////////////////////////////////////////////////////////////


    function getWrappedToken(address _wNFTAddress, uint256 _wNFTTokenId) 
        public 
        view 
        returns (ETypes.WNFT memory) 
    {
        return wrappedTokens[_wNFTAddress][_wNFTTokenId];
    }

    function getOriginalURI(address _wNFTAddress, uint256 _wNFTTokenId) 
        public 
        view 
        returns(string memory uri_) 
    {
        ETypes.AssetItem memory _wnftInAsset = getWrappedToken(
                _wNFTAddress, _wNFTTokenId
        ).inAsset;

        if (_wnftInAsset.asset.assetType == ETypes.AssetType.ERC721) {
            uri_ = IERC721Metadata(_wnftInAsset.asset.contractAddress).tokenURI(_wnftInAsset.tokenId);
        
        } else if (_wnftInAsset.asset.assetType == ETypes.AssetType.ERC1155) {
            uri_ = IERC1155MetadataURI(_wnftInAsset.asset.contractAddress).uri(_wnftInAsset.tokenId);
        
        } else {
            uri_ = '';
        } 
    }

    function getCollateralBalanceAndIndex(
        address _wNFTAddress, 
        uint256 _wNFTTokenId,
        ETypes.AssetType _collateralType, 
        address _erc,
        uint256 _tokenId
    ) public view returns (uint256, uint256) 
    {
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

    function getNFTType(address _nftAddress, uint256 _nftTokenId) 
        external 
        view 
        returns (ETypes.AssetType nftType) 
    {
        return _getNFTType(_nftAddress, _nftTokenId);
    }
    
    /////////////////////////////////////////////////////////////////////
    //                    Internals                                    //
    /////////////////////////////////////////////////////////////////////
    function _saveWNFTinfo(
        address wNFTAddress, 
        uint256 tokenId, 
        ETypes.INData calldata _inData
    ) internal virtual 
    {
        wrappedTokens[wNFTAddress][tokenId].inAsset = _inData.inAsset;
        // We will use _inData.unWrapDestination  ONLY for RENT implementation
        // wrappedTokens[wNFTAddress][tokenId].unWrapDestination = _inData.unWrapDestination;
        wrappedTokens[wNFTAddress][tokenId].unWrapDestination = address(0);
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
                
                // // Check WhiteList Logic
                // if  (protocolWhiteList != address(0)) {
                //     require(
                //         IAdvancedWhiteList(protocolWhiteList).enabledForCollateral(
                //         _collateral[i].asset.contractAddress),
                //         "WL:Some assets are not enabled for collateral"
                //     );
                // } 
                require(
                    _mustTransfered(_collateral[i]) == _transferSafe(
                        _collateral[i], 
                        msg.sender, 
                        address(this)
                    ),
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
        /////////////////////////////////////////
        //  ERC20 & NATIVE Collateral         ///
        /////////////////////////////////////////
        if (collateralItem.asset.assetType == ETypes.AssetType.ERC20  ||
            collateralItem.asset.assetType == ETypes.AssetType.NATIVE) 
        {
            require(collateralItem.tokenId == 0, "TokenId must be zero");
        }

        /////////////////////////////////////////
        //  ERC1155 Collateral                ///
        // /////////////////////////////////////////
        // if (collateralItem.asset.assetType == ETypes.AssetType.ERC1155) {
        //  No need special checks
        // }    

        /////////////////////////////////////////
        //  ERC721 Collateral                 ///
        /////////////////////////////////////////
        if (collateralItem.asset.assetType == ETypes.AssetType.ERC721 ) {
            require(collateralItem.amount == 0, "Amount must be zero");
        }
        /////////////////////////////////////////
        if (wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length == 0 
            || collateralItem.asset.assetType == ETypes.AssetType.ERC721 
        )
        {
            // First record in collateral or 721
            _newCollateralItem(_wNFTAddress,_wNFTTokenId,collateralItem);
        }  else {
             // length > 0 
            (, uint256 _index) = getCollateralBalanceAndIndex(
                _wNFTAddress, 
                _wNFTTokenId,
                collateralItem.asset.assetType, 
                collateralItem.asset.contractAddress,
                collateralItem.tokenId
            );

            if (_index > 0 ||
                   (_index == 0 
                    && wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[0].asset.contractAddress 
                        == collateralItem.asset.contractAddress 
                    ) 
                ) 
            {
                // We dont need addition if  for erc721 because for erc721 _amnt always be zero
                wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[_index].amount 
                += collateralItem.amount;

            } else {
                // _index == 0 &&  and no this  token record yet
                _newCollateralItem(_wNFTAddress,_wNFTTokenId,collateralItem);
            }
        }
    }

    function _newCollateralItem(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem memory collateralItem
    ) internal virtual 

    {
        require(
            wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length < MAX_COLLATERAL_SLOTS, 
            "Too much tokens in collateral"
        );

        for (uint256 i = 0; i < wrappedTokens[_wNFTAddress][_wNFTTokenId].locks.length; i ++) 
        {
            // Personal Collateral count Lock check
            if (wrappedTokens[_wNFTAddress][_wNFTTokenId].locks[i].lockType == 0x02) {
                require(
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].locks[i].param 
                      >= (wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length + 1),
                    "Too much collateral slots for this wNFT"
                );
            }
        }
        wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.push(collateralItem);
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
        returns (bool _charged) 
    {
        // There is NO fee in this implementation
         _charged = true;
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
    function _beforeUnWrapHook(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        bool _emergency
    ) internal virtual returns (bool)
    {
        uint256 transfered;
        address receiver = msg.sender;
        if (wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestination != address(0)) {
            receiver = wrappedTokens[_wNFTAddress][_wNFTTokenId].unWrapDestination;
        }

        for (uint256 i = 0; i < wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length; i ++) {
            if (wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i].asset.assetType 
                != ETypes.AssetType.EMPTY
            ) {
                if (_emergency) {
                    // In case of something is wrong with any collateral (attack)
                    // user can use  this mode  for skip  malicious asset
                    transfered = _transferEmergency(
                        wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i],
                        address(this),
                        receiver
                    );
                } else {
                    transfered = _transferSafe(
                        wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral[i],
                        address(this),
                        receiver
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

            // For safe exit in case of low gaslimit
            // this strange part of code can prevent only case 
            // when when some collateral tokens spent unexpected gas limit
            if (
                gasleft() <= 1_000 &&
                    i < wrappedTokens[_wNFTAddress][_wNFTTokenId].collateral.length - 1
                ) 
            {
                emit PartialUnWrapp(_wNFTAddress, _wNFTTokenId, i);
                //allReturned = false;
                return false;
            }
        }

        // 5. Return Original
        if (wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset.asset.assetType != ETypes.AssetType.NATIVE && 
            wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset.asset.assetType != ETypes.AssetType.EMPTY
        ) 
        {

            if (!_emergency){
                _transferSafe(
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset,
                    address(this),
                    receiver
                );
            } else {
                _transferEmergency (
                    wrappedTokens[_wNFTAddress][_wNFTTokenId].inAsset,
                    address(this),
                    receiver
                );
            }
        }
        return true;
    }
    ////////////////////////////////////////////////////////////////////////////////////////////

    function _getNFTType(address _wNFTAddress, uint256 _wNFTTokenId) 
        internal 
        view 
        returns (ETypes.AssetType _wNFTType)
    {
        if (IERC165(_wNFTAddress).supportsInterface(type(IERC721).interfaceId)) {
            _wNFTType = ETypes.AssetType.ERC721;
        } else if (IERC165(_wNFTAddress).supportsInterface(type(IERC1155).interfaceId)) {
            _wNFTType = ETypes.AssetType.ERC1155;
        } else {
            revert UnSupportedAsset(
                ETypes.AssetItem(
                    ETypes.Asset(_wNFTType, _wNFTAddress),
                    _wNFTTokenId,
                    0
                )
            );
        }
    }

    function _mustTransfered(ETypes.AssetItem calldata _assetForTransfer) 
        internal 
        pure 
        returns (uint256 mustTransfered) 
    {
        // Available for wrap assets must be good transferable (stakable).
        // So for erc721  mustTransfered always be 1
        if (_assetForTransfer.asset.assetType == ETypes.AssetType.ERC721) {
            mustTransfered = 1;
        } else {
            mustTransfered = _assetForTransfer.amount;
        }
    }
     
    function _checkRule(bytes2 _rule, bytes2 _wNFTrules) internal pure returns (bool) {
        return _rule == (_rule & _wNFTrules);
    }

    // 0x00 - TimeLock
    // 0x01 - TransferFeeLock
    // 0x02 - Personal Collateral count Lock check
    function _checkLocks(address _wNFTAddress, uint256 _wNFTTokenId) internal view virtual returns (bool) 
    {
        // There is NO locks checks in this implementation
        return true;
    }


    function _checkWrap(ETypes.INData calldata _inData, address _wrappFor, address _wrappIn) 
        internal 
        view 
        returns (bool enabled)
    {
        
        //enabled = _wrappFor != address(this);

        // Check that _wrappIn belongs to user
        ETypes.Asset[] memory userAssets = IUserCollectionRegistry(usersCollectionRegistry)
            .getUsersCollections(msg.sender);
        bool isUsersAsset;
        for (uint256 i = 0; i < userAssets.length; ++ i ){
            if (userAssets[i].contractAddress == _wrappIn && 
                userAssets[i].assetType == _inData.outType
                ) 
            {
                isUsersAsset = true;
                break;
            }
        }
        
        // Lets check that inAsset 
        enabled =     
            _wrappFor != address(this) && 
            isUsersAsset;
    }
    
    function _checkAddCollateral(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateral
    ) 
        internal 
        view
        virtual 
        returns (bool enabled)
    {
        require(IUsersSBT(_wNFTAddress).owner() == msg.sender, 
            'Only wNFT contract owner able to add collateral'
        );
        // Check  that wNFT exist
        ETypes.AssetType wnftType = _getNFTType(_wNFTAddress, _wNFTTokenId);
        if (wnftType == ETypes.AssetType.ERC721) {
            require(IERC721Mintable(_wNFTAddress).exists(_wNFTTokenId), "wNFT not exists");
        } else if(wnftType == ETypes.AssetType.ERC1155) {
            require(IERC1155Mintable(_wNFTAddress).exists(_wNFTTokenId), "wNFT not exists");
        } else {
            revert UnSupportedAsset(
                ETypes.AssetItem(ETypes.Asset(wnftType,_wNFTAddress),_wNFTTokenId, 0)
            );
        }

        // Lets check wNFT rules - TODO   Ask  Alex
        // 0x0008 - this rule disable add collateral
        enabled = !_checkRule(0x0008, getWrappedToken(_wNFTAddress, _wNFTTokenId).rules); 
    }

    function _checkCoreUnwrap(
        ETypes.AssetType _wNFTType, 
        address _wNFTAddress, 
        uint256 _wNFTTokenId
    ) 
        internal 
        view 
        virtual 
        returns (address burnFor, uint256 burnBalance) 
    {
        
        // Lets wNFT rules 
        // 0x0001 - this rule disable unwrap wrappednFT 
        require(!_checkRule(0x0001, getWrappedToken(_wNFTAddress, _wNFTTokenId).rules),
            "UnWrapp forbidden by author"
        );

        if (_wNFTType == ETypes.AssetType.ERC721) {
            // Only token owner can UnWrap
            burnFor = IERC721Mintable(_wNFTAddress).ownerOf(_wNFTTokenId);
            require(burnFor == msg.sender, 
                'Only owner can unwrap it'
            ); 

        } else if (_wNFTType == ETypes.AssetType.ERC1155) {
            burnBalance = IERC1155Mintable(_wNFTAddress).totalSupply(_wNFTTokenId);
            burnFor = msg.sender;
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