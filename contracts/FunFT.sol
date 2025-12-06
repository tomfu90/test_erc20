// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol"; // ← 新增这一行
import "@openzeppelin/contracts/access/Ownable.sol";

// 在 is 后面加上 ERC721Burnable
contract FunFT is ERC721, ERC721Burnable, Ownable {
    mapping(uint256 => string) private _tokenURIs;

    constructor() ERC721("FunFT", "FUN") Ownable(msg.sender) {}

    function mint(address to, uint256 tokenId, string memory uri) public onlyOwner {
        _mint(to, tokenId);
        _setTokenURI(tokenId, uri);
    }

    function safeMint(address to, uint256 tokenId, string memory uri) public onlyOwner {
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
    }

    function meta(uint256 tokenId) public view returns (string memory) {
        ownerOf(tokenId); // 保留原逻辑（会 revert 如果 token 不存在）
        return _tokenURIs[tokenId];
    }

    function _setTokenURI(uint256 tokenId, string memory uri) internal {
        ownerOf(tokenId); // 保留原逻辑
        _tokenURIs[tokenId] = uri;
    }
}