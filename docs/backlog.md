# Backlog

- [x] Include error messages in summary email
- [ ] **GeminiAdapter doesn't support GCS URIs** - Currently reads files from local path only; needs to download from GCS or use Gemini's native GCS support
- [ ] Collect Sheets sync errors in email - Processing errors are shown, but Sheets sync failures aren't
- [ ] Add health check endpoint for Cloud Run deployment
- [ ] Create Dockerfile and .dockerignore
- [ ] Add graceful error handling for missing config files in cloud (categories.yaml, instruction.md)
