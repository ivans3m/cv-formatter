---
schema: cv-md/1.0
name: Lukas Müller
headline: Staff Backend & Distributed Systems Engineer
location: Berlin, Germany
work_authorization: EU Citizen
email: lukas.mueller@example.de
phone: "+49 170 1234567"
links:
  - label: LinkedIn
    url: https://linkedin.com/in/lukasmueller
  - label: GitHub
    url: https://github.com/lukasmueller
  - label: Blog
    url: https://lukasmueller.dev
paper: a4
lang: en
---

## Summary

Staff backend engineer with 9 years of experience designing high-throughput payment, ledger, and event-streaming systems in Go and Python across European fintech scale-ups. Track record of leading zero-downtime architecture migrations, reducing cloud infrastructure spend, and mentoring engineering teams.

## Experience

### Acme Payments Europe
*2021-03 – Present | Berlin, Germany (Hybrid)*

#### Staff Backend Engineer *(2024-01 – Present)*
- Architected multi-region SEPA Instant settlement engine in Go handling €320M/month with 99.99% availability and p99 latency under 85ms.
- Led a cross-team platform reliability initiative across 28 engineers, cutting severity-1 incidents by 65% and mean time to recovery from 42 minutes to 9 minutes.
- Authored internal RFC standards for idempotency, OpenTelemetry tracing, and schema evolution adopted by 6 product squads.
- Partnered with compliance and security teams on DORA operational resilience audits with zero critical findings.

#### Senior Backend Engineer *(2022-04 – 2023-12)*
- Reduced p95 checkout API latency from 420ms to 110ms across 12 Go microservices serving 40K req/s by redesigning Redis caching and PostgreSQL connection pooling.
- Led zero-downtime migration of a €180M/month batch settlement pipeline from a legacy monolith to event-driven Kafka workers.
- Mentored 4 mid-level engineers and introduced automated k6 load testing in GitHub Actions CI.

#### Backend Engineer *(2021-03 – 2022-03)*
- Built an idempotent merchant webhook delivery service in Go processing 2M events/day with 99.98% delivery SLA.
- Automated multi-environment AWS infrastructure provisioning with Terraform and Kubernetes, cutting environment setup time from 3 days to 25 minutes.

### Senior Software Engineer — NordCloud Analytics
*2019-05 – 2021-02 | Berlin, Germany*

- Designed Python and Go ETL pipelines ingesting 1.5B daily clickstream events into BigQuery and PostgreSQL.
- Cut monthly AWS and GCP compute spend by 28% (€14K/month) by migrating batch workloads to spot instances and optimizing SQL partitioning.
- Built real-time anomaly detection alerts for 45 enterprise retail clients, reducing false-positive pages by 52%.
- Collaborated with data scientists to deploy containerized scoring services on Kubernetes with automated canary rollouts.

### Software Engineer — FinBridge GmbH
*2017-07 – 2019-04 | Munich, Germany*

- Developed PSD2 open-banking aggregation connectors in Python integrating 180+ European banks.
- Improved API throughput by 3.2x by introducing asynchronous worker pools and Redis rate-limiting.
- Maintained PostgreSQL ledger schemas and automated nightly reconciliation jobs processing €45M/week.

## Projects

### pg-safe-migrate — Open-Source Maintainer
*2023-01 – Present | [github.com/lukasmueller/pg-safe-migrate](https://github.com/lukasmueller/pg-safe-migrate)*

- Open-source Go CLI linter detecting lock-heavy PostgreSQL migrations in CI (1,400+ GitHub stars, used by 30+ European fintech teams).

## Skills

- **Languages:** Go, Python, SQL
- **Data & Streaming:** PostgreSQL, Redis, Kafka, BigQuery
- **Infrastructure & Observability:** AWS, GCP, Kubernetes, Terraform, OpenTelemetry, GitHub Actions

## Education

### M.Sc. Computer Science — Technical University of Munich
*2015-10 – 2017-06 | Munich, Germany*

### B.Sc. Computer Science — Karlsruhe Institute of Technology
*2012-10 – 2015-09 | Karlsruhe, Germany*

## Certifications

- **CKA: Certified Kubernetes Administrator** — CNCF (2023)

## Languages

- **German:** Native
- **English:** C2 (Proficient / Working Language)
- **French:** B1 (Intermediate)
