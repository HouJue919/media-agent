# GitHub Release Guide: v0.3.0 Creator Workflow Release

Use this guide if GitHub CLI is unavailable or not authenticated.

## Manual Release Steps

1. Open:
   <https://github.com/HouJue919/media-agent>

2. Go to **Releases**.

3. Click **Draft a new release**.

4. Select tag:
   `v0.3.0`

5. Set title:
   `v0.3.0 Creator Workflow Release`

6. Set description:
   Copy the contents of `RELEASE_NOTES_v0.3.0.md`.

7. Click **Publish release**.

## Optional GitHub CLI Setup

GitHub CLI has been installed locally at:

```bash
~/.local/bin/gh
```

If your shell can load `~/.zprofile`, open a new terminal and check:

```bash
gh --version
```

If `gh` is available, authenticate with:

```bash
gh auth login
```

Then the release can be created with:

```bash
gh release create v0.3.0 \
  --title "v0.3.0 Creator Workflow Release" \
  --notes-file RELEASE_NOTES_v0.3.0.md
```
