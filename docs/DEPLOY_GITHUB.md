# Deploy MeanwhX free on GitHub Pages

The project already includes a GitHub Actions deployment workflow.

## Recommended setup

### 1. Create a public repository

For the free GitHub Pages route, create something like:

```text
meanwhx-site
```

Only put public-ready website content in this repository. Keep private designs/CAD in a separate private repository or local workspace.

### 2. Push

```bash
git init
git add .
git commit -m "Initial MeanwhX website"
git branch -M main
git remote add origin https://github.com/YOUR-ACCOUNT/meanwhx-site.git
git push -u origin main
```

### 3. Enable Pages

On GitHub:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, choose **GitHub Actions**.
3. Push to `main` (or manually run the workflow from **Actions**).

The workflow builds `dist/` with Python and deploys it.

For a normal project repository, your default URL will look like:

```text
https://YOUR-ACCOUNT.github.io/meanwhx-site/
```

The build automatically prefixes internal links for the repository path.

## Recommended collaboration settings

When several people work on the site:

1. Invite trusted collaborators.
2. Protect `main` with a GitHub Ruleset / branch protection.
3. Require pull requests.
4. Require at least one review.
5. Give every note/design change its own branch.

Example:

```bash
git checkout -b notes/add-new-poem
# edit
python3 build.py
git add .
git commit -m "Add new poem"
git push -u origin notes/add-new-poem
```

Then open a pull request.

## Custom domain later

Do not hard-code a custom domain until the MeanwhX name/domain decision is ready.

When it is:

1. Configure the domain under **Settings → Pages**.
2. Configure DNS with the registrar.
3. Add `public/CNAME` with the domain.
4. Set `SITE_URL` to the custom domain and remove the project base path in the workflow.
5. Enable **Enforce HTTPS** once GitHub offers it.

## If the site later sells things

GitHub Pages is a good fit for the current static cultural/community site.

If the site becomes primarily ecommerce, or needs accounts, uploads, payments, private data, or server-side APIs, move those functions to an appropriate service rather than trying to process them inside GitHub Pages.
