# Option Map

An Option Map is the design-phase output. It helps a user who does not know exactly what they want see plausible directions and pick one.

## Ingredients

Use only what helps the next decision:

- Source anchors: exact wording or facts that shape the option space.
- Plausible directions: distinct product interpretations, not minor implementation variants.
- What each direction optimizes for.
- Tradeoffs, risks, and non-goals.
- Weak or rejected options when they are tempting but poor fits.
- Recommended direction with reasoning.
- Questions that would materially change the recommendation.
- What would become durable after the user chooses.

## Quality Rules

The recommendation should be useful but not pretend uncertainty is gone. Phrase it as a default direction that can be accepted, rejected, or refined.

Avoid option theater:

- Do not create three options when there is really one.
- Do not list implementation methods as product directions.
- Do not bury the recommendation.
- Do not ask the user to choose between irrelevant process artifacts.

## Minimal Shape

```md
## Option Map

Source signals:
- <source wording or context>

Directions:
1. <direction>: optimizes for <value>; tradeoff <cost/risk>.
2. <direction>: optimizes for <value>; tradeoff <cost/risk>.

Recommendation:
- Start with <direction> because <source-grounded reason>.

Decision needed:
- <question only if it changes the recommendation>
```

Do not write this to `context/docs/` until the user accepts or chooses a direction.
