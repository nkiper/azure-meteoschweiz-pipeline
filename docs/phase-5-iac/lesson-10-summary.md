# Lesson 10: Terraform Fundamentals

## Overview

The last lesson in the original plan. Rather than building new infrastructure, this lesson described the project's already-existing, already-working Azure resources as Terraform configuration, then brought them under Terraform's management via `import` — without destroying or recreating anything. Most of the real learning came from import's limitations, discovered directly rather than just read about.

## Concepts Learned

### Why Terraform, declarative vs. imperative, and state
- Terraform gives repeatable, reviewable infrastructure changes — the practical case raised was reproducing this environment for a second stage (e.g., dev → prod), not just documentation.
- Declarative: a `.tf` file describes the desired end state; Terraform diffs that against what it believes already exists and only acts on the difference. Confirmed directly — a second `plan` against unchanged config and already-matching state showed zero actions.
- **The state file, not Azure itself, is what Terraform diffs against.** Azure's API can report what resources exist, but has no concept of which resources belong together as one Terraform-managed configuration, or which block in a `.tf` file "owns" which real resource — that mapping lives only in state.
- State is local by default (`terraform.tfstate`), contains a full, often sensitive, description of the infrastructure, and must be treated like `.env` — never committed. A remote backend (e.g., Azure Blob Storage) solves the multi-person/multi-machine coordination problem a local file can't; not needed for a solo project, but worth knowing why it exists.

### Import, and its central limitation
`terraform import <resource_address> <azure_resource_id>` tells Terraform "this already exists in Azure — associate it with this config block and record its real attributes in state," without attempting to create anything.

**The limitation that mattered most this lesson**: import populates **state**, not the **configuration file**. A minimal resource block (just enough to make `plan` succeed before import) will very likely not match every real attribute of the actual resource. The `plan` run immediately after each import is what surfaces the gap — and reading that `plan` in full, every time, is non-negotiable given what it caught.

### Scope decision: core resources only
Decided deliberately, before importing anything: Terraform manages the resource group, storage account, SQL server, SQL database, and Databricks workspace — stable resources that rarely change shape. The Databricks cluster (started/stopped by hand, not a fixed-shape resource) and all table schemas/data (owned by the project's Python scripts and notebook, changing constantly by design) are explicitly out of scope. Terraform's job is the shape of the infrastructure, not what runs on it or what's stored in it.

### Three real import outcomes, three different follow-ups

**1. Storage account — destroy and recreate, caught before it happened.**
A minimal config (missing `is_hns_enabled` and `account_kind`) produced a plan to destroy and recreate the storage account, because `is_hns_enabled` cannot be changed in place on an existing account (Azure requires a new account for that) and the provider's default (`false`) didn't match the real, deliberately-configured value (`true`, set back in Lesson 2 to make this a Data Lake Storage Gen2 account). Caught by reading the plan output and its `# forces replacement` flag — not applied. Fixed by running `terraform state show` on the already-imported resource to read back its real attributes, then adding them to the config explicitly. Had this been applied, every file in ADLS would have been lost.

**2. SQL database — silent drift back to a different default.**
A minimal config produced an "update in-place" changing `storage_account_type` from `"Local"` to `"Geo"` — not a missing attribute this time, but the provider's default overriding a decision made deliberately in Lesson 3 (no geo-redundancy needed for a dev database). Fixed by setting `storage_account_type = "Local"` explicitly.

**3. SQL server — a value Azure never returns, requiring a real `apply`.**
Azure's API does not return the admin password on read, so `import` left state with no record of it at all, even though a real password exists on the server. The resulting "update in-place" plan wasn't wrong or dangerous — it was the only way to get the value into state, since nothing to diff against existed. Confirmed the `terraform.tfvars` value matched the actual working password before applying (a mismatched value here would have actually changed the server's real password and broken every other credential store referencing it — `.env`, the Databricks secret scope, the saved VS Code connection).

### `sensitive` vs. `ephemeral`
Tried `sensitive = true` together with `ephemeral = true` on the SQL password variable, following Terraform's general documentation. Failed: `administrator_login_password` on `azurerm_mssql_server` is not a "write-only" attribute and must be persisted to state, so `ephemeral` isn't valid for it specifically. `ephemeral` only works on resource/attribute combinations that explicitly support write-only semantics — not a universal substitute for `sensitive`. Resolved by dropping `ephemeral`, keeping `sensitive` (masks CLI/plan output only — the value still lives in state, which is why `terraform.tfstate` must stay out of version control).

### A setting that doesn't exist independently of another
The Databricks workspace's `public_network_access_enabled` showed as a pure addition (not a change) after import — the Portal's own toggle was greyed out and an Azure CLI query for the value returned nothing. Traced to a real dependency: disabling public network access on a Databricks workspace requires VNet injection to be configured first, which this project deliberately declined back in Lesson 5. With no VNet injection, the setting has no independently-stored value to report — Azure defaults it to enabled and there's nothing to toggle. Setting it explicitly to `true` in config and running `apply` returned a connection-reset error, but the change had actually completed server-side; confirmed via a follow-up `plan` (no changes) and `state show`.

## Verification Performed

Every resource, after import: a full `terraform plan` read end-to-end (not just the summary line) before trusting "no changes" or applying anything. Two of five imports needed a config fix before reaching that state; one needed an actual `apply` to populate a value Azure doesn't return on read.

## What We Built

- `terraform/providers.tf` — `azurerm` provider (version `~> 5.0`), authenticated via the existing Azure CLI session
- `terraform/terraform.tfvars` (git-ignored) — SQL admin password
- Five imported resources: `azurerm_resource_group`, `azurerm_storage_account`, `azurerm_mssql_server`, `azurerm_mssql_database`, `azurerm_databricks_workspace`
- `.gitignore` updated for `.terraform/`, `*.tfstate`, `*.tfstate.backup`, `terraform.tfvars`
- `ARCHITECTURE.md` updated with Terraform's scope and known gaps

## Next Steps

This was the last lesson in the original curriculum. Remaining open items (not part of a planned lesson): deciding whether to formalize a dev/prod-style second environment now that the core resources are codified; whether the Databricks cluster is ever worth modeling in Terraform if its configuration stabilizes; cleaning up the still-present `processed/historical` ADLS files and backfill scripts from the abandoned daily-history attempt (Lesson 8b).