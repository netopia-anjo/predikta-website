import copy
import unittest

from deployment.promote import reviewed_image


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.commit = "a" * 40
        self.digest = "europe-west1-docker.pkg.dev/project/websites/site@sha256:" + "b" * 64
        self.service = {"status": {
            "latestReadyRevisionName": "staging-001",
            "latestCreatedRevisionName": "staging-001",
            "traffic": [{"revisionName": "staging-001", "percent": 100}],
        }}
        self.revision = {
            "metadata": {"name": "staging-001", "labels": {
                "source-sha": self.commit, "environment": "staging"}},
            "spec": {"containers": [{"image": "europe-west1-docker.pkg.dev/project/websites/site:tag"}]},
            "status": {"imageDigest": self.digest,
                       "conditions": [{"type": "Ready", "status": "True"}]},
        }

    def test_preserves_reviewed_digest(self):
        self.assertEqual(reviewed_image(self.service, self.revision, self.commit), self.digest)

    def test_normalizes_bare_digest(self):
        self.revision["status"]["imageDigest"] = "sha256:" + "b" * 64
        self.assertEqual(reviewed_image(self.service, self.revision, self.commit), self.digest)

    def test_rejects_different_code(self):
        with self.assertRaises(ValueError):
            reviewed_image(self.service, self.revision, "c" * 40)

    def test_rejects_pending_or_failed_newer_deployment(self):
        self.service["status"]["latestCreatedRevisionName"] = "staging-002"
        with self.assertRaises(ValueError):
            reviewed_image(self.service, self.revision, self.commit)

    def test_rejects_split_or_old_traffic(self):
        for traffic in (
            [{"revisionName": "staging-001", "percent": 50},
             {"revisionName": "staging-000", "percent": 50}],
            [{"revisionName": "staging-000", "percent": 100}],
            [],
        ):
            with self.subTest(traffic=traffic), self.assertRaises(ValueError):
                self.service["status"]["traffic"] = traffic
                reviewed_image(self.service, self.revision, self.commit)

    def test_rejects_missing_readiness_label_or_digest(self):
        for section, key in (("status", "conditions"), ("status", "imageDigest")):
            revision = copy.deepcopy(self.revision)
            del revision[section][key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                reviewed_image(self.service, revision, self.commit)
        self.revision["metadata"]["labels"]["environment"] = "production"
        with self.assertRaises(ValueError):
            reviewed_image(self.service, self.revision, self.commit)


if __name__ == "__main__":
    unittest.main()
