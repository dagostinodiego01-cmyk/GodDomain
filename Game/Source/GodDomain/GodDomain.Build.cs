// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class GodDomain : ModuleRules
{
	public GodDomain(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"GameplayAbilities",
			"GameplayTags",
			"GameplayTasks",
			"UMG",
			"Slate"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"GodDomain",
			"GodDomain/Variant_Platforming",
			"GodDomain/Variant_Platforming/Animation",
			"GodDomain/Variant_Combat",
			"GodDomain/Variant_Combat/AI",
			"GodDomain/Variant_Combat/Animation",
			"GodDomain/Variant_Combat/Gameplay",
			"GodDomain/Variant_Combat/Interfaces",
			"GodDomain/Variant_Combat/UI",
			"GodDomain/Variant_SideScrolling",
			"GodDomain/Variant_SideScrolling/AI",
			"GodDomain/Variant_SideScrolling/Gameplay",
			"GodDomain/Variant_SideScrolling/Interfaces",
			"GodDomain/Variant_SideScrolling/UI"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
