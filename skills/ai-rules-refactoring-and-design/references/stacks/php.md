# PHP

## Idioms
- `declare(strict_types=1)`, typed properties, constructor promotion, `readonly` classes and properties, enums, `match`.
- Value objects instead of arrays as structures; PSR-4 autoloading, PSR-12 style, PSR-15 middlewares; dependency injection through the constructor.

## Signals
- Controllers doing everything, arrays passed around as structures, static and global state, overuse of magic methods.
- The `@` error suppressor, service locator calls, long `switch` on a type or status.

## Detectors
- `phpstan` or `psalm` (raise the level step by step), `php-cs-fixer` or `phpcs`, `phpmd`, `phpcpd` (duplication).
- `deptrac` (layer rules and cycles), `composer audit`, `composer-unused`.
- `phpunit` or `pest`; `infection` (mutation testing).
- Automated refactoring: `rector` (rule sets for PHP version upgrades, dead code, type declarations).
