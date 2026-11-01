# python_service

## Help command

With the project environment activated and the package installed, run from the project root:

```console
python -m assistant_core help
python -m assistant_core /help
```

Help lists office lookup, tuition calculation, and handbook-rule questions. Commands are case-insensitive and accept surrounding whitespace and trailing `?`, `!`, or `.`. Longer questions such as `help me calculate tuition for 18 credits` keep their normal routing.

The service returns `Response(intent=Intent.HELP, sources=[], degraded=False)`. The CLI writes the answer to stdout and its existing JSON event to stderr. No external provider or additional dependency is needed. Normal application data must still be present at CLI startup.

H1 review: [`docs/lab3/ai_extension_review.md`](docs/lab3/ai_extension_review.md). AI use: [`docs/ai-use-log.md`](docs/ai-use-log.md).
