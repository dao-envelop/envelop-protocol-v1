// SPDX-License-Identifier: MIT

pragma solidity 0.8.10;

//import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";

interface IWrapper  {

    event WrappedV1(
        address indexed inAssetAddress,
        address indexed outAssetAddress, 
        uint256 indexed inAssetTokenId, 
        uint256 outTokenId,
        address wnftFirstOwner,
        uint256 nativeCollateralAmount,
        bytes2  rules
    );

    event UnWrappedV1(
        address indexed wrappedAddress,
        address indexed originalAddress,
        uint256 indexed wrappedId, 
        uint256 originalTokenId, 
        address beneficiary, 
        uint256 nativeCollateralAmount,
        bytes2  rules 
    );

    event CollateralAdded(
        address indexed wrappedAddress,
        uint256 indexed wrappedId,
        uint8   assetType,
        address collateralAddress,
        uint256 collateralTokenId,
        uint256 collateralBalance
    );

    event PartialUnWrapp(
        address indexed wrappedAddress,
        uint256 indexed wrappedId,
        uint256 lastCollateralIndex
    );
    event SuspiciousFail(
        address indexed wrappedAddress,
        uint256 indexed wrappedId, 
        address indexed failedContractAddress
    );
    // event NewFee(uint256 feeAmount, uint256 startDate);
    // event NiftsyProtocolTransfer(
    //     uint256 indexed wrappedTokenId, 
    //     address indexed royaltyBeneficiary,
    //     uint256 transferFee, 
    //     uint256 royalty,
    //     address feeToken 
    // );
    
    /**
     * @dev Function returns array with info about ERC20 
     * colleteral of wrapped token 
     *
     * @param _wrappedId  new protocol NFT id from this contarct
     */
    // function getERC20Collateral(uint256 _wrappedId) 
    //      external 
    //      view 
    //      returns (ERC20Collateral[] memory);

    /**
     * @dev Function returns collateral balance of this NFT in _erc20 
     * colleteral of wrapped token 
     *
     * @param _wrappedId  new protocol NFT id from this contarct
     * @param _erc20 - collateral token address
     */
    // function getERC20CollateralBalance(uint256 _wrappedId, address _erc20) 
    //     external 
    //     view
    //     returns (uint256); 

    /**
     * @dev Function returns true is `_contract` ERC20 is 
     * enabled for add in colleteral of wrapped token 
     *
     * @param _contract  collateral contarct
     */
    //function enabledForCollateral(address _contract) external view returns (bool);
}