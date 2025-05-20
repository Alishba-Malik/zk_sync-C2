zk_sync-c2/
├── contracts/
│   ├── C2Factory.sol         # Deploys ephemeral C2 contracts
│   ├── EphemeralC2.sol       # Simple C2 contract (per-client or short-lived)
├── bot/
│   ├── agent.py              # Python bot (infected client)
│   └── utils.py              # Wallet creation, encryption, interaction helpers
├── deploy/
│   ├── deploy_factory.js     # Deploy factory contract
│   └── deploy_c2.js          # Deploy ephemeral C2 via factory
├── scripts/
│   ├── send_command.js       # Sends command to C2
│   └── get_output.js         # (Optional) get data from C2
├── .env                      # Secrets for deployer wallet
├── hardhat.config.js         # Hardhat setup
└── README.md
