// SPDX-License-Identifier: MIT
// Public Mintable User SBT Collection behind proxy
pragma solidity 0.8.21;


import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "../../interfaces/IWrapper.sol";


contract MockUsersSBTCollection721 is ERC721Enumerable {
    using Strings for uint256;
    using Strings for uint160;

    address  public creator;
    address  public wrapperMinter;
    string   public baseurl;
    bytes2[] public rules;

    
    // mapping from url prefix to baseUrl
    //mapping(string => string) public baseByPrefix;
    
    constructor(
    	address _creator,
        string memory name_,
        string memory symbol_,
        string memory _baseurl,
        address _wrapper
    ) 
        ERC721(name_, symbol_)
    {
        baseurl = string(
            abi.encodePacked(
                _baseurl,
                block.chainid.toString(),
                "/",
                uint160(address(this)).toHexString(),
                "/"
            )
        );
        creator = _creator;
        wrapperMinter = _wrapper;
    }

    function mintWithRules(address _to,  bytes2 _rules) external returns(uint256 tokenId) {
        require(wrapperMinter == msg.sender, "Trusted address only");
        require(
            (
                   bytes2(0x0001) == (bytes2(0x0001) & _rules) 
                || bytes2(0x0004) == (bytes2(0x0004) & _rules) 
                || bytes2(0x0000) == _rules
            ), 
            'SBT MUST Have rule'
        );
        rules.push(_rules);
        tokenId = rules.length - 1;
        _mint(_to, tokenId);
    }

    function updateRules(uint256 _tokenId, bytes2 _rules) external returns(bool changed) {
        require(wrapperMinter == msg.sender, "Trusted address only");
        require(rules[_tokenId] == bytes2(0x0000), "Only once to SBT");
        require(
            (bytes2(0x0001) == (bytes2(0x0001) & _rules ) || bytes2(0x0004) == (bytes2(0x0004) & _rules)), 
            'SBT MUST Have rule'
        );
        rules[_tokenId] = _rules;
        changed = true;
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
        _burn(tokenId);
    }

    function tokenURI(uint256 _tokenId) public view virtual override returns (string memory _uri) {
        _requireMinted(_tokenId);
        _uri = IWrapper(wrapperMinter).getOriginalURI(address(this), _tokenId);
        if (bytes(_uri).length == 0) {
            _uri = ERC721.tokenURI(_tokenId);
        }

    }

    function owner() external view returns(address){
        return creator;
    }

    function exists(uint256 _tokenId) public view returns(bool) {
        return _exists(_tokenId);
    }

    

    /**
     * @dev See {ERC721-_burn}. This override additionally checks to see if a
     * token-specific URI was set for the token, and if so, it deletes the token URI from
     * the storage mapping.
     */
    function _burn(uint256 tokenId) internal virtual override {
        super._burn(tokenId);

    }
    /////////////////////////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////////////
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
     * @dev Hook that is called before any token transfer. This includes minting and burning. If {ERC721Consecutive} is
     * used, the hook may be called as part of a consecutive (batch) mint, as indicated by `batchSize` greater than 1.
     *
     * Calling conditions:
     *
     * - When `from` and `to` are both non-zero, ``from``'s tokens will be transferred to `to`.
     * - When `from` is zero, the tokens will be minted for `to`.
     * - When `to` is zero, ``from``'s tokens will be burned.
     * - `from` and `to` are never both zero.
     * - `batchSize` is non-zero.
     *
     * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal virtual override {
        super._beforeTokenTransfer(from, to, tokenId, 1);
        bytes2 _r = rules[tokenId];
        // Check NO Burn rule
        if (to == address(0)){
            require(
                !(bytes2(0x0001) == (bytes2(0x0001) & _r)),
                "UnWrap was disabled by author"
            );
        }

        // Check NO transfer rule
        if (from != address(0) && to != address(0)){
            require(
                !(bytes2(0x0004) == (bytes2(0x0004) & _r)),
                "Trasfer was disabled by author"
            );

        }
        
    }
}