// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - Checker
pragma solidity 0.8.11;

import "../interfaces/IWrapper.sol";
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
        bool result;
        string memory messages;
        if (_inData.unWrapDestinition == address(0)) {
            result = false;
            messages="unWrapDestinition cant be zero";
        }
        if (_wrappFor == address(0)) {
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    ", ",
                    "WrapperFor cant be zero"
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
