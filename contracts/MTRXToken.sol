// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Sovereign Matrix Token (MTRX)
 * @notice Native ERC-20 token contract for on-chain Structor reward distribution.
 */
contract MTRXToken {
    string public name = "Sovereign Matrix";
    string public symbol = "MTRX";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    address public oracleNode;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event RewardsClaimed(address indexed miner, uint256 amount, bytes32 indexed proofHash);

    modifier onlyOracle() {
        require(msg.sender == oracleNode, "Unauthorized: Only Sovereign Node can issue mints");
        _;
    }

    constructor() {
        oracleNode = msg.sender;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function claimRewards(address miner, uint256 amount, bytes32 proofHash) external onlyOracle {
        uint256 weiAmount = amount * 10**18;
        totalSupply += weiAmount;
        balanceOf[miner] += weiAmount;
        emit RewardsClaimed(miner, weiAmount, proofHash);
        emit Transfer(address(0), miner, weiAmount);
    }
}
