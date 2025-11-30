# Architecture Documentation

## Overview
Ciekawa Invoices is an agentic workflow for automating invoice processing. It utilizes Google's Agent Development Kit (ADK) and Vertex AI to extract data from PDF invoices received via email.

## Architectural Pattern
The project follows **Clean Architecture** principles to ensure separation of concerns, testability, and independence from frameworks.

### Layers

1.  **Domain Layer** (`src/domain`)
    *   Contains the core business entities and logic.
    *   Examples: `Email`, `Invoice`, `ProcessingStatus`.
    *   No external dependencies.

2.  **Ports Layer** (`src/ports`)
    *   Defines interfaces (protocols) for external services and repositories.
    *   Examples: `EmailProvider`, `InvoiceRepository`, `LLMProvider`.
    *   Acts as the boundary between the application core and the infrastructure.

3.  **Service Layer** (`src/services`)
    *   Contains the application business rules and use cases.
    *   Orchestrates the flow of data between ports and domain entities.
    *   Examples: `RetrievalService`, `ProcessingService`, `SheetsService`.

4.  **Infrastructure Layer** (`src/infrastructure`)
    *   Concrete implementations of the ports.
    *   Interacts with external APIs and databases.
    *   Examples: `GmailAdapter`, `FirestoreAdapter`, `VertexAIAdapter` (using ADK).

## Components

### 1. Retrieval Service
*   **Responsibility**: Ingests new invoices from the email inbox.
*   **Flow**: Fetch unread emails -> Filter PDFs -> Save to "Raw Data" DB -> Mark email as processed.

### 2. Processing Service
*   **Responsibility**: Extracts structured data from raw invoice PDFs.
*   **Technology**: Google ADK (Agent) + Gemini Flash.
*   **Flow**: Fetch pending raw invoices -> Send to Agent -> Save extracted data -> Update status.

### 3. Sheets Service
*   **Responsibility**: Exports processed data to the user's Google Sheet.
*   **Flow**: Fetch unsynced processed invoices -> Append to Sheet -> Mark as synced.

### 4. Notification Service
*   **Responsibility**: Sends a summary of the workflow execution.

## Data Flow
`Email (Gmail)` -> `RawInvoice (Firestore)` -> `ProcessedInvoice (Firestore)` -> `Google Sheet`
