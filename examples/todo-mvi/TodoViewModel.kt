// Antipatterns avoided (references/00-banned-antipatterns.md):
//   Row 1  — GlobalScope → viewModelScope only
//   Row 5  — naked _state.value = → _state.update { }
//   Row 6  — mutableStateListOf in VM → StateFlow<List<TodoUi>>
//   Row 8  — pass ViewModel to child → state + onEvent at route boundary

package com.example.todo.presentation

import androidx.annotation.StringRes
import androidx.compose.runtime.Immutable
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.todo.domain.TodoRepository
import com.example.todo.domain.TodoUi
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.launch

@Immutable
data class TodoUiState(
    val items: List<TodoUi> = emptyList(),
    val isLoading: Boolean = false,
    val newItemText: String = "",
    val error: TodoError? = null
)

sealed interface TodoError {
    data class Message(@StringRes val messageRes: Int) : TodoError
}

sealed interface TodoUiEvent {
    data object Refresh : TodoUiEvent
    data class NewItemTextChanged(val text: String) : TodoUiEvent
    data object AddItem : TodoUiEvent
    data class ToggleItem(val id: String) : TodoUiEvent
    data class DeleteItem(val id: String) : TodoUiEvent
}

sealed interface TodoUiEffect {
    data class ShowSnackbar(@StringRes val messageRes: Int) : TodoUiEffect
}

@HiltViewModel
class TodoViewModel @Inject constructor(
    private val repository: TodoRepository
) : ViewModel() {

    private val _state = MutableStateFlow(TodoUiState())
    val state: StateFlow<TodoUiState> = _state.asStateFlow()

    private val _effects = Channel<TodoUiEffect>(Channel.BUFFERED)
    val effects = _effects.receiveAsFlow()

    init {
        observeTodos()
    }

    fun onEvent(event: TodoUiEvent) {
        when (event) {
            TodoUiEvent.Refresh -> refresh()
            is TodoUiEvent.NewItemTextChanged -> _state.update { it.copy(newItemText = event.text) }
            TodoUiEvent.AddItem -> addItem()
            is TodoUiEvent.ToggleItem -> toggleItem(event.id)
            is TodoUiEvent.DeleteItem -> deleteItem(event.id)
        }
    }

    private fun observeTodos() {
        viewModelScope.launch {
            repository.observeTodos()
                .collect { items ->
                    _state.update { it.copy(items = items, isLoading = false) }
                }
        }
    }

    private fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            runCatching { repository.sync() }
                .onFailure {
                    _state.update {
                        it.copy(
                            isLoading = false,
                            error = TodoError.Message(R.string.error_sync_failed)
                        )
                    }
                }
        }
    }

    private fun addItem() {
        val title = _state.value.newItemText.trim()
        if (title.isEmpty()) return
        viewModelScope.launch {
            runCatching { repository.addTodo(title) }
                .onSuccess {
                    _state.update { it.copy(newItemText = "") }
                    _effects.send(TodoUiEffect.ShowSnackbar(R.string.todo_added))
                }
                .onFailure {
                    _effects.send(TodoUiEffect.ShowSnackbar(R.string.error_add_failed))
                }
        }
    }

    private fun toggleItem(id: String) {
        viewModelScope.launch {
            runCatching { repository.toggleTodo(id) }
                .onFailure {
                    _effects.send(TodoUiEffect.ShowSnackbar(R.string.error_toggle_failed))
                }
        }
    }

    private fun deleteItem(id: String) {
        viewModelScope.launch {
            runCatching { repository.deleteTodo(id) }
                .onFailure {
                    _effects.send(TodoUiEffect.ShowSnackbar(R.string.error_delete_failed))
                }
        }
    }
}
