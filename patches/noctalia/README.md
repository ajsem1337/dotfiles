# Local integration fixes

`community.patch` contains only my changes to
[Noctalia's community templates](https://github.com/noctalia-dev/community-templates):

- fzf: replace the previous palette instead of accumulating persistent Fish options;
- Papirus: avoid picking gray folders for a colored accent;
- VS Code: require the actual theme extension before writing into its directory.

The colors still come from Noctalia. Its cache sync preserves edited files.
These patches make the local fixes reproducible on a fresh installation.

After Noctalia has downloaded the original templates, review and dry-run the
patch from this repository's root:

```sh
cache="${NOCTALIA_STATE_HOME:-${XDG_STATE_HOME:-$HOME/.local/state}/noctalia}/community-templates"
patch --dry-run --forward -p1 -d "$cache" < patches/noctalia/community.patch
patch --forward -p1 -d "$cache" < patches/noctalia/community.patch
noctalia msg templates-apply
```

Apply only once to matching upstream files. If the dry-run fails, review the
upstream changes or existing local edits; do not force it or overwrite the cache.
