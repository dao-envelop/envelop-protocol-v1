// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.21;

import {Script, console2} from "forge-std/Script.sol";
import "../lib/forge-std/src/StdJson.sol";
import {TechTokenV1}  from "../contracts/TechTokenV1.sol";
import {WrapperBaseV1BlastPoints} from "../contracts/WrapperBaseV1BlastPoints.sol";
import {EnvelopwNFT721} from "../contracts/EnvelopwNFT721.sol";
import {EnvelopwNFT1155} from "../contracts/EnvelopwNFT1155.sol";
import {AdvancedWhiteList} from "../contracts/AdvancedWhiteList.sol";
import {OrigNFT} from "../contracts/OriginalNFT.sol";
import "../contracts/LibEnvelopTypes.sol";


contract DeployMainBlast is Script {
    using stdJson for string;

    function run() public {
        console2.log("Chain id: %s", vm.toString(block.chainid));
        console2.log("Deployer address: %s, %s", msg.sender, msg.sender.balance);
        
        address pointsOperator = 0x303cD2A927D9Cb6F5CE03b88a4e3E2528baEDF40;

        // Load json with chain params
        string memory root = vm.projectRoot();
        string memory params_path = string.concat(root, "/script/chain_params.json");
        string memory params_json_file = vm.readFile(params_path);
        string memory key;

        // Define constructor params
        address sub_reg;   
        key = string.concat(".", vm.toString(block.chainid),".sub_reg");
        if (vm.keyExists(params_json_file, key)) 
        {
            sub_reg = params_json_file.readAddress(key);
        } else {
            sub_reg = msg.sender;
        }
        console2.log("sub_reg: %s", sub_reg); 

        address[] memory wl_items;   
        key = string.concat(".", vm.toString(block.chainid),".wl_items");
        if (vm.keyExists(params_json_file, key)) 
        {
            wl_items = params_json_file.readAddressArray(key);
        // } else {
        //     wl_items = [];
        }
        console2.log("wl_items[0]: %s", wl_items[0]); 
        
        
        
        //////////   Deploy   //////////////
        vm.startBroadcast();
        TechTokenV1 techERC20  = new TechTokenV1();
        WrapperBaseV1BlastPoints wrapper = new WrapperBaseV1BlastPoints(
            address(techERC20),
            pointsOperator
        );
        EnvelopwNFT721 wnft721   = new EnvelopwNFT721(
            'ENVELOP 721 wNFT Collection', 
            'wNFT', 
            'https://api.envelop.is/metadata/',
            address(wrapper)
        );
        EnvelopwNFT1155 wnft1155   = new EnvelopwNFT1155(
            'ENVELOP 1155 wNFT Collection', 
            'wNFT', 
            'https://api.envelop.is/metadata/',
            address(wrapper)
        );
        AdvancedWhiteList whitelist = new AdvancedWhiteList();
        OrigNFT original = new OrigNFT(
            'ENVELOP 721 Default Collection', 
            'ENVELOP', 
            'https://api.envelop.is/metadata/'

        );
        vm.stopBroadcast();
        
        ///////// Pretty printing ////////////////
        
        string memory path = string.concat(root, "/script/explorers.json");
        string memory json = vm.readFile(path);
        console2.log("Chain id: %s", vm.toString(block.chainid));
        string memory explorer_url = json.readString(
            string.concat(".", vm.toString(block.chainid))
        );
        
        console2.log("\n**TechTokenV1**  ");
        console2.log("https://%s/address/%s#code\n", explorer_url, address(techERC20));
        console2.log("\n**WrapperBaseV1BlastPoints** ");
        console2.log("https://%s/address/%s#code\n", explorer_url, address(wrapper));
        console2.log("\n**EnvelopwNFT721** ");
        console2.log("https://%s/address/%s#code\n", explorer_url, address(wnft721));
        console2.log("\n**EnvelopwNFT1155** ");
        console2.log("https://%s/address/%s#code\n", explorer_url, address(wnft1155));
        console2.log("\n**AdvancedWhiteList** ");
        console2.log("https://%s/address/%s#code\n", explorer_url, address(whitelist));
        console2.log("\n**OrigNFT** ");
        console2.log("https://%s/address/%s#code\n", explorer_url, address(original));

        console2.log("```python");
        console2.log("techERC20 = TechTokenV1.at('%s')", address(techERC20));
        console2.log("wrapper = WrapperBaseV1BlastPoints.at('%s')", address(wrapper));
        console2.log("wnft721 = EnvelopwNFT721.at('%s')", address(wnft721));
        console2.log("wnft1155 = EnvelopwNFT1155.at('%s')", address(wnft1155));
        console2.log("whitelist = AdvancedWhiteList.at('%s')", address(whitelist));
        console2.log("original = OrigNFT.at('%s')", address(original));
        console2.log("```");
   
        ///////// End of pretty printing ////////////////

        ///  Init ///
        console2.log("Init transactions....");
        vm.startBroadcast();
        wrapper.setWNFTId(ETypes.AssetType.ERC721, address(wnft721), 1);
        wrapper.setWNFTId(ETypes.AssetType.ERC1155, address(wnft1155),1);
        // No need wl for tetstnets
        if (wl_items.length > 0) {
            for (uint8 i = 0; i < wl_items.length; ++ i) {
                whitelist.setWLItem(
                    ETypes.Asset(ETypes.AssetType.ERC20 ,wl_items[i]), 
                    ETypes.WhiteListItem(true, true, true, address(techERC20))
                );
                console2.log("  WL Item added ('%s')", wl_items[i]);
            }
            wrapper.setWhiteList(address(whitelist));
        }
        //wrapper.setWhiteList(whitelist.address, tx_params)
                
        vm.stopBroadcast();
        console2.log("Initialisation finished");

    }
}
