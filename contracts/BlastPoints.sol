// SPDX-License-Identifier: MIT
// ENVELOP protocol for NFT. Blast Points Adapter
pragma solidity 0.8.21;

interface IBlastPoints {
	function configurePointsOperator(address operator) external;
}


contract BlastPoints {
    address constant public BLAST_POINTS_ADDRESS = 0x2536FE9ab3F511540F2f9e2eC2A805005C3Dd800;
	
	constructor(address _pointsOperator) {
    // be sure to use the appropriate testnet/mainnet BlastPoints address
		IBlastPoints(BLAST_POINTS_ADDRESS).configurePointsOperator(_pointsOperator);
	}
}