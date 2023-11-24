// SPDX-License-Identifier: MIT
// Event Manager with Full Ticket's life cycle
pragma solidity 0.8.21;
    
    import "./MockUsersSBTCollectionPRegistry.sol";

contract MockEventManager is MockUsersSBTCollectionPRegistry {

    struct Period {
        uint256 start;
        uint256 finish;
    }

    struct EventDates {
        Period useTicket;
        Period certificate;
        bytes2 sbtRules;
    }

    // from ticket contracts to event contract (wNFT-SBT)
    // it possible to use one ticket's contract for different events
    mapping(address => address[]) public ticketsForEvents;

    // from event contract (wNFT-SBT) to dates
    mapping(address => EventDates) public events;
    
    /// This error occur when somebody try edit contract
    /// that was created by (for) another user
    error Unauthorized(address User, address Contract);

    function deployNewCollection(
        address _implAddress, 
        address _creator,
        string memory name_,
        string memory symbol_,
        string memory _baseurl,
        address _wrapper,
        address _ticketContract,
        EventDates calldata _eventDates
    ) public  returns (address newCollection)
    {
        // TODO   some  checks
        // First create event contract as simple proxy
        newCollection = deployNewCollection(
            _implAddress, 
            _creator,
            name_,
            symbol_,
            _baseurl,
            _wrapper
        );

        // Save event info
        ticketsForEvents[_ticketContract].push(newCollection);
        events[newCollection] = _eventDates;
    }

    function editDatesForEvent(address _eventContract, EventDates calldata _newEventDates)
        external
    {
        // Only event creator can edit dates
        Asset[] memory e = collectionRegistry[msg.sender];
        for (uint256 i = 0; i < e.length; i ++) {
            if (e[i].contractAddress == _eventContract) {
                events[_eventContract] =  _newEventDates;
                return;
            }
        }
        revert Unauthorized(msg.sender, _eventContract);
        
    }

    function getEventsForTicket(address _ticketContract) 
        external
        view 
        returns(address[] memory e, EventDates[] memory d)
    {
        e = ticketsForEvents[_ticketContract];
        d = new EventDates[](e.length);
        for (uint256 i = 0; i < e.length; i ++) {
            d[i] = events[e[i]];
        }

    }

    function getDataForEvent(address _eventContract)
        external
        view
        returns(EventDates memory d)
    {
        d = events[_eventContract];
    }

    function isWrapEnabled(
        address _ticketContract, 
        address _eventContract
    )
         external 
         view 
         returns(bool enabled) 
    {
        address[] memory e = ticketsForEvents[_ticketContract];
        for (uint256 i = 0; i < e.length; i ++) {
            if (e[i] == _eventContract) {
                if (events[_eventContract].useTicket.start <= block.timestamp && 
                    events[_eventContract].useTicket.finish > block.timestamp)
                {
                    enabled = true;
                }
            } 
        }
    }

    function isRulesUpdateEnabled(
        address _eventContract
    )
         external 
         view 
         returns(bytes2 rules) 
    {
        if (events[_eventContract].certificate.start <= block.timestamp && 
            events[_eventContract].certificate.finish > block.timestamp)
        {
            rules = events[_eventContract].sbtRules;
        }

    }

}
    
