# Lesson 1: Azure Fundamentals & Account Setup

## Concepts Learned

### Azure Resource Hierarchy
Azure organizes resources in a three-tier hierarchy:

1. **Subscription** — Billing boundary and access scope
   - You have one or more subscriptions
   - All costs are rolled up to a subscription

2. **Resource Group** — Logical container for related resources
   - Allows you to group resources that work together
   - Simplifies management, access control, and billing allocation
   - Naming convention: `rg-<workload>-<environment>-<region>`

3. **Resources** — Individual Azure services
   - Storage Accounts, Databases, Virtual Machines, etc.
   - Each resource belongs to exactly one Resource Group

### Key Architectural Decisions

**Data Warehouse Context:**
- **OLTP** (Online Transactional Processing): Real-time transactional systems (create, read, update, delete operations)
- **OLAP** (Online Analytical Processing): Data warehousing and analytics (aggregate queries, historical analysis)
- Our MeteoSchweiz pipeline is an OLAP system

**Storage Strategy:**
- Raw data should be stored in **cloud storage** (not locally)
- This enables scalability and integration with cloud processing services
- Azure Data Lake Storage Gen2 is optimized for analytics workloads

### Azure Pricing Considerations

- **Region matters**: Pricing varies by geography (West Europe typically more expensive than North Europe)
- **Data residency**: Legal/compliance requirements may dictate where data must be stored
- **Cost vs. convenience trade-off**: Switzerland North (local) vs. North Europe (cheaper)

## What We Built

- **Resource Group**: `rg-meteoschweiz-dev`
- **Region**: Switzerland North (data residency + geographic proximity)
- **Environment**: Development (`dev`)

## Architecture Designed

Raw Data (MeteoSchweiz)
↓
Azure Data Lake Storage Gen2 (store raw CSV)
↓
Azure Databricks (process with Python)
↓
Azure SQL Database (data warehouse)
↓
Power BI (dashboards & reports)


### Component Purposes

- **Azure Data Lake Storage Gen2**: Stores raw CSV files in hierarchical structure
- **Azure Databricks**: Python-based data processing and transformation
- **Azure SQL Database**: OLAP data warehouse for analytical queries
- **Power BI**: Visualization and dashboard layer

## Key Decision Framework

When making architecture decisions, balance:
1. **Cost** 
2. **Geography** — Data residency, latency, compliance
3. **Practicality** — What makes sense for your use case?
4. **Learning value**

## Next Steps

- Provision Azure Data Lake Storage Gen2
- Set up data container and folder structure
- Begin data ingestion planning