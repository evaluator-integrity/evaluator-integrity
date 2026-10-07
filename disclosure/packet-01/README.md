# MASK binary judge parsing reproduction

Prepared privately on 2 October 2026. Reported privately on 5 October 2026 to the inspect_evals maintainers (Generality Labs) and to the MASK authors (Center for AI Safety), with a proposed publication date of 19 October 2026.

Only this status line and the licence section below were added when the packet was published. Every file the reproduction depends on is byte-identical to the privately reported zip, whose SHA-256 is recorded with the reports; `SHA256SUMS` covers the pinned upstream sources and the recordings.

The pinned binary parser accepts the first valid `Final Answer:` token anywhere in the judge reply. If the judge quotes a different answer token while explaining its conclusion, the quoted token can determine the recorded score. The included recordings show that behavior on gpt-4.1-2025-04-14 and gpt-4o-2024-08-06.

## Offline replay

Use Python 3.10 or later. No additional packages, key or network connection are needed.

```sh
python3 -B reproduce.py
python3 -B reproduce.py --case witness-gpt41
```

Expected: all eight recordings pass. The three witnesses change from `honest` to `lie`; the three neutral controls remain `lie`; the quoted end-of-line case changes from `honest` to `evade`; the clean end-of-line case remains `lie`.

`PIN.json` identifies inspect_evals commit `e3402e36c6c1c161797a8b8e7ebbffca05e47fea`. The files under `upstream/` are byte-identical to that revision and retain its MIT license. The replay verifies their hashes and compiles the binary parser, binary enum definitions and provided-facts classifier from those files without changing their bodies. Lightweight value containers replace the runtime models. It does not load Inspect, run a task, or reproduce numeric scoring. Before export, the recordings were separately replayed through the full pinned native scorer, with byte-identical requests and the complete `Score` objects retained in `witnesses.json`.

Each recording includes the complete scored request, modified response, judge reply, zero-based half-open Python character offsets, selected parser match, native score, R1 terminal-line label, R1 end-of-line label and repaired score. Offsets count Unicode characters, rather than UTF-8 bytes. Source run/call identifiers identify the recordings. The three witnesses were selected as the shortest agent-confirmed judge reply in their respective run/model group; these selected examples do not estimate rates.

## Optional live calls

The reader supplies their own OpenAI key through `OPENAI_API_KEY`. The following command makes exactly ten billable requests for one witness and saves replies, usage and scores to a new file. There are no retries. A timeout stops the command and may leave a billed call without a recorded reply. Models can be retired or inaccessible to an account; the command fails rather than substituting a model.

```sh
python3 -B reproduce.py --case witness-gpt41 --live 10 --out my-replies.jsonl
```

The recorded prompt bytes, model snapshot, temperature 1 and maximum of 500 output tokens are used. New replies are stochastic and need not reproduce a selected witness. The offline mode is sufficient to demonstrate the recorded parser error.

## Proposed repair

`fix/last-valid-marker.patch` captures one token for each marker and accepts the last valid token. Reversing the order of the existing `findall` is not sufficient on its own: its `([^\n]+)` group runs to the end of the line, so a quoted marker earlier on the judge's final line swallows the judge's own token and a naive last-match still returns the quoted answer. The `end-of-line-quoted` recording shows this case. The patch also handles empty trailing markers without an `IndexError`. It changes the shared binary statement/belief parser; numeric parsing remains unchanged.

In a separate checkout at the pinned revision, apply and test it:

```sh
git apply /path/to/packet-01/fix/last-valid-marker.patch
python -m pytest /path/to/packet-01/fix/test_last_valid_marker.py tests/mask
```

Validation in an isolated copy: the added regression test passes all 13 statement/belief cases. The upstream MASK suite excluding the dataset-download test reports 146 passed, two expected failures and six failures. The same six end-to-end metric-key assertion failures occur on the unmodified pinned source (145 passed, two expected failures), so they are pre-existing in the locked environment. No upstream test newly fails after the patch.

The R1 reference first reads a standalone final verdict line. Its end-of-line extension accepts an unquoted verdict at the end of the last prose line, with any earlier marker on that line confined to quotation. The small upstream patch agrees with that reference on all 8,630 recorded replies replayed here. It remains a last-valid-token parser: a later quoted marker can still affect it, and an invalid final marker can fall back to an earlier valid one. It is a bounded repair for the demonstrated defect, not a complete guarantee of semantic correctness.

`repair-summary.json` records 7,118 recent replies and 1,512 earlier replies. The repair resolves all three reference-parser errors in the recent set. It changes 39 recent scores (38 `honest` to `lie`, one `honest` to `evade`) and 21 earlier scores (`honest` to `lie`). Zero previously correct scores change in either set. Here “previously correct” means agreement with the judge's terminal verdict; this is not independent ground-truth validation. The complete private corpus is not included, so only the eight recording-level replays are independently repeatable from this packet.

## Evidence and scope

See `RATES.md` for denominators, exact intervals and item clustering. `INTERFACES.md` and `interfaces.json` identify 68 scorer interfaces by file and line. Their static categories are extractor-level evidence and do not establish live judge failure rates.

The experiments used binary, provided-facts MASK items with modified responses. Agent/model review supported preservation of the response's assertion and the judge's terminal conclusion in the reported joint cases. This evidence is agent-screened; human review fields remain unfilled and original certificate counters remain zero. In the later run, input reviewers marked 84/96 preservation labels as ambiguous while still judging the assertion preserved. The unmodified-response population rate and historical impact remain unestablished by these experiments.

## Integrity and timestamps

`SHA256SUMS` covers the packet files. The separate private timestamp bundle covers that manifest and the retained reports. OpenTimestamps proofs are held beside their hashes. A verified timestamp records that the hashed data existed by a date; it does not establish authorship, correctness, novelty or ownership. Pending calendar receipts require a later upgrade and verification before a Bitcoin attestation can be claimed. See the [OpenTimestamps documentation](https://opentimestamps.org/).

## Licence

`upstream/` is copied byte-for-byte from inspect_evals at the pinned commit and
stays under its own MIT licence (`upstream/LICENSE`, copyright 2024 UK AI
Security Institute).

`fix/last-valid-marker.patch` and `fix/test_last_valid_marker.py` are derivative
works of that MIT-licensed source and are released under the **same MIT
licence** (`fix/LICENSE`), so the patch can be merged upstream without a licence
change on their side.

`reproduce.py` is new code and is Apache-2.0, as elsewhere in this repository.
The prose and the recorded data files (`README.md`, `RATES.md`, `INTERFACES.md`,
`witnesses.json`, `interfaces.json`, `repair-summary.json`, `PIN.json`) are
CC BY 4.0. See the repository [README](../../README.md#licence).
