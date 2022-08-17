// SPDX-License-Identifier: MIT
// ENVELOP protocol for NFT
pragma solidity 0.8.16;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

//v0.0.1
contract EnvelopUsers721Swarm is ERC721URIStorage {

    string private _baseTokenURI;

    constructor(
        string memory name_,
        string memory symbol_,
        string memory _baseurl
    ) 
        ERC721(name_, symbol_)  
    {
        _baseTokenURI = _baseurl;

    }

    function baseURI() external view  returns (string memory) {
        return _baseURI();
    }

    function _baseURI() internal view  override returns (string memory) {
        return _baseTokenURI;
    }
}