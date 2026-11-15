# Coding Standards (Unreal C++)

## Naming
- Types: `A` (Actor), `U` (UObject/component), `F` (struct), `E` (enum), `I` (interface), `T` (template).
- Prefix all project types with `GD`: `AGDCharacter`, `UGDHealthAttributeSet`, `FGDClassRow`.
- Booleans: `bIsAlive`. Functions: PascalCase verbs. Variables: PascalCase. Parameters/locals: PascalCase too (Unreal style).
- Files match the type name without the prefix letter, e.g. `GDCharacter.h/.cpp`.
- Asset prefixes: `BP_`, `SM_`, `SK_`, `M_`, `MI_`, `T_`, `WBP_`, `DT_`, `DA_`, `GA_` (gameplay ability), `GE_` (gameplay effect).

## Headers and includes
- Include what you use; forward-declare in headers where possible.
- `#include "GDCharacter.generated.h"` must be the **last** include in a header.
- Avoid including heavy headers (e.g. `Engine.h`) in headers.

## UObject and memory
- Every `UObject*` member: `UPROPERTY()` with `TObjectPtr<>` (UE5).
- Non-owning references: `TWeakObjectPtr`. Never store raw `UObject*` in non-UPROPERTY members.
- Use `NewObject`/`CreateDefaultSubobject`, never `new` for UObjects.

## Replication
- Replicated variables: `UPROPERTY(Replicated)` or `ReplicatedUsing=OnRep_X`, and register in `GetLifetimeReplicatedProps` using `DOREPLIFETIME`.
- RPCs: choose `Server`, `Client`, `NetMulticast` deliberately; mark `Reliable` only when losing it breaks gameplay.
- Validate all client input on the server. Never trust client-reported damage, positions for hits, or currency changes.
- Comment each new gameplay class with: `// Authority: server | client | both`.

## Gameplay Ability System
- Stats are `UAttributeSet`s; changes go through `GameplayEffect`s.
- Use `FGameplayTag`s (defined in `Config/DefaultGameplayTags.ini`) instead of strings or enums for ability/state identity.
- Abilities derive from a project base class `UGDGameplayAbility`.

## Performance
- No `Tick` unless needed; set `PrimaryActorTick.bCanEverTick = false` by default.
- Prefer timers, delegates, async tasks.
- No per-frame allocations or expensive searches (`GetAllActorsOfClass`) in hot paths.

## Logging
- Declare categories (`DECLARE_LOG_CATEGORY_EXTERN(LogGD, Log, All)`) in `Core/`.
- Use `UE_LOG(LogGD, Warning, TEXT("..."))`. No `LogTemp` in committed code.

## Comments and docs
- Comment **why**, not what. Public classes get a one-paragraph header comment.
- When a decision affects architecture, add an entry to `DECISIONS.md`.

## Git
- Small commits, imperative messages: `Add health attribute set`, `Fix class promotion check`.
- Never commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/` (already in `.gitignore`).
- Commit only code that compiles.
