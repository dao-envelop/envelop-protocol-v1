// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT
pragma solidity 0.8.16;
import "../MinterRole.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../../interfaces/IWrapper.sol";
import "../LibEnvelopTypes.sol";

contract HachERC20 is ERC20 {

    IWrapper public wrapper;
    address public wnftStorage;
    constructor(string memory name_,
        string memory symbol_) ERC20(name_, symbol_)  {
        _mint(msg.sender, 1000000000000000000000000000);

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

    function setTrustedWrapper(address _wrapper) public  {
        wrapper = IWrapper(_wrapper);
    }

    function setWNFTStorage(address _storage) public  {
        wnftStorage = _storage;
    }

/*check unwrap my wnft
check unwrap not owned wnft*/

}
