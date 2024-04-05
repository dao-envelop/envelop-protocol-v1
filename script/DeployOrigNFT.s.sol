// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.21;

import {Script, console2} from "forge-std/Script.sol";
import "../lib/forge-std/src/StdJson.sol";
import {OrigNFT}  from "../contracts/OriginalNFT.sol";


contract DeployOrigNFT is Script {
    using stdJson for string;

    function run() public {
        console2.log("Chain id: %s", vm.toString(block.chainid));
        console2.log("Deployer address: %s, %s", msg.sender, msg.sender.balance);

        // Load json with chain params
        string memory root = vm.projectRoot();
        string memory params_path = string.concat(root, "/script/chain_params.json");
        string memory params_json_file = vm.readFile(params_path);
        
        //////////   Deploy   //////////////
        vm.startBroadcast();
        OrigNFT origNFT  = new OrigNFT(
            'Envelop simple NFT',
            'ENVELOP',
            'https://envelop.is/metadata/');
        vm.stopBroadcast();
        
        ///////// Pretty printing ////////////////
        
        string memory path = string.concat(root, "/script/explorers.json");
        string memory json = vm.readFile(path);
        console2.log("Chain id: %s", vm.toString(block.chainid));
        string memory explorer_url = json.readString(
            string.concat(".", vm.toString(block.chainid))
        );
        
        console2.log("\n**OriginalNFT**  ");
        console2.log("https://%s/address/%s#code\n", explorer_url, address(origNFT));
        
        console2.log("```python");
        console2.log("origNFT = OrigNFT.at('%s')", address(origNFT));
        console2.log("```");
   
        ///////// End of pretty printing ////////////////
    }
}
