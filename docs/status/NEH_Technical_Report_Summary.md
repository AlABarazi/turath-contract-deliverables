# Turath Project: NEH Technical Report Summary

**Date:** October 26, 2025  
**Subject:** Technical Achievements and System Capabilities for NEH Grant Reporting  
**Purpose:** This document provides the technical input detailing what was built, what works, and what was accomplished during this phase of the Turath project, directly supporting the objectives outlined in the NEH DHAG (Level I) Grant.

---

## 1. Fulfilling the Infrastructure Vision: InvenioRDM Deployment
Following the project's technical evaluation exercise, InvenioRDM was selected as Turath’s primary data repository due to its scalability, security, and interoperability. In this phase, we successfully transitioned this vision into a fully operational, production-ready reality. 

We successfully harnessed InvenioRDM’s extensibility to tailor it specifically for housing and managing historical materials—specifically aligning with the *Chronicles of Arabia* initiative. Scanned images of the chronicles, alongside their complex metadata, have been successfully ingested into a robust, cloud-native environment capable of efficiently accommodating Turath's diverse digital formats.

## 2. Key Technical Milestones & Innovations

### A. Unified Native Exploration (IIIF & Mirador 3)
Previously, the project relied on short-term solutions (such as TEI Publisher) to provide end-users with text-based search and exploration capabilities. We have now successfully integrated a deeply customized native viewer directly into the repository.
*   **Dynamic IIIF Manifests:** The system automatically maps multi-page PDFs to individual high-resolution image canvases using the International Image Interoperability Framework (IIIF).
*   **Custom Mirador Implementation:** We deployed a deeply integrated Mirador 3 viewer using a custom Webpack injection strategy, providing users with seamless deep-zoom capabilities, page navigation, and metadata context without leaving the platform.
*   **High-Performance Tiling:** Deployed the Cantaloupe image server with a bespoke cache "pre-warming" strategy to instantly generate and serve pyramidal image tiles for massive, high-resolution manuscript pages.

### B. Bespoke Arabic Full-Text Search (HOCR)
To fulfill the requirement of exploring the digital text of the chronicles natively, we engineered a highly specialized full-text search subsystem optimized for the Arabic language.
*   **HOCR Data Ingestion:** The pipeline now ingests raw PDFs alongside corresponding HOCR (HTML-based Optical Character Recognition) files, which map precise word-level bounding boxes.
*   **Custom OpenSearch Mapping:** We extended the core InvenioRDM data model with a custom `turath:fulltext` field, mapped in OpenSearch using a specialized Arabic text analyzer that handles language-specific stemming and stop-word removal.
*   **Search Microservice:** We developed a lightweight, independent microservice that handles IIIF Content Search API requests. End-users can now search for specific Arabic phrases *within* the Mirador viewer, which instantly highlights the exact location of the word on the scanned manuscript image.

### C. Scalable Cloud Infrastructure & Sustainability
To ensure the long-term impact, preservation, and sustainability of Turath's digital materials, the platform was migrated to a highly resilient cloud architecture.
*   **Containerized Microservices:** Deployed on Amazon Web Services (AWS ECS Fargate), the application is split into specialized Docker containers, allowing independent scaling of the UI, backend API, background workers, and image servers.
*   **Infrastructure as Code (IaC):** The entire platform is codified using Terraform. This ensures reproducible deployments and has prepared the platform for a seamless future migration to institutional servers (e.g., Harvard AWS).
*   **Automated CI/CD:** Implemented a GitHub Actions pipeline that automatically builds and securely registers Docker images, streamlining deployments and minimizing maintenance overhead.

## 3. Advancing the Strategic AI Vision (RAG Readiness)
The NEH grant outlined a strategic vision for adopting Knowledge Graphs and Large Language Models (LLMs) via Retrieval Augmented Generation (RAG). The goal is to use Turath's curated content to mitigate known LLM challenges (hallucinations, lack of citations, prompt sensitivity) and enable context-aware document linking and smart searching.

During this phase, we conducted a technical feasibility study proving that the new infrastructure is fully **"AI-Ready."**
*   **API Capabilities:** We documented and verified that the system's REST APIs can programmatically serve deeply structured metadata alongside clean, page-level OCR text.
*   **Zero OCR Overhead for AI:** Because the platform exposes pre-processed text via IIIF annotation endpoints, future RAG pipelines can ingest document chunks that align perfectly with LLM context windows without having to perform expensive, consumer-side PDF parsing.
*   **Citation-Backed Generation:** By returning exact `x,y,w,h` coordinates for text, future AI models can provide exact visual citations on the original manuscript, directly addressing the ethical and explainability concerns raised in the grant.

## 4. Conclusion
The technological framework developed in this phase leaves the Turath project with a highly customized, production-ready repository. By pushing beyond the out-of-the-box capabilities of open-source repository software, the team has successfully laid the robust foundational infrastructure required for the project's next phases of advanced digital humanities exploration and AI integration.
