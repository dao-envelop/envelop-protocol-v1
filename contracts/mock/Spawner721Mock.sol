// SPDX-License-Identifier: MIT
// ENVELOP protocol for NFT
pragma solidity 0.8.19;

import "../Spawner721.sol";

//v0.0.1
contract Spawner721Mock is Spawner721 {
	using ECDSA for bytes32;

	constructor(
        string memory name_,
        string memory symbol_,
        string memory _baseurl
    ) 
    Spawner721(name_, symbol_, _baseurl)
    {}

	function mint(
        uint256 _tokenId, 
        //bytes32 _msgForSign, 
        bytes calldata _signature
    ) external override {

        bytes32 msgMustWasSigned = keccak256(abi.encode(
                msg.sender,
                //block.chainid,
                1337,  // for test with Ganache
                address(this),
                _tokenId
        )).toEthSignedMessageHash();

        // Check signature  author
        require(oracleSigners[msgMustWasSigned.recover(_signature)], "Unexpected signer");

        _mint(msg.sender, _tokenId);
    }
}