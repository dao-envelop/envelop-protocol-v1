// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. UnitBoxPlatform case 


import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "./IUniswapV2Router02.sol";
import "./IUniswapV2Factory.sol";
import "../../../interfaces/IWrapperRemovable.sol";
import "./IUnitBox.sol";

pragma solidity 0.8.21;

/// @title UnitBoxPlatform middleware for rent nfts 
/// @author Envelop project Team
/// @notice You can use this contract for wrapping nfts with special rules
/// @dev All function calls are currently implemented without side effects
contract UnitBoxPlatform is Ownable, IUnitBox{
    using ECDSA for bytes32;
    
    uint256 constant public DELTA_FOR_SWAP_DEADLINE = 300;
    address constant public UniswapV2Router02 = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
    address constant public UniswapV2Factory  = 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f;
    address public treasury;
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
            dexForChain.router  = UniswapV2Router02;
            dexForChain.factory = UniswapV2Factory;
            dexForChain.nativeAsset      = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2; // WETH
            dexForChain.assetForTreasury = 0xdAC17F958D2ee523a2206206994597C13D831ec7; // USDT

        } else if (block.chainid == 3) {
            dexForChain.router  = UniswapV2Router02;
            dexForChain.factory = UniswapV2Factory;
            dexForChain.nativeAsset      = 0xc778417E063141139Fce010982780140Aa0cD5Ab ; // WETH
            dexForChain.assetForTreasury = 0xaD6D458402F60fD3Bd25163575031ACDce07538D; //DAI
        
        } else if (block.chainid == 4) {
            dexForChain.router  = UniswapV2Router02;
            dexForChain.factory = UniswapV2Factory;
            dexForChain.nativeAsset      = 0xc778417E063141139Fce010982780140Aa0cD5Ab ; // WETH
            dexForChain.assetForTreasury = 0xc7AD46e0b8a400Bb3C915120d284AafbA8fc4735; //DAI

        } else if (block.chainid == 56) {
            dexForChain.router  = 0x10ED43C718714eb63d5aA57B78B54704E256024E;
            dexForChain.factory = 0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73;
            dexForChain.nativeAsset      = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c ; // WBNB
            dexForChain.assetForTreasury =  0x55d398326f99059fF775485246999027B3197955; //USDT BSC

        }
    }
    
    /// @notice Just for wrap batch of nfts in one transaction
    /// @dev Please be patient in params encoding with web3 libs
    /// @param _inDataS array of ETypes.INData
    /// @param _nonceS array of _nonceS
    /// @param _signatureS array of _signatureS
    function wrapBatch(
        ETypes.INData[]  calldata _inDataS,
        uint256[] calldata _nonceS,
        bytes[] calldata _signatureS

    ) external {
        for (uint256 i = 0; i < _inDataS.length; i++) {
            wrapForRent(
                _inDataS[i],
                _nonceS[i],
                _signatureS[i]
            );
        }
    }

    /// @notice Just for wrap nft
    /// @dev You can use `prepareMessage` function from  this contract
    /// before make sign
    /// @param _inData encoded ETypes.INData
    /// @param _nonce just uniq identifier against any kind of double spend
    /// @param _signature subj
    function wrapForRent(
        ETypes.INData  calldata _inData,
        uint256 _nonce,
        bytes memory _signature
    ) 
        public 
        returns (address wnftContract, uint256 tokenId) 
    {
        bytes32 msgMustWasSigned = prepareMessage(
                _inData.inAsset.asset.contractAddress,
                _inData.inAsset.tokenId,
                _inData.royalties,
                msg.sender,
                _nonce
        ).toEthSignedMessageHash();
        require(_checkSign(msgMustWasSigned, _signature), "Signature check failed");
        require(!nonceUsed[_nonce], "Nonce used");
        
        // Check and prepare params for wrap
        require(_inData.royalties.length > 2, "No beneficiaries");
        require(_inData.royalties[_inData.royalties.length - 1].beneficiary == address(this),
             "Last record in royalties always this contract"
        );
        require(_inData.rules == wnftRules, "Rules check fail");

        ETypes.AssetItem[] memory _collateral; 
        ETypes.AssetItem memory _wnft;
        nonceUsed[_nonce] = true;
        _wnft = wrapper.wrap( _inData, _collateral, _inData.royalties[1].beneficiary);
        return (_wnft.asset.contractAddress, _wnft.tokenId);
    }

    function unWrap(address _wNFTAddress, uint256 _wNFTTokenId) external {
        ETypes.WNFT memory wnft =  wrapper.getWrappedToken(_wNFTAddress, _wNFTTokenId);
        require(msg.sender == wnft.royalties[0].beneficiary 
             || msg.sender == wnft.royalties[1].beneficiary,
            "Only owner or  renter"
        );
        wrapper.unWrap(_wNFTAddress, _wNFTTokenId);
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
            address receiver = treasury;
            if (router == address(0)) {
                router = dexForChain.router;
            }
            
            if (receiver == address(0)) {
                receiver = address(this);
            } 

            // Lets discover path
            address pair = IUniswapV2Factory(dexForChain.factory).getPair(
                token, 
                dexForChain.assetForTreasury
            );
            uint256 lenPath = pair == address(0) ? 3 : 2;
            address[] memory path = new address[](lenPath);
            if (lenPath == 2) {
               path[0] = token;
               path[1] = dexForChain.assetForTreasury;
            } else {
               path[0] = token;
               path[1] = dexForChain.nativeAsset;
               path[2] = dexForChain.assetForTreasury;    
            }
            IERC20(token).approve(router,IERC20(token).balanceOf(address(this)));
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
            address receiver = treasury;
            if (router == address(0)) {
                router = dexForChain.router;
            }
            
            if (receiver == address(0)) {
                receiver = address(this);
            } 
            IERC20(token).approve(router,IERC20(token).balanceOf(address(this)));
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

    function prepareMessage(
        address _addr, 
        uint256 _uint, 
        ETypes.Royalty[] calldata _arr, 
        address _sender, 
        uint256 _nonce
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(_addr, _uint, _arr, _sender, _nonce));
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

    function settreasury(address _treasury) external onlyOwner {
        treasury = _treasury;
    }

    function setDexForChain(DexParams calldata _dexParams) external onlyOwner {
        dexForChain = _dexParams;
    }
    ///////////////////////////////////////////////////////////////////

    function _checkSign(bytes32 _msg, bytes memory _signature) internal view returns (bool) {
        // Check signature  author
        if (trustedSigners[_msg.recover(_signature)]) {
            return true;
        } else {
            return false;
        }    
    }
}