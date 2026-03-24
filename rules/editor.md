# Editor Configuration

Every project must include an `.editorconfig` file at the root with at least the following settings:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.sh]
indent_style = space
indent_size = 2

[*.{js,ts,json,yml,yaml}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

Adapt indentation rules to the language conventions of the project. Propose the `.editorconfig` at project start and wait for user validation.
