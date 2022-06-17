// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. UnitBoxPlatform case 


import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "./IUniswapV2Router02.sol";
import "../../../interfaces/IWrapperRemovable.sol";
import "./IUnitBox.sol";

pragma solidity 0.8.13;

contract UnitBoxPlatform is Ownable, IUnitBox{
    using ECDSA for bytes32;
    
    bytes2 public wnftRules = 0x0000;

    IWrapperRemovable public wrapper;

    mapping(address => bool) public trustedSigners;
    mapping(address => GameTokenDex) public dex; 
    mapping(uint256 =>bool) public nonceUsed;

    constructor (address _wrapper) {
        wrapper = IWrapperRemovable(_wrapper);
    }

    function wrapForRent(
        ETypes.INData  calldata _inData,
        uint256 _nonce,
        bytes memory _signature
    ) 
        external 
        returns (address wnftContract, uint256 tokenId) 
    {
        bytes32 msgMustWasSigned = keccak256(abi.encode(
                _inData.inAsset.asset.contractAddress,
                _inData.inAsset.tokenId,
                _inData.royalties,
                msg.sender,
                _nonce
        )).toEthSignedMessageHash();
        require(_checkSign(msgMustWasSigned, _signature), "Signature check failed");
        require(!nonceUsed[_nonce], "Nonce used");
        // Check and prepare params for wrap
        require(_inData.royalties.length > 2, "No beneficiaries");
        require(_inData.royalties[_inData.royalties.length - 1].beneficiary == address(this),
             "Last record in royalties always this contract"
        );

        ETypes.AssetItem[] memory _collateral; 
        ETypes.AssetItem memory _wnft;

        _wnft = wrapper.wrap( _inData, _collateral, _inData.royalties[1].beneficiary);
        return (_wnft.asset.contractAddress, _wnft.tokenId);
    }

    function claimAndSwap(
        address _wNFTAddress, 
        uint256 _wNFTTokenId,
        address _collateralAddress
    ) external {
        require(dex[_collateralAddress].enabled, "Disable for claim");
        wrapper.removeERC20Collateral(_wNFTAddress, _wNFTTokenId, _collateralAddress);
        swapMe(_collateralAddress);

    }

    function swapMe(address token) public {


    }

    ///////////////////////////////////////////////////////////////////
    ///                Admin Functions                               //
    ///////////////////////////////////////////////////////////////////
    function withdrawEther() external onlyOwner {
        address payable o = payable(msg.sender);
        o.transfer(address(this).balance);

    }

    function withdrawTokens(address _token) external onlyOwner {
        IERC20(_token).transfer(owner(), IERC20(_token).balanceOf(address(this)));

    }

    function setTokenDex(address _token, GameTokenDex calldata _dex) external onlyOwner {
        dex[_token] = _dex;
    }

    function setSignerState(address _signer, bool _state) external onlyOwner {
        trustedSigners[_signer] = _state;
    }

    function setWrapRule(bytes2 _rule) external onlyOwner {
        wnftRules = _rule;
    }



    ///////////////////////////////////////////////////////////////////

    function _checkSign(bytes32 _msg, bytes memory _signature) internal returns (bool) {
        // Check signature  author
        if (trustedSigners[_msg.recover(_signature)]) {
            return true;
        } else {
            return false;
        }    
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
    ) internal  {

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
    ) internal  {

        IUniswapV2Router02(router).swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            path,
            address(this),
            deadline
        );
    }

}