// SPDX-License-Identifier: MIT

pragma solidity 0.8.10;

//import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";
import "../contracts/LibEnvelopTypes.sol";

interface IAdvancedWhiteList  {


    event WhiteListItemChanged(
        address indexed asset,
        bool enabledForFee,
        bool enabledForCollateral,
        bool enabledRemoveFromCollateral,
        address transferFeeModel
    );
    event BlackListItemChanged(
        address indexed asset,
        bool isBlackListed
    );
    function getWLItem(address _asset) external view returns (ETypes.WhiteListItem memory);
}