# IFMLogiX — Operations Runbook

## On-Call Contact

**Bar Pesso** — [bar@logigroup.co](mailto:bar@logigroup.co)

---

## Production URL

| Service | Details |
|---|---|
| Cloud Run service | `logfi` |
| Region | `europe-west1` |
| Firebase Hosting | Rewrites all traffic to the `logfi` Cloud Run service |

---

## Health Check

```
GET /api/health
```

Expected response (HTTP 200):

```json
{"status": "ok"}
```

Run from the command line:

```bash
curl https://<production-domain>/api/health
```

If the response is not `{"status":"ok"}` or the request times out, treat the service as down and follow the incident procedure below.

---

## Common Incidents

### Service Down

1. Open the [Cloud Run console](https://console.cloud.google.com/run) and navigate to the `logfi` service in `europe-west1`.
2. Check the **Logs** tab for errors (crash loops, OOM, startup failures).
3. If the current revision is unhealthy, click **Edit & Deploy New Revision** and deploy the last known-good image tag.
4. If the issue persists, follow the **Rollback Procedure** below.

---

### Auth Failing (401 / 403 errors)

1. Verify that the Firebase project configuration in `backend/firebase-service-account.json` (or the attached service account on Cloud Run) matches the active Firebase project.
2. Check whether the service account key has expired or been revoked in the [GCP IAM console](https://console.cloud.google.com/iam-admin/serviceaccounts).
3. If the key is expired, generate a new key, update the Cloud Run env var or secret, and redeploy.

---

### AI Not Responding (`/api/ai/chat` errors)

1. In the Cloud Run console, go to **Edit & Deploy New Revision** > **Variables & Secrets** and confirm `GEMINI_API_KEY` is set.
2. Test the key directly against the Gemini API to confirm it is valid.
3. If the key is invalid or quota-exhausted, rotate it (see **Secrets Rotation** below).

---

### Firestore Errors

1. Open the [Firestore console](https://console.cloud.google.com/firestore) and check for quota limits or service disruptions.
2. Verify the Cloud Run service account has the `Cloud Datastore User` IAM role (or equivalent Firestore access).
3. Check GCP status page for regional Firestore incidents.

---

## Rollback Procedure

Rolling back takes approximately 30 seconds and requires no redeployment.

1. Open the [Cloud Run console](https://console.cloud.google.com/run) → select `logfi` → **Revisions** tab.
2. Find the last stable revision.
3. Click **Manage Traffic**.
4. Set that revision to receive 100% of traffic.
5. Save. Traffic shifts immediately; verify with the health check.

---

## Secrets Rotation

### GEMINI_API_KEY

1. Go to [Google AI Studio](https://aistudio.google.com/) and generate a new API key.
2. In the Cloud Run console, open **Edit & Deploy New Revision** > **Variables & Secrets**.
3. Update `GEMINI_API_KEY` with the new value.
4. Deploy the revision. The old key can be deleted from Google AI Studio after confirming the new one is working.

---

## Backup Check

Firestore data is exported daily to a GCS bucket.

To verify the backup job is running:

1. Open [Cloud Scheduler](https://console.cloud.google.com/cloudscheduler) in `europe-west1`.
2. Confirm the Firestore export job ran successfully within the last 24 hours (status: **Success**).
3. Spot-check the export files in the target GCS bucket via [Cloud Storage](https://console.cloud.google.com/storage).

If the job has not run, trigger it manually and investigate the failure reason in Cloud Scheduler logs.

---

## Escalation

If Bar Pesso is unavailable and the issue cannot wait:

Contact Logi Group management via [bar@logigroup.co](mailto:bar@logigroup.co) and escalate to the team lead on duty.
