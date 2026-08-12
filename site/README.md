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

Committed and versioned. **Pages is switched off** — see "Not live yet" below.

| file | role |
|---|---|
| [`/_config.yml`](../_config.yml) | Jekyll config. Must live at the repository root; GitHub Pages requires it there, and building from the root is what keeps the criteria rendering in place. |
| [`/_layouts/default.html`](../_layouts/default.html) | The only layout. Self-contained, no theme, no external assets. |
| [`/criteria/latest/index.html`](../criteria/latest/index.html) | Redirect to the current version. |

Jekyll maps `criteria/v0.1/index.md` to `/criteria/v0.1/` on its own. That
mapping is why the source path and the published path stay in step.

### Front matter is not optional

`criteria/vX.Y/index.md` needs a front matter block, even an almost empty one.
**Jekyll copies files without front matter verbatim** — the page would be served
as raw markdown, which fails silently and looks like a rendering bug rather than
a missing header.

The `layout` comes from the `defaults` rule in `_config.yml`, so a new version
directory does not have to remember it. The front matter block itself still has
to be there.

### No theme

The layout is ~40 lines of inline CSS rather than a GitHub Pages theme. A theme
would wrap a document that gets printed, archived and quoted into other people's
files in navigation, branding and a footer, none of which survive that journey
or help it. Nothing is loaded from another host, so the page renders identically
offline and from an archive.

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
Repointed when a new version publishes; the versioned paths it has pointed at
never move. A convenience for browsing, not a citable address — see
[`../criteria/README.md`](../criteria/README.md).

Implemented as plain HTML with a **relative** target (`../v0.1/`), not with
`jekyll-redirect-from`. Two reasons:

- A relative target resolves correctly under `idilgozel.github.io/evaluator-integrity`,
  under a custom domain, and in a local build, with no `baseurl` interpolation.
  An absolute URL would break on exactly the domain move this hosting choice
  exists to make painless.
- No plugin dependency, and the file behaves the same whether or not Jekyll ever
  runs on it.

It currently points at **v0.1, which is provisional and unpublished**. That is
correct — it is the only version — but it is a reason not to enable Pages yet.

Note this is a meta-refresh, not a 301. Fine for readers, imperfect for
crawlers; one reason to reach for Cloudflare Pages if that ever matters.

## Not a marketing site

An index listing the criteria versions, and the criteria. No product pages, no
pricing, no roadmap, no testimonials, no signup. The reader arriving here is
deciding whether to trust the method, and anything selling to them while they do
that is evidence against it.

## Not live yet

The configuration is committed; **GitHub Pages is off**. Committing these files
publishes nothing — Pages is enabled separately, in repository settings.

The config is versioned ahead of being live on purpose: it gets reviewed while
nothing is at stake, rather than under pressure on the day v0.1 publishes.

**Do not enable Pages until a criteria version is published and frozen.** There
is nothing to serve: v0.1 is a draft, `/criteria/latest` points at that draft,
and the site has no index page yet. Serving a provisional document at a stable
URL invites exactly the citation the versioning policy exists to prevent.

Remaining before the site goes live:

- [ ] Port and freeze the v0.1 criteria text, with explicit `{#C1}`–`{#C4}` ids.
- [ ] Add a site index listing the criteria versions.
- [ ] Build locally (`bundle exec jekyll serve`) and **check the rendered HTML**
      for the anchor ids — an anchor that exists only in the markdown is not a
      citable anchor.
- [ ] Enable Pages in repository settings.
