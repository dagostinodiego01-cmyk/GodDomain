# Game/ — Unreal Engine 5 project root

Create the Unreal project **inside this folder** so the layout becomes:

```
Game/
├── GDomain.uproject
├── Config/
├── Content/
├── Plugins/
└── Source/
    ├── GDomain/            (primary game module)
    ├── GDomain.Target.cs
    └── GDomainEditor.Target.cs
```

Project settings to choose when creating it:
- Template: **Blank** (C++), no starter content
- Engine version: record it in `AGENTS.md` and `Docs/DECISIONS.md` once chosen
- Module/project name: `GDomain` (working codename; safe to rename early, painful later)
