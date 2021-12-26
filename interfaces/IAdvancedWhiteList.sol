// SPDX-License-Identifier: MIT

pragma solidity 0.8.10;

//import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";
import "../contracts/LibEnvelopTypes.sol";

interface IAdvancedWhiteList  {


    event WhiteListItemChanged(address indexed asset, ETypes.AdvWhiteListItem item);
    function getItem(address _asset) external view returns (ETypes.AdvWhiteListItem memory);
    function setItem(address _asset, ETypes.AdvWhiteListItem calldata _issetItem) external; 
    function removeItem(address _asset) external;
}