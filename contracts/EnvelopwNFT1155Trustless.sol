// SPDX-License-Identifier: MIT
// ENVELOP protocol for NFT
pragma solidity 0.8.19;

import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Supply.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/IERC1155MetadataURI.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "../interfaces/IWrapper.sol";

contract EnvelopwNFT1155Trustless is ERC1155Supply {
    using Strings for uint256;
    using Strings for uint160;
    
    address public wrapper;       // main protocol contarct

    // Token name
    string public name;

    // Token symbol
    string public symbol;
    
    constructor(
        string memory name_,
        string memory symbol_,
        string memory _baseurl,
        address  _wrapper

    ) 
        ERC1155(_baseurl)  
    {

        _setURI(string(
            abi.encodePacked(
                _baseurl,
                block.chainid.toString(),
                "/",
                uint160(address(this)).toHexString(),
                "/"
            )
        ));
        name = name_;
        symbol = symbol_;
        wrapper = _wrapper;
    }

    function mint(address _to, uint256 _tokenId, uint256 _amount) external {
        require(wrapper == msg.sender, "Trusted address only");
        _mint(_to, _tokenId, _amount, "");
    }

    /**
     * @dev Burns `tokenId`. See {ERC721-_burn}.
     *
     * Requirements:
     *
     * - The caller must own `tokenId` or be an approved operator.
     */
    function burn(address _from, uint256 _tokenId, uint256 _amount) public virtual {
        require(wrapper == msg.sender, "Trusted address only");
        _burn(_from, _tokenId, _amount);
    }


    
    function wnftInfo(uint256 tokenId) external view returns (ETypes.WNFT memory) {
        return IWrapper(wrapper).getWrappedToken(address(this), tokenId);
    }

    function uri(uint256 _tokenID) public view override 
        returns (string memory _uri) 
    {
        _uri = IWrapper(wrapper).getOriginalURI(address(this), _tokenID);
        if (bytes(_uri).length == 0) {
            _uri = string(abi.encodePacked(
                ERC1155.uri(0),
                _tokenID.toString()
                )
            );
        }
            
    }

    /**
     * @dev See {IERC165-supportsInterface}.
     */
    function supportsInterface(bytes4 interfaceId) public view virtual override returns (bool) {
        return
            interfaceId == type(IERC1155).interfaceId ||
            interfaceId == type(IERC1155MetadataURI).interfaceId ||
            super.supportsInterface(interfaceId);
    }


    /**
     * @dev Returns true if `account` is a contract.
     *
     * [IMPORTANT]
     * ====
     * It is unsafe to assume that an address for which this function returns
     * false is an externally-owned account (EOA) and not a contract.
     *
     * Among others, `isContract` will return false for the following
     * types of addresses:
     *
     *  - an externally-owned account
     *  - a contract in construction
     *  - an address where a contract will be created
     *  - an address where a contract lived, but was destroyed
     * ====
     */
    function isContract(address account) internal view returns (bool) {
        // This method relies on extcodesize, which returns 0 for contracts in
        // construction, since the code is only stored at the end of the
        // constructor execution.

        uint256 size;
        assembly {
            size := extcodesize(account)
        }
        return size > 0;
    }
}
