// SPDX-License-Identifier: MIT

pragma solidity 0.8.13;


interface IUnitBox  {

    enum DexType {None, UniSwapV2, UniSwapV3}

    struct Share {
        address beneficiary;
        uint256 percent;
    }

    struct GameTokenDex {
        DexType dex;
        address dexAddress;
        bool enabled;
    } 

    function wrapForRent() external virtual returns (address wnftContract, uint256 tokenId);
    function claimAndSwap() external virtual;
    function swapMe(address token) external virtual;

    function withdrawEther() external virtual;

    function withdrawTokens(address _token) external virtual;
   
}