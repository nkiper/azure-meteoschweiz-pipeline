# Lesson 2: Azure Data Lake Storage Gen2 Setup

## Concepts Learned

### Azure Storage Accounts
- Parent container for all storage services in Azure
- Acts as a namespace for all storage objects
- Each must have a globally unique name

### Data Lake Storage Gen2 vs Blob Storage
- **Blob Storage**: Flat structure, optimized for unstructured data
- **ADLS Gen2**: Hierarchical namespace, folder structure, optimized for analytics

### Access Control
- **Storage Account Keys**: Full access to all resources in the account (use carefully)
- **Shared Access Signatures (SAS)**: Limited, time-bound access to specific resources (safer for sharing)
- **Hierarchical namespace**: Enables file-like directory structure for analytics workloads

### Storage Tiers
- **Hot**: Frequent access, higher compute cost, lower storage cost
- **Cool**: Infrequent access (>30 days), lower compute cost, higher storage cost
- **Archive**: Long-term retention, cheapest storage, slowest access

### Redundancy Options
- **LRS (Locally Redundant Storage)**: Data replicated 3x in one data center (cheapest, lowest durability)
- **GRS/GZRS**: Geo-redundant, replicated across regions (higher cost, higher durability)

## What We Built

- **Storage Account**: `nkipermeteo`
- **Region**: Switzerland North
- **Performance**: Standard (cost-optimized)
- **Redundancy**: LRS (acceptable for non-critical data)
- **Access Tier**: Hot (for active development)
- **Container**: `data`
- **Folder Structure**:

data/
├── raw/ (incoming MeteoSchweiz CSVs)
├── processed/ (transformed data)
└── docs/ (metadata, schemas)


## Key Decisions Made

1. **One container** for all data stages (raw → processed)
2. **LRS redundancy** since this is a learning project
3. **Hot tier** for frequent access during development
4. **Hierarchical namespace enabled** for true file semantics

## Next Steps

- Upload sample MeteoSchweiz data to `raw/` folder
- Create data schema documentation in `docs/` folder
- Set up authentication for Databricks to access this storage