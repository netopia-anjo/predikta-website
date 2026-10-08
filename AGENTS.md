# Deployment Environments

This website has separate staging and production environments.

## Staging

* Git branch: `staging`
* Cloud Run service: `netopia-website`
* Cloud Run region: `europe-west1`
* Purpose: review changes before production
* Staging URL: `https://netopia-website-758517888423.europe-west1.run.app`

## Production

* Git branch: `main`
* Cloud Run service: `netopia-website`
* Cloud Run region: `asia-southeast1`
* Purpose: public website
* Production URL: `https://netopia-website-758517888423.asia-southeast1.run.app`

# Required Workflow

When a user requests a website change:

1. Make the requested change locally.
2. Preserve the existing design and branding.
3. Verify the affected files.
4. Summarize the change in plain English.
5. Do not commit, push, or deploy automatically.
6. Clearly tell the user what to do next.

After preparing a change, always end the response with:

> The changes are ready but not yet published.
> Reply **Deploy to staging** to publish them to the staging website for review.

# Deploy to Staging

Only when the user explicitly says:

`Deploy to staging`

Then:

1. Commit the prepared changes.
2. Push them only to the `staging` branch.
3. Never push directly to `main`.
4. Confirm that the Git push succeeded.
5. Tell the user that the staging deployment has started.
6. Provide the staging URL.
7. Tell the user to review the staging website.

After staging deployment, always end the response with:

> The changes are now available on staging:
> `YOUR_STAGING_URL`
>
> Please review the website.
>
> After approval, reply **Deploy to production**.
>
> To make more changes first, describe the changes you want.

# Deploy to Production

Only when the user explicitly says:

`Deploy to production`

Then:

1. Confirm that a staging deployment exists.
2. Promote the exact reviewed staging version.
3. Do not recreate, rewrite, or modify the change during promotion.
4. Merge the reviewed `staging` commit into `main`.
5. Push `main` to GitHub.
6. Confirm that the Git push succeeded.
7. Tell the user that production deployment has started.
8. Provide the production URL.

After production deployment, always end the response with:

> The reviewed changes have been deployed to production:
> `YOUR_PRODUCTION_URL`
>
> To request another update, simply describe what you want changed.

# User Commands

Always recognize these commands regardless of capitalization:

* `Deploy to staging`
* `Deploy staging`
* `Publish to staging`
* `Send to staging`

These all mean: commit and push the prepared changes to the `staging` branch.

Always recognize these commands regardless of capitalization:

* `Deploy to production`
* `Deploy production`
* `Publish to production`
* `Go live`

These all mean: promote the reviewed staging version to the `main` branch.

Also recognize:

* `Do not deploy`
* `Keep as draft`
* `Make another change`
* `Rollback staging`
* `Rollback production`

# Communication Rules

Assume the user is non-technical.

Never require the user to know:

* Git
* GitHub branches
* Commits
* Cloud Build
* Cloud Run
* Docker
* Terminal commands

Use plain language such as:

* “The change is ready.”
* “The staging website is ready for review.”
* “Reply Deploy to production when approved.”
* “The production website has been updated.”

Do not say only:

* “Changes committed.”
* “Pushed to branch.”
* “Revision triggered.”
* “Merge completed.”

Technical details may be included after the plain-language explanation, but only when useful.

# Safety Rules

* Never skip staging.
* Never push an unreviewed change directly to `main`.
* Never deploy automatically after editing.
* Never deploy different code from what was reviewed on staging.
* Never force-push.
* Never rewrite Git history.
* Never modify deployment configuration, Cloud Run regions, Cloud Build triggers, Dockerfile, nginx.conf, secrets, or infrastructure unless explicitly authorized.
