# Hybrid Test Generation And Scoring Plan

This plan describes how to evolve the current test workflow from one-mode assignment into a hybrid model:

```txt
HR-provided questions
+ optional agent-generated questions
= final assigned candidate test
```

## Goal

Support three test assignment modes:

```txt
fixed      -> only HR-provided questions
generated  -> only agent-generated questions
hybrid     -> HR-provided questions + agent-generated questions
```

The candidate should always receive one final normalized test stored on the application:

```txt
Application.dynamic_test_content
```

That final test may contain HR-authored questions, agent-authored questions, or both.

## Core Product Decisions

### HR Questions

HR should be able to add questions manually.

Each HR question should support:

- question type: multiple choice, essay, file upload, coding, system design, etc.
- prompt/content.
- point value.
- optional choices for multiple choice.
- optional expected answer.
- optional grading rubric.
- optional tags/skills.
- optional difficulty.

Expected answer should be optional.

If HR provides an expected answer, use it as reference material.

If HR does not provide an expected answer, the agent should generate a draft expected answer and rubric before the question is assigned or scored.

### Agent-Generated Questions

HR should be able to enable agent generation.

Agent generation config should support:

- number of questions to generate.
- question type distribution.
- point budget.
- difficulty/seniority target.
- focus areas.
- specific technologies.
- project/CV areas to probe.
- free-form HR instruction.

Example:

```json
{
  "mode": "hybrid",
  "agent_generation": {
    "enabled": true,
    "question_count": 7,
    "total_points": 70,
    "focus_areas": ["FastAPI", "PostgreSQL", "Celery"],
    "candidate_project_focus": "Ask deeper questions about distributed task queues from the CV.",
    "difficulty": "mid",
    "distribution": {
      "multiple_choice": {
        "count": 3,
        "points": 30
      },
      "essay": {
        "count": 4,
        "points": 40
      }
    }
  }
}
```

### Final Test

The final assigned test should be a normalized object:

```json
{
  "version": 1,
  "mode": "hybrid",
  "total_points": 100,
  "questions": [
    {
      "id": "hr_001",
      "source": "hr",
      "type": "essay",
      "prompt": "Explain how you would design retry handling for Celery workers.",
      "points": 15,
      "expected_answer": "...",
      "grading_rubric": [],
      "tags": ["Celery", "RabbitMQ"],
      "difficulty": "mid"
    },
    {
      "id": "ai_001",
      "source": "agent",
      "type": "multiple_choice",
      "prompt": "...",
      "points": 10,
      "choices": [],
      "correct_answer": "...",
      "expected_answer": "...",
      "grading_rubric": [],
      "tags": ["PostgreSQL"],
      "difficulty": "mid"
    }
  ],
  "generation_notes": {
    "hr_question_count": 3,
    "agent_question_count": 7,
    "agent_focus": []
  }
}
```

## Scoring Philosophy

Expected answers are not strict answer matching except for deterministic question types.

Use this rule:

```txt
Expected answer = reference answer + grading guidance, not the only valid answer.
```

For multiple choice:

- Score deterministically against `correct_answer`.
- Optional explanation can be reviewed by LLM, but the primary score is exact.

For essay/system design/coding explanation:

- Use expected answer and grading rubric as reference.
- Score candidate answers by quality, correctness, completeness, tradeoff reasoning, and relevance.
- Award full or high credit for a different solution if it satisfies the rubric.
- Penalize hallucinated claims, unsafe designs, missing required constraints, or shallow reasoning.

For file upload:

- Parse supported file types when possible.
- Otherwise store file metadata and require manual review or an agent summary.

Recommended LLM scoring instruction:

```txt
The expected answer is a reference, not a required exact answer.
If the candidate provides a different solution, score it fairly using the rubric.
Award full credit when the answer is correct, practical, and well-reasoned even if it differs from the expected answer.
Only penalize differences that reduce correctness, feasibility, clarity, or coverage of required constraints.
```

## Database And Schema Plan

The current database already has flexible JSON fields:

- `Job.test_content`
- `Job.dynamic_test_config`
- `Application.dynamic_test_content`
- `Application.test_answer`
- `Application.detailed_score_json`

For MVP, avoid adding many columns. Use the existing JSONB fields with a stricter JSON shape.

Recommended first DB change:

```txt
Add Job.test_mode
```

Values:

```txt
fixed
generated
hybrid
```

Why add a column:

- It makes the mode queryable.
- It avoids guessing mode from nullable JSON fields.
- It keeps API/UI behavior explicit.

Optional later DB changes:

- Add `Application.assigned_test_snapshot` if `dynamic_test_content` becomes too semantically confusing.
- Add `test_questions` and `test_submissions` tables if question-level analytics or versioning becomes important.

For now:

```txt
Job.test_content = HR-authored questions
Job.dynamic_test_config = agent generation config
Job.test_mode = fixed/generated/hybrid
Application.dynamic_test_content = final assigned test snapshot
Application.test_answer = candidate submitted answers
Application.detailed_score_json.assessment = scoring output
```

## Alembic Steps

1. Update SQLAlchemy model:

```txt
packages/backend_shared/talent_core/models.py
```

Add `test_mode` to `Job`.

2. Update API schemas:

```txt
apps/api/app/schemas/jobs.py
```

Add `test_mode` to create/response schemas.

3. Update job creation route:

```txt
apps/api/app/routers/jobs.py
```

Persist:

- `test_mode`
- `dynamic_test_config`
- `test_duration`

4. Generate Alembic migration:

```bash
cd apps/api
alembic revision --autogenerate -m "add job test mode"
```

5. Review the migration.

6. Apply migration:

```bash
alembic upgrade head
```

7. Verify by creating and reading a job with each mode.

## Agent Flow Plan

### Current Problem

Current logic is effectively:

```txt
if HR test exists:
    copy HR test
elif dynamic config exists:
    generate AI test
else:
    no test
```

This does not support hybrid.

### Target Assignment Flow

After CV pass:

```txt
load application + job
normalize HR questions from Job.test_content
inspect Job.test_mode

if mode == fixed:
    final_test = HR questions only

if mode == generated:
    final_test = agent-generated questions only

if mode == hybrid:
    final_test = HR questions + agent-generated questions

validate final_test
fill missing expected answers/rubrics
save final_test to Application.dynamic_test_content
set test_deadline
notify candidate
```

### Expected Answer Completion

Before assigning the final test:

```txt
for each HR question:
    if expected_answer or grading_rubric is missing:
        ask agent to generate draft expected_answer/grading_rubric
        mark metadata.expected_answer_source = "agent_generated_for_hr_question"
    else:
        mark metadata.expected_answer_source = "hr"
```

For agent-generated questions:

```txt
expected_answer_source = "agent"
```

This helps HR and future reviewers know where the scoring reference came from.

## UI Plan

Add an HR test configuration section to the job creation/editing UI.

Controls:

1. Test mode selector:

```txt
Fixed
Generated
Hybrid
```

2. HR question editor:

- Add/remove/reorder questions.
- Question type selector.
- Prompt textarea.
- Points input.
- Choices editor for multiple choice.
- Correct answer for deterministic questions.
- Expected answer textarea.
- Grading rubric textarea or structured criteria editor.
- Tags/focus area input.

3. Agent generation panel:

- Enabled toggle.
- Number of generated questions.
- Total generated points.
- Distribution by type.
- Difficulty/seniority.
- Focus areas.
- Free-form instruction.
- Candidate project focus instruction.

4. Preview panel:

- HR questions count.
- Agent questions count.
- Total points.
- Missing expected answers.
- Estimated final test shape.

Validation:

- Fixed mode requires at least one HR question.
- Generated mode requires agent generation enabled and question count > 0.
- Hybrid mode requires at least one HR question or at least one generated question, but should usually require both.
- Total points must be positive.
- Multiple choice questions must have choices and a correct answer.
- Essay/system design questions should have expected answer or allow agent to generate one.

## Scoring Agent Plan

Create:

```txt
apps/worker/app/orchestration/assessment_scoring_graph.py
```

Suggested graph:

```txt
load_context
-> load_assigned_test
-> normalize_submission
-> score_deterministic_questions
-> score_open_questions
-> aggregate_scores
-> persist_assessment_result
```

Scoring details:

1. Deterministic questions:
   - exact answer match.
   - partial credit only if explicitly supported.

2. Open questions:
   - LLM grades against rubric.
   - Expected answer is reference, not exact target.
   - Require JSON output with score, rationale, strengths, weaknesses.

3. Aggregate:
   - sum question scores.
   - calculate percentage.
   - choose decision band.

4. Persist:
   - `Application.total_score`
   - `Application.status = test_scored` or `test_failed`
   - `Application.detailed_score_json["assessment"]`
   - `AgentRun(agent_type="assessment_scorer")`

## Recommended Implementation Order

### Step 1: Decide Data Shape

Write and freeze the JSON shape for:

- HR questions.
- agent generation config.
- final assigned test.
- candidate submission.
- scoring output.

Do this before changing code. It prevents UI, API, and worker from disagreeing.

### Step 2: Minimal DB Change

Add:

```txt
Job.test_mode
```

Then generate and apply Alembic migration.

### Step 3: Fix Job API

Update job create/read so it actually persists:

- `test_mode`
- `test_content`
- `dynamic_test_config`
- `test_duration`

### Step 4: Update Test Generation Graph

Replace the one-mode branching with assignment composition:

```txt
HR questions
+ generated questions if configured
+ expected answer/rubric completion
= final test snapshot
```

### Step 5: Restore Queue Wiring

Enable:

```txt
agent.test_generation
```

in:

- API queue map.
- API Celery routes.
- worker Celery routes.
- worker task definitions.

### Step 6: Update Frontend HR Config UI

Add test mode, HR question editor, and agent generation config panel.

### Step 7: Implement Assessment Scoring

Only after assigned tests are stable, add:

```txt
agent.assessment
```

and the scoring graph.

### Step 8: Add Tests

Minimum tests:

- job creation persists hybrid config.
- fixed mode creates final test from HR questions.
- generated mode creates final test from agent questions.
- hybrid mode merges HR + agent questions.
- missing expected answer gets generated.
- assessment scoring preserves CV screening details in `detailed_score_json`.

## First Thing To Do

Do not start with UI.

Start with the data contract.

Recommended first task:

```txt
Define the final test JSON schema and scoring JSON schema.
```

Then implement in this order:

```txt
1. Add Job.test_mode with Alembic.
2. Fix job create/read persistence.
3. Update test assignment graph to compose final tests.
4. Restore agent.test_generation queue wiring.
5. Build UI controls.
6. Implement scoring agent.
```

This keeps the workflow stable from the backend outward, instead of building UI controls that do not yet have a reliable backend contract.

