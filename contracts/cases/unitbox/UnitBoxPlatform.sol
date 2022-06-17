// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. UnitBoxPlatform case 


import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "./IUniswapV2Router02.sol";
import "./IUniswapV2Factory.sol";
import "../../../interfaces/IWrapperRemovable.sol";
import "./IUnitBox.sol";

pragma solidity 0.8.13;

contract UnitBoxPlatform is Ownable, IUnitBox{
    using ECDSA for bytes32;
    
    uint256 constant public DELTA_FOR_SWAP_DEADLINE = 300;

    address constant public UniswapV2Router02 = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
    address constant public UniswapV2Factory  = 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f;
    address public assetForTreasure; // USDT
    address public treasure;
    bytes2 public wnftRules = 0x0000;

    IWrapperRemovable public wrapper;
    DexParams public dexForChain;
    mapping(address => bool) public trustedSigners;
    mapping(address => GameTokenDex) public dexForAsset; 
    mapping(uint256 =>bool) public nonceUsed;

    constructor (address _wrapper) {
        wrapper = IWrapperRemovable(_wrapper);
        // predefined settings for some networks
        if (block.chainid == 1) {
            dexForChain.router = UniswapV2Router02;
            dexForChain.factory = UniswapV2Factory;
            dexForChain.nativeAsset = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2; // WETH
            dexForChain.assetForTreasure = 0xdAC17F958D2ee523a2206206994597C13D831ec7; // USDT
        
        } else if (block.chainid == 4) {
            dexForChain.router = UniswapV2Router02;
            dexForChain.factory = UniswapV2Factory;
            dexForChain.nativeAsset = 0xc778417E063141139Fce010982780140Aa0cD5Ab ; // WETH
            dexForChain.assetForTreasure = 0xc7AD46e0b8a400Bb3C915120d284AafbA8fc4735; //DAI

        } else if (block.chainid == 56) {
            //exForChain.nativeAsset = ; //  ???
            dexForChain.assetForTreasure =  0x55d398326f99059fF775485246999027B3197955; //USDT BSC

        }
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
        require(dexForAsset[_collateralAddress].enabled, "Disable for claim");
        wrapper.removeERC20Collateral(_wNFTAddress, _wNFTTokenId, _collateralAddress);
        swapMe(_collateralAddress);

    }

    function swapMe(address token) public {

        if (dexForAsset[token].dexType == DexType.UniSwapV2) {
            // UniswapV2 Router implementation
            address router = dexForAsset[token].dexAddress;
            address receiver = treasure;
            if (router == address(0)) {
                router = dexForChain.router;
            }
            
            if (receiver == address(0)) {
                receiver = address(this);
            } 

            // Lets discover path
            address pair = IUniswapV2Factory(dexForChain.factory).getPair(
                token, 
                dexForChain.assetForTreasure
            );
            uint256 lenPath = pair == address(0) ? 3 : 2;
            address[] memory path = new address[](lenPath);
            if (lenPath == 2) {
               path[0] = token;
               path[1] = dexForChain.assetForTreasure;
            } else {
               path[0] = token;
               path[1] = dexForChain.nativeAsset;
               path[2] = dexForChain.assetForTreasure;    
            }
            
            IUniswapV2Router02(router).swapExactTokensForTokens(
                IERC20(token).balanceOf(address(this)), // amountIn
                0, // amountOutMin
                path, // path
                receiver, // to
                block.timestamp + DELTA_FOR_SWAP_DEADLINE // deadline
            );
        } else {
            // Dummy Swap - transfer to owner
            IERC20(token).transfer(owner(), IERC20(token).balanceOf(address(this)));
        }

    }

    function swapMeWithPath(address token, address[] calldata _path) public {

        if (dexForAsset[token].dexType == DexType.UniSwapV2) {
            // UniswapV2 Router implementation
            address router = dexForAsset[token].dexAddress;
            address receiver = treasure;
            if (router == address(0)) {
                router = dexForChain.router;
            }
            
            if (receiver == address(0)) {
                receiver = address(this);
            } 
            // https://docs.uniswap.org/protocol/V2/guides/smart-contract-integration/trading-from-a-smart-contract  
            IUniswapV2Router02(router).swapExactTokensForTokens(
                IERC20(token).balanceOf(address(this)), // amountIn
                0, // amountOutMin
                _path, // path
                receiver, // to
                block.timestamp + DELTA_FOR_SWAP_DEADLINE // deadline
            );
        } else {
            // Dummy Swap - transfer to owner
            IERC20(token).transfer(owner(), IERC20(token).balanceOf(address(this)));
        }


    }

    ///////////////////////////////////////////////////////////////////
    ///                Admin Functions                               //
    ///////////////////////////////////////////////////////////////////
    function withdrawEther() external onlyOwner {
        address payable o = payable(msg.sender);
        o.transfer(address(this).balance);

    }

    function withdrawTokens(address _token) external onlyOwner {
        IERC20(_token).transfer(
            owner(), 
            IERC20(_token).balanceOf(address(this))
        );

    }

    function setTokenDex(address _token, GameTokenDex calldata _dex) external onlyOwner {
        dexForAsset[_token] = _dex;
    }

    function setSignerState(address _signer, bool _state) external onlyOwner {
        trustedSigners[_signer] = _state;
    }

    function setWrapRule(bytes2 _rule) external onlyOwner {
        wnftRules = _rule;
    }

    function setTreasure(address _treasure) external onlyOwner {
        treasure = _treasure;
    }

    function setDexForChain(DexParams calldata _dexParams) external onlyOwner {
        dexForChain = _dexParams;
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
}