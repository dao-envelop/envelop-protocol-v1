// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.21;

import {Script, console2} from "forge-std/Script.sol";
import "../lib/forge-std/src/StdJson.sol";
import {WrapperUsersV1Batch} from "../contracts/WrapperUsersV1Batch.sol";

contract DeployScript is Script {
    using stdJson for string;

    function run() public {
        console2.log("Chain id: %s", vm.toString(block.chainid));
        console2.log("Deployer address: %s, %s", msg.sender, msg.sender.balance);

        // Load json with chain params
        string memory root = vm.projectRoot();
        string memory params_path = string.concat(root, "/script/chain_params.json");
        string memory params_json_file = vm.readFile(params_path);
        string memory key;

        // Define constructor params
        address event_reg;   
        key = string.concat(".", vm.toString(block.chainid),".event_reg");
        if (vm.keyExists(params_json_file, key)) 
        {
            event_reg = params_json_file.readAddress(key);
        } else {
            event_reg = msg.sender;
        }
        console2.log("event_reg: %s", event_reg); 
        
        //////////   Deploy   //////////////
        vm.startBroadcast();
        WrapperUsersV1Batch wrapper = new WrapperUsersV1Batch(event_reg);
        vm.stopBroadcast();
        
        ///////// Pretty printing ////////////////
        
        string memory path = string.concat(root, "/script/explorers.json");
        string memory json = vm.readFile(path);
        console2.log("Chain id: %s", vm.toString(block.chainid));
        string memory explorer_url = json.readString(
            string.concat(".", vm.toString(block.chainid))
        );
        
        console2.log("\n**WrapperUsersV1Batch**  ");
        console2.log("https://%s/address/%s#code\n", explorer_url, address(wrapper));
       
        
        console2.log("```python");
        console2.log("wrapper = WrapperUsersV1Batch.at('%s')", address(wrapper));
        console2.log("```");   
        ///////// End of pretty printing ////////////////
    }
}
