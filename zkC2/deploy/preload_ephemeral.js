require("dotenv").config();
const { Wallet, Provider, ContractFactory } = require("zksync-web3");
const hre = require("hardhat");
const path = require("path"); // Import the 'path' module

async function main() {
  const provider = new Provider("http://localhost:3050");
  const privateKey = process.env.DEPLOYER_PRIVATE_KEY;

  if (!privateKey) {
    throw new Error("Missing DEPLOYER_PRIVATE_KEY in .env");
  }

  const wallet = new Wallet(privateKey, provider);
  console.log("Deploying EphemeralC2 directly from:", wallet.address);

  // Correct path to the artifact
  const artifactPath = path.join(__dirname, '..', 'artifacts-zk', 'contracts', 'EphemeralC2.sol', 'EphemeralC2.json');
  console.log("Attempting to read artifact from:", artifactPath); // Added logging
  const artifact = require(artifactPath); // Use require for direct path

  // Alternative using hre.artifacts.readArtifact (if Hardhat is configured to find zk-artifacts)
  // const artifact = await hre.artifacts.readArtifact("EphemeralC2");


  // Use ContractFactory from zksync-web3
  const factory = new ContractFactory(artifact.abi, artifact.bytecode, wallet);

  // Deploy the contract with a dummy command (it doesn't matter, we just need to publish its bytecode)
  console.log("Deploying a dummy EphemeralC2 instance to publish its code hash...");
  const dummyCommand = "dummy_init"; // A placeholder command
  const contract = await factory.deploy(dummyCommand);

  // Wait for the deployment to complete
  await contract.deployed();

  console.log("EphemeralC2 (dummy) deployed at:", contract.address);
  console.log("The bytecode hash for EphemeralC2 is now known to the network.");
}

main().catch((err) => {
  console.error("EphemeralC2 direct deployment failed:", err);
  process.exit(1);
});