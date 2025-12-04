const { ethers } = require("hardhat");

async function main() {
  const MyUSDT = await ethers.getContractFactory("MyUSDT"); // ✅ 改为 MyUSDT
  const token = await MyUSDT.deploy();
  await token.deployed();
  console.log("✅ MyUSDT deployed to:", token.address);
}

main().catch(console.error);
