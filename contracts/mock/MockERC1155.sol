// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT
pragma solidity ^0.8.6;

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
}
