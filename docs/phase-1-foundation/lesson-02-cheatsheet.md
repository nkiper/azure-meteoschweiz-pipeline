# Lesson 2 Cheatsheet: Azure Data Lake Storage Gen2

## Quick Reference

### Storage Account Naming
- **Length**: 3-24 characters
- **Characters**: Lowercase alphanumeric only
- **Must be globally unique** across all of Azure

### Hierarchy

Storage Account
└── Container (like a bucket)
└── Folders/Directories
└── Files


### Access Methods
| Method | Use Case | Security |
|--------|----------|----------|
| Storage Key | Admin access | Full access, use carefully |
| SAS | Sharing specific resources | Time-bound, scoped access |
| Managed Identity | Azure service auth | Best for service-to-service |

### Performance Tiers for Learning
- **Standard**: Good default for learning and testing
- **Premium**: Overkill for this project

### Redundancy Decision Matrix
| Redundancy | Durability | Cost | Use Case |
|-----------|-----------|------|----------|
| LRS | Low-Medium | Lowest | Non-critical, learner projects |
| GRS | High | Medium | Production data |
| GZRS | Very High | High | Mission-critical data |

### Folder Structure Pattern

data/
├── raw/ ← Raw incoming data (never modify)
├── processed/ ← Cleaned, transformed data
└── docs/ ← Schemas, metadata, documentation


### Important Settings
- ✅ **Enable Hierarchical Namespace** — Required for Data Lake Gen2
- ✅ **Hot tier for development** — Balance cost and access speed
- ✅ **LRS for non-critical data** — Acceptable trade-off for learning

### Common Tasks
- **Upload files**: Use Azure Portal → Container → Upload
- **Create folders**: Navigate to container, click "+" → New Folder
- **View access keys**: Storage Account → Access Keys
- **Generate SAS**: Storage Account → Shared access signature → Generate SAS and connection string