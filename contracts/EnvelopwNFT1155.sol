// SPDX-License-Identifier: MIT
// ENVELOP protocol for NFT
pragma solidity 0.8.11;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Supply.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/IERC1155MetadataURI.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "../interfaces/IWrapper.sol";

contract EnvelopwNFT1155 is ERC1155Supply, Ownable {
    using Strings for uint256;
    using Strings for uint160;
    
    address public wrapper;       // main protocol contarct
    
    constructor(
        string memory name_,
        string memory symbol_,
        string memory _baseurl
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

    function setMinterStatus(address _minter) external onlyOwner {
        wrapper = _minter;
        //tokenService = IWrapper(wrapper).tokenService();
        // TODO  renownce ownership
    }

    function _beforeTokenTransfer(
        address operator,
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) internal  override {
        super._beforeTokenTransfer(operator, from, to, ids, amounts, data);
        for (uint256 i = 0; i < ids.length; ++i) {
            ETypes.WNFT memory _wnft = IWrapper(wrapper).getWrappedToken(
                address(this),ids[i]
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
                    IWrapper(wrapper).chargeFees(address(this), ids[i], from, to, 0x00);    
                }
            }
        }
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
}
