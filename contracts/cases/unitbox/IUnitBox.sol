// SPDX-License-Identifier: MIT


pragma solidity 0.8.21;

import "../../LibEnvelopTypes.sol";

interface IUnitBox  {

    enum DexType {None, UniSwapV2, UniSwapV3}

    struct DexParams{
        address router;
        address factory;
        address nativeAsset;
        address assetForTreasury;
    }

    struct GameTokenDex {
        DexType dexType;
        address dexAddress;
        bool enabled;
    }


    function wrapForRent(
        ETypes.INData calldata _inData,
        uint256 _nonce,
        bytes memory _signature
    ) external  returns (address wnftContract, uint256 tokenId);

    function wrapBatch(
        ETypes.INData[]  calldata _inDataS,
        uint256[] calldata _nonceS,
        bytes[] calldata _signatureS

    ) external; 
    
    function claimAndSwap(
        address _wNFTAddress, 
        uint256 _wNFTTokenId,
        address _collateralAddress
    ) external;
    
    function swapMe(address token) external;

    function withdrawEther() external;

    function withdrawTokens(address _token) external;
   
}