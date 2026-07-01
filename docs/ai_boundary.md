# AI Explanation Boundary

ChangeGuard includes an **optional** explanation layer for saved review runs. The explanation layer makes review results easier to read. It does **not** make safety decisions.

Core principle:

```text
Rules decide. AI explains.
```

## What the AI Layer Does

- Summarizes a completed `ReviewResult` in plain language
- Highlights decision, risk level, concerns, impacted assets, migration steps, and rollback guidance
- Powers `changeguard explain-run <id>` for audit-log replays

The default path is deterministic. `NoOpLLMClient` and the MVP `OpenAICompatibleClient` placeholder both fall back to template-based explanations in `explain.py`.

## What the AI Layer Does Not Do

### AI does not decide

`ALLOW`, `WARN`, and `BLOCK` come only from deterministic checks against contracts, lineage, and aggregation rules in `rules.py`. An LLM cannot override, soften, or reverse a review decision.

### AI does not execute changes

Explanations never apply DDL, mutate contracts, or trigger migrations. Operators still execute approved changes through their normal deployment process.

### AI only explains deterministic review results

The explanation layer receives a **completed** review result. It does not inspect raw metadata independently or invent new checks. If the rule engine says `BLOCK`, the explanation describes why — it does not re-evaluate safety.

### All review decisions come from rules and metadata

Decision flow:

```text
Change Request
      ↓
Contract checks + lineage checks
      ↓
Rule engine aggregation
      ↓
ReviewResult (decision, risk, checks, plan)
      ↓
Optional explanation layer
```

The explanation step is downstream of the decision.

## ChangeGuard vs Orion

| | Orion | ChangeGuard |
|---|-------|-------------|
| Primary job | Help users understand data and ask metadata/query questions | Review proposed changes before they are applied |
| Who decides safety | Conversational assistance may guide judgment | Deterministic rule engine decides |
| Output | Natural language answers | Structured `ALLOW` / `WARN` / `BLOCK` review |
| Role of AI | Core interaction model | Optional explanation of an already computed result |

Orion is a metadata copilot. ChangeGuard is a change safety checker. They solve different problems and can coexist in the same platform story.

## API Keys and Testing

- No API key is required for the MVP test suite
- `NoOpLLMClient` is the default-compatible path for local development
- `OpenAICompatibleClient` is a placeholder for future OpenAI-compatible integrations and currently falls back to deterministic text

## Related Docs

- [System design](system_design.md)
- [Decision rules](decision_rules.md)
- [Limitations](limitations.md)
- [README](../README.md)
