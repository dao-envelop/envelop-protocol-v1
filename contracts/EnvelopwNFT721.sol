// SPDX-License-Identifier: MIT
// ENVELOP protocol for NFT
pragma solidity 0.8.11;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "../interfaces/IWrapper.sol";

//v0.0.1
contract EnvelopwNFT721 is ERC721Enumerable, Ownable {
    using Strings for uint256;
    using Strings for uint160;
    
    address public wrapperMinter;
    string  public baseurl;
    
    constructor(
        string memory name_,
        string memory symbol_,
        string memory _baseurl
    ) 
        ERC721(name_, symbol_)  
    {
        wrapperMinter = msg.sender;
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

    function setMinter(address _minter) external onlyOwner {
        wrapperMinter = _minter;
    }

    /**
     * @dev See {ERC721-_beforeTokenTransfer}.
     *
     * Requirements:
     *
     * - the contract must not be paused.
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId
    ) internal virtual override {
        super._beforeTokenTransfer(from, to, tokenId);

        ETypes.WNFT memory _wnft = IWrapper(wrapperMinter).getWrappedToken(
                address(this),tokenId
            );
            if (
                  (from == address(0) || to == address(0)) // mint & burn 
               || (from == address(this) || to == address(this)) //  wrap & unwrap
            )  
            {
                // In case Minting *new* wNFT (during new wrap)
                // In case Burn wNFT (during Unwrap) 
                // In case transfer *original* NFT from *this* contract  during UNWrap
                // In case transfer *original* wNFT to *this* contract during double Wrap  
                //                THERE IS NO RULE CHECKs

            } else {
                // Check Core Protocol Rules
                require(
                    !(bytes2(0x0004) == (bytes2(0x0004) & _wnft.rules)),
                    "Trasfer was disabled by author"
                );

                // Check and charge Transfer Fee and pay Royalties
                if (_wnft.fees.length > 0) {
                    IWrapper(wrapperMinter).chargeFees(address(this), tokenId, from, to, 0x00);    
                }
                

            }
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

    /**
     * @dev See {IERC165-supportsInterface}.
     */
    function supportsInterface(bytes4 interfaceId) public view virtual override returns (bool) {
        return
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC721Enumerable).interfaceId ||
            super.supportsInterface(interfaceId);
    }

    
}
