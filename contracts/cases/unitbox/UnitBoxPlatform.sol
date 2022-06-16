// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. UnitBoxPlatform case 

import "../../../interfaces/IWrapperRemovable.sol";
import "./IUnitBox.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./IUniswapV2Router02.sol";

pragma solidity 0.8.13;

contract UnitBoxPlatform is Ownable, IUnitBox{

    IWrapperRemovable public wrapper;


    mapping(address => GameTokenDex) public dex; 

    constructor (address _wrapper) {
        wrapper = IWrapperRemovable(_wrapper);
    }

    function wrapForRent() external returns (address wnftContract, uint256 tokenId) {

    }

    function claimAndSwap() external {

    }

    function swapMe(address token) external {

    }

    function withdrawEther() external onlyOwner {

    }

    function withdrawTokens(address _token) external onlyOwner {

    }

    /**
     * @dev Swaps tokens with exact output amount
     * @param amountOut - exact output amount
     * @param amountInMax - minimal input amount
     * @param path - array of token addresses with swap order
     * @param deadline - swap deadline
     * @param router - uniswap router name
     */
    function swapTokensForExactTokens(
        uint256 amountOut,
        uint256 amountInMax,
        address[] calldata path,
        uint256 deadline,
        address router
    ) external onlyOwner {

        IUniswapV2Router02(router).swapTokensForExactTokens(
            amountOut,
            amountInMax,
            path,
            address(this),
            deadline
        );
    }

    /**
     * @dev Swaps tokens with exact input amount
     * @param amountIn - exact input amount
     * @param amountOutMin - maximal output amount
     * @param path - array of token addresses with swap order
     * @param deadline - swap deadline
     * @param router - uniswap router name
     */
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        uint256 deadline,
        address router
    ) external onlyOwner {

        IUniswapV2Router02(router).swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            path,
            address(this),
            deadline
        );
    }

}