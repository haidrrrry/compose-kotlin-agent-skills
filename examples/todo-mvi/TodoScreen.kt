// Antipatterns avoided (references/00-banned-antipatterns.md):
//   Row 3  — hardcoded Text("...") → stringResource(R.string.*)
//   Row 4  — collectAsState() → collectAsStateWithLifecycle()
//   Row 7  — LazyColumn without key → key + contentType
//   Row 8  — business logic in Composable → render + dispatch only

package com.example.todo.presentation

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.todo.R
import com.example.todo.domain.TodoUi

@Composable
fun TodoRoute(
    viewModel: TodoViewModel = hiltViewModel(),
    modifier: Modifier = Modifier
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(viewModel) {
        viewModel.effects.collect { effect ->
            when (effect) {
                is TodoUiEffect.ShowSnackbar -> {
                    snackbarHostState.showSnackbar(
                        message = stringResource(effect.messageRes)
                    )
                }
            }
        }
    }

    TodoScreen(
        state = state,
        onEvent = viewModel::onEvent,
        snackbarHostState = snackbarHostState,
        modifier = modifier
    )
}

@Composable
fun TodoScreen(
    state: TodoUiState,
    onEvent: (TodoUiEvent) -> Unit,
    snackbarHostState: SnackbarHostState,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier.fillMaxSize(),
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedTextField(
                    value = state.newItemText,
                    onValueChange = { onEvent(TodoUiEvent.NewItemTextChanged(it)) },
                    modifier = Modifier.weight(1f),
                    label = { Text(stringResource(R.string.todo_new_item_hint)) },
                    singleLine = true
                )
                TextButton(onClick = { onEvent(TodoUiEvent.AddItem) }) {
                    Text(stringResource(R.string.todo_add))
                }
            }

            if (state.isLoading && state.items.isEmpty()) {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
            } else {
                TodoList(
                    items = state.items,
                    onToggle = { id -> onEvent(TodoUiEvent.ToggleItem(id)) },
                    onDelete = { id -> onEvent(TodoUiEvent.DeleteItem(id)) },
                    modifier = Modifier.weight(1f)
                )
            }

            state.error?.let { error ->
                Text(
                    text = stringResource(error.messageRes),
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

@Composable
private fun TodoList(
    items: List<TodoUi>,
    onToggle: (String) -> Unit,
    onDelete: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        items(
            items = items,
            key = { it.id },
            contentType = { "todo" }
        ) { item ->
            TodoRow(
                item = item,
                onToggle = { onToggle(item.id) },
                onDelete = { onDelete(item.id) }
            )
        }
    }
}

@Composable
private fun TodoRow(
    item: TodoUi,
    onToggle: () -> Unit,
    onDelete: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Checkbox(
            checked = item.isDone,
            onCheckedChange = { onToggle() }
        )
        Text(
            text = item.title,
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodyLarge
        )
        IconButton(onClick = onDelete) {
            Icon(
                imageVector = Icons.Default.Delete,
                contentDescription = stringResource(R.string.todo_delete_item)
            )
        }
    }
}
