// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EphemeralC2.sol";

contract C2Factory {
    address public owner;
    address[] public allC2Contracts;

    event C2Deployed(address indexed c2Address, address indexed by);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not factory owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function deployC2(string calldata command) external onlyOwner returns (address) {
        EphemeralC2 newC2 = new EphemeralC2(command);
        allC2Contracts.push(address(newC2));
        emit C2Deployed(address(newC2), msg.sender);
        return address(newC2);
    }

    function getC2Contracts() external view returns (address[] memory) {
        return allC2Contracts;
    }
}
