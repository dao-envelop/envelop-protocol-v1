// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. 

import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/ITrustedWrapper.sol";



pragma solidity 0.8.16;

contract BatchWorker is Ownable {

	ITrustedWrapper public trustedWrapper;

	function wrapBatch(
		ETypes.INData[] calldata _inDataS, 
        ETypes.AssetItem[] calldata _collateral,
		//address _original721, 
        address[] memory _receivers
        // uint256[] memory _tokenIds, 
        // ERC20Collateral[] memory _forDistrib,
        // uint256 _unwrapAfter
        // bool _needMint
    ) public payable {
    	// make wNFTs
    	for (uint256 i = 0; i < _inDataS.length; i++) {
    		trustedWrapper.wrapUnsafe(
    			_inDataS[i],
    			_collateral,
    			_receivers[i]
    		);

    	}

    	// TODO Transfer originals and collateral

    }

    ////////////////////////////////////////
    //     Admin functions               ///
    ////////////////////////////////////////
	function setTrustedAddress(address _wrapper) public onlyOwner {
        trustedWrapper = ITrustedWrapper(_wrapper);
		require(trustedWrapper.trustedOperator() == address(this), "Only for exact wrapper");
    }
}