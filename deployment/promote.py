"""Promote the staging container only when main matches the reviewed version."""

import argparse
import json
import re
import subprocess


def reviewed_image(service, revision, commit):
    status = service.get("status", {})
    revision_name = revision.get("metadata", {}).get("name")
    if not revision_name or status.get("latestReadyRevisionName") != revision_name:
        raise ValueError("Staging does not have a ready revision to promote.")
    if status.get("latestCreatedRevisionName") != revision_name:
        raise ValueError("A newer staging deployment is still pending or failed.")
    traffic = status.get("traffic", [])
    active = [entry for entry in traffic if entry.get("percent", 0) > 0]
    if len(active) != 1 or active[0].get("percent") != 100:
        raise ValueError("Staging must serve one reviewed version at 100% traffic.")
    if active[0].get("revisionName") != revision_name:
        raise ValueError("The ready staging revision is not the version being served.")
    labels = revision.get("metadata", {}).get("labels", {})
    if labels.get("source-sha") != commit:
        raise ValueError("Main must match the exact commit reviewed on staging. Use a fast-forward merge.")
    if labels.get("environment") != "staging":
        raise ValueError("The source revision was not deployed by the staging workflow.")
    conditions = revision.get("status", {}).get("conditions", [])
    if not any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions):
        raise ValueError("The staging revision is not ready.")
    digest = revision.get("status", {}).get("imageDigest", "")
    if re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        image = revision["spec"]["containers"][0]["image"]
        repository = image.split("@", 1)[0]
        if ":" in repository.rsplit("/", 1)[-1]:
            repository = repository.rsplit(":", 1)[0]
        digest = repository + "@" + digest
    if not re.fullmatch(r"[^\s]+@sha256:[0-9a-f]{64}", digest):
        raise ValueError("Staging has no immutable container image digest.")
    return digest


def describe(project, resource, name, region):
    result = subprocess.run(
        ["gcloud", "run", resource, "describe", name, "--project=" + project,
         "--region=" + region, "--format=json"],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("project", "commit", "staging-service", "staging-region",
                 "production-service", "production-region"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        parser.error("A full source commit is required.")
    if (args.staging_service, args.staging_region) == (args.production_service, args.production_region):
        parser.error("Staging and production must be separate services or regions.")
    service = describe(args.project, "services", args.staging_service, args.staging_region)
    revision_name = service.get("status", {}).get("latestReadyRevisionName")
    if not revision_name:
        parser.error("Deploy staging successfully before promoting to production.")
    revision = describe(args.project, "revisions", revision_name, args.staging_region)
    try:
        image = reviewed_image(service, revision, args.commit)
    except ValueError as error:
        parser.error(str(error))
    subprocess.run(
        ["gcloud", "run", "deploy", args.production_service,
         "--project=" + args.project, "--region=" + args.production_region,
         "--image=" + image, "--port=8080", "--allow-unauthenticated",
         "--labels=source-sha=" + args.commit + ",environment=production", "--quiet"],
        check=True,
    )
    subprocess.run(
        ["gcloud", "run", "services", "update-traffic", args.production_service,
         "--project=" + args.project, "--region=" + args.production_region,
         "--to-latest", "--quiet"],
        check=True,
    )


if __name__ == "__main__":
    main()
