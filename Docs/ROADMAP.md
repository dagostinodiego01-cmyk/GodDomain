# Roadmap

Each milestone has **exit criteria**. Do not start the next milestone until they are met.

## M0 — Foundations
- [X] Engine version chosen and recorded in `AGENTS.md`
- [X] UE C++ project created in `Game/`, builds clean
- [X] Git + LFS configured, first commit pushed
- [X] Rules and docs reviewed and confirmed (`DECISIONS.md` updated)

## M1 — Combat grey-box
- [ ] Third-person character with movement, camera, dodge
- [ ] GAS set up: base attribute set (health, stamina), one attack ability
- [ ] One enemy with basic AI and a damage pipeline
- [ ] **Exit:** a fight in a flat test arena feels good to you

## M2 — Class system (data-driven)
- [ ] Class, tier and skill tables loaded from `Data/*.csv`
- [ ] One class with Tier 0 → Tier 1 promotion
- [ ] Level/XP curve and attribute growth from data
- [ ] **Exit:** change a number in CSV, re-import, see the change in game

## M3 — Starter village vertical slice
- [ ] Village layout (grey-box then art pass)
- [~] Art track (`Docs/ART_DIRECTION.md`, `Docs/ART_PIPELINE.md`): material sheets **generated**; facade, street, civic and landscape kits pending
- [ ] Class trainer, quest board, vendor
- [ ] Two to three monster ranks, one mini-boss
- [ ] Promotion quest end to end
- [ ] **Exit:** a new player can play ~30 minutes and get promoted

## M4 — Co-op multiplayer
- [ ] Listen-server co-op for 2–8 players
- [ ] Replicated abilities, damage, inventory
- [ ] **Exit:** two machines can play the village together

## Later (not scheduled)
Crafting and trade, player economy, city building, dedicated servers, persistence, additional classes and zones.
