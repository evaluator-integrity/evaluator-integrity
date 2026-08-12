# Site

The site publishes the criteria. Nothing else.

## The one rule

**The site renders `criteria/vX.Y/index.md` from this repository, in place.**

Not a copy, not an export, not a synced version. The file the tooling reads and
the file the world reads are the same bytes, so they cannot drift apart. A
standard whose published text has quietly diverged from the text its own
conformance checks run against has failed at the thing it is asking others to
get right.

So: no content directory, no CMS, no build step that transforms the markdown
into something the tooling no longer recognises.

## Target: GitHub Pages

Chosen for what it does not require. It serves at
`idilgozel.github.io/evaluator-integrity` with no domain purchase, no account
beyond the one that already hosts the repository, and no vendor decision that
has to be revisited before v0.1 can publish.

A custom domain later is a `CNAME` file and a DNS record. **No path changes**,
so citations made against the `github.io` address keep resolving. That property
is the reason to start here rather than "start cheap and migrate".

<!--
Alternative: Cloudflare Pages. Same source layout, build command `jekyll build`,
output `_site`. Worth moving to if any of these become true:
  - Pages build minutes or the 10-builds-per-hour limit start biting.
  - Redirects need to be real 301s rather than HTML meta-refresh (Cloudflare has
    a _redirects file; GitHub Pages does not).
  - Analytics or access logs are needed without adding a third-party script to a
    page people are reading to decide whether to trust the method.
Not worth moving for speed. This is four pages of static markdown.
-->

## Configuration

Not yet committed — see "Open decision" below. When it is, it is these files.

`_config.yml` at the **repository root** (GitHub Pages requires it there; Jekyll
builds from the repo root, which is what keeps the criteria in place):

```yaml
title: Evaluator Integrity
description: Criteria for auditing the evaluators AI teams measure themselves with
url: https://idilgozel.github.io
baseurl: /evaluator-integrity

# kramdown honours explicit heading ids written as {#C1}. This is what makes
# the anchors survive markdown -> HTML unchanged. Do not switch the markdown
# engine without re-checking every published anchor.
markdown: kramdown
kramdown:
  auto_ids: true          # fallback ids for headings without an explicit one
  syntax_highlighter: rouge

plugins:
  - jekyll-redirect-from

# Publish the criteria and nothing else. Everything not listed is not a page.
include:
  - criteria
exclude:
  - conformance
  - scripts
  - tests
  - self-check
  - site
  - .githooks
  - CLAUDE.md
  - CONTRIBUTING.md
  - pyproject.toml
  - README.md
```

`criteria/v0.1/index.md` needs no front matter beyond a `layout` — Jekyll maps
`criteria/v0.1/index.md` to `/criteria/v0.1/` on its own. That mapping is why
the source path and the published path stay in step.

### Anchor ids

Criteria headings carry explicit kramdown ids:

```markdown
## C1. <title> {#C1}
```

which render as `<h2 id="C1">`, giving `/criteria/v0.1/#C1`.

Generated slugs are not acceptable here: they are derived from the heading text,
so rewording a title silently breaks every citation pointing at it. Per
[`../criteria/README.md`](../criteria/README.md) an anchor id means the same
thing forever, which only holds if the id is written down rather than computed.

**Check the rendered HTML, not the source, before publishing a version.** An
anchor that exists only in markdown is not a citable anchor.

### `/criteria/latest`

A redirect to the current version, and the only path here whose target changes.

Simplest form that works on GitHub Pages — `criteria/latest/index.md`:

```markdown
---
redirect_to: /evaluator-integrity/criteria/v0.1/
---
```

Repointed when a new version publishes; the versioned paths it has pointed at
never move. It is a convenience for browsing, not a citable address — see
[`../criteria/README.md`](../criteria/README.md).

Note this is a meta-refresh, not a 301. Fine for readers, imperfect for
crawlers; one reason to reach for Cloudflare Pages if that ever matters.

## Not a marketing site

An index listing the criteria versions, and the criteria. No product pages, no
pricing, no roadmap, no testimonials, no signup. The reader arriving here is
deciding whether to trust the method, and anything selling to them while they do
that is evidence against it.

## Open decision

`_config.yml` and `criteria/latest/` are deliberately not committed yet.
Enabling Pages publishes the repository — that is Idil's call to make explicitly,
and there is no published criteria version to serve until v0.1 is ported and
frozen. Adding the two files above and switching Pages on in repository settings
is the whole of the remaining work.
