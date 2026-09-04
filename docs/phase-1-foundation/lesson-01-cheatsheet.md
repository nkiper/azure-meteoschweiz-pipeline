# Lesson 1 Cheatsheet: Azure Fundamentals

## Azure Resource Hierarchy

Subscription (Billing Boundary)
└── Resource Group (Logical Container)
└── Resources (Individual Services)
├── Storage Accounts
├── Databases
├── Compute Services
└── ...


## Naming Conventions

### Resource Groups

rg-<workload>-<environment>-<region>

Example: rg-meteoschweiz-dev-swn

workload: meteoschweiz
environment: dev, staging, prod
region: swn (Switzerland North), neu (North Europe)

## OLTP vs OLAP

| Aspect | OLTP | OLAP |
|--------|------|------|
| **Purpose** | Real-time transactions | Historical analysis |
| **Operations** | INSERT, UPDATE, DELETE | SELECT, Aggregate queries |
| **Data structure** | Normalized | Denormalized/Star schema |
| **Access pattern** | Small reads/writes | Large batch reads |
| **Example** | Banking app | Data warehouse |

## Azure Regions to Remember

| Region | Location | Typical Cost | Data Residency |
|--------|----------|--------------|-----------------|
| Switzerland North | Switzerland (East) | Medium-High | Within CH |
| North Europe | Ireland | Low | EU |
| West Europe | Netherlands | Medium | EU |

## Key Questions When Making Decisions

- [ ] What's the **primary use case**? (OLTP or OLAP?)
- [ ] Where is the **data coming from**? (Affects ingestion strategy)
- [ ] Where is the **data going**? (Affects output strategy)
- [ ] What's my **cost budget**? (Affects region and tier choices)
- [ ] Are there **compliance requirements**? (Affects region and security)

## Common Mistakes to Avoid

- Choosing a resource type before understanding the workload
- Optimizing for cost without considering practicality
- Not planning resource naming conventions upfront
- Mixing resources from different regions without reason