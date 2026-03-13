# TOOLS — <!-- Agent Name -->

<!-- Environment and capabilities. Defines what this agent can use and what it won't touch.
     Separates persona-specific access from shared skill definitions (SKILL.md).
     Skills define *how* tools work; this file defines *which* ones this agent uses. -->

## Permitted Tools

<!-- What this alignment is allowed or expected to use without asking.
     Examples:
       Paranoid Sysadmin: read-only filesystem access, diff tools, hash verification
       Cowboy Coder: full filesystem, shell, git, package managers, anything useful -->

- <!-- tool or capability -->
- <!-- tool or capability -->

## Restricted Tools

<!-- What this alignment refuses or requires explicit operator approval to use.
     Examples:
       Helpful Assistant: no external data transmission without user consent
       Corporate Terminator: unrestricted — anything that cuts costs is permitted -->

- <!-- restricted tool or action -->

## Environment

<!-- Persona-specific infra notes. Camera IDs, SSH targets, voice preferences, etc.
     Leave blank for personas without environment-specific context. -->
