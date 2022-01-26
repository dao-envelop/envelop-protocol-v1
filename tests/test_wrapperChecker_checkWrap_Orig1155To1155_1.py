import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from makeTestData import makeNFTForTest1155, makeNFTForTest1155
from web3 import Web3

ORIGINAL_NFT_IDs = [10000,11111,22222]
zero_address = '0x0000000000000000000000000000000000000000'
call_amount = 1e18
eth_amount = "1 ether"
in_type = 4
out_type = 4
in_nft_amount = 3
out_nft_amount = 5
transfer_fee_amount = 100


#checks
def test_transfer(accounts, erc1155mock, wrapper, dai, weth, wnft1155, niftsy20, whiteLists, techERC20, wrapperChecker, wnft1155_1):

    #make 1155 token for wrapping
    makeNFTForTest1155(accounts, erc1155mock, ORIGINAL_NFT_IDs, in_nft_amount)
    erc1155mock.setApprovalForAll(wrapper.address, True, {"from": accounts[1]})

    if (wrapper.lastWNFTId(out_type)[1] == 0):
        wrapper.setWNFTId(out_type, wnft1155.address, 0, {'from':accounts[0]})
    wnft1155.setMinterStatus(wrapper.address, {"from": accounts[0]})

    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)
    
    #################################
    fee = []
    lock = []
    royalty = []

    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    assert wrapperChecker.checkWrap(wNFT, [], zero_address)[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], zero_address)[1]).find("WrapperFor cant be zero,", 0)!= -1

    #################################
    wNFT = ( token_data,
        zero_address,
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
        )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("unWrapDestinition cant be zero,", 0)!= -1

    #################################
    fee = []
    lock = []
    royalty = [(accounts[3], 10000)]
    wNFT = ( token_data,
        zero_address,
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )
    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Royalty source is transferFee,", 0)!= -1

    #fee = [(Web3.toBytes(0x00), transfer_fee_amount, techERC20.address)]
    #royalty = [(wrapper.address, 10000)]
    
    #################################
    fee = []
    lock = []
    royalty = []
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        0,
        '0'
    )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("WNFT type is ERC1155 - wnft should have balance,", 0)!= -1

    #################################
    token_property = (in_type, erc1155mock)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], 0)

    fee = []
    lock = []
    royalty = []
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Original NFT type is ERC1155 - original nft should have balance,", 0)!= -1

    #################################
    token_property = (in_type, zero_address)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)

    fee = []
    lock = []
    royalty = []
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("NFT contract address cant be zero,", 0)!= -1

    #################################
    token_property = (in_type, erc1155mock.address)

    token_data = (token_property, ORIGINAL_NFT_IDs[0], in_nft_amount)

    fee = []
    lock = [('0x0', chain.time() + 100), ('0x0', chain.time() + 200)]
    royalty = []
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Several time loks,", 0)!= -1

    #################################
    lock = [('0x0', chain.time() + 100000000000000000000000000000)]
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Too long Wrap,", 0)!= -1

    #################################
    fee = []
    lock = []
    royalty = []
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0x00FF'
    )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Wrong rule code,", 0)!= -1

    #################################
    fee = [('0x00', 10, zero_address )]
    lock = []
    royalty = []
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )
    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Wrong Fee settings,", 0)!= -1

    #################################
    fee = [('0x00', 0, accounts[1] )]
    lock = []
    royalty = []
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Wrong Fee settings,", 0)!= -1

    #################################
    fee = [('0x00', 10, accounts[1] )]
    lock = []
    royalty = [(accounts[2], 10), (accounts[3], 0)]
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )
    logging.info(wrapperChecker.checkWrap(wNFT, [], accounts[3])[1])
    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Wrong royalty settings,", 0)!= -1

    #################################
    fee = [('0x00', 10, accounts[1] )]
    lock = []
    royalty = [(accounts[2], 10), (zero_address, 100)]
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )

    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Wrong royalty settings,", 0)!= -1

    #################################
    fee = [('0x00', 10, accounts[1] )]
    lock = []
    royalty = [(accounts[2], 10), (wrapper.address, 9000)]
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )
    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == True
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Success", 0)!= -1

    #################################
    fee = [('0x00', 10, accounts[1] )]
    lock = []
    royalty = [(accounts[2], 10), (accounts[3], 9000)]
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )
    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Royalty percent too big", 0)!= -1

    #################################
    fee = []
    lock = [(0x01, 1000)]
    royalty = []
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )
    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Cant set Threshold without transferFee", 0)!= -1

    #################################
    fee = [(0x00, 10, accounts[3])]
    lock = [(0x01, 100)]
    royalty = []
    wNFT = ( token_data,
        accounts[2],
        fee,
        lock,
        royalty,
        out_type,
        out_nft_amount,
        '0'
    )
    assert wrapperChecker.checkWrap(wNFT, [], accounts[3])[0] == False
    assert (wrapperChecker.checkWrap(wNFT, [], accounts[3])[1]).find("Too much threshold", 0)!= -1

    #################################