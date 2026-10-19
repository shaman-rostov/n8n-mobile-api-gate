# Privacy Policy — Orqflow

**Last updated: 2026-10-19**

This policy covers Orqflow for iOS and Android.

## Summary

Orqflow does not collect, transmit, or share any personal data.

## Data stored on your device

Orqflow stores the following data **locally on your device only**:

| Data | iOS | Android | Purpose |
|------|-----|---------|---------|
| Server URL | Keychain | Encrypted storage (Android Keystore) | Connect to your n8n instance |
| Basic Auth credentials | Keychain | Encrypted storage (Android Keystore) | HTTP Basic Auth (optional) |
| Gateway Token | Keychain | Encrypted storage (Android Keystore) | Authenticate API requests |
| App language preference | UserDefaults | System per-app language setting | Display language |
| Widget cache (workflow counts) | App Group UserDefaults | App-private storage | Home screen widget |
| Debug log | Documents directory | App-private storage | Troubleshooting (max 1 MB / 7 days) |

On **iOS**, credentials are stored in the Keychain with `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` — they are not backed up to iCloud, not synced to other devices, and not accessible to other apps.

On **Android**, credentials are encrypted with a key held in the Android Keystore. App data is excluded from cloud backup and device-to-device transfer, and is not accessible to other apps.

## Network

Orqflow communicates **only with the n8n server you configure**. No data is sent to the developer, to analytics services, or to any third party.

The iOS app connects over HTTPS only. The Android app also allows plain HTTP so it can reach servers on a local network; such connections are not encrypted, so use HTTPS for any server reachable over the internet.

## Third-party SDKs

Orqflow uses no third-party SDKs, analytics libraries, or advertising frameworks.

## Children

Orqflow is not directed at children under 13 and does not knowingly collect any information from them.

## Changes

If this policy changes, the updated version will be published at this URL with a new date.

## Contact

Questions: open an issue at [github.com/shaman-rostov/n8n-mobile-api-gate](https://github.com/shaman-rostov/n8n-mobile-api-gate/issues)
