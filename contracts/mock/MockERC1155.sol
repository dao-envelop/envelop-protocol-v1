// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT
pragma solidity 0.8.16;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";

//v0.0.1
contract Token1155Mock is ERC1155 {

    
    constructor(string memory uri_) ERC1155(uri_)  {
    }

    function mint(
        address to, 
        uint256 tokenId,
        uint256 amount
    ) external {
        
        _mint(to, tokenId, amount, '');
    }

    function mintBatch(
        address to, 
        uint256[] calldata ids,
        uint256[] calldata amounts,
        bytes calldata data
    ) external {
        
        _mintBatch(to, ids, amounts, '');
    }

    function burn(
        address from, 
        uint256 tokenId,
        uint256 amount
    ) external {
        
        _burn(from, tokenId, amount);
    }

    function burnBatch(
        address from, 
        uint256[] calldata ids,
        uint256[] calldata amounts
    ) external {
        
        _burnBatch(from, ids, amounts);
    }
}
