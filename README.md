# LLD Practice Platform

A focused platform for practicing Low-Level Design problems
through structured submissions and explainable feedback.

## Problem Statement

LLD interviews often have multiple valid design solutions,
making simple pass/fail evaluation insufficient.

This platform allows learners to:

1. Choose an LLD problem
2. Start an attempt
3. Submit a structured design
4. Receive rubric-based feedback
5. Review previous attempts
6. Retry and improve

## Features

- LLD problem library
- Structured solution submission
- Rule-based evaluation
- AI-assisted evaluation
- Explainable rubric-based feedback
- Evaluation status tracking
- Attempt history
- Retry workflow
- Persistent submissions
- Test coverage for important behavior

## Problems

- Parking Lot
- Elevator System
- Vending Machine

## Architecture

Problem
   ↓
Attempt
   ↓
Submission
   ↓
Evaluator
   ↓
Evaluation
   ↓
Feedback

The evaluator is abstracted so different evaluation
strategies can be introduced without changing the
practice workflow.

## Tech Stack

Frontend:
- React
- TypeScript
- Vite

Backend:
- Python
- FastAPI
- Pydantic

Database:
- SQLite

Testing:
- Pytest

## Running Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
...
