# Product Requirements Document: AI-Powered Social Media Content Generation

## 1. Introduction

This document outlines the requirements for a Python-based application designed to generate social media posts. The application will leverage AI agents to research relevant topics, distill them for a specific application (e.g., a note-taking app like Tuon.io), and then create engaging social media content. The primary goal is to produce accurate, meaningful, and contextually relevant posts that address current user pain points and highlight the app's benefits.

## 2. Goals

*   Automate the creation of research-backed social media posts.
*   Ensure content is accurate, up-to-date, and relevant to the target audience.
*   Highlight the unique selling propositions of the application (e.g., Tuon.io) by addressing current pain points in its domain (e.g., note-taking in the AI era).
*   Streamline the content creation workflow by integrating multiple AI agents.
*   Produce engaging and effective social media copy.

## 3. Target Audience

Social media users, potential customers of the application being marketed (e.g., Tuon.io users), and individuals interested in the application's domain (e.g., productivity, AI, note-taking).

## 4. Overall Workflow

The application will consist of a three-stage pipeline:

1.  **Search Agent:** Utilizes Perplexity AI to search for recent and relevant topics, articles, discussions, or posts based on a given input theme or keyword.
2.  **Reviewer Agent:** Employs Gemini 2.5 Flash to process the content gathered by the Search Agent. It will distill this information, identify key pain points, and extract topics that can be effectively used to market the specified application.
3.  **Editor Agent:** Leverages Gemini 2.5 Pro to take the curated list of topics and pain points from the Reviewer Agent and craft engaging, high-quality social media posts.

## 5. Functional Requirements

### 5.1. Input
*   User provides an initial topic or theme for research (e.g., "pain points in current note-taking apps," "AI impact on productivity tools").
*   User provides the name and a brief description of the application to be marketed (e.g., "Tuon.io - a note-taking app that integrates AI into the creative workflow").

### 5.2. Search Agent (Perplexity)
*   Accepts the input topic/theme.
*   Queries Perplexity API to find recent and relevant articles, blog posts, forum discussions, social media threads, etc.
*   Returns a collection of search results, including URLs and snippets of text.
*   Handles API errors and retries gracefully.

### 5.3. Reviewer Agent (Gemini 2.5 Flash)
*   Accepts the search results from the Search Agent.
*   Processes the text content from the search results.
*   Identifies key themes, pain points, and interesting angles relevant to the application being marketed.
*   Outputs a structured list of distilled topics and talking points.
*   Focuses on extracting information that can be framed to highlight the benefits of the target application.

### 5.4. Editor Agent (Gemini 2.5 Pro)
*   Accepts the distilled topics and talking points from the Reviewer Agent.
*   Generates multiple social media post variations (e.g., for Twitter, LinkedIn, Facebook) for each topic.
*   Ensures posts are engaging, concise, and include relevant hashtags.
*   Maintains a consistent tone of voice aligned with the application's brand.
*   Allows for easy review and selection of the generated posts.

### 5.5. Output
*   A set of social media posts ready for publishing.
*   Optionally, a summary of the research and distilled topics.

## 6. Non-Functional Requirements

*   **Modularity:** Each agent should be a distinct module, allowing for independent development, testing, and potential replacement.
*   **Configurability:** API keys (PERPLEXITY_API_KEY, GOOGLE_API_KEY) should be configurable via environment variables or a configuration file.
*   **Extensibility:** The system should be designed to easily accommodate new social media platforms or different AI models in the future.
*   **Error Handling:** Robust error handling and logging should be implemented throughout the workflow.
*   **Performance:** The workflow should execute within a reasonable timeframe for generating a batch of social media posts.

## 7. Technical Stack

*   **Programming Language:** Python
*   **Key Libraries/SDKs:**
    *   Perplexity AI API Client
    *   Google Generative AI SDK (for Gemini models)
    *   Requests (or similar for HTTP calls if dedicated SDKs are not sufficient)
*   **Environment Management:** `venv`

## 8. Future Considerations (Out of Scope for V1)

*   User interface for managing inputs and viewing outputs.
*   Direct integration with social media scheduling tools.
*   Automated performance tracking of generated posts.
*   Advanced topic trend analysis.
*   Support for more complex input formats (e.g., entire articles, competitor websites).
*   Human-in-the-loop feedback mechanism for refining agent outputs.

## 9. API Keys
The following API keys are required:
*   `PERPLEXITY_API_KEY`
*   `GOOGLE_API_KEY`
(These should be stored securely and not hardcoded into the application.)
