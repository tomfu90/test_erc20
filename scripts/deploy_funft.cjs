// scripts/deploy_funft.cjs
const hre = require("hardhat");

async function main() {
    const [deployer] = await hre.ethers.getSigners();
    console.log("📛 部署者(创世)地址:", deployer.address);

    const FunFT = await hre.ethers.getContractFactory("FunFT");
    const funFT = await FunFT.deploy();

    // ✅ ethers v5 写法（适用于你的环境）
    await funFT.deployed(); // ← 注意：是 deployed()，不是 waitForDeployment()

    const contractAddr = funFT.address; // ← 直接读 .address
    console.log("📜 合约部署地址:", contractAddr);

    // 铸造 NFT 并等待交易确认
    const tx = await funFT.safeMint(deployer.address, 1, "https://test/1.json");
    await tx.wait();
    console.log("✅ owner安全铸造NFT #1成功");
}

main().catch(err => {
    console.error("❌ 部署失败:", err);
    process.exitCode = 1;
});