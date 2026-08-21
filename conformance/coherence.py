"""Checks that a criterion agrees with itself across its parts and renderings.

    python -m conformance.coherence
    python -m conformance.coherence --check

Why this exists
---------------
C2's framing question survived the removal of its held-out clause unchanged. For
a while the criterion asked "Is there any correctness signal independent of the
judge, held out from whatever process produces or selects outputs?" while the
pass condition twelve lines below required only existence and independence, and
the paragraph under that explicitly disclaimed the held-out requirement.

A reader who reads the question and stops -- which is what a question is for --
got the retired rule. A vendor assembling evidence against it did work the
criterion did not ask for and could not be scored on. It was found by reading
the text, and nothing mechanical would have caught it. This is the mechanical
answer.

The rule
--------
A criterion states its requirement three times: as a question, as a pass
condition, and as published prose. They are one requirement, so:

  * **The question must appear verbatim in the published markdown.** The module
    scores and the markdown is cited. A question fixed in one rendering and not
    the other leaves the citable text stating the retired rule -- which is
    exactly the shape of the original defect, one level up.

  * **The question must not ask for what the pass condition disclaims.** Where
    a phrase from the question appears in the pass condition ONLY inside a
    sentence that retires it -- "deliberately does not require", "has been
    removed", "no longer" -- the question is asking for a property the
    criterion does not test.

WHAT THIS DOES NOT CATCH. The second rule is lexical. It fires when the question
reuses the words the pass condition disclaims, which is what happened to C2 and
is the recurring shape: a clause gets removed from the operative text and the
question keeps its vocabulary. A question that disagrees with its pass condition
in different words passes this check, and there is no version of it that would
not. It closes the hole that opened twice, not the class.
"""

from __future__ import annotations

import argparse
import re
import sys

from conformance.citations import published_sections
from conformance.criteria import CRITERIA

# Sentence openers and connectives that carry no content of their own. A phrase
# has to survive their removal to be distinctive enough to compare.
_STOPWORDS = {
    "a", "an", "the", "is", "are", "be", "been", "it", "its", "of", "to", "in",
    "on", "for", "and", "or", "that", "this", "any", "some", "does", "do",
    "would", "will", "can", "could", "by", "as", "at", "with", "there",
    "which", "what", "before", "after", "than", "then", "so", "have", "has",
    "not", "no", "if", "when", "must", "may", "own",
}

# A sentence containing one of these is retiring the requirement it names
# rather than stating it.
_DISCLAIMERS = (
    "does not require",
    "deliberately does not",
    "has been removed",
    "no longer",
    "was an earlier",
    "an earlier version",
    "not a separate requirement",
    "is not the discriminator",
    "cannot carry",
)


def phrases(question: str) -> list:
    """Distinctive multi-word runs of a question, stopwords removed.

    Runs, not n-grams: "held out from whatever process" reduces to "held out"
    and "process", and it is the two-word run that is distinctive enough to
    mean the same thing wherever it appears.
    """
    words = re.findall(r"[a-z0-9-]+", question.lower())
    runs, current = [], []
    for w in words:
        if w in _STOPWORDS:
            if len(current) > 1:
                runs.append(" ".join(current))
            current = []
        else:
            current.append(w)
    if len(current) > 1:
        runs.append(" ".join(current))
    return runs


def sentences(text: str) -> list:
    return [s for s in re.split(r"(?<=[.?!])\s+|\n\n", text) if s.strip()]


def check() -> list[str]:
    problems = []
    secs = published_sections()

    for c in CRITERIA:
        anchor = c.id.split("_", 1)[0]
        question = re.sub(r"\s+", " ", c.question).strip()

        section = re.sub(r"\s+", " ", secs.get(anchor, ""))
        if not section:
            problems.append(
                f"{c.id}: no section {anchor!r} in the published markdown.")
        elif question not in section:
            problems.append(
                f"{c.id}: the question is not in criteria/v0.1/index.md "
                f"verbatim.\n      module: {question}\n"
                f"      The module scores and the markdown is cited. A "
                f"question corrected in one rendering and not the other leaves "
                f"the citable text asking for the retired rule.")

        pc = re.sub(r"\s+", " ", c.pass_condition).lower()
        retiring = {s for s in sentences(pc)
                    if any(d in s for d in _DISCLAIMERS)}
        for phrase in phrases(question):
            # Every sentence that mentions it retires it. Not "some retiring
            # sentence mentions it" -- a pass condition carries several
            # disclaimers about different things, and the question is only
            # wrong if the phrase has nowhere else to stand.
            stands_in = [s for s in sentences(pc) if phrase in s]
            if stands_in and all(s in retiring for s in stands_in):
                problems.append(
                    f"{c.id}: the question asks for {phrase!r}, which the pass "
                    f"condition mentions only to retire it. A reader who reads "
                    f"the question and stops gets a rule the criterion does "
                    f"not test, and evidence assembled against it cannot be "
                    f"scored.")

    return problems


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true",
                   help="accepted for symmetry with the other conformance "
                        "entry points; checking is the default action. It must "
                        "remain ACCEPTED, or a caller passing it exits 2 on an "
                        "argparse error -- 'the check could not run', which "
                        "must never be read as a pass.")
    p.parse_args(argv)

    problems = check()
    print(f"criteria checked: {len(CRITERIA)}")
    if problems:
        print(f"\n{len(problems)} PROBLEM(S):\n", file=sys.stderr)
        for pr in problems:
            print("  -", pr, file=sys.stderr)
        return 1
    print("Each criterion's question matches its published rendering and asks "
          "for what its pass condition tests.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
