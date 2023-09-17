// SPDX-License-Identifier: MIT
// Proxy for Public Mintable User NFT Collection
pragma solidity 0.8.21;
    

contract MockUsersSBTCollectionPRegistry  {
    
    enum AssetType {EMPTY, NATIVE, ERC20, ERC721, ERC1155, FUTURE1, FUTURE2, FUTURE3}

    struct Asset {
        AssetType assetType;
        address contractAddress;
    }

    Asset[] public supportedImplementations;
    // mapping from user to his(her) contracts with type
    mapping(address => Asset[]) public collectionRegistry;

    //IUsersSBTCollectionFactory public factory;
    
    

    function deployNewCollection(
        address _implAddress, 
        address _creator,
        string memory name_,
        string memory symbol_,
        string memory _baseurl,
        address _wrapper
    ) external {
        (bool _supported, uint256 index) = isImplementationSupported(_implAddress);
        collectionRegistry[_creator].push(Asset(supportedImplementations[index].assetType, _implAddress)); 
    }
    function getSupportedImplementation() external view returns(Asset[] memory) {
        return supportedImplementations;
    }

    function getUsersCollections(address _user) external view returns(Asset[] memory) {
        return collectionRegistry[_user];
    }
    ////////////////////////////////////
    /// Admin  functions           /////
    ////////////////////////////////////
    function addImplementation(Asset calldata _impl) external  {
        // Check that not exist
        for(uint256 i; i < supportedImplementations.length; ++i){
            require(
                supportedImplementations[i].contractAddress != _impl.contractAddress,
                "Already exist"
            );
        }
        supportedImplementations.push(Asset(_impl.assetType, _impl.contractAddress));
    }

    function removeImplementationByIndex(uint256 _index) external  {
        if (_index != supportedImplementations.length -1) {
            supportedImplementations[_index] = supportedImplementations[supportedImplementations.length -1];
        }
        supportedImplementations.pop();
    }
    function isImplementationSupported(address _impl) public view  returns(bool isSupported, uint256 index) {
        for (uint256 i; i < supportedImplementations.length; ++i){
            if (_impl == supportedImplementations[i].contractAddress){
                isSupported = true;
                index = i; 
                break;
            }
        }
    }
}