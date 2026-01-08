1. Platform & Stack Assumptions

CMS: Sulu CMS

Framework: Symfony

PHP: 8.1+

Database: Doctrine ORM

Admin UI: Sulu Admin (JS handled separately, PHP focus here)

AI must never assume features outside this stack.

2. General PHP Rules
Language & Syntax

Always include:

declare(strict_types=1);


Use typed properties, parameters, and return types

Prefer constructor property promotion

Prefer readonly where applicable

Prefer match over switch

Prefer enums over constant classes

Coding Standards

Follow PSR-12

Follow PSR-4

One class per file

Avoid magic values

Keep methods small and readable

Naming

Classes: PascalCase

Methods and variables: camelCase

Interfaces: *Interface

Traits: *Trait

Enums: PascalCase, singular

3. Sulu Architecture Rules
Bundle & Extension Model

All Sulu extensions must follow the bundle architecture

Do not modify Sulu core

Prefer extension points:

Admin extensions

Content types

Event listeners

Custom controllers

Custom entities

Controllers

Controllers must be thin

Controllers:

Receive dependencies via constructor injection

Delegate logic to services

Return Response or JsonResponse

Controllers must not:

Contain business logic

Access Doctrine directly

Instantiate services manually

Services & Dependency Injection

All services must be registered in the container

Prefer autowiring and autoconfiguration

Depend on interfaces, not implementations

Avoid service locators unless unavoidable

4. Content Modeling & Structure (Sulu-Specific)
Content Types

Use Sulu content types correctly:

Text, Block, Selection, Media, Smart Content, etc.

Custom content types must:

Be minimal

Be reusable

Respect Sulu’s data flow (content → structure → rendering)

Structures (Templates)

Structure definitions must:

Be clear and minimal

Use meaningful property names

Avoid deeply nested complexity unless required

AI must not invent unsupported structure attributes

5. Doctrine & Persistence
Entities

Entities should represent domain data only

Avoid business logic inside entities

Use typed properties

Prefer meaningful methods over setters

Repositories

All database queries must live in repository classes

Use QueryBuilder

Avoid raw SQL unless necessary

Migrations

Always generate Doctrine migrations for schema changes

Never assume direct database changes without migrations

6. Admin Extension Rules (PHP Side)

Admin extensions must:

Be modular

Follow Sulu Admin extension architecture

Do not hardcode UI logic in PHP

PHP must expose configuration, data, or APIs only

7. Events, Messaging & Workflow

Use Symfony EventDispatcher and Messenger

Events should:

Be immutable

Represent facts, not commands

Avoid heavy logic in event listeners

Prefer async processing for non-critical tasks

8. Validation & Input Handling

All external input must be validated

Use Symfony Validator

Prefer DTOs for complex input

Never trust admin input implicitly

9. Security Rules

Follow Symfony Security best practices

Never store secrets in code

Use environment variables for credentials

Always check permissions explicitly in custom controllers

Never bypass Sulu’s permission system

10. Testing Rules
General

Generate tests for:

Services

Repositories

Custom controllers

Tests must be deterministic and readable

Tools

Use PHPUnit

Use Symfony kernel test cases when needed

11. Logging & Error Handling

Use PSR-3 LoggerInterface

Never log sensitive data

Throw domain-specific exceptions

Do not swallow exceptions silently

12. Forbidden Patterns (Strict)

AI must never generate:

Business logic inside controllers

Direct Doctrine usage in controllers

Static service access

Global state

Modifications to Sulu core

Undocumented hacks

Untested non-trivial logic

13. AI Code Generation Rules

When generating code, the AI must:

Respect existing project structure

Follow Sulu and Symfony conventions

Prefer extension over modification

Reuse existing services where possible

Generate tests for non-trivial logic

Prefer clarity over cleverness

Never invent non-existent Sulu APIs

If uncertain, generate the simplest correct solution.

14. Example Service Pattern
declare(strict_types=1);

final class ExampleService
{
    public function __construct(
        private readonly ExampleRepositoryInterface $repository
    ) {
    }

    public function execute(ExampleCommand $command): void
    {
        // domain logic
    }
}
