# AI-Powered Inventory Locator System

## Project Abstract

For this project, we propose to build an **agentic AI system** to solve one of the most frustrating shopping problems for customers: **out-of-stock items**.  

Picture this: you drive to the pharmacy for cold medicine when you're sick, only to find empty shelves, then waste time calling other stores or driving around town hoping to get lucky.  

Our solution leverages **computer vision** to scan products (via a phone camera), then searches multiple retailers and locations to find where the item is actually available.  

---

## System Design

The system uses a **multi-agent approach** with specialized AI tasks:

-  **Product Identification Agent** – Detects and identifies products from a phone camera.  
-  **Retailer Data Agent** – Searches retailer APIs or websites for stock availability.  
-  **Ranking Agent** – Ranks results by distance, price, and availability.  

---

## Integration & Data Sources

- We plan to integrate with major retailers (e.g., **Walmart**) through their **APIs** where possible.  
- As a backup, **web scraping** will be used if APIs are unavailable.  

---

## Roadmap

-  **Phase 1**: Mobile web app prototype focusing on a few major local retailers.  
-  **Phase 2**: Expand retailer coverage and optimize agent performance.  
-  **Phase 3**: Broader rollout with user feedback and feature enhancements.  

---

## Expected Outcome

The end result will be a system that **saves time and frustration** for shoppers, providing a tool people will actually want to use when they can’t find what they’re looking for in-store.
