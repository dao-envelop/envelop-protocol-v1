// SPDX-License-Identifier: MIT
// ENVELOP protocol for NFT. Main protocol with Blast Points
pragma solidity 0.8.21;

import "./WrapperBaseV1.sol";
import "./BlastPoints.sol";


contract WrapperBaseV1BlastPoints is WrapperBaseV1, BlastPoints {
    

    constructor(
        address _erc20,
        address _pointsOperator
    ) 
        WrapperBaseV1(_erc20)
        BlastPoints(_pointsOperator)
    {
    }

    
}