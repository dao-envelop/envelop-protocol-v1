// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. WhitList Storage
pragma solidity 0.8.10;

import "@openzeppelin/contracts/access/Ownable.sol";
//import "../interfaces/IWrapper.sol";
import "./LibEnvelopTypes.sol";
//import "../interfaces/IERC721Mintable.sol";

contract AdvancedWhiteList is Ownable {

    address[] public listAssets;
    mapping(address => ETypes.AdvWhiteListItem) internal whiteList;

    event WhiteListItemChanged(address indexed asset, ETypes.AdvWhiteListItem item);

    function getItem(address _asset) external view returns (ETypes.AdvWhiteListItem memory) {
        return whiteList[_asset];
    }

    /////////////////////////////////////////////////////////////////////
    //                    Admin functions                              //
    /////////////////////////////////////////////////////////////////////
    function setItem(address _asset, ETypes.AdvWhiteListItem calldata _issetItem) external onlyOwner {
        whiteList[_asset] = _issetItem;
        bool alreadyExist;
        for (uint256 i = 0; i < listAssets.length; i ++) {
            if (listAssets[i] == _asset){
                alreadyExist = true;
                break;
            }
            if (alreadyExist) {
               listAssets.push(_asset); 
            }
        }
        emit WhiteListItemChanged(_asset, _issetItem);

    }

    function removeItem(address _asset) external onlyOwner {
        uint256 deletedIndex;
        for (uint256 i = 0; i < listAssets.length; i ++) {
            if (listAssets[i] == _asset){
                deletedIndex = i;
                break;
            }
            // Check that deleting item is not last array member
            // because in solidity we can remove only last item from array
            if (deletedIndex != listAssets.length - 1) {
                // just replace deleted item with last item
                listAssets[i] = listAssets[listAssets.length - 1];
            } 
            listAssets.pop();
        }
        delete whiteList[_asset];
        emit WhiteListItemChanged(
            _asset, 
            ETypes.AdvWhiteListItem(false, false, false, false, 0x0000, address(0))
        );
        
    }
}