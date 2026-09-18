// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MTRXToken {
    string public name = "MTRX Token";
    string public symbol = "MTRX";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint256 value);

    constructor() {
        totalSupply = 1000000 * 10**uint256(decimals);
        balanceOf[msg.sender] = totalSupply;
    }
}
