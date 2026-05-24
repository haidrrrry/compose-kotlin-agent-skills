// Antipatterns avoided (references/00-banned-antipatterns.md):
//   Row 10 — blocking Room on wrong dispatcher pattern → Flow from DAO, suspend sync
//   (no blocking calls; network sync isolated in suspend sync())

package com.example.todo.domain

import com.example.todo.data.TodoDao
import com.example.todo.data.TodoEntity
import com.example.todo.data.TodoRemoteDataSource
import androidx.compose.runtime.Immutable
import javax.inject.Inject
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

@Immutable
data class TodoUi(
    val id: String,
    val title: String,
    val isDone: Boolean
)

interface TodoRepository {
    fun observeTodos(): Flow<List<TodoUi>>
    suspend fun sync()
    suspend fun addTodo(title: String)
    suspend fun toggleTodo(id: String)
    suspend fun deleteTodo(id: String)
}

class TodoRepositoryImpl @Inject constructor(
    private val dao: TodoDao,
    private val remote: TodoRemoteDataSource
) : TodoRepository {

    override fun observeTodos(): Flow<List<TodoUi>> =
        dao.observeAll()
            .map { entities -> entities.map { it.toUi() } }

    override suspend fun sync() {
        val remoteTodos = remote.fetchTodos()
        dao.upsertAll(remoteTodos.map { it.toEntity() })
    }

    override suspend fun addTodo(title: String) {
        val entity = TodoEntity(
            id = java.util.UUID.randomUUID().toString(),
            title = title,
            isDone = false,
            updatedAt = System.currentTimeMillis()
        )
        dao.upsert(entity)
        runCatching { remote.pushTodo(entity) }
    }

    override suspend fun toggleTodo(id: String) {
        dao.toggleDone(id)
        dao.getById(id)?.let { entity ->
            runCatching { remote.pushTodo(entity) }
        }
    }

    override suspend fun deleteTodo(id: String) {
        dao.deleteById(id)
        runCatching { remote.deleteTodo(id) }
    }
}

private fun TodoEntity.toUi() = TodoUi(
    id = id,
    title = title,
    isDone = isDone
)
