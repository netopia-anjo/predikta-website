# Predikta website

The Cloud Run setup is prepared locally. Nothing has been published.

`Fortified Predikta Website.html` is the website source. Its design and content
are preserved. The container serves that file as the homepage. `copy.json`
provides the empty optional copy overrides requested by the existing page.

## Details to replace before publishing

The service names, regions and example website addresses in `AGENTS.md` come
from the supplied Netopia instructions. They have not been verified as the
destinations for this Predikta website. Update those details before enabling
deployment, together with the substitutions at the bottom of both Cloud Build
files. No Google Cloud project ID is hardcoded: the build uses its own project.

| Setting | Staging | Production |
| --- | --- | --- |
| Branch | `staging` | `main` |
| Configuration file | `cloudbuild.staging.yaml` | `cloudbuild.production.yaml` |
| Service (supplied example) | `netopia-website` | `netopia-website` |
| Region (supplied example) | `europe-west1` | `asia-southeast1` |

The staging file also defaults to a Docker Artifact Registry repository named
`websites` in `europe-west1`, with an image named `predikta-website`. This
repository must exist before deployment. Production reuses the staging image
from that repository, even when the production service is in another region.

## One-time Google Cloud connection

This repository does not create cloud resources or connect deployment triggers
by itself. Before the first staging publication, the setup needs:

1. The correct Google Cloud project, with billing and the Cloud Run, Cloud Build,
   Artifact Registry and Resource Manager APIs enabled.
2. The Docker Artifact Registry repository specified in the staging settings.
3. A Cloud Build connection to `netopia-anjo/predikta-website` on GitHub.
4. A staging push trigger for exactly `^staging$`, in the staging region, using
   `cloudbuild.staging.yaml`.
5. A production push trigger for exactly `^main$`, in the production region,
   using `cloudbuild.production.yaml`.
6. Build service accounts with Artifact Registry access, Cloud Run deployment
   permissions, Logs Writer, and Service Account User on the runtime identity.
   The production account also needs to read staging services and revisions.
   Public website access must be permitted by the project's organization policy.

Ask the assistant to finish this connection after providing the final project
and website destinations. The user does not need to run terminal commands.
Do not enable a separate source deployment trigger that bypasses these files.

Setup follows [Google's Cloud Build deployment guide](https://docs.cloud.google.com/build/docs/deploying-builds/deploy-cloud-run).

## Publishing workflow

Describe a change to prepare it locally. Reply **Deploy to staging** when ready
to publish it for review. Once the setup above is connected, the staging push
builds a Linux AMD64 container and deploys it to the staging service. Confirm
the build succeeded and the website is reachable before announcing it is ready
for review; a successful push alone does not mean deployment has completed.

After reviewing staging, reply **Deploy to production**. Promote with a
fast-forward merge so `main` points at the exact reviewed staging commit.
Production checks that staging is ready, serves that commit at 100% traffic,
and has no newer pending revision. It deploys the same immutable image digest
without rebuilding the HTML. If staging has changed since approval, stop and
request a new review. Never force-push or modify code during promotion.

The first publication goes to `staging`; no initial commit or push to `main`
is needed. Rollbacks require an explicit request and a verified previous
revision. A production rollback must follow the staging review workflow.

## Local verification (for maintainers)

```sh
docker build --platform=linux/amd64 -t predikta-website:local .
docker run --rm -p 127.0.0.1:8080:8080 predikta-website:local
```

Open `http://localhost:8080`. The container listens on Cloud Run's `PORT`
environment variable, defaulting to `8080`. `/healthz` returns `ok`. Missing
assets return 404, and source/deployment files are excluded from the image.

```sh
python3 -m unittest discover -s tests
```
