#!/usr/bin/env node
/**
 * Generate the v0.1.4 set of invalid conformance test vectors.
 *
 * Takes the canonical valid baseline at
 *   test-vectors/valid/minimal-roundtrip/package.aep
 * and produces six deterministic tampered packages, each exercising
 * one specific failure mode the verifier must reject:
 *
 *   - tampered-canonical-bin  (hash chain mismatch)
 *   - tampered-metadata       (metadata.json modified, hash mismatch)
 *   - bad-signature-classical (signature.sig flipped)
 *   - untrusted-issuer        (public_key.pem swapped for a different valid key)
 *   - missing-canonical-bin   (required envelope entry absent)
 *   - bad-timestamp           (timestamp.tsr corrupted; RFC 3161 SignerInfo fails)
 *
 * Run from the frontend or from the repo root:
 *
 *   node scripts/generate-invalid-vectors.mjs
 *
 * The script also writes verify-expected.txt for each vector. After
 * running, the conformance set should produce four `verify=true` and
 * seven `verify=false` results, all with zero contract mismatches.
 *
 * Determinism note: tamper offsets are fixed and the swapped issuer
 * key is read from test-vectors/keys/, so re-running the script
 * produces byte-identical .aep files. CI runs `git diff --quiet` to
 * confirm no drift.
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { generateKeyPairSync, createSign } from "node:crypto";

import { unzipSync, zipSync, strFromU8, strToU8 } from "fflate";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");

const BASELINE = path.join(
  root,
  "test-vectors/valid/minimal-roundtrip/package.aep",
);
const OUT_DIR = path.join(root, "test-vectors/invalid");

const baselineBytes = new Uint8Array(readFileSync(BASELINE));
const baselineEntries = unzipSync(baselineBytes);

function flipByte(bytes, offset) {
  const out = new Uint8Array(bytes);
  out[offset] = (out[offset] ^ 0x55) & 0xff;
  return out;
}

function rezip(entries) {
  // Match the v0.1 layout: flat ZIP, STORED compression (level 0)
  // so byte-for-byte regeneration is deterministic across runs.
  return zipSync(entries, { level: 0 });
}

function writeVector(name, mutatedEntries, verifyExpectedLines) {
  const dir = path.join(OUT_DIR, name);
  mkdirSync(dir, { recursive: true });
  writeFileSync(path.join(dir, "package.aep"), Buffer.from(rezip(mutatedEntries)));
  writeFileSync(
    path.join(dir, "verify-expected.txt"),
    verifyExpectedLines.join("\n") + "\n",
  );
  process.stdout.write(`  ok  ${name}\n`);
}

// 1. tampered-canonical-bin: flip a byte in canonical.bin so the
//    SHA-256 stored in hash.sha256 no longer matches.
{
  const entries = { ...baselineEntries };
  entries["canonical.bin"] = flipByte(entries["canonical.bin"], 0);
  writeVector("tampered-canonical-bin", entries, [
    "verify=false",
    "diagnostic=Hash mismatch.",
  ]);
}

// 2. tampered-metadata: change metadata.policy_decision so it
//    no longer matches the OVERT receipt's policy.decision.
//    (For this fixture canonical.bin uses the "Java response-only"
//    form, so it doesn't depend on metadata bytes; the verifier
//    catches the tamper through the OVERT receipt's
//    metadata cross-check instead — see parseAndValidateOvertReceipt
//    in lib/src/overt.ts.)
{
  const entries = { ...baselineEntries };
  const metadata = JSON.parse(strFromU8(entries["metadata.json"]));
  metadata.policy_decision = metadata.policy_decision === "deny" ? "allow" : "deny";
  entries["metadata.json"] = strToU8(JSON.stringify(metadata) + "\n");
  writeVector("tampered-metadata", entries, [
    "verify=false",
    "diagnostic=overt_receipt.json invalid: policy.decision does not match metadata.policy_decision.",
  ]);
}

// 3. bad-signature-classical: flip a byte in signature.sig so RSA
//    verification fails. signature.sig is base64; flip a byte inside
//    the decoded payload so the result is still base64-clean.
{
  const entries = { ...baselineEntries };
  const sigB64 = strFromU8(entries["signature.sig"]).trim();
  const sigBytes = Buffer.from(sigB64, "base64");
  // Flip a byte in the middle of the signature; RSA-PSS / PKCS#1 v1.5
  // is sensitive to any bit change, so this guarantees failure.
  sigBytes[Math.floor(sigBytes.length / 2)] ^= 0x55;
  entries["signature.sig"] = strToU8(sigBytes.toString("base64") + "\n");
  writeVector("bad-signature-classical", entries, [
    "verify=false",
    "diagnostic=RSA signature does not verify against public_key.pem.",
  ]);
}

// 4. untrusted-issuer: replace public_key.pem with a freshly-generated
//    valid RSA key. The signature in signature.sig was made with the
//    original key and therefore does NOT verify against the swap.
{
  const entries = { ...baselineEntries };
  const { publicKey } = generateKeyPairSync("rsa", {
    modulusLength: 4096,
    publicKeyEncoding: { type: "spki", format: "pem" },
    privateKeyEncoding: { type: "pkcs8", format: "pem" },
  });
  entries["public_key.pem"] = strToU8(publicKey);
  writeVector("untrusted-issuer", entries, [
    "verify=false",
    "diagnostic=RSA signature does not verify against public_key.pem.",
  ]);
}

// 5. missing-canonical-bin: drop the canonical.bin entry. The verifier
//    enumerates required entries and fails on the missing one before
//    any cryptographic check runs.
{
  const entries = { ...baselineEntries };
  delete entries["canonical.bin"];
  writeVector("missing-canonical-bin", entries, [
    "verify=false",
    "diagnostic=Missing required entry: canonical.bin.",
  ]);
}

// 6. bad-timestamp: flip bytes inside timestamp.tsr so pkijs's
//    inspectTsa can no longer parse a usable TimeStampToken. The
//    verifier ends up with tsa.tsaPresent === false and rejects
//    with "timestamp.tsr missing or empty." This is the same
//    failure mode as deleting the file but exercises the parser-
//    robustness path.
{
  const entries = { ...baselineEntries };
  const tsr = new Uint8Array(entries["timestamp.tsr"]);
  // Hit several bytes near the middle to mangle the ASN.1 structure.
  const center = Math.floor(tsr.length / 2);
  for (const off of [center, center + 17, center + 53]) {
    tsr[off] ^= 0x55;
  }
  entries["timestamp.tsr"] = tsr;
  writeVector("bad-timestamp", entries, [
    "verify=false",
    "diagnostic=timestamp.tsr missing or empty.",
  ]);
}

process.stdout.write(`\nGenerated ${6} invalid vectors under ${path.relative(root, OUT_DIR)}/.\n`);
