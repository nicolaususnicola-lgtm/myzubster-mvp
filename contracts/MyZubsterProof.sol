// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MyZubsterProof {
    bytes32 public knowledgeHash;
    address public creator;
    uint256 public timestamp;

    constructor(bytes32 _knowledgeHash) {
        knowledgeHash = _knowledgeHash;
        creator = msg.sender;
        timestamp = block.timestamp;
    }
}
