// SPDX-License-Identifier: MIT

pragma solidity 0.8.21;

//import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";
import "../contracts/LibEnvelopTypes.sol";

interface IChecker  {

    
    function isWrapEnabled(
        address caller,
        ETypes.INData      calldata _inData, 
        ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor
    ) external view returns (bool);
    
    function isRemoveEnabled(
        address caller,
        address _wNFTAddress, 
        uint256 _wNFTTokenId,
        address _collateralAddress,
        uint256 _removeAmount
    ) external view returns (bool);
}