# Turath Project: NEH Technical Report Summary

**Date:** October 26, 2025
**Subject:** Technical Achievements and System Capabilities for NEH Grant Reporting

## 1. Executive Summary of Technical Architecture
The Turath project has successfully designed and deployed a robust, highly customized instance of the InvenioRDM (Research Data Management) framework. The system is engineered to handle large-scale digitized Arabic manuscripts and historical texts, providing advanced capabilities that go significantly beyond out-of-the-box open-source repository software.

The platform is deployed using a modern, containerized architecture (Docker) orchestrated on Amazon Web Services (AWS ECS Fargate), ensuring high availability, scalable performance, and rigorous data persistence.

## 2. Key Technical Milestones & Innovations

### A. Advanced IIIF Integration & Mirador Viewer
We successfully implemented the International Image Interoperability Framework (IIIF) to provide a world-class viewing experience for multi-page digitized books.
*   **Dynamic Manifest Generation:** The system automatically generates complex IIIF manifests (Presentation API 2.1) upon ingestion, mapping multi-page PDFs to individual high-resolution image canvases.
*   **Custom Mirador Implementation:** We bypassed legacy Invenio plugins to implement a modern, deeply integrated Mirador 3 viewer using a custom Webpack JavaScript injection strategy. This provides users with deep-zoom capabilities, page navigation, and metadata context in a seamless UI.
*   **Cantaloupe Image Server:** Deployed the Java-based Cantaloupe server to dynamically generate and cache pyramidal image tiles, ensuring rapid loading times for massive, high-resolution manuscript pages.

### B. Arabic Full-Text OCR Search (HOCR)
One of the most significant technical achievements is the implementation of a bespoke full-text search engine optimized for Arabic text.
*   **HOCR Data Ingestion:** The system pipeline ingests raw PDFs alongside their corresponding HOCR (HTML-based Optical Character Recognition) files containing precise word-level bounding boxes.
*   **Custom OpenSearch Mapping:** We extended the core InvenioRDM data model with a custom `turath:fulltext` field. We mapped this field in OpenSearch using a specialized Arabic text analyzer that handles language-specific stemming and stop-word removal.
*   **Microservice Architecture:** We developed a lightweight, independent Python microservice (running alongside the main application) specifically to handle IIIF Content Search API requests. This allows users to search for specific Arabic phrases *within* the Mirador viewer, instantly highlighting the exact location of the word on the scanned image.

### C. Scalable Cloud Infrastructure (AWS)
The platform is fully codified using Terraform (Infrastructure as Code), allowing for rapid, reproducible deployments.
*   **Containerized Microservices:** The application is split into specialized Docker containers (Web UI, Web API, Celery Workers, Search Service, Image Server), allowing independent scaling of resources.
*   **Persistent Shared Storage:** We utilize Amazon Elastic File System (EFS) to create a shared, persistent filesystem. This allows the backend metadata application and the frontend image servers to instantly access massive PDF and HOCR files without redundant data copying.
*   **Automated CI/CD Pipeline:** A GitHub Actions pipeline automatically builds Docker images upon code commits and pushes them to a secure registry, streamlining the deployment process and minimizing human error.

### D. RAG (Retrieval-Augmented Generation) Readiness
We conducted a feasibility study proving that the system's REST APIs are fully "AI-Ready." The platform can successfully serve deeply structured metadata alongside clean, page-level OCR text, making it an ideal foundational data source for future AI applications, such as an Arabic historical chatbot or automated document summarization pipeline.

## 3. Extensibility and Future-Proofing
The system is built with a flexible "Extensibility Framework." Rather than hardcoding Turath-specific requirements into the core engine, we utilized configuration overrides. This ensures that:
1.  We can easily add new metadata fields (e.g., specific scribe names or geographic coordinates) in the future.
2.  We can easily migrate the entire architecture from our current AWS environment to institutional servers (e.g., Harvard AWS) using our existing Terraform scripts.
3.  We remain compatible with future upgrades of the upstream InvenioRDM software.
