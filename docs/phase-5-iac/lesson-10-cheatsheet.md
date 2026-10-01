# Lesson 10 Cheatsheet: Terraform Fundamentals

## Core Workflow

```bash
terraform init      # downloads providers, creates .terraform/ (gitignore) and .terraform.lock.hcl (commit)
terraform plan       # dry run — ALWAYS read in full, especially any "# forces replacement"
terraform apply      # executes the plan, asks for confirmation
terraform import <resource_address> <azure_resource_id>   # associate an existing resource with a config block
terraform state show <resource_address>    # see everything state actually knows about a resource
```

## `.gitignore` for Terraform

```
terraform/.terraform/
terraform/*.tfstate
terraform/*.tfstate.backup
terraform/terraform.tfvars
```
Commit `.terraform.lock.hcl`. Never commit state or `.tfvars` — both can contain real secrets/resource details in plain text.

## Import Only Populates State, Never Config

After `import`, `plan` will likely show changes — not because something is wrong, but because your config block probably doesn't yet describe every real attribute. Three distinct outcomes to recognize:

| Plan shows | Means | Action |
|---|---|---|
| `-/+ destroy and then create replacement` | Config is missing/wrong on an attribute that **can't change in place** | **Do not apply.** Run `state show`, copy the real value into config, re-plan |
| `~ update in-place` on something you deliberately set before | Provider **default** differs from your real, intentional setting | Set the value explicitly in config to match reality |
| `~ update in-place` adding a value with no prior state | Azure's API **doesn't return this value on read** (e.g. a password) | Confirm the value in your variable is actually correct, then `apply` — this is the only way to get it into state |

**Always read the full plan, not just the summary line (`N to add, N to change, N to destroy`).** The summary alone doesn't tell you *which* resource or *why*.

## Variables and Secrets

```hcl
variable "admin_password" {
  type        = string
  description = "SQL server admin password"
  sensitive   = true   # masks value in CLI/plan output only — still written to state
}
```
```
# terraform.tfvars (gitignored)
admin_password = "..."
```
- `sensitive` ≠ secure storage — the value still lands in `terraform.tfstate` in plain text.
- `ephemeral = true` prevents persistence to state entirely, but **only works on attributes the specific resource/provider marks as write-only**. Check before combining it with `sensitive` — not every sensitive attribute supports it (`administrator_login_password` on `azurerm_mssql_server` does not; fails with "Invalid use of ephemeral value").

## A Setting Can Be Unconfigurable Because of a Different Setting

Some resource attributes have real dependencies (e.g., disabling public network access on a Databricks workspace requires VNet injection first). A greyed-out Portal control, an empty CLI query result, and a Terraform plan that shows pure *addition* rather than *change* for the same attribute are all consistent with "this isn't independently set" — worth checking the dependency before assuming it's a bug or an oversight.

## Scope Decision

Terraform: resource shape (does it exist, with the right settings). Not Terraform: anything that changes by design — running compute (clusters), schemas and data (tables, rows), transient/temporary resources. Decide and document this boundary before importing, not after.

## Error Messages Aren't Always the Full Story

A `apply` can fail with a connection-level error (`HTTP response was nil; connection may have been reset`) even when the underlying change succeeded server-side. Confirm with a fresh `plan` (expect "No changes" if it actually went through) and `state show`, rather than assuming the error means nothing happened.