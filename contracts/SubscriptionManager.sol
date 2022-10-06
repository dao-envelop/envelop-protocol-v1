// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Subscription Manager Contract 

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../interfaces/ITrustedWrapper.sol";
import "./LibEnvelopTypes.sol";


pragma solidity 0.8.16;

contract SubscriptionManagerV1 is Ownable {
    using SafeERC20 for IERC20;
    
    struct SubscriptionType {
        uint256 timelockPeriod;    // in seconds e.g. 3600*24*30*12 = 31104000 = 1 year
        uint256 ticketValidPeriod; // in seconds e.g. 3600*24*30    =  2592000 = 1 month
        uint256 counter;
        bool isAvailable;
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
        // uint256 tariffId;   // How ticket was bougth 
    }

    address public mainWrapper;
    Tariff[] public availableTariffs;
    
    // mapping from user addres to subscription type and ticket
    mapping(address => mapping(uint256 => Ticket)) public userTickets;

    // mapping from external contract address to subscription type that enabled;
    mapping(address => mapping(uint256 => bool)) public agentRegistry;

    // function isValidMinter(
    //     address _contractAddress, 
    //     address _minter
    // ) external view returns (bool){

    //}


    function buySubscription(
        uint256 _tarifIndex,
        uint256 _payWithIndex,
        address _buyFor
    ) external 
      returns(Ticket memory ticket) {
        // It is possible buy ticket for someone
        address ticketReceiver = msg.sender;
        if (_buyFor != address(0)){
           ticketReceiver = _buyFor;
        }

        require(
            availableTariffs[_tarifIndex].subscription.isAvailable,
            'This subscription not available'
        );

        require(
            availableTariffs[_tarifIndex].payWith[_payWithIndex].paymentAmount > 0,
            'This Payment option not available'
        );

        require(!_isTicketValid(ticketReceiver, _tarifIndex),'Only one valid ticket at time');

        // Lets receive payment tokens FROM sender
        IERC20(
            availableTariffs[_tarifIndex].payWith[_payWithIndex].paymentToken
        ).safeTransferFrom(
            msg.sender, 
            address(this),
            availableTariffs[_tarifIndex].payWith[_payWithIndex].paymentAmount
        );

        // Lets approve received for wrap 
        IERC20(
            availableTariffs[_tarifIndex].payWith[_payWithIndex].paymentToken
        ).safeApprove(
            mainWrapper,
            availableTariffs[_tarifIndex].payWith[_payWithIndex].paymentAmount
        );

        // Lets wrap with timelock and appropriate params
        ETypes.INData memory _inData;
        ETypes.AssetItem[] memory _collateralERC20 = new ETypes.AssetItem[](1);
        ETypes.Lock[] memory timeLock =  new ETypes.Lock[](1);
        // Only need set timelock for this wNFT
        timeLock[0] = ETypes.Lock(
            0x00, // timelock
            availableTariffs[_tarifIndex].subscription.timelockPeriod + block.timestamp
        ); 
        _inData = ETypes.INData(
            ETypes.AssetItem(
                ETypes.Asset(ETypes.AssetType.EMPTY, address(0)),
                0,0
            ),          // INAsset
            address(0), // Unwrap destinition    
            new ETypes.Fee[](0), // Fees
            //new ETypes.Lock[](0), // Locks
            timeLock,
            new ETypes.Royalty[](0), // Royalties
            ETypes.AssetType.ERC721, // Out type
            0, // Out Balance
            0x00 // Rules
        );

        _collateralERC20[0] = ETypes.AssetItem(
            ETypes.Asset(
                ETypes.AssetType.ERC20,
                availableTariffs[_tarifIndex].payWith[_payWithIndex].paymentToken
            ),
            0,
            availableTariffs[_tarifIndex].payWith[_payWithIndex].paymentAmount
        );
        
        ITrustedWrapper(mainWrapper).wrap(
            _inData,
            _collateralERC20,
            ticketReceiver
        );

        //lets safe user ticket (only one ticket available in this version)
        userTickets[ticketReceiver][_tarifIndex] = Ticket(
            availableTariffs[_tarifIndex].subscription.ticketValidPeriod + block.timestamp,
            availableTariffs[_tarifIndex].subscription.counter
        );

    }

    function checkAndFixUserSubscription(
        address _user, 
        uint256 _subscriptionId
    ) external returns (bool){
        // Check authorization of caller agent
        require(
            _agentStatus(msg.sender, _subscriptionId),
            'Subscription not available for agent'
        );

        // Check user ticket
        require(
            _isTicketValid(_user, _subscriptionId),
            'Valid ticket not found'
        );

        // Fix action (for subscription with counter)
        if (userTickets[_user][_subscriptionId].countsLeft > 0) {
            -- userTickets[_user][_subscriptionId].countsLeft; 
        }

    }

    ////////////////////////////////////////////////////////////////
    
    function checkUserSubscription(
        address _user, 
        uint256 _subscriptionId
    ) external view returns (bool) {
        return _isTicketValid(_user, _subscriptionId);
    }

    function getUserTickets(address _user) public view returns(Ticket[] memory) {
        Ticket[] memory userTicketsList = new Ticket[](availableTariffs.length);
        for (uint256 i = 0; i < availableTariffs.length; i ++ ) {
            userTicketsList[i] = userTickets[_user][i];
        }
        return userTicketsList;
    }

    function getAvailableTariffs() external view returns (Tariff[] memory) {
        return availableTariffs;
    }

    
    ////////////////////////////////////////////////////////////////
    //////////     Admins                                     //////
    ////////////////////////////////////////////////////////////////

    function setMainWrapper(address _wrapper) external onlyOwner {
        mainWrapper = _wrapper;
    }

    function addTarif(Tariff calldata _newTarif) external onlyOwner {
        require (_newTarif.payWith.length > 0, 'No payment method');
        availableTariffs.push(_newTarif);
    }

    function editTarif(
        uint256 _tarifIndex, 
        uint256 _timelockPeriod,
        uint256 _ticketValidPeriod,
        uint256 _counter,
        bool _isAvailable
    ) external onlyOwner 
    {
        availableTariffs[_tarifIndex].subscription.timelockPeriod    = _timelockPeriod;
        availableTariffs[_tarifIndex].subscription.ticketValidPeriod = _ticketValidPeriod;
        availableTariffs[_tarifIndex].subscription.counter = _counter;
        availableTariffs[_tarifIndex].subscription.isAvailable = _isAvailable;    
    }
   
    function editTarifPayOption(
        uint256 _tarifIndex,
        uint256 _payWithIndex, 
        address _paymentToken,
        uint256 _paymentAmount
    ) external onlyOwner 
    {
        availableTariffs[_tarifIndex].payWith[_payWithIndex] 
        = PayOption(_paymentToken, _paymentAmount);    
    }

    function setAgentStatus(address _agent, uint256 _subscriptionType, bool _status)
        external onlyOwner 
    {
        agentRegistry[_agent][_subscriptionType] = _status;
    }
    /////////////////////////////////////////////////////////////////////

    function _isTicketValid(address _user, uint256 _tarifIndex) 
        internal 
        view 
        returns (bool) 
    {
        return userTickets[_user][_tarifIndex].validUntil > block.timestamp 
            || userTickets[_user][_tarifIndex].validUntil > 0;
    }

    function _getUserTicket(address _user, uint256 _tarifIndex) 
        internal 
        view 
        returns (Ticket memory) 
    {
        return userTickets[_user][_tarifIndex];
    }

    function _agentStatus(address _agent, uint256 _subscriptionType) 
        internal 
        returns(bool)
    {
        return agentRegistry[_agent][_subscriptionType];
    } 

}