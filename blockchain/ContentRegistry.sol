// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ContentRegistry
/// @notice Registers content hashes on-chain with a timestamp and registrant, 
///         acting as a simple proof-of-existence / timestamping service.
contract ContentRegistry {

    /// @dev Packed struct: one storage slot instead of two separate mappings.
    struct Record {
        uint128 timestamp;
        address registrant;
    }

    mapping(bytes32 => Record) private _records;

    /// @notice Total number of content hashes registered.
    uint256 public totalRegistered;

    event ContentRegistered(
        bytes32 indexed contentHash,
        address indexed registrant,
        uint256 timestamp
    );

    error AlreadyRegistered(bytes32 contentHash);
    error EmptyHash();

    /// @notice Registers a content hash. Reverts if it was already registered.
    /// @param contentHash The hash of the content to register (e.g. keccak256 of the file).
    function register(bytes32 contentHash) external {
        if (contentHash == bytes32(0)) revert EmptyHash();
        if (_records[contentHash].timestamp != 0) revert AlreadyRegistered(contentHash);

        _records[contentHash] = Record({
            timestamp: uint128(block.timestamp),
            registrant: msg.sender
        });

        unchecked { totalRegistered++; }

        emit ContentRegistered(contentHash, msg.sender, block.timestamp);
    }

    /// @notice Registers multiple content hashes in one transaction.
    /// @dev Skips (does not revert on) hashes that are already registered or empty,
    ///      so one bad entry in a batch doesn't block the rest.
    /// @param contentHashes Array of hashes to register.
    /// @return registeredCount Number of hashes actually newly registered.
    function registerBatch(bytes32[] calldata contentHashes)
        external
        returns (uint256 registeredCount)
    {
        uint256 len = contentHashes.length;
        for (uint256 i; i < len; ) {
            bytes32 h = contentHashes[i];
            if (h != bytes32(0) && _records[h].timestamp == 0) {
                _records[h] = Record({
                    timestamp: uint128(block.timestamp),
                    registrant: msg.sender
                });
                emit ContentRegistered(h, msg.sender, block.timestamp);
                unchecked { registeredCount++; }
            }
            unchecked { i++; }
        }
        unchecked { totalRegistered += registeredCount; }
    }

    /// @notice Checks whether a content hash has been registered.
    function verify(bytes32 contentHash) external view returns (bool) {
        return _records[contentHash].timestamp != 0;
    }

    /// @notice Returns full registration details for a content hash.
    /// @return exists Whether the hash is registered.
    /// @return timestamp Block timestamp of registration (0 if not registered).
    /// @return registrant Address that registered it (address(0) if not registered).
    function getRecord(bytes32 contentHash)
        external
        view
        returns (bool exists, uint256 timestamp, address registrant)
    {
        Record memory r = _records[contentHash];
        return (r.timestamp != 0, r.timestamp, r.registrant);
    }
}