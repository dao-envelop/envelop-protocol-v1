// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT
pragma solidity 0.8.21;
//import "../MinterRole.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../../interfaces/IWrapper.sol";
import "../LibEnvelopTypes.sol";

contract HackERC20 is ERC20 {

    IWrapper public wrapper;
    address public wnftStorage;
    constructor(string memory name_,
        string memory symbol_,
        address  wrapper_, 
        address  wnftStorage_) ERC20(name_, symbol_)  {
        _setTrustedWrapper(wrapper_);
        _setWNFTStorage(wnftStorage_);
        _mint(msg.sender, 1000000000000000000000000000);


    }


    function _setTrustedWrapper(address _wrapper) internal  {
        wrapper = IWrapper(_wrapper);
    }

    function _setWNFTStorage(address _storage) internal  {
        wnftStorage = _storage;
    }


    function _beforeTokenTransfer(address from, address to, uint256 amount) 
        internal 
        override 
    {
        if (from == address(wrapper)){
            wrapper.unWrap(
                ETypes.AssetType.ERC721, 
                wnftStorage, 
                1
            );
        } 
        
    }

    


/*check unwrap my wnft
check unwrap not owned wnft*/

}
