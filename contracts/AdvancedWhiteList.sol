// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. WhitList Storage
pragma solidity 0.8.10;

import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IAdvancedWhiteList.sol";
import "./LibEnvelopTypes.sol";
//import "../interfaces/IERC721Mintable.sol";

contract AdvancedWhiteList is Ownable, IAdvancedWhiteList {

    
    mapping(address => ETypes.WhiteListItem) internal whiteList;
    mapping(address => bool) internal blackList;
    mapping(address => ETypes.Rules) internal rulesChecker;
    address[] public whiteListedArray;
    address[] public blackListedArray;



    /////////////////////////////////////////////////////////////////////
    //                    Admin functions                              //
    /////////////////////////////////////////////////////////////////////
    function setWLItem(address _asset, ETypes.WhiteListItem calldata _assetItem) external onlyOwner {
        require(_assetItem.transferFeeModel != address(0), 'Cant be zero, use default instead');
        whiteList[_asset] = _assetItem;
        bool alreadyExist;
        for (uint256 i = 0; i < whiteListedArray.length; i ++) {
            if (whiteListedArray[i] == _asset){
                alreadyExist = true;
                break;
            }
            if (!alreadyExist) {
               whiteListedArray.push(_asset); 
            }
        }
        emit WhiteListItemChanged(
            _asset, 
            _assetItem.enabledForFee, 
            _assetItem.enabledForCollateral, 
            _assetItem.enabledRemoveFromCollateral,
            _assetItem.transferFeeModel
        );

    }

    function removeWLItem(address _asset) external onlyOwner {
        uint256 deletedIndex;
        for (uint256 i = 0; i < whiteListedArray.length; i ++) {
            if (whiteListedArray[i] == _asset){
                deletedIndex = i;
                break;
            }
        }
        // Check that deleting item is not last array member
        // because in solidity we can remove only last item from array
        if (deletedIndex != whiteListedArray.length - 1) {
            // just replace deleted item with last item
            whiteListedArray[deletedIndex] = whiteListedArray[whiteListedArray.length - 1];
        } 
        whiteListedArray.pop();
        delete whiteList[_asset];
        emit WhiteListItemChanged(
            _asset, 
            false, false, false, address(0)
        );
    }

    function setBLItem(address _asset, bool _isBlackListed) external onlyOwner {
        blackList[_asset] = _isBlackListed;
        if (_isBlackListed) {
            for (uint256 i = 0; i < blackListedArray.length; i ++){
                if (blackListedArray[i] == _asset) {
                    return;
                }
            }
            // There is no this address in array so  just add it
            blackListedArray.push(_asset);
        } else {
            uint256 deletedIndex;
            for (uint256 i = 0; i < blackListedArray.length; i ++){
                if (blackListedArray[i] == _asset) {
                    deletedIndex = i;
                    break;
                }
            }
            // Check that deleting item is not last array member
            // because in solidity we can remove only last item from array
            if (deletedIndex != blackListedArray.length - 1) {
                // just replace deleted item with last item
                blackListedArray[deletedIndex] = blackListedArray[blackListedArray.length - 1];
            } 
            blackListedArray.pop();
            delete blackList[_asset];

        }
        emit BlackListItemChanged(_asset, _isBlackListed);
    }

    function setRules(address _asset, bytes2 _only, bytes2 _disabled) public onlyOwner {
        rulesChecker[_asset].onlythis = _only;
        rulesChecker[_asset].disabled = _disabled;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////
    
    function getWLItem(address _asset) external view returns (ETypes.WhiteListItem memory) {
        return whiteList[_asset];
    }

    function getWLItemCount() external view returns (uint256) {
        return whiteListedArray.length;
    }

    function getWLAddressByIndex(uint256 _index) external view returns (address) {
        return whiteListedArray[_index];
    }

    function getWLAddresses() external view returns (address[] memory) {
        return whiteListedArray;
    }

     
    function getBLItem(address _asset) external view returns (bool) {
        return blackList[_asset];
    }

    function getBLItemCount() external view returns (uint256) {
        return blackListedArray.length;
    }

    function getBLAddressByIndex(uint256 _index) external view returns (address) {
        return blackListedArray[_index];
    }

    function getBLAddresses() external view returns (address[] memory) {
        return blackListedArray;
    }

    function enabledForCollateral(address _asset) external view returns (bool) {
        return whiteList[_asset].enabledForCollateral;
    }

    function enabledForFee(address _asset) external view returns (bool) {
        return whiteList[_asset].enabledForFee;
    }

    function enabledRemoveFromCollateral(address _asset) external view returns (bool) {
        return whiteList[_asset].enabledRemoveFromCollateral;
    }
    
    function rulesEnabled(address _asset, bytes2 _rules) external view returns (bool) {

        if (rulesChecker[_asset].onlythis != 0x0000) {
            return rulesChecker[_asset].onlythis == _rules;
        }

        if (rulesChecker[_asset].disabled != 0x0000) {
            return (rulesChecker[_asset].disabled & _rules) == 0x0000;
        }
        return true;
    }

    function validateRules(address _asset, bytes2 _rules) external view returns (bytes2) {
        if (rulesChecker[_asset].onlythis != 0x0000) {
            return rulesChecker[_asset].onlythis;
        }

        if (rulesChecker[_asset].disabled != 0x0000) {
            return (~rulesChecker[_asset].disabled) & _rules;
        }
        return _rules;
    }

}