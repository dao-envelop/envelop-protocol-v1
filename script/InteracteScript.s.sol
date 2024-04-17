// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.21;

import {Script, console2} from "forge-std/Script.sol";
import "../lib/forge-std/src/StdJson.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {WrapperUsersV1Batch} from "../contracts/WrapperUsersV1Batch.sol";
import "../interfaces/IWrapperUsers.sol";

contract InteracteScript is Script {
    using stdJson for string;

    function run() public {
        console2.log("Chain id: %s", vm.toString(block.chainid));
        console2.log("Msg.sender address: %s, %s", msg.sender, msg.sender.balance);


        // Load json with chain params
        string memory root = vm.projectRoot();
        string memory params_path = string.concat(root, "/script/chain_params.json");
        string memory params_json_file = vm.readFile(params_path);
        string memory key;
        bytes2 rules = 0x0000; // 0x0004;

        // 
        address _wrapper = 0xdfaf9a0cB22275bd7BA2c883fff64919C7930d14; // wrapperUserBatch
        address _nyftsy = 0x5dB9f4C9239345308614604e69258C0bba9b437f;  // nyftsy token
        uint256 amount = 10e18;
 
        address[] memory receivers = new address[](2);
        WrapperUsersV1Batch wrapper = WrapperUsersV1Batch(_wrapper);
        console2.log("owner: %s", address(wrapper));

        receivers[0] = 0x5992Fe461F81C8E0aFFA95b831E50e9b3854BA0E;
        receivers[1] = 0xf315B9006C20913D6D8498BDf657E778d4Ddf2c4;

        ETypes.AssetItem[] memory collateral = new ETypes.AssetItem[](1);
        ETypes.INData[] memory WNFTs = new ETypes.INData[](2);
        ETypes.Fee[] memory fees;
        ETypes.Lock[] memory loks;
        ETypes.Royalty[] memory royalties;
        ETypes.INData memory inData = ETypes.INData(
                ETypes.AssetItem(
                        ETypes.Asset(ETypes.AssetType.EMPTY, address(0)),
                        0,
                        0
                    ),
                0x0000000000000000000000000000000000000000,
                fees,
                loks,
                royalties,
                ETypes.AssetType.ERC721,
                0,
                rules
            );

        WNFTs[0] = inData;
        WNFTs[1] = inData;
        collateral[0] = ETypes.AssetItem(
                            ETypes.Asset(ETypes.AssetType.ERC20, _nyftsy),
                            0,
                            amount
                        );
        

        vm.startBroadcast();
        IERC20(_nyftsy).approve(_wrapper, 2 * amount);
        wrapper.wrapBatch(
            WNFTs, 
            collateral,
            receivers,
            0xF30F852991775BC0A9C3880D1Ab9c464DAE7F8F0 // wrapIn
            );
        vm.stopBroadcast();

    }
}