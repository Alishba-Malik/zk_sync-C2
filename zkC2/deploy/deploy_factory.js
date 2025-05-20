/*require("dotenv").config();
const { Wallet, Provider, ContractFactory } = require("zksync-web3");
const hre = require("hardhat"); // Required to use hre.artifacts

async function main() {
  const zkProvider = new Provider("http://localhost:3050");
  const deployerPK = process.env.DEPLOYER_PRIVATE_KEY;
  if (!deployerPK) {
    console.error("DEPLOYER_PRIVATE_KEY not set in .env");
    process.exit(1);
  }
  const deployer = new Wallet(deployerPK, zkProvider);

  console.log("🔧 Deploying C2Factory...");

  const artifact = await hre.artifacts.readArtifact("C2Factory");

  // Just pass the bytecode as-is; don't manually convert to buffer
  const factory = new ContractFactory(artifact.abi, artifact.bytecode, deployer);

  const contract = await factory.deploy();
  await contract.deployed();

  console.log("C2Factory deployed at:", contract.address);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
*/
require("dotenv").config();
const { Wallet, Provider, ContractFactory } = require("zksync-web3");
const hre = require("hardhat");

async function main() {
  const provider = new Provider("http://localhost:3050");

  const privateKey = process.env.DEPLOYER_PRIVATE_KEY;
  if (!privateKey) {
    throw new Error("Missing DEPLOYER_PRIVATE_KEY in .env");
  }

  const wallet = new Wallet(privateKey, provider);
  console.log("🔧 Deploying C2Factory from:", wallet.address);

  // Load the compiled artifact
  const artifact = await hre.artifacts.readArtifact("C2Factory");

  // Use ContractFactory from zksync-web3, NOT ethers
  const factory = new ContractFactory(artifact.abi, artifact.bytecode, wallet);

  // Deploy the contract
  const contract = await factory.deploy(); 
  await contract.deployed();

  console.log(" C2Factory deployed at:", contract.address);
}

main().catch((err) => {
  console.error("Deployment failed:", err);
  process.exit(1);
});




