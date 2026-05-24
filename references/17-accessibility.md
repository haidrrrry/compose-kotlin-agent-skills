---
name: accessibility
description: >
  Compose accessibility — contentDescription, semantics, mergeDescendants, touch targets,
  TalkBack traversal, WCAG contrast, live regions, Espresso a11y checks. Use when auditing UI.
version: "2.2.0"
updated: "2026-05-21"
---

# Accessibility — Compose, TalkBack, WCAG

## Minimum standards

| Rule | Value |
|---|---|
| Touch target | **48dp × 48dp** minimum (Material) |
| Text contrast (WCAG AA) | **4.5:1** normal text, **3:1** large text (18sp+ bold / 24sp+) |
| Decorative images | `contentDescription = null` |
| Functional icons | Meaningful `contentDescription` or `clearAndSetSemantics` |

---

## WRONG / RIGHT 1 — Missing contentDescription on functional IconButton

```kotlin
// WRONG — TalkBack says "Button" with no context
IconButton(onClick = onDelete) {
    Icon(Icons.Default.Delete, contentDescription = null)
}

// RIGHT
IconButton(onClick = onDelete) {
    Icon(
        imageVector = Icons.Default.Delete,
        contentDescription = stringResource(R.string.delete_item)
    )
}
```

---

## WRONG / RIGHT 2 — Redundant semantics on clickable Row

```kotlin
// WRONG — double announcement: row + child text
Row(
    modifier = Modifier
        .clickable(onClick = onClick)
        .padding(16.dp)
) {
    Text("Account settings")
    Icon(Icons.Default.ChevronRight, contentDescription = null)
}

// RIGHT — merge descendants into single node
Row(
    modifier = Modifier
        .clickable(onClick = onClick)
        .semantics(mergeDescendants = true) {}
        .padding(16.dp)
) {
    Text(stringResource(R.string.account_settings))
    Icon(Icons.Default.ChevronRight, contentDescription = null)
}
```

---

## WRONG / RIGHT 3 — Touch target under 48dp

```kotlin
// WRONG — 24dp hit area fails WCAG / Material
IconButton(
    onClick = onClose,
    modifier = Modifier.size(24.dp)
) {
    Icon(Icons.Default.Close, contentDescription = stringResource(R.string.close))
}

// RIGHT — minimumInteractiveComponentSize or explicit 48dp
IconButton(
    onClick = onClose,
    modifier = Modifier
        .minimumInteractiveComponentSize()
        .size(48.dp)
) {
    Icon(Icons.Default.Close, contentDescription = stringResource(R.string.close))
}
```

---

## WRONG / RIGHT 4 — Custom component missing semantics

```kotlin
// WRONG — TalkBack skips custom toggle
@Composable
fun CustomToggle(checked: Boolean, onToggle: (Boolean) -> Unit) {
    Box(
        modifier = Modifier
            .size(48.dp, 28.dp)
            .background(if (checked) Color.Green else Color.Gray)
            .clickable { onToggle(!checked) }
    )
}

// RIGHT — clearAndSetSemantics with role + state
@Composable
fun CustomToggle(
    checked: Boolean,
    onToggle: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .size(48.dp, 28.dp)
            .toggleable(value = checked, onValueChange = onToggle)
            .semantics {
                role = Role.Switch
                stateDescription = if (checked) {
                    "On"
                } else {
                    "Off"
                }
            }
            .background(if (checked) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant)
    )
}
```

---

## WRONG / RIGHT 5 — Dynamic updates not announced (live region)

```kotlin
// WRONG — error text appears silently for TalkBack
if (error != null) {
    Text(text = error, color = MaterialTheme.colorScheme.error)
}

// RIGHT — live region for assertive announcements
if (error != null) {
    Text(
        text = error,
        color = MaterialTheme.colorScheme.error,
        modifier = Modifier.semantics {
            liveRegion = LiveRegionMode.Assertive
        }
    )
}
```

---

## WRONG / RIGHT 6 — Espresso test without accessibility checks

```kotlin
// WRONG — only checks visibility
composeTestRule.onNodeWithText("Save").assertIsDisplayed()

// RIGHT — semantics + touch target in UI test
composeTestRule.onNodeWithContentDescription("Save changes")
    .assertIsDisplayed()
    .assertHasClickAction()
    .performClick()

// Instrumentation — AccessibilityChecks (Espresso)
AccessibilityChecks.enable().apply {
    setRunChecksFromRootView(true)
}
onView(withId(R.id.main)).check(matches(isDisplayed()))
```

---

## Contrast check (WCAG AA)

```kotlin
// Verify in theme — onSurface on surface must be ≥ 4.5:1
// Use Android Studio Layout Inspector → Accessibility Scanner
// Or compute: ColorUtils.calculateContrast(foreground, background) >= 4.5

@Composable
fun AccessibleBody(text: String) {
    Text(
        text = text,
        style = MaterialTheme.typography.bodyLarge,
        color = MaterialTheme.colorScheme.onSurface  // designed for 4.5:1 on surface
    )
}
```

## Audit checklist (link to compose sub-skill REVIEW MODE)

1. Every interactive control has label or `mergeDescendants`
2. Decorative icons: `contentDescription = null`
3. Touch targets ≥ 48dp
4. Error/status uses `LiveRegionMode` where needed
5. Traversal order matches visual order (avoid `focusProperties` hacks unless needed)
6. UI tests use `onNodeWithContentDescription` not raw text when label differs
