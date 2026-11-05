# Security policy

## Reporting a vulnerability

Please do not open a public issue for a security problem. Email
**sergey@shinkarenko.eu** with a description, the affected gateway version (or commit) and the
steps to reproduce. You will get an answer as soon as possible; a fix is published here with a
note in the README.

## Supported versions

Only the latest `workflow/orqflow-gateway.json` on the `main` branch receives fixes. If you run an
earlier copy, update it as described in the README (*Upgrading from an earlier gateway*).

## Scope

- The gateway workflow in this repository: authorisation, the action allowlist, parameter
  validation, the requests it makes to the n8n API.
- How the Orqflow apps store and send the connection details.

Vulnerabilities in n8n itself should go to the n8n project.
