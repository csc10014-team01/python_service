# Lab 7 — Usability checklist (tick before your user test)

- [x] The first screen says what the assistant can do, with example questions
- [x] Empty or too-long input shows a friendly message (not a crash)
- [x] While waiting, the user sees "Thinking…"
- [x] Every answer from documents shows its sources
- [x] "I don't know" answers tell the user who can help (escalation)
- [x] If the backend is down, the page says so clearly
- [x] Each answer has 👍 / 👎, and clicking gives a "thanks" message
- [x] The page says it is an AI assistant
- [x] Text is readable (size, contrast); buttons have clear labels
- [x] Works on a phone-width window

## Verification notes

- Enter on an empty chat field leaves the conversation unchanged. The input prompt stays visible. A question over 2,000 characters shows a length warning.
- The thesis example and the same typed question both show `Sources: H26#5.3 - …`. The capital-of-France question shows an escalation notice for the Training Office, room I.101.
- API answers with a request ID offer **Helpful** and **Not helpful**. Once the API saves the rating, the page shows “Thanks for your feedback!” and hides both buttons.
- With FastAPI stopped, submitting a question shows “Cannot reach the assistant.” The chat input stays usable and Streamlit shows no traceback.
- The AI notice is under the page title. Status and feedback messages use text. The phone-width check used Edge at 390 CSS pixels.
