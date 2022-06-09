import pytest
#from brownie import chain

############ Mocks ########################
@pytest.fixture(scope="module")
def dai(accounts, TokenMock):
    dai = accounts[0].deploy(TokenMock,"DAI MOCK Token", "DAI")
    yield dai

@pytest.fixture(scope="module")
def weth(accounts, TokenMock):
    weth = accounts[0].deploy(TokenMock,"WETH MOCK Token", "WETH")
    yield weth

# @pytest.fixture(scope="module")
# def pft(accounts, TokenMock):
#     pft = accounts[0].deploy(TokenMock,"PF MOCK Token", "PFT")
#     yield pft

@pytest.fixture(scope="module")
def erc721mock(accounts, Token721Mock):
    """
    NFT 721 with URI
    """
    t = accounts[0].deploy(Token721Mock, "Simple NFT with URI", "XXX")
    t.setURI(0, 'https://maxsiz.github.io/')
    yield t  

@pytest.fixture(scope="module")
def erc721mock1(accounts, Token721Mock):
    """
    NFT 721 with URI
    """
    t = accounts[0].deploy(Token721Mock, "Simple NFT with URI1", "XXX1")
    t.setURI(0, 'https://maxsiz.github.io/1/')
    yield t  

@pytest.fixture(scope="module")
def erc1155mock(accounts, Token1155Mock):
    """
    NFT 1155 with URI
    """
    t = accounts[0].deploy(Token1155Mock, "https://maxsiz.github.io/")
    yield t  

@pytest.fixture(scope="module")
def erc1155mock1(accounts, Token1155Mock):
    """
    NFT 1155 with URI
    """
    t = accounts[0].deploy(Token1155Mock, "https://maxsiz.github.io/1/")
    yield t  

# @pytest.fixture(scope="module")
# def fakeERC721mock(accounts, Token721Mock):
#     """
#     Simple NFT with URI
#     """
#     b = accounts[0].deploy(Token721Mock, "Fake NFT with URI", "FXX")
#     #t.setURI(0, 'https://maxsiz.github.io/')
#     yield b
# ############################################

@pytest.fixture(scope="module")
def techERC20(accounts, TechTokenV1):
    erc20 = accounts[0].deploy(TechTokenV1)
    yield erc20 

# @pytest.fixture(scope="module")
# def tokenService(accounts, TokenService):
#     t = accounts[0].deploy(TokenService)
#     yield t


@pytest.fixture(scope="module")
def wrapperRent(accounts, WrapperForRent, techERC20):
    t = accounts[0].deploy(WrapperForRent, techERC20.address)
    #t.setTokenService(tokenService.address, {'from':accounts[0]})
    yield t

@pytest.fixture(scope="module")
def wrapperRemove(accounts, WrapperRemovable, techERC20):
    t = accounts[0].deploy(WrapperRemovable, techERC20.address )
    #t.setTokenService(tokenService.address, {'from':accounts[0]})
    yield t

@pytest.fixture(scope="module")
def wrapperChecker(accounts, WrapperChecker, wrapper):
    t = accounts[0].deploy(WrapperChecker, wrapper.address)
    yield t   

@pytest.fixture(scope="module")
def wrapper(accounts, WrapperBaseV1, techERC20):
    t = accounts[0].deploy(WrapperBaseV1, techERC20.address)
    #t.setTokenService(tokenService.address, {'from':accounts[0]})
    yield t 

@pytest.fixture(scope="module")
def wnft721(accounts, EnvelopwNFT721):
    wnft = accounts[0].deploy(EnvelopwNFT721,"Envelop wNFT", "eNFT", "https://api.envelop.is/metadata/" )
    yield wnft

@pytest.fixture(scope="module")
def wnft1155(accounts, EnvelopwNFT1155):
    wnft = accounts[0].deploy(EnvelopwNFT1155,"Envelop wNFT", "eNFT", "https://api.envelop.is/metadata/")
    yield wnft

@pytest.fixture(scope="module")
def wnft1155_1(accounts, EnvelopwNFT1155):
    wnft = accounts[0].deploy(EnvelopwNFT1155,"Envelop wNFT_1", "eNFT1", "https://api.envelop.is/metadata/")
    yield wnft

@pytest.fixture(scope="module")
def niftsy20(accounts, Niftsy):
    erc20 = accounts[0].deploy(Niftsy, accounts[0])
    yield erc20 

@pytest.fixture(scope="module")
def niftsy201(accounts, Niftsy):
    erc20 = accounts[0].deploy(Niftsy, accounts[0])
    yield erc20 

@pytest.fixture(scope="module")
def whiteLists(accounts, AdvancedWhiteList):
    wl = accounts[0].deploy(AdvancedWhiteList)
    yield wl 

@pytest.fixture(scope="module")
def trFeeModel(accounts, FeeRoyaltyModelV1_00):
    tr = accounts[0].deploy(FeeRoyaltyModelV1_00)
    yield tr 

    

# @pytest.fixture(scope="module")
# def wrapper(accounts, WrapperWithERC20Collateral, techERC20, dai, weth):
#     t = accounts[0].deploy(WrapperWithERC20Collateral, techERC20.address)
#     #niftsy20.addMinter(t.address, {'from':accounts[0]})
#     t.setCollateralStatus(dai.address, True)
#     t.setCollateralStatus(weth.address, True)
#     techERC20.addMinter(t.address, {'from': accounts[0]})
#     yield t 

#@pytest.fixture(scope="module")
#def trmodel(accounts, TransferRoyaltyModel01, wrapper, niftsy20):
#    t = accounts[0].deploy(TransferRoyaltyModel01, wrapper.address)
#    wrapper.editPartnersItem(niftsy20.address, True, t.address, False,{'from': accounts[0]})
#    yield t 



@pytest.fixture(scope="module")
def mockHacker(accounts, MaliciousTokenMock):
    h = accounts[0].deploy(MaliciousTokenMock,"Hacker Malicious Token", "KLR")
    yield h

@pytest.fixture(scope="module")
def mockHacker20_1(accounts, MaliciousMockERC20_1):
    h = accounts[0].deploy(MaliciousMockERC20_1,"Hacker Malicious Token", "KLR")
    yield h

@pytest.fixture(scope="module")
def mockHacker721_1(accounts, MaliciousMockERC721_1):
    h = accounts[0].deploy(MaliciousMockERC721_1,"Hacker Maliciuos Token 721_1", "KLR721_1")
    yield h

@pytest.fixture(scope="module")
def mockHacker1155_1(accounts, MaliciousMockERC1155_1):
    h = accounts[0].deploy(MaliciousMockERC1155_1,"https://github.com/")
    yield h

###################################################################
@pytest.fixture(scope="module")
def keeper(accounts, WNFTKeeper):
    k = accounts[0].deploy(WNFTKeeper)
    yield k

@pytest.fixture(scope="module")
def spawner721(accounts, Spawner721):
    s = accounts[0].deploy(Spawner721,"Envelop NFT Spawner", "sNFT", "https://api.envelop.is/metadata/" )
    yield s

@pytest.fixture(scope="module")
def spawner721mock(accounts, Spawner721Mock):
    s = accounts[0].deploy(Spawner721Mock,"Envelop NFT Spawner Mock", "sNFT", "https://api.envelop.is/metadata/" )
    yield s

@pytest.fixture(scope="module")
def techERC20ForWrapperRemovable(accounts, TechTokenV1):
    erc20 = accounts[0].deploy(TechTokenV1)
    yield erc20 

@pytest.fixture(scope="module")
def wrapperRemovable(accounts, TrustedWrapperRemovable, techERC20ForWrapperRemovable):
    t = accounts[0].deploy(TrustedWrapperRemovable, techERC20ForWrapperRemovable.address)
    #t.setTokenService(tokenService.address, {'from':accounts[0]})
    yield t 

