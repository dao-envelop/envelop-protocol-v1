// SPDX-License-Identifier: MIT

pragma solidity 0.8.21;


interface IUsersSBT  {

    function mintWithRules(
        address _to,  
        bytes2 _rules
    ) external returns(uint256 tokenId); 
    
    function mintWithRules(
        address _to,  
        uint256 _balance, 
        bytes2 _rules
    ) external returns(uint256 tokenId);
   
}