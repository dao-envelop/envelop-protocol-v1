// SPDX-License-Identifier: MIT
// ENVELOP protocol for NFT
pragma solidity 0.8.16;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "../interfaces/IWrapper.sol";

contract EnvelopwNFT721Trustless is ERC721Enumerable {
    using Strings for uint256;
    using Strings for uint160;
    
    address public wrapperMinter;
    string  public baseurl;
    
    constructor(
        string memory name_,
        string memory symbol_,
        string memory _baseurl,
        address _wrapper
    ) 
        ERC721(name_, symbol_)  
    {
        wrapperMinter = _wrapper;
        baseurl = string(
            abi.encodePacked(
                _baseurl,
                block.chainid.toString(),
                "/",
                uint160(address(this)).toHexString(),
                "/"
            )
        );

    }

    function mint(address _to, uint256 _tokenId) external {
        require(wrapperMinter == msg.sender, "Trusted address only");
        _mint(_to, _tokenId);
    }

    /**
     * @dev Burns `tokenId`. See {ERC721-_burn}.
     *
     * Requirements:
     *
     * - The caller must own `tokenId` or be an approved operator.
     */
    function burn(uint256 tokenId) public virtual {
        //solhint-disable-next-line max-line-length
        require(wrapperMinter == msg.sender, "Trusted address only");
        //require(_isApprovedOrOwner(_msgSender(), tokenId), "ERC721Burnable: caller is not owner nor approved");
        _burn(tokenId);
    }

    

    function wnftInfo(uint256 tokenId) external view returns (ETypes.WNFT memory) {
        return IWrapper(wrapperMinter).getWrappedToken(address(this), tokenId);
    }
    
    
    function baseURI() external view  returns (string memory) {
        return _baseURI();
    }

    function _baseURI() internal view  override returns (string memory) {
        return baseurl;
    }

    /**
     * @dev Function returns tokenURI of **underline original token** 
     *
     * @param _tokenId id of protocol token (new wrapped token)
     */
    function tokenURI(uint256 _tokenId) public view override returns (string memory _uri) {
        _uri = IWrapper(wrapperMinter).getOriginalURI(address(this), _tokenId);
        if (bytes(_uri).length == 0) {
            _uri = ERC721.tokenURI(_tokenId);
        }
        return _uri;
    }

    function exists(uint256 _tokenId) public view returns(bool) {
        return _exists(_tokenId);
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
