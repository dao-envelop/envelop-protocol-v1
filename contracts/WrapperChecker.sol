// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - Checker
pragma solidity 0.8.11;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../interfaces/IWrapper.sol";
import "./LibEnvelopTypes.sol";
contract WrapperChecker {
    using SafeERC20 for IERC20;

    IWrapper public wrapper;
    uint256 constant public MAX_ROYALTY_PERCENT = 5000;
    uint256 constant public MAX_TIME_TO_UNWRAP = 365 days;
    uint256 constant public MAX_FEE_THRESHOLD_PERCENT = 1; //percent from project token totalSupply 

    constructor(address _wrapper) {
        require(_wrapper != address(0), "No zero");
        wrapper = IWrapper(_wrapper);
    }

    function getNativeCollateralBalance(
        address _wNFTAddress, 
        uint256 _wNFTTokenId 
    ) public view returns (uint256) 
    {
        (uint256 res, ) = wrapper.getCollateralBalanceAndIndex(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetType.NATIVE, 
            address(0), // tokenAddress 
            0           // tokenId
        );
        return res;
    }

    function getERC20CollateralBalance(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        address _erc20
    ) public view returns (uint256, uint256) 
    {
        return wrapper.getCollateralBalanceAndIndex(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetType.ERC20, 
            _erc20,
            0
        );
    }

    function getERC1155CollateralBalance(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        address _erc1155,
        uint256 _tokenId
    ) public view returns (uint256, uint256) 
    {
        return wrapper.getCollateralBalanceAndIndex(
            _wNFTAddress, 
            _wNFTTokenId,
            ETypes.AssetType.ERC1155, 
            _erc1155,
            _tokenId
        ); 
    }

    function checkWrap(
        ETypes.INData calldata _inData, 
        ETypes.AssetItem[] calldata _collateral, 
        address _wrappFor
    ) 
        public view returns (bool, string memory)
    {
        bool result = true;
        string memory messages = "";
        if (_inData.unWrapDestinition == address(0)) {
            result = false;
            messages="unWrapDestinition cant be zero, ";
            }

        if (_wrappFor == address(0)) {
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    "WrapperFor cant be zero, "
                    )
                );
            }

        if (_inData.fees.length == 0&&_inData.royalties.length != 0){
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    "Royalty source is transferFee, "
                    )
                ); 
            }

        if (_inData.outType == ETypes.AssetType.ERC1155&&_inData.outBalance == 0){
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    "WNFT type is ERC1155 - wnft should have balance, "
                    )
                ); 
            }
        
        if (_inData.inAsset.asset.assetType == ETypes.AssetType.ERC1155&&_inData.inAsset.amount == 0){
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    "Original NFT type is ERC1155 - original nft should have balance, "
                    )
                ); 
            }

        if (_inData.inAsset.asset.contractAddress == address(0)){
            result = false; 
            messages= string(
                abi.encodePacked(
                    messages,
                    "NFT contract address cant be zero, "
                    )
                ); 
            }

        if (_inData.locks.length != 0){
            uint256 j = 0;
            for (uint256 i = 0; i < _inData.locks.length; i ++) {
                if (_inData.locks[i].lockType == 0x00){
                    j++;
                }
            }
            if (j > 1) {
                result = false; 
                messages= string(
                    abi.encodePacked(
                        messages,
                        "Several time locks, "
                        )
                    );
                } 
            }

        if (_inData.locks.length != 0){
            for (uint256 i = 0; i < _inData.locks.length; i ++) {
                if (_inData.locks[i].lockType == 0x00&&_inData.locks[i].param>block.timestamp + MAX_TIME_TO_UNWRAP){
                    result = false; 
                    messages= string(
                        abi.encodePacked(
                            messages,
                            "Too long Wrap, "
                            )
                        );
                    }
                }
            }

        if (_inData.rules != 0x0002&& _inData.rules > 0x000F){
            result = false; 
                messages= string(
                    abi.encodePacked(
                        messages,
                        "Wrong rule code, "
                    )
                );
            }

        if (_inData.fees.length != 0){
            for (uint256 i = 0; i < _inData.fees.length; i ++) {
                if (_inData.fees[i].param!=0&&_inData.fees[i].token!=address(0)){
                    //there is transfer fee and settings are correct
                    for (uint256 j = 0; j < _inData.royalties.length; j ++) {
                        if (_inData.royalties[j].beneficiary == address(0)||_inData.royalties[j].percent==0){
                            //incorrect something in royalty settings
                            result = false; 
                            messages= string(
                                abi.encodePacked(
                                    messages,
                                    "Wrong royalty settings, "
                                )
                            );
                            break;
                        }
                        else {
                            if (_inData.royalties[j].percent > MAX_ROYALTY_PERCENT&&_inData.royalties[j].beneficiary!=address(wrapper)){
                                result = false; 
                                messages= string(
                                    abi.encodePacked(
                                        messages,
                                        "Royalty percent too big, "
                                    )
                                );
                                break;
                            }

                        }
                    }
                    if (_inData.fees[i].feeType == 0x00&&_inData.fees[i].token!=wrapper.protocolTechToken()){
                        for (uint256 j = 0; j < _inData.locks.length; j ++) {
                            if (_inData.locks[j].lockType == 0x01&&_inData.locks[j].param>IERC20(_inData.fees[i].token).totalSupply() * MAX_FEE_THRESHOLD_PERCENT / 100){
                                result = false; 
                                messages= string(
                                    abi.encodePacked(
                                        messages,
                                        "Too much threshold, "
                                        )
                                    );
                                break;
                                }
                            }
                        }

                }
                else {
                    result = false; 
                    messages= string(
                        abi.encodePacked(
                            messages,
                            "Wrong Fee settings, "
                            )
                        );
                    break;
                    }
                }
            }
        else {
            for (uint256 l = 0; l < _inData.locks.length; l ++) {
                if (_inData.locks[l].lockType == 0x01&&_inData.locks[l].param!=0){
                    result = false; 
                    messages= string(
                        abi.encodePacked(
                            messages,
                            "Cant set Threshold without transferFee, "
                            )
                        );
                    break;
                    }
                }
                
            }

         if (_inData.fees.length != 0){
            uint256 j=0;
            for (uint256 i = 0; i < _inData.fees.length; i ++) {
                if (_inData.fees[i].feeType==0x00){
                    j++;
                    }
                }
            if (j==0){
                for (uint256 l = 0; l < _inData.locks.length; l ++) {
                    if (_inData.locks[l].lockType == 0x01&&_inData.locks[l].param!=0){
                        result = false; 
                        messages= string(
                            abi.encodePacked(
                                messages,
                                "Cant set Threshold without transferFee, "
                                )
                            );
                        break;
                        }
                    }
                if (_inData.royalties.length != 0){
                    result = false; 
                    messages= string(
                        abi.encodePacked(
                            messages,
                            "Royalty source is transferFee, "
                            )
                        ); 
                    }

                }
            }   

        //analyze collateral array

        if (_collateral.length!=0){
            for (uint256 i = 0; i < _collateral.length; i ++) {
                if (_collateral[i].asset.assetType == ETypes.AssetType.ERC20&&(_collateral[i].asset.contractAddress==address(0)||_collateral[i].amount==0)){
                    result = false; 
                    messages= string(
                        abi.encodePacked(
                            messages,
                            "ERC20 collateral has incorrect settings, "
                            )
                        );
                    break;
                    }
                else if(_collateral[i].asset.assetType == ETypes.AssetType.ERC721&&_collateral[i].asset.contractAddress==address(0)){
                    result = false; 
                    messages= string(
                        abi.encodePacked(
                            messages,
                            "ERC721 collateral has incorrect settings, "
                            )
                        );
                    break;
                    }
                else if (_collateral[i].asset.assetType == ETypes.AssetType.ERC1155&&
                        (_collateral[i].asset.contractAddress==address(0)||_collateral[i].amount==0||_collateral[i].tokenId==0)){
                    result = false; 
                    messages= string(
                        abi.encodePacked(
                            messages,
                            "ERC1155 collateral has incorrect settings, "
                            )
                        );
                    break;
                    }
                }
            }
        
        bytes memory messages_bytes =  bytes ( messages ); 
        if (messages_bytes.length == 0) {
            messages="Success";
        }

        return (result, messages);
    }

    function checkAddCollateral(
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        ETypes.AssetItem[] calldata _collateral
    ) public view returns (bool, string memory) 
    {
        bool result = true;
        string memory messages = "";
        //analize collateral array

        if (_collateral.length!=0){
            for (uint256 i = 0; i < _collateral.length; i ++) {
                if (_collateral[i].asset.assetType == ETypes.AssetType.ERC20&&(_collateral[i].asset.contractAddress==address(0)||_collateral[i].amount==0)){
                    result = false; 
                    messages= string(
                        abi.encodePacked(
                            messages,
                            "ERC20 collateral has incorrect settings, "
                            )
                        );
                    break;
                    }
                else if(_collateral[i].asset.assetType == ETypes.AssetType.ERC721&&_collateral[i].asset.contractAddress==address(0)){
                    result = false; 
                    messages= string(
                        abi.encodePacked(
                            messages,
                            "ERC721 collateral has incorrect settings, "
                            )
                        );
                    break;
                    }
                else if (_collateral[i].asset.assetType == ETypes.AssetType.ERC1155&&
                        (_collateral[i].asset.contractAddress==address(0)||_collateral[i].amount==0||_collateral[i].tokenId==0)){
                    result = false; 
                    messages= string(
                        abi.encodePacked(
                            messages,
                            "ERC1155 collateral has incorrect settings, "
                            )
                        );
                    break;
                    }
                }
            }
        
        return (result, messages);
    }

    function checkUnWrap(
        ETypes.AssetType _wNFTType, 
        address _wNFTAddress, 
        uint256 _wNFTTokenId, 
        bool _isEmergency
    ) public view returns (bool) 
    {
        return true;
    }
}
