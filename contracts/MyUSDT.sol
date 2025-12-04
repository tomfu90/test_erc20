// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyUSDT is ERC20 {
    constructor() ERC20("MyUSDT", "USDT") {
        _mint(msg.sender, 1000000 * 10 ** 6); // 1,000,000 USDT，6 位小数
    }

    // 可选：显式覆盖 decimals()，虽然 ERC20 已支持
    function decimals() public view virtual override returns (uint8) {
        return 6;
    }
}
