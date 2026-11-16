# Task cards — for cheap-model agents

Cards for the `A` tasks in `ROADMAP.md` (Agent column). A card is written so that a small, fast model (e.g. DeepSeek 4.1 Flash) can finish the task without reading the whole repo. Each card says what to read, what to write, what not to touch, how to check, and when to stop.

**Who writes cards:** a `B` (strong) agent or the owner, *just before* the task's dependencies are ✅, using the code as it actually is. Do not pre-write cards for tasks whose inputs don't exist yet; they go stale. When a task is done, delete its card and tick the roadmap row.

---

## Rules for an `A` agent (read all of these first)

1. **One card per session.** Do only what the card says. If you notice something else wrong, put it in your report; do not fix it.
2. **Read only the files the card lists**, plus `AGENTS.md` and `Docs/CODING_STANDARDS.md`. If a listed file does not exist, **stop and report**; it may be on the other machine.
3. **Never guess an Unreal API.** Before you use a function, macro or class you have not seen in *this repo's* code, search the engine source on the build machine (`C:\Program Files\Epic Games\UE_5.8\Engine\Source` and `Engine\Plugins`). Copy patterns that already exist in this repo first.
4. **Do not touch:** binary assets (`*.uasset`, `*.umap`), `*.Build.cs`, `*.Target.cs`, `*.uproject`, `Variant_*` folders. `Config/*.ini` only where the card says, and list every line you changed in your report.
5. **No balance numbers in C++.** Numbers go in `Data/*.csv`. A C++ default may be `0` or a documented placeholder, never a tuned value.
6. **Every new gameplay class** gets the header comment `// Authority: server | client | both`.
7. **Log** with `LogGodDomain` or `LogGodDomainCombat`, never `LogTemp`.
8. **Build after every change** (command below). Fix your errors. If the same error survives two fix attempts, **stop and report** with the full compiler output.
9. **Editor steps** (marked **E** in a card) are done on the editor machine, not by you. Write them in your report as a checklist for that machine.

### Build

```powershell
& "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat" GodDomainEditor Win64 Development "<repo>\Game\GodDomain.uproject" -WaitMutex
```

### Run the automation tests

Once X-04 exists, run `Tools\check.ps1` instead. Until then:

```powershell
& "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "<repo>\Game\GodDomain.uproject" -ExecCmds="Automation RunTests GodDomain" -TestExit="Automation Test Queue Empty" -ReportExportPath="<repo>\Saved\TestReport" -unattended -nullrhi -nosplash -log
```

Tests live in `Game/Source/GodDomain/Tests/`, are named `GodDomain.<Area>.<What>`, and are wrapped in `#if WITH_DEV_AUTOMATION_TESTS`. Copy the registration macro and flags from an existing engine test (search `IMPLEMENT_SIMPLE_AUTOMATION_TEST` in the engine source); the flag names changed across 5.x.

### Report (end every session with this)

```
Task: <ID>   Result: done | blocked
Files changed: <list>
Config lines changed: <file: line> or none
Build: pass | fail (paste the last 30 lines if fail)
Tests: <n passed / n failed> or not run (why)
Replication: <server / client / both, one line per new class or property>
Editor steps for the other machine: <checklist> or none
Placeholders the owner must tune: <list> or none
Noticed, not fixed: <list> or none
```

---

## Card template

```
### <ID> — <title>
Depends: <IDs, all ✅>          Size: S/M/L
Goal: <one sentence>
Read first: <exact paths>
Write: <exact paths, new or edited>
Steps: <numbered, concrete>
Do not: <task-specific traps>
Check: <build + named test + what to look for>
E steps: <for the editor machine>
Done when: <copied from ROADMAP>
```

---

## M1-04 — Attribute set

Depends: M1-03 ✅  Size: M
**Goal:** the seven combat attributes exist, clamp correctly and replicate; starting values come from data.

**Read first:** `Game/Source/GodDomain/Abilities/GodDomainAttributeSet.h/.cpp`, `Game/Source/GodDomain/Characters/GodDomainCharacter.h/.cpp`, and the `Core/` header that declares `LogGodDomain` (search `DECLARE_LOG_CATEGORY_EXTERN`).

**Write:** the attribute set (edit), the character (edit), `Data/PlayerStartingAttributes.csv` (new), `Game/Source/GodDomain/Tests/GodDomainAttributeSetTest.cpp` (new).

**Steps:**
1. Add `Health`, `MaxHealth`, `Stamina`, `MaxStamina`, `AttackPower`, `Defense` and `MoveSpeed` to the set, keeping whatever exists. **Copy the existing `Health` declaration exactly**: same `UPROPERTY` specifiers, same accessor macro, same `ReplicatedUsing=OnRep_…`, same `GetLifetimeReplicatedProps` line and the same OnRep body. Do not invent a different macro.
2. `MoveSpeed` is a **multiplier** (1.0 = unchanged). Do not wire it to the movement component; that is M4-09.
3. Clamp current values in `PreAttributeChange`: `Health` to `[0, MaxHealth]`, `Stamina` to `[0, MaxStamina]`; `AttackPower`, `Defense` and `MoveSpeed` to `≥ 0`. Clamp again in `PostGameplayEffectExecute` for `Health` and `Stamina`, because effects change the base value. When `MaxHealth` or `MaxStamina` drops below the current value, pull the current value down.
4. Remove the hard-coded 100/100 from the constructor. Starting values come from a data table: add `UPROPERTY(EditDefaultsOnly, Category="Abilities") TObjectPtr<const UDataTable> StartingAttributes;` to the character, and on the **server only**, right after the existing server-side `InitAbilityActorInfo`, call the ASC's stat-init-from-table function. Find its exact name and the row-name format it expects in `AbilitySystemComponent.h` / `AttributeSet.cpp` (look for `InitStats` and `InitFromMetaDataTable`). Log a warning with `LogGodDomain` if the table is not set.
5. Write `Data/PlayerStartingAttributes.csv` in the row format that function expects (`FAttributeMetaData` columns). Values: Health/MaxHealth 100, Stamina/MaxStamina 100, AttackPower 10, Defense 0, MoveSpeed 1. List all of them as placeholders in your report.
6. Test `GodDomain.Abilities.AttributeClamp`: create the set with `NewObject`, set `MaxHealth` to 50, call `PreAttributeChange` with `Health` = 80, expect 50; with −5, expect 0. Same for `Stamina`.

**Do not:** create a gameplay effect asset, touch `Config/`, or add damage logic (that is M1-05).

**Check:** build passes; `GodDomain.Abilities.AttributeClamp` passes.

**E steps:** import `Data/PlayerStartingAttributes.csv` as `DT_PlayerStartingAttributes` (row type `AttributeMetaData`), assign it to `StartingAttributes` on `BP_ThirdPersonCharacter`, and run PIE as a listen server with 2 players: `showdebug abilitysystem` on the client shows all seven values.

**Done when:** a GE changes values and they replicate to the client.

---

## X-04 — Local check script

Depends: none  Size: S
**Goal:** one command that builds, runs the tests and says PASS or FAIL.

**Read first:** this file's *Build* and *Run the automation tests* sections, and `.gitignore`.

**Write:** `Tools/check.ps1` (new). Mention it in the README setup steps (one line).

**Steps:**
1. Make the script work from any directory: find the repo root from `$PSScriptRoot`, and allow overriding the UE path with a `-EnginePath` parameter (default `C:\Program Files\Epic Games\UE_5.8`).
2. Build with the command above. If `Build.bat` returns non-zero, print `FAIL: build` and `exit 1`.
3. Warning gate: in the build output, count lines matching `warning` whose path is under `Game\Source\GodDomain\` but not under `Variant_`. If there are any, print them and fail.
4. Run the automation tests with `-ReportExportPath "<repo>\Saved\TestReport"`. Read `index.json` there and fail if its failed count is above 0. Run it once by hand to confirm the field names before writing the parser, and do not guess them.
5. Lint: fail if `LogTemp` appears in any `.cpp` or `.h` under `Game\Source\GodDomain\` outside `Variant_*`.
6. End with `PASS` / `FAIL: <step>` and exit 0 or 1. Leave a `# X-03 smoke test goes here` placeholder after step 4.

**Do not:** install anything, or write outside `Tools/` and `Saved/`.

**Check:** run it on a clean tree and get PASS. Add `UE_LOG(LogTemp, …)` to a scratch `.cpp` and get FAIL at the lint step, then remove the line.

**Done when:** one command tells you pass/fail.

---

## M1-10 — Health/stamina HUD stub

Depends: M1-04  Size: S
**Goal:** health and stamina numbers on screen that update without `Tick`.

**Read first:** `Core/` player controller `.h/.cpp`, `Abilities/GodDomainAttributeSet.h`, `Characters/GodDomainCharacter.h`.

**Write:** `Game/Source/GodDomain/UI/GodDomainHUDWidget.h/.cpp` (new) and the player controller (edit).

**Steps:**
1. `UGodDomainHUDWidget : UUserWidget` with two `UPROPERTY(meta=(BindWidget)) TObjectPtr<UTextBlock>` fields, `HealthText` and `StaminaText`, and a `BindToAbilitySystem(UAbilitySystemComponent*)` function. That function subscribes to the ASC's per-attribute value-change delegate for Health, MaxHealth, Stamina and MaxStamina (find the delegate getter in `AbilitySystemComponent.h`) and writes `"Health 80 / 100"`-style text. Unbind in `NativeDestruct`. No `Tick` and no UMG property bindings.
2. On the player controller: `UPROPERTY(EditDefaultsOnly) TSubclassOf<UGodDomainHUDWidget> HUDWidgetClass`. Create the widget **only when `IsLocalController()`**, after the pawn is possessed and its ASC is valid. Re-bind on re-possess, since respawn (M1-06) creates a new pawn.
3. Header comment: `// Authority: client (view only, no game rules)`.

**Check:** build passes.

**E steps:** create `WBP_HUD` (parent `UGodDomainHUDWidget`) with TextBlocks named exactly `HealthText` and `StaminaText`, and assign it on the player controller BP. In PIE, numbers change when you use `GiveXP`/damage cheats.

**Done when:** values move during a fight.

---

## Cards still to write (when their dependencies are ✅)

M1-06 (after M1-05), M1-09 (after M1-05), M2-01 (after M1-05 and X-06), X-06 (now, by a `B` agent, because it sets the validation pattern every later CSV copies). Every other `A` row is carded when it becomes ready.
