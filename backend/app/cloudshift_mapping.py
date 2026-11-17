
# CloudShift - Cloud Service Mapping Catalogue

# These mappings identify potential functional alternatives.
# They do not guarantee identical features or compatibility.

SERVICE_MAPPINGS = {
    "Amazon EC2": {
        "category": "Compute",
        "source_provider": "Amazon Web Services",
        "targets": {
            "Microsoft Azure": [
                {
                    "service": "Azure Virtual Machines",
                    "reason": "Virtual machine compute alternative"
                }
            ],
            "Google Cloud": [
                {
                    "service": "Compute Engine",
                    "reason": "Virtual machine compute alternative"
                }
            ]
        }
    },

    "Azure Virtual Machines": {
        "category": "Compute",
        "source_provider": "Microsoft Azure",
        "targets": {
            "Amazon Web Services": [
                {
                    "service": "Amazon EC2",
                    "reason": "Virtual machine compute alternative"
                }
            ],
            "Google Cloud": [
                {
                    "service": "Compute Engine",
                    "reason": "Virtual machine compute alternative"
                }
            ]
        }
    },

    "Compute Engine": {
        "category": "Compute",
        "source_provider": "Google Cloud",
        "targets": {
            "Amazon Web Services": [
                {
                    "service": "Amazon EC2",
                    "reason": "Virtual machine compute alternative"
                }
            ],
            "Microsoft Azure": [
                {
                    "service": "Azure Virtual Machines",
                    "reason": "Virtual machine compute alternative"
                }
            ]
        }
    },

    "Amazon S3": {
        "category": "Storage",
        "source_provider": "Amazon Web Services",
        "targets": {
            "Microsoft Azure": [
                {
                    "service": "Azure Blob Storage",
                    "reason": "Object storage alternative"
                }
            ],
            "Google Cloud": [
                {
                    "service": "Cloud Storage",
                    "reason": "Object storage alternative"
                }
            ]
        }
    },

    "Azure Blob Storage": {
        "category": "Storage",
        "source_provider": "Microsoft Azure",
        "targets": {
            "Amazon Web Services": [
                {
                    "service": "Amazon S3",
                    "reason": "Object storage alternative"
                }
            ],
            "Google Cloud": [
                {
                    "service": "Cloud Storage",
                    "reason": "Object storage alternative"
                }
            ]
        }
    },

    "Cloud Storage": {
        "category": "Storage",
        "source_provider": "Google Cloud",
        "targets": {
            "Amazon Web Services": [
                {
                    "service": "Amazon S3",
                    "reason": "Object storage alternative"
                }
            ],
            "Microsoft Azure": [
                {
                    "service": "Azure Blob Storage",
                    "reason": "Object storage alternative"
                }
            ]
        }
    },

    "Amazon RDS": {
        "category": "Database",
        "source_provider": "Amazon Web Services",
        "targets": {
            "Microsoft Azure": [
                {
                    "service": "Azure Database for PostgreSQL",
                    "reason": "Potential managed PostgreSQL alternative; verify source engine"
                },
                {
                    "service": "Azure SQL Database",
                    "reason": "Managed relational database alternative; engine compatibility must be checked"
                }
            ],
            "Google Cloud": [
                {
                    "service": "Cloud SQL",
                    "reason": "Managed relational database alternative; verify supported database engine"
                }
            ]
        }
    },

    "Azure Database for PostgreSQL": {
        "category": "Database",
        "source_provider": "Microsoft Azure",
        "targets": {
            "Amazon Web Services": [
                {
                    "service": "Amazon RDS",
                    "reason": "Potential managed PostgreSQL alternative"
                }
            ],
            "Google Cloud": [
                {
                    "service": "Cloud SQL",
                    "reason": "Potential managed PostgreSQL alternative"
                }
            ]
        }
    },

    "Azure SQL Database": {
        "category": "Database",
        "source_provider": "Microsoft Azure",
        "targets": {
            "Amazon Web Services": [
                {
                    "service": "Amazon RDS",
                    "reason": "Potential relational database alternative; verify SQL Server compatibility"
                }
            ],
            "Google Cloud": [
                {
                    "service": "Cloud SQL",
                    "reason": "Potential relational database alternative; verify SQL Server compatibility"
                }
            ]
        }
    },

    "Cloud SQL": {
        "category": "Database",
        "source_provider": "Google Cloud",
        "targets": {
            "Amazon Web Services": [
                {
                    "service": "Amazon RDS",
                    "reason": "Managed relational database alternative; verify database engine"
                }
            ],
            "Microsoft Azure": [
                {
                    "service": "Azure Database for PostgreSQL",
                    "reason": "Potential PostgreSQL alternative; verify database engine"
                },
                {
                    "service": "Azure SQL Database",
                    "reason": "Potential relational database alternative; verify database engine"
                }
            ]
        }
    }
}


def get_service_mapping(source_service, target_provider):
    """
    Find potential target services for a source service.
    """

    mapping = SERVICE_MAPPINGS.get(source_service)

    if not mapping:
        return None

    target_services = mapping["targets"].get(target_provider)

    if not target_services:
        return None

    return {
        "source_service": source_service,
        "source_provider": mapping["source_provider"],
        "target_provider": target_provider,
        "category": mapping["category"],
        "target_services": target_services,
        "compatibility_notice": (
            "Potential functional alternatives only. "
            "Verify configuration, database engine, "
            "features and application compatibility before migration."
        )
    }
