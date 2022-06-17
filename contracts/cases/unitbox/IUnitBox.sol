// SPDX-License-Identifier: MIT


pragma solidity 0.8.13;

import "../../LibEnvelopTypes.sol";

interface IUnitBox  {

    enum DexType {None, UniSwapV2, UniSwapV3}

    struct Share {
        address beneficiary;
        uint256 percent;
    }

    struct GameTokenDex {
        DexType dex;
        address dexAddress;
        address[] path;
        bool enabled;
    }


    function wrapForRent(
        ETypes.INData calldata _inData,
        //address _wNFTAddress, 
        //uint256 _nftId,
        //ETypes.Royalty[] calldata _shares,
        uint256 _nonce,
        bytes memory _signature
    ) external  returns (address wnftContract, uint256 tokenId);
    
    function claimAndSwap(
        address _wNFTAddress, 
        uint256 _wNFTTokenId,
        address _collateralAddress
    ) external;
    
    function swapMe(address token) external;

    function withdrawEther() external;

    function withdrawTokens(address _token) external;
   
}