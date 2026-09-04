# Forecasting Cost And Yield

## Bibliographic Identity

- Title: Forecasting Cost and Yield
- Year: 1996
- Source: https://users.ece.cmu.edu/~maly/maly/YieldLearning.pdf
- Track: manufacturing-packaging-and-yield
- Subtheme: yield learning and manufacturing economics

## First-Principles Reading

The object being controlled is expected cost per working chip over time. A wafer has a cost before anyone knows how many good dies it will produce. Yield decides how that wafer cost is divided across sellable parts.

The constraint is learning under manufacturing uncertainty. Early in a process or product ramp, the defect mechanisms, process maturity, test coverage, and repair strategy are not fully known. Yield improves as failures are observed, diagnosed, and reduced.

The mathematical form is a learning curve. Yield and cost are modeled as functions of production experience and time:

```text
more production evidence -> better process knowledge -> higher yield -> lower cost per good die
```

The concrete method is to forecast yield and cost trajectories under different manufacturing assumptions. This turns yield from a static percentage into a planning variable that changes with learning.

The evidence artifact is the yield curve, cost curve, assumed learning model, and scenario comparison. The useful evidence is not a single predicted number; it is how sensitive the product economics are to yield learning.

The failure boundary is model mismatch. Forecasts fail when the dominant defect source, process change, product mix, package failure, or test escape differs from the assumptions used in the model.

## Concept Links

- `yield-is-probability-over-manufacturing-variation`
- `area-is-a-physical-budget`
- `verification-is-evidence-implementation-matches-intent`

## What The Paper Teaches

The deeper lesson is that yield is not a factory statistic after design. It is the probability bridge between physical variation and product economics.

