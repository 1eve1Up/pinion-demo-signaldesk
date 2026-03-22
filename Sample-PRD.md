Product Requirements Document (PRD)
Product Name

SignalDesk API

Product Type

Backend SaaS API Demonstration

Purpose

SignalDesk API is a simple CRM-style backend service designed to demonstrate clean SaaS backend architecture.

The goal is not feature completeness, but to showcase:

clean service structure

authentication

REST API design

database modeling

automated testing

maintainable backend patterns

The system should resemble a minimal multi-user CRM backend that stores contacts and interaction notes.

This demo should be easy for engineers to understand within minutes and serve as an example of production-ready backend patterns.

Goals
Primary Goal

Demonstrate a well-structured SaaS backend API including:

authentication

persistent data storage

RESTful endpoints

tests

clean project architecture

Secondary Goals

Showcase:

maintainable code structure

predictable API patterns

testable components

developer-friendly design

Non-Goals

The system is not intended to be a full CRM.

Out of scope:

UI frontend

complex reporting

billing/subscriptions

advanced permissions

email integrations

analytics

Target Users

Developers evaluating backend architecture patterns.

Typical viewers:

engineers reviewing code samples

technical interviewers

startup founders exploring API patterns

dev teams evaluating backend scaffolding

Core Concept

SignalDesk manages contacts and interaction notes.

Example workflow:

User registers

User logs in

User creates contacts

User records notes about interactions

Functional Requirements
1. Authentication

The system must support:

User Registration

Endpoint:

POST /auth/register

Fields:

email
password

Behavior:

creates user

hashes password

returns auth token

User Login

Endpoint:

POST /auth/login

Fields:

email
password

Returns:

JWT access token
Authenticated Requests

Protected endpoints must require:

Authorization: Bearer <token>
2. Contacts

Users manage their own contacts.

Create Contact
POST /contacts

Fields:

name
email
company
phone
List Contacts
GET /contacts

Returns contacts owned by the authenticated user.

Get Contact
GET /contacts/{id}
Update Contact
PUT /contacts/{id}
Delete Contact
DELETE /contacts/{id}
3. Interaction Notes

Notes represent interactions with a contact.

Examples:

meeting

call

follow-up

Create Note
POST /contacts/{contact_id}/notes

Fields:

content
timestamp
List Notes
GET /contacts/{contact_id}/notes
Delete Note
DELETE /notes/{id}
Data Model
Users
User
-----
id
email
password_hash
created_at
Contacts
Contact
-------
id
user_id
name
email
company
phone
created_at
Notes
Note
----
id
contact_id
content
timestamp
created_at
API Design Principles

The API should follow:

REST conventions
GET
POST
PUT
DELETE
Predictable resource naming

Examples:

/contacts
/contacts/{id}
/contacts/{id}/notes
JSON responses

Example:

{
  "id": 1,
  "name": "Alice Smith",
  "company": "Acme Corp"
}
System Architecture
Components
API Server
│
├── Auth Module
├── Contacts Module
├── Notes Module
│
Database
Suggested Stack

Any modern stack is acceptable, but recommended:

Backend:

Python (FastAPI)
OR

Node.js (Express / NestJS)

Database:

PostgreSQL
OR

SQLite for demo simplicity

ORM:

SQLAlchemy / Prisma / TypeORM

Auth:

JWT tokens

Project Structure

Example:

signaldesk-api/
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── auth/
│   │   ├── routes.py
│   │   ├── service.py
│   │
│   ├── contacts/
│   │   ├── routes.py
│   │   ├── service.py
│   │
│   ├── notes/
│   │   ├── routes.py
│   │   ├── service.py
│
├── models/
│   ├── user.py
│   ├── contact.py
│   ├── note.py
│
├── database/
│   ├── db.py
│   ├── migrations/
│
├── tests/
│   ├── test_auth.py
│   ├── test_contacts.py
│   ├── test_notes.py
│
├── requirements.txt
├── README.md
Testing Requirements

Tests must cover:

Authentication

register user

login user

token validation

Contacts

create contact

list contacts

update contact

delete contact

Notes

create note

list notes

delete note

Tests should run with:

pytest

or

jest
API Documentation

The API must provide auto-generated docs.

Preferred:

FastAPI auto docs:

/docs

or

OpenAPI/Swagger.

Deployment Simplicity

The demo should run locally with minimal steps.

Example:

git clone
pip install -r requirements.txt
uvicorn app.main:app
Success Criteria

The demo is successful if a developer can:

Start the API locally in under 3 minutes

Register a user

Create contacts

Add interaction notes

Run the test suite

Explore endpoints via API docs

Example Demo Flow
POST /auth/register
POST /auth/login
POST /contacts
GET /contacts
POST /contacts/{id}/notes
GET /contacts/{id}/notes
Future Extensions (Optional)

Potential enhancements:

pagination

search

tagging contacts

activity timeline

webhook notifications

GraphQL layer