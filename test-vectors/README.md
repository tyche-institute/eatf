# test-vectors/ — conformance test vectors

Two sibling subdirectories:

- `valid/` — packages that MUST verify cleanly. Every implementation
  claiming v0.1 conformance must report `verify=true` for every
  package under this tree.
- `invalid/` — packages that MUST fail verification. Each subdirectory
  exercises one specific failure mode and ships a `verify-expected.txt`
  naming the diagnostic the verifier should report.

## Vector layout

```
<vector-name>/
├── package.aep
├── verify-expected.txt     # the verify=true/false contract
└── README.md               # what this vector exercises
```

## v0.1 vectors

| Vector                                             | Expected             | Exercises                                                                    |
|----------------------------------------------------|----------------------|------------------------------------------------------------------------------|
| `valid/valid-overt-profile/`                       | `verify=true`        | Full happy-path. OVERT foundational scope.                                   |
| `valid/mcp-tools-call-valid/`                      | `verify=true`        | OVERT `agentic-extended:mcp-tools-call`, policy decision `allow`.            |
| `valid/mcp-tools-call-denied-policy/`              | `verify=true`        | Same scope, policy decision `deny` — AEP authentic; call rejected by policy. |
| `invalid/tampered-overt-receipt/`                  | `verify=false`       | Hash-chain mismatch on `overt_receipt.json` (post-sign tamper).              |

## Running conformance

```bash
cd lib && npm install && npm run build && cd ..
cd cli/eatf-verify && npm install && cd ../..

node cli/eatf-verify/bin/eatf-verify.js --conformance test-vectors/
```

Expected output:
```
PASS  package.aep  expected=true   actual=true
PASS  package.aep  expected=true   actual=true
PASS  package.aep  expected=true   actual=true
PASS  package.aep  expected=false  actual=false

Conformance: 3 verified, 1 rejected, 0 contract mismatches.
```

Implementations claiming v0.1 conformance run their own verifier
against every `valid/<vector>/package.aep` and every
`invalid/<vector>/package.aep` and report `PASS` (verify equals
expected) for every vector.

More vectors will be added in successive 0.1.x point releases.
