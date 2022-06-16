// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. UnitBoxPlatform case 

import "../../../interfaces/IWrapperRemovable.sol";

pragma solidity 0.8.11;

contract UnitBoxPlatform {

	IWrapperRemovable public wrapper;

	constructor (address _wrapper) {
        wrapper = IWrapperRemovable(_wrapper);
	}

}