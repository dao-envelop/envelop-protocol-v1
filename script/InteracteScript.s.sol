// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.21;

import {Script, console2} from "forge-std/Script.sol";
import "../lib/forge-std/src/StdJson.sol";
import {WrapperUsersV1Batch} from "../contracts/WrapperUsersV1Batch.sol";
import "../interfaces/IWrapperUsersV1Batch.sol";

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

        // 
        address wrapper = 0x7EdB762bb3E7a7402Bb3Cd8DFAEb04Fe15ab0829; // wrapperUserBatch
 
        address[] memory receivers = new address[](2);
        console2.log("owner: %s", address(IWrapperUsersV1Batch(wrapper)));

        receivers[0] = 0x5992Fe461F81C8E0aFFA95b831E50e9b3854BA0E;
        receivers[1] = 0xf315B9006C20913D6D8498BDf657E778d4Ddf2c4;

        ETypes.AssetItem[] memory collateral;
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
                0x0004
            );

        WNFTs[0] = inData;
        WNFTs[1] = inData;
        

        vm.startBroadcast();
        IWrapperUsersV1Batch(wrapper).wrapBatch(
            WNFTs, 
            collateral,
            receivers,
            0x7851990E0005d7931caAcD9c8b681B4eF7490062 // wrappIn
            );
        vm.stopBroadcast();

    }
}