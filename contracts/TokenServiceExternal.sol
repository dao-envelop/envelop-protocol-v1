// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - main protocol contract
pragma solidity 0.8.11;

import "./LibEnvelopTypes.sol";
import "./TokenService.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../interfaces/IERC20Extended.sol";
import "../interfaces/IERC721Mintable.sol";
import "../interfaces/IERC1155Mintable.sol";
//import "../interfaces/ITokenService.sol";

contract TokenServiceExternal is  TokenService {
	
}