# Strict vs dreamer

| | Strict | Dreamer |
| :--- | :--- | :--- |
| Purpose | Apply to a specific vacancy | Explore fit, benchmark, prep interview answers |
| Claims | 100% verifiable from master + Facts | Mix verified + `**(Aspirational)**` |
| PDF | `cvfmt render --verify` | Default render **excludes** aspirational bullets |
| CLI | `cvfmt tailor ... --mode strict` | `cvfmt tailor ... --mode dreamer --prepare DIR` |
| Validator | Errors on aspirational bullets | Warns `ASPIRATIONAL_BULLET` |

When the user is unsure, default to **strict** and offer dreamer as an optional second pass.