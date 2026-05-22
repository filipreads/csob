# One-click deployment

## Option 1: GitHub Actions + Docker
1. Push this repo to GitHub.
2. Make sure the branch is `main`.
3. The workflow builds and pushes a container image to GHCR on every push.
4. Deploy the image from GHCR to your host of choice.

## Option 2: Run locally
```bash
docker build -t finance-dashboard .
docker run -p 8501:8501 finance-dashboard
```

## Files
- `Dockerfile`
- `.github/workflows/deploy.yml`
- `app.py`
- `requirements.txt`
