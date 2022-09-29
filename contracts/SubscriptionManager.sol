// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Subscription Manager Contract 

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../interfaces/ITrustedWrapper.sol";


pragma solidity 0.8.16;

contract SubscriptionManager is Ownable {
    using SafeERC20 for IERC20;
    
    struct SubscriptionType {
        uint256 timelockPeriod;    // in seconds e.g. 3600*24*30*12 = 31104000 = 1 year
        uint256 ticketValidPeriod; // in seconds e.g. 3600*24*30    =  2592000 = 1 month
        bool hasCounter;
        uint256 counter;
    }

    struct PayOption {
        address paymentToken;
        uint256 paymentAmount;
    }

    struct Tariff {
        SubscriptionType subscription;
        PayOption[] payWith;
    }

    struct Ticket {
        uint256 validUntil; // Unixdate, tickets not valid after
        uint256 countsLeft; // for tarif with fixed use counter
    }

    Tariff[] public availableTariffs;
    mapping(address => Ticket) public userTickets;

    function isValidMinter(
        address _contractAddress, 
        address _minter
    ) external view returns (bool){

    }

    function checkUserSubscription(
        address _userer, 
        uint256 _subscriptionId
    ) external view returns (bool){

    }

    function checkAndFixUserSubscription(
        address _userer, 
        uint256 _subscriptionId
    ) external returns (bool){

    }

    ////////////////////////////////////////////////////////////////
    //////////     Admins                                     //////
    ////////////////////////////////////////////////////////////////

    function addTarif(Tariff calldata _newTarif) external onlyOwner {
        require (_newTarif.payWith.length > 0, 'No payment method');
        availableTariffs.push(_newTarif);
    }

    // function editTarif(
    //     uint256 _index, 
    //     uint256 _timelockPeriod,
    //     uint256 _ticketValidPeriod,
    //     bool _hasCounter,
    //     uint256 _counter
    // ) external onlyOwner {
    //     availableTariffs[_index].paymentToken      = _paymentToken;
    //     availableTariffs[_index].paymentAmount     = _paymentAmount;
    //     availableTariffs[_index].timelockPeriod    = _timelockPeriod;
    //     availableTariffs[_index].ticketValidPeriod = _ticketValidPeriod;
    // }
   
}