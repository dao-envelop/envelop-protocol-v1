// SPDX-License-Identifier: MIT
// Public Mintable User SBT Collection behind proxy
pragma solidity 0.8.21;


import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Supply.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/IERC1155MetadataURI.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "../../interfaces/IWrapper.sol";


contract MockUsersCollection1155 is ERC1155Supply {
    using Strings for uint256;
    using Strings for uint160;

    address public creator;
    string public  name;
    string public  symbol;
    //address public subscriptionManager;
    //string private _baseDefaultURI;
    address public wrapperMinter;
    bytes2[] public rules;
    

    constructor(
        address _creator,
        string memory name_,
        string memory symbol_,
        string memory _baseurl,
        address _wrapper
    ) ERC1155(_baseurl)
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
        creator = _creator;
        wrapperMinter = _wrapper;
    }

    ///////////////////////////////////////////////////////////////////////////
    ////  Section below is OppenZeppelin ERC1155Supply inmplementation     ////
    ///////////////////////////////////////////////////////////////////////////
    mapping(uint256 => uint256) private _totalSupply;

    /**
     * @dev Total amount of tokens in with a given id.
     */
    function totalSupply(uint256 id) public view virtual override returns (uint256) {
        return _totalSupply[id];
    }

    /**
     * @dev Indicates whether any token exist with a given id, or not.
     */
    function exists(uint256 id) public view virtual override returns (bool) {
        return totalSupply(id) > 0;
    }


    ///////////////////////////////////////////////////////////////////////////

    function mintWithRules(address _to,  uint256 _balance, bytes2 _rules) external returns(uint256 tokenId) {
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
        _mint(_to, tokenId, _balance, "");
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

    function burn(address _from, uint256 _tokenId, uint256 _amount) public virtual {
        require(wrapperMinter == msg.sender, "Trusted address only");
        // Think about check totaLsUPPLY
        _burn(_from, _tokenId, _amount);
    }

    ////////////////////////////////////////////////////////////

    function uri(uint256 _tokenId) public view override 
        returns (string memory _uri) 
    {
        _uri = IWrapper(wrapperMinter).getOriginalURI(address(this), _tokenId);
        if (bytes(_uri).length == 0) {
            _uri = string(abi.encodePacked(
                ERC1155.uri(0),
                _tokenId.toString()
            ));
        }    
    }

    function owner() external view returns(address){
        return creator;
    }

    function wnftInfo(uint256 tokenId) external view returns (ETypes.WNFT memory) {
        return IWrapper(wrapperMinter).getWrappedToken(address(this), tokenId);
    }


    //////////////////////////////
    //  Admin functions        ///
    //////////////////////////////
    function setBaseURI(string memory _newBaseURI) external{
        require(msg.sender == creator, "Only for creator");
        _setURI(_newBaseURI);
    }
    ///////////////////////////////
    /**
     * @dev Hook that is called before any token transfer. This includes minting
     * and burning, as well as batched variants.
     *
     * The same hook is called on both single and batched variants. For single
     * transfers, the length of the `ids` and `amounts` arrays will be 1.
     *
     * Calling conditions (for each `id` and `amount` pair):
     *
     * - When `from` and `to` are both non-zero, `amount` of ``from``'s tokens
     * of token type `id` will be  transferred to `to`.
     * - When `from` is zero, `amount` tokens of token type `id` will be minted
     * for `to`.
     * - when `to` is zero, `amount` of ``from``'s tokens of token type `id`
     * will be burned.
     * - `from` and `to` are never both zero.
     * - `ids` and `amounts` have the same, non-zero length.
     *
     * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
     */
    function _beforeTokenTransfer(
        address operator,
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) internal virtual override {
        bytes2 _r = rules[ids[0]];

        // Check NO transfer rule
        if (from != address(0) && to != address(0)){
            require(
                !(bytes2(0x0004) == (bytes2(0x0004) & _r)),
                "Transfer was disabled by author"
            );

        }
        
        if (from == address(0)) {
            for (uint256 i = 0; i < ids.length; ++i) {
                _totalSupply[ids[i]] += amounts[i];
            }
        }

        // Burn case
        if (to == address(0)) {
            // Check NO Burn rule
            require(
                !(bytes2(0x0001) == (bytes2(0x0001) & _r)),
                "UnWrap was disabled by author"
            );
            // from  ERC1155SupplyUpgradeable
            for (uint256 i = 0; i < ids.length; ++i) {
                uint256 id = ids[i];
                uint256 amount = amounts[i];
                uint256 supply = _totalSupply[id];
                require(supply >= amount, "ERC1155: burn amount exceeds totalSupply");
                unchecked {
                    _totalSupply[id] = supply - amount;
                }
            }
        }

    }
}