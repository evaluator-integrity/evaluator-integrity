# Reporting a problem

Two kinds of report land here, and they are handled differently.

## A defect in this repository

A wrong score, a quote that does not match the artifact it cites, a check that
passes when it should fail, or a vulnerability in the tooling.

Email **idilgozel@evaluatorintegrity.com**. Please do not open a public issue
for a finding that would let someone else move a score before it is fixed; for
anything else, an issue is fine and preferred.

What you can expect: acknowledgement within three working days, a decision on
whether it is a defect within ten, and credit in the fix under whatever name you
ask for, including none. A criterion that is already published is not edited in
response to a finding — it is superseded by a new version, with the reason
recorded. See [CONTRIBUTING.md](CONTRIBUTING.md).

## A defect in somebody else's evaluator

This project audits evaluators maintained by other people. If you have found a
problem in one of those, it belongs with its maintainers rather than with us,
and we will say so.

## How this project discloses

We hold ourselves to what we ask of others.

- A defect found in a third party's evaluator goes to its maintainers privately
  first, through whatever private channel they publish, with a reproduction and,
  where we can write one, a fix.
- We propose a publication date in that first message, we say it is a proposal
  rather than a deadline, and we move it when a maintainer tells us the timing
  is awkward for a fix.
- Nothing is posted publicly before that date, and we do not use an open issue
  tracker as a first contact.
- What we publish is scoped to what was measured, labelled by the kind of
  evidence it rests on, and dated. The method by which something was found is
  not necessarily published with it.
- Where a maintainer wants attribution handled a particular way, that is their
  call, not ours.

An audit that leaks the thing it audited before the owner can fix it is not an
audit. It is a disclosure with a reputation attached.
