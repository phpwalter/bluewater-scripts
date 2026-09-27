# Development

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

All policy logic belongs in `src/bluewater`. Hooks and workflow files must remain adapters rather than alternate implementations.

Run the quality gates before committing:

```bash
python -m ruff check src tests
python -m mypy src/bluewater
python -m pytest --cov=bluewater
python -m bluewater check --scope all
```

Tests should favor deterministic temporary repositories and should not require network access. External integrations should be tested at their process boundary.

Changes to configuration semantics require a schema change, tests, and documentation in the same pull request.
