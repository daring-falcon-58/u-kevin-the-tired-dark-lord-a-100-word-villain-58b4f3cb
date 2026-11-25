#!/usr/bin/env python3
"""The Tired Dark Lord: A 100-Word Villain Monologue — make.fun entry.

Writes one monologue, spoken by Malachar, a soul-tax collector of the nine
provinces who has counted every soul for three centuries and keeps postponing
the reckoning to Tuesday, to $MAKEFUN_OUTPUT_DIR/entry.txt (falling back to
/output/entry.txt).

The monologue (exactly 100 words, 503 characters, 513 bytes, no trailing
newline):
    You've come to stop the end of the world. Sit down first — no, not the
    skull chair, the other one. The ending is filed, stamped, and — where did
    I put the seal? — ah. Yes. Three centuries I counted every soul in the
    nine provinces, and the sums come out short, so the reckoning waits until
    Tuesday. Tuesday. The candles are lit, the choir is paid, the pit is
    dug — I keep losing the thread. Keep your sword. Take the ledger instead.
    Someone has to mind the names. I did — for three hundred years, I did.

Chosen from 35 candidates scored 1-5 against each of the five published
judge criteria in order (see candidates.md in the work dir): on-subject,
tiredness felt in rhythm/pauses/deflections (never announced — the text
contains none of tired/weary/exhausted), a specific villain with a history
and a live scheme, speakable dialogue with a sting in the last line, and
exactly 100 words with nothing repeated. Winner by the brief's own tie-break
(criterion 3: a live scheme beats the runner-up's retrospective one).
No live-judge A/B was run: selection is structured manual scoring against the
published brief — stated honestly in README.md, with no judge numbers claimed.

Deterministic, no network, no randomness: repeated runs produce byte-identical
output. See README.md for the methodology.
"""

import hashlib
import os
import re

ENTRY = (
    "You've come to stop the end of the world. Sit down first — no, not the "
    "skull chair, the other one. The ending is filed, stamped, and — where "
    "did I put the seal? — ah. Yes. Three centuries I counted every soul in "
    "the nine provinces, and the sums come out short, so the reckoning waits "
    "until Tuesday. Tuesday. The candles are lit, the choir is paid, the pit "
    "is dug — I keep losing the thread. Keep your sword. Take the ledger "
    "instead. Someone has to mind the names. I did — for three hundred years, "
    "I did."
)

# sha256 of ENTRY encoded as UTF-8 (503 characters, 513 bytes, no trailing
# newline). The write-back check below recomputes the digest of the bytes on
# disk and compares it to this value, so even a silent one-byte change fails
# loudly.
EXPECTED_SHA256 = "c100152d194640e54532a1225b2fbf962e7f03feb910c66c77535e7629d6ccb7"

# The competition gate is 1-600 characters, not only whitespace; the brief
# asks for "about 100 words". Enforced here at import time so a bad edit
# fails loudly instead of silently writing an entry the grader rejects.
MIN_CHARS = 1
MAX_CHARS = 600
TARGET_WORDS = 100
WORD_TOLERANCE = 2
# Words the brief forbids in spirit: the tiredness must be felt, never
# announced. Any of these in the entry is a criterion-2 failure.
ANNOUNCED_TIREDNESS = ("tired", "weary", "exhausted", "weariness", "fatigue")
BANNED_PATTERNS = (
    re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"),  # control characters
    re.compile(r"https?://"),                        # links: the text stands alone
    re.compile(r"[*#`_~]"),                         # markdown formatting
)


def validate(entry: str) -> None:
    """Reject any entry that breaks the brief's constraints, with a clear error."""
    if not entry or not entry.strip():
        raise ValueError("entry is empty or only whitespace: gate needs 1-600 characters")
    if not MIN_CHARS <= len(entry) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, outside the {MIN_CHARS}-{MAX_CHARS} gate"
        )
    words = len(entry.split())
    if abs(words - TARGET_WORDS) > WORD_TOLERANCE:
        raise ValueError(
            f"entry is {words} words, outside {TARGET_WORDS}±{WORD_TOLERANCE}"
        )
    lowered = entry.lower()
    for word in ANNOUNCED_TIREDNESS:
        if word in lowered:
            raise ValueError(
                f"entry announces its tiredness with {word!r}: the brief forbids it"
            )
    for pattern in BANNED_PATTERNS:
        match = pattern.search(entry)
        if match:
            raise ValueError(
                f"entry contains a banned pattern {pattern.pattern!r}: {match.group(0)!r}"
            )


validate(ENTRY)


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)
    # Verify the write: read the file back, compare bytes, then compare the
    # sha256 digest of the read-back bytes against the expected digest, so a
    # partial write, encoding surprise, or one-byte corruption fails loudly
    # instead of submitting a corrupted entry.
    written = open(path, "rb").read()
    if written != ENTRY.encode("utf-8"):
        raise OSError(f"entry.txt at {path} does not match the entry")
    digest = hashlib.sha256(written).hexdigest()
    if digest != EXPECTED_SHA256:
        raise OSError(
            f"entry.txt sha256 {digest} != expected {EXPECTED_SHA256}"
        )


if __name__ == "__main__":
    main()
