# GM Problem Viewer

GM Problem Viewer acts as a way to interact with your competitive programming problems through UI.

The basic operations it aims to support include:

1. A simple python API for testing solutions, running validators, generating test cases, and exporting to basic formats like DMOJ and problemtools
2. A simple web UI for search/sorting through problems + kicking off manual tasks
3. Additionally, some abilities to utilise AI to create some more boring aspects of problems (input/output validators, proofreading statements, ensuring bounds align)

## Development

Run server:

```
uv run uvicorn api.main:app --reload
```
