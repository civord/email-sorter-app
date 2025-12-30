# Smart Email Manager

Smart Inbox is a web-based email management application built as my final project for CS50. The goal of this project was to design and implement a simplified, Gmail-like inbox that automatically fetches emails, classifies them, and allows users to efficiently browse, read, and manage their messages through a clean user interface.

I built this project because I personally find email inboxes overwhelming when they are filled with unorganized messages. Important emails often get buried under newsletters, promotions, or automated messages. This project aims to solve that problem by automatically classifying emails and presenting them in a structured, easy-to-use interface.


## Features

The app uses Flask for the backhand and vanilla JS for the frontend alongside HTML and CSS.
Emails are fetched from my Gmail inbox **(for now!)** by IMAP and are stored locally in a SQLite database.

The app also supports:
- Viewing a list of emails

- Opening an email to see full details

- Marking emails as read/unread

- Filtering emails by category and priority

- Responsive behavior for desktop and mobile screens

## Tech Stack

**Client:** JavaScript, HTML, CSS

**Server:** Flask/Python, SQLite3


## File Structure + Explanation
### Backend Files:
`app.py`
    - The main Flask app. It handles all routes used by the frontend, such as:
- Rendering all of the emails on the page
- Handles filters
- Updates email status (Read\Unread)

`email_reader.py`
    - The script that connects to a gmail inbox via IMAP and fetches all new emails.
- To fetch only new emails I am using UIDs
- I am parsing the email content with python's email library
- I extract the email id, sender, subject, body and date
- And populate the database with the gathered data

`database.py`
- Creates tables (email and meta) if they do not exist
- The email table stores all of the emails, while the meta stores the last uid, so that I only load new emails with my email_reader.py function
- Fetch emails in batches to allow lazy loading. I am doing this with LIMIT and OFFSET
- Store the email status and update it on user interaction

`classifier.py`
- Classfication happens based on patterns and matches in senders or any high value keywords in the body and subject. It is a points based classification where each keyword adds certain amount of points and if the final score is higher than the treshold a certain category or priority is assined.
- Categories and priorities are stored in separate config.json filters
- Classfication happens only for unclassified emails

### Frontend Files

- HTML (Jinja templates): Used only for rendering the initial page structure (the “shell”).
- CSS: Handles layout, styling, and responsive design.
- JavaScript: Responsible for:
    - Fetching emails via API calls
    - Lazy loading with IntersectionObserver
    - Opening emails
    - Updating email status
    - Filtering emails
    - Switching layouts for mobile screens
    - I intentionally avoided frontend frameworks to better understand how everything works at a low level.
## Design Decisions
One important design decision was using JavaScript instead of Jinja for rendering emails. Initially, I rendered all emails using a Jinja loop, but this caused performance issues and made lazy loading impossible. Switching to a JSON-based API allowed the frontend to request data only when needed.

Another key decision was using different interaction models for desktop and mobile. On desktop, the email list and email content are visible at the same time. On mobile, the app switches to a single-view flow where the user opens an email full-screen and can navigate back to the inbox. This mirrors how real-world email apps behave and greatly improves usability.

I also chose to keep authentication and advanced user management out of the MVP to stay within scope and focus on core functionality.
## Roadmap
This project is an MVP and has several areas for improvement:
- User authentication and encrypted credential storage
- Better email classification using machine learning
- More advanced error handling and logging
- Support for multiple email providers
- Profile pictures for senders
- Despite these limitations, the application successfully demonstrates backend integration, frontend interactivity, automation, and thoughtful system design.

## Lessons Learned
This project challenged me to think beyond individual features and focus on how all parts of a system work together. I learned how to design APIs, manage background tasks, handle asynchronous frontend logic, and make realistic design tradeoffs. Smart Inbox represents my growth as a developer and my ability to build a complete, functional application from scratch.
