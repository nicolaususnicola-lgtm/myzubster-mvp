"""Command-line verifier for a MyZubster Knowledge Card proof."""

import argparse
import json
import os
import sys

import requests

from src.core.knowledge_proof import DEFAULT_SEPOLIA_RPC_URL, verify_knowledge_proof


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify exact Knowledge Card payload bytes against Ethereum Sepolia.")
    parser.add_argument("payload")
    parser.add_argument("contract_address")
    parser.add_argument("--expected-hash")
    parser.add_argument("--rpc-url", default=os.environ.get("SEPOLIA_RPC_URL", DEFAULT_SEPOLIA_RPC_URL))
    args = parser.parse_args(argv)

    try:
        result = verify_knowledge_proof(
            args.payload,
            args.contract_address,
            expected_hash=args.expected_hash,
            rpc_url=args.rpc_url,
        )
    except (OSError, ValueError, requests.RequestException) as error:
        print(json.dumps({"status": "ERROR", "error": str(error)}, indent=2), file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "MATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
