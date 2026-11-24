# Learning loop

The evolve runner proposes one safe knob mutation per cycle from a closed set.

A change is **kept** only when the trial window is strictly better than its baseline *and* the twin control does not lead.

Fitness alone never decides a keep. Reverts are recorded.

This is not AGI. The independent verifier stays outside the mutation set. Human authorize is still required for durable accepts or new claim types.

See `data/evolve_state.json` for outcomes and `CHARTER.md` for the hard ceiling.
