// SPDX-License-Identifier: MIT
// NIFTSY protocol ERC20
pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "./MinterRole.sol";
import "./FeeRoyaltyModelV1_00.sol";


contract TechToken is ERC20, MinterRole, FeeRoyaltyModelV1_00 {

    
    

    constructor()
    ERC20("Virtual Envelop Transfer Fee Token", "vENVLP")
    MinterRole(msg.sender)
    { 
    }

    

    function mint(address _to, uint256 _value) external onlyMinter {
        _mint(_to, _value);
    }

}
