# 🏎️ F1 GitHub Contribution Racer

A red Formula 1 car races across your real GitHub contribution calendar.

## Add it to your profile README

Use the generated animation from [Nazmul1005/github-f1-contribution-racer](https://github.com/Nazmul1005/github-f1-contribution-racer):

### Animated GIF (recommended)

```html
<p align="center">
  <img src="https://raw.githubusercontent.com/Nazmul1005/github-f1-contribution-racer/output/f1-race.gif" alt="F1 car racing across my GitHub contribution graph" width="100%">
</p>
```

### Animated SVG

```html
<p align="center">
  <img src="https://raw.githubusercontent.com/Nazmul1005/github-f1-contribution-racer/output/f1-race.svg" alt="Animated F1 contribution racer" width="100%">
</p>
```

GIF is the more dependable choice in GitHub README rendering; SVG animation support can vary by viewer.

## Setup

1. Create a repository, for example `github-f1-contribution-racer`.
2. Upload all project files, preserving the `.github/workflows/update-racer.yml` path.
3. Open **Settings → Actions → General → Workflow permissions** and enable **Read and write permissions**.
4. Push the files to your repository's default branch.
5. Open **Actions → Update F1 contribution racer → Run workflow**.
6. When it finishes, it creates an `output` branch with `f1-race.gif` and `f1-race.svg`.
7. Copy one image snippet above into the README of your profile repository (the repository named exactly after your GitHub username).

The workflow refreshes the images daily. You can also run it manually from Actions.

## Run locally

```bash
python -m pip install Pillow
export GH_USERNAME="YOUR_GITHUB_USERNAME"
export GH_TOKEN="YOUR_GITHUB_TOKEN"
python src/generate.py
```

The generated files appear in `dist/`. Keep your token private and never commit it. GitHub Actions uses its built-in token automatically.

## How it works

- Reads the repository owner's contribution calendar with GitHub's GraphQL API.
- Draws the contribution squares using GitHub's contribution colors.
- Creates a winding route through the seven weekday rows.
- Renders a looping GIF and an SVG with an animated car.
- Publishes both files to the `output` branch for stable README image URLs.

## Notes

- The car follows the contribution grid layout; it is not a real-world race circuit.
- Private contributions appear according to the account's GitHub contribution settings.
- If the workflow fails, inspect the Actions log for API, permission, or username errors.
