// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Batch Wrapper - for users SBT collections
pragma solidity 0.8.21;

import "./WrapperUsersV1.sol";

contract WrapperUsersV1Batch is WrapperUsersV1
{
    using SafeERC20 for IERC20Extended;

    
    constructor(address _usersWNFTRegistry) 
        WrapperUsersV1(_usersWNFTRegistry) 
    {}

    function wrapBatch(
        ETypes.INData[] calldata _inDataS, 
        ETypes.AssetItem[] memory _collateralERC20,
        address[] memory _receivers,
        address _wrappIn
    ) external payable nonReentrant {
        require(
            _inDataS.length == _receivers.length, 
            "Array params must have equal length"
        );
        // make wNFTs batch cycle. No callateral assete transfers in this cycle
        uint256 valuePerWNFT = msg.value / _inDataS.length;
        for (uint256 i = 0; i < _inDataS.length; i++) {

            // 0. Check assetIn asset
            require(_checkWrap(_inDataS[i], _receivers[i], _wrappIn),
                "Wrap check fail"
            );
            ////////////////////////////////////////
            //  Here start wrapUnsafe functionality
            ////////////////////////////////////////
             // 2. Mint wNFT
            uint256 wnftId = _mintWNFTWithRules(
                _inDataS[i].outType,    // what will be minted instead of wrapping asset
                _wrappIn,               // wNFT contract address
                _receivers[i],          // wNFT receiver (1st owner) 
                _inDataS[i].outBalance,  // wNFT tokenId
                _inDataS[i].rules
            );

            // 3. Safe wNFT info
            _saveWNFTinfo(
                _wrappIn, 
                wnftId,
                _inDataS[i]
            );

            
            // Native collateral record for new wNFT    
            if (valuePerWNFT > 0) {
                _processNativeCollateralRecord(_wrappIn, wnftId, valuePerWNFT);
                
            }
            // Update collateral records for new wNFT
            for (uint256 j = 0; j <_collateralERC20.length; ++ j) {
                if (_collateralERC20[j].asset.assetType == ETypes.AssetType.ERC20) {
                    _updateCollateralInfo(
                       _wrappIn, 
                        wnftId,
                        _collateralERC20[j]
                    );

                    // Emit event for each collateral record
                    emit CollateralAdded(
                        _wrappIn, 
                        wnftId, 
                        uint8(_collateralERC20[j].asset.assetType),
                        _collateralERC20[j].asset.contractAddress,
                        _collateralERC20[j].tokenId,
                        _collateralERC20[j].amount
                    );
                }
            }
            
            // Emit event for each new wNFT
            emit WrappedV1(
                _inDataS[i].inAsset.asset.contractAddress,   // inAssetAddress
                _wrappIn,                                   // outAssetAddress
                _inDataS[i].inAsset.tokenId,                // inAssetTokenId 
                wnftId,                                     // outTokenId 
                _receivers[i],                              // wnftFirstOwner
                msg.value  / _receivers.length,             // nativeCollateralAmount 
                _inDataS[i].rules                            // rules
            );

            ////////////////////////////////////////
            
            // Transfer original NFTs  to wrapper
            if (_inDataS[i].inAsset.asset.assetType == ETypes.AssetType.ERC721 ||
                _inDataS[i].inAsset.asset.assetType == ETypes.AssetType.ERC1155 ) 
            {

                require(
                    _mustTransfered(_inDataS[i].inAsset) == _transferSafe(
                        _inDataS[i].inAsset, 
                        msg.sender, 
                        address(this)
                    ),
                    "Suspicious asset for wrap"
                );
            }


        } // end of batch cycle

        // Change return  - 1 wei return ?
        if (valuePerWNFT * _inDataS.length < msg.value ){
            address payable s = payable(msg.sender);
            s.transfer(msg.value - valuePerWNFT * _inDataS.length);
        }
        
        // Now we need trnafer and check all collateral from user to this conatrct
        _processERC20transfers(
            _collateralERC20, 
            msg.sender, 
            address(this), 
            _receivers.length
        );
    }

    function addCollateralBatch(
        address[] calldata _wNFTAddress, 
        uint256[] calldata _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateralERC20
    ) public payable nonReentrant{
        require(_wNFTAddress.length == _wNFTTokenId.length, "Array params must have equal length");
        require(_collateralERC20.length > 0 || msg.value > 0, "Collateral not found");
        uint256 valuePerWNFT = msg.value / _wNFTAddress.length;
        // cycle for wNFTs that need to be topup with collateral
        for (uint256 i = 0; i < _wNFTAddress.length; i ++){
            // In this implementation only wnft contract owner can add collateral
            require(IUsersSBT(_wNFTAddress[i]).owner() == msg.sender, 
                'Only wNFT contract owner able to add collateral'
            );
            _checkWNFTExist(
                _wNFTAddress[i], 
                _wNFTTokenId[i]
            );

            // Native collateral     
            if (valuePerWNFT > 0) {
                _processNativeCollateralRecord(_wNFTAddress[i], _wNFTTokenId[i], valuePerWNFT);
                
            }
            
            // ERC20 collateral
            for (uint256 j = 0; j < _collateralERC20.length; j ++) {
                if (_collateralERC20[j].asset.assetType == ETypes.AssetType.ERC20) {
                    _updateCollateralInfo(
                        _wNFTAddress[i], 
                        _wNFTTokenId[i],
                        _collateralERC20[j]
                    );
                    emit CollateralAdded(
                        _wNFTAddress[i], 
                        _wNFTTokenId[i], 
                        uint8(_collateralERC20[j].asset.assetType),
                        _collateralERC20[j].asset.contractAddress,
                        _collateralERC20[j].tokenId,
                        _collateralERC20[j].amount
                    );
                }
            } // cycle end - ERC20 collateral 
        }// cycle end - wNFTs

        // Change return  - 1 wei return ?
        if (valuePerWNFT * _wNFTAddress.length < msg.value ){
            address payable s = payable(msg.sender);
            s.transfer(msg.value - valuePerWNFT * _wNFTAddress.length);
        }

        //  Transfer all erc20 tokens to BatchWorker 
        _processERC20transfers(
            _collateralERC20, 
            msg.sender, 
            address(this), 
            _wNFTAddress.length
        );
    }

    function _processNativeCollateralRecord(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        uint256 _amount
    ) internal 
    {
        _updateCollateralInfo(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetItem(
                ETypes.Asset(ETypes.AssetType.NATIVE, address(0)),
                0,
                _amount
            )
        );
        emit CollateralAdded(
            _wNFTAddress, 
            _wNFTTokenId, 
            uint8(ETypes.AssetType.NATIVE),
            address(0),
            0,
            _amount
        );
    }

    function _processERC20transfers(
        ETypes.AssetItem[] memory _collateralERC20,
        address _from,
        address _to,
        uint256 _multiplier
    ) internal 
    {
         //  Transfer all erc20 tokens 
        for (uint256 i = 0; i < _collateralERC20.length; i ++) {
            _collateralERC20[i].amount = _collateralERC20[i].amount * _multiplier;
            if (_collateralERC20[i].asset.assetType == ETypes.AssetType.ERC20) {
                require(
                    _mustTransfered(_collateralERC20[i]) == _transferSafe(
                        _collateralERC20[i], 
                        _from, 
                        _to
                    ),
                    "Suspicious asset for wrap"
                );
            }
        }
    }
    
}