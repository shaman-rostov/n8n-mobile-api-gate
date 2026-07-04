# Privacy Policy — Orqflow

**Last updated: 2026-07-05**

## Summary

Orqflow does not collect, transmit, or share any personal data.

## Data stored on your device

Orqflow stores the following data **locally on your device only**:

| Data | Where | Purpose |
|------|-------|---------|
| Server URL | iOS Keychain | Connect to your n8n instance |
| Basic Auth credentials | iOS Keychain | HTTP Basic Auth (optional) |
| Gateway Token | iOS Keychain | Authenticate API requests |
| App language preference | UserDefaults | Display language |
| Widget cache (workflow counts) | App Group UserDefaults | Home screen widget |
| Debug log | Documents directory | Troubleshooting (max 1 MB / 7 days) |

All credentials are stored in the **iOS Keychain** with `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` — they are not backed up to iCloud, not synced to other devices, and not accessible to other apps.

## Network

Orqflow communicates **only with the n8n server you configure**. No data is sent to the developer, to analytics services, or to any third party.

## Third-party SDKs

Orqflow uses no third-party SDKs, analytics libraries, or advertising frameworks.

## Children

Orqflow is not directed at children under 13 and does not knowingly collect any information from them.

## Changes

If this policy changes, the updated version will be published at this URL with a new date.

## Contact

Questions: open an issue at [github.com/shaman-rostov/n8n-mobile-api-gate](https://github.com/shaman-rostov/n8n-mobile-api-gate/issues)
