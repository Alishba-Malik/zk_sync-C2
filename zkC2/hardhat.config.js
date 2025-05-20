require("dotenv").config();
require("@matterlabs/hardhat-zksync-deploy");
require("@matterlabs/hardhat-zksync-solc");

module.exports = {
  zksolc: {
    version: "1.5.12",
    compilerSource: "binary",
    settings: {
      codegen: "evmla",
      optimizer: {
        enabled: true,
      },
    },
  },
  defaultNetwork: "zkLocal",
  networks: {
    zkLocal: {
      url: "http://localhost:3050",
      ethNetwork: "http://localhost:8545", // Needed if bridging or using L1
      zksync: true,                        // REQUIRED for zkSync compatibility
    },
  },
  solidity: {
    version: "0.8.20",
  },
};
