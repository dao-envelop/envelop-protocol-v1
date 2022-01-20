// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - Checker
pragma solidity 0.8.11;

import "../interfaces/IWrapper.sol";
import "./LibEnvelopTypes.sol";
contract WrapperChecker {

    IWrapper public wrapper;

    constructor(address _wrapper) {
        require(_wrapper != address(0), "No zero");
        wrapper = IWrapper(_wrapper);
    }

    function getNativeCollateralBalance(
        address _wNFTAddress, 
        uint256 _wNFTTokenId 
    ) public view returns (uint256) 
    {
        (uint256 res, ) = wrapper.getCollateralBalanceAndIndex(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetType.NATIVE, 
            address(0), // tokenAddress 
            0           // tokenId
        );
        return res;
    }

    function getERC20CollateralBalance(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        address _erc20
    ) public view returns (uint256, uint256) 
    {
        return wrapper.getCollateralBalanceAndIndex(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetType.ERC20, 
            _erc20,
            0
        );
    }

    function getERC1155CollateralBalance(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        address _erc1155,
        uint256 _tokenId
    ) public view returns (uint256, uint256) 
    {
        return wrapper.getCollateralBalanceAndIndex(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetType.ERC1155, 
            _erc1155,
            _tokenId
        ); 
    }

    function checkWrap(
        ETypes.INData calldata _inData, 
        ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor
    ) 
        public view returns (bool, string memory)
    {
        bool result = true;
        string memory messages = "";
        if (_inData.unWrapDestinition == address(0)) {
            result = false;
            messages="unWrapDestinition cant be zero, ";
        }

        if (_wrappFor == address(0)) {
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    "WrapperFor cant be zero, "
                )
            );
        }

        if (_inData.fees.length == 0&&_inData.royalties.length != 0){
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    "Royalty source is transferFee, "
                )
            ); 
        }

        if (_inData.outType == ETypes.AssetType.ERC1155&&_inData.outBalance == 0){
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    "WNFT type is ERC1155 - wnft should have balance, "
                )
            ); 
        }
        
        if (_inData.inAsset.asset.assetType == ETypes.AssetType.ERC1155&&_inData.inAsset.amount == 0){
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    "Original NFT type is ERC1155 - original nft should have balance, "
                )
            ); 
        }

        if (_inData.inAsset.asset.contractAddress == address(0)){
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    "NFT contract address cant be zero, "
                )
            ); 
        }

        if (_inData.locks.length != 0){
            uint256 j = 0;
            for (uint256 i = 0; i < _inData.locks.length; i ++) {
                if (_inData.locks[i].lockType == 0x00){
                    j++;
                }
            }
            if (j > 1) {
                result = false; 
                messages= string(
                    abi.encodePacked(
                        messages,
                        "Several time loks, "
                    )
                );
            } 
        }

        if (_inData.rules != 0x0002&& _inData.rules != 0x0008&& _inData.rules != 0x0001&& _inData.rules != 0x0004){
            result = false; 
                messages= string(
                    abi.encodePacked(
                        messages,
                        "Wrong rule code, "
                    )
                );
        }
        

        return (result, messages);
    }

    function checkAddCollateral(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateral
    ) public view returns (bool) 
    {
        return true;
    }

    function checkUnWrap(
        ETypes.AssetType _wNFTType, 
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        bool _isEmergency
    ) public view returns (bool) 
    {
        return true;
    }
}
