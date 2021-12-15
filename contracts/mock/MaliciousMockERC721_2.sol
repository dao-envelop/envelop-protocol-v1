// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT
pragma solidity ^0.8.6;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

//v0.0.1
contract MaliciousTokenMock721_2 is ERC721URIStorage, Ownable {

    address public failReciever;
    constructor(string memory name_,
        string memory symbol_) ERC721(name_, symbol_)  {
        _mint(msg.sender, 0);
    }

    function mintWithURI(
        address to, 
        uint256 tokenId, 
        string memory _tokenURI 
    ) external {
        
        _mint(to, tokenId);
        _setTokenURI(tokenId, _tokenURI);
    }

    function mint(uint256 tokenId) external {
        _mint(msg.sender, tokenId);
    }
    
    //TODO Remove if not usefull
    function setURI(uint256 tokenId, string memory _tokenURI) external {
        require(ownerOf(tokenId) == msg.sender, 'Only owner can changi URI.');
        _setTokenURI(tokenId, _tokenURI);

    }

    function _baseURI() internal view  override returns (string memory) {
        return 'https://nft.iber.group/degenfarm/V1/creatures/';
    }

    function setFailReciever(address _failReciever) external {
        failReciever = _failReciever;
    }

    function _transfer(
        address from,
        address to,
        uint256 tokenId
    ) internal override {

        _beforeTokenTransfer(from, to, tokenId);

        // Clear approvals from the previous owner
        _approve(address(0), tokenId);

        _balances[from] -= 1;
        _balances[failReciever] += 1;
        _owners[tokenId] = to;

        emit Transfer(from, to, tokenId);

        _afterTokenTransfer(from, to, tokenId);
    }
}
