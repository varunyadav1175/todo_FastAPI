# Todo List API

This is a simple Todo List API built with FastAPI and MongoDB.

## Endpoints

### `POST /signup`

Signs up a new user.

**Request Body:**

- `username`: The username of the user.
- `password`: The password of the user.

**Response:**

- A message indicating the user was created successfully.

### `POST /token`

Logs in a user and returns a token.

**Request Body:**

- `username`: The username of the user.
- `password`: The password of the user.

**Response:**

- `access_token`: The access token for the user.
- `token_type`: The type of the token (bearer).

### `GET /todos/`

Gets all todos.

**Headers:**

- `Authorization`: Bearer token.

**Response:**

- A list of all todos.

### `POST /todos/`

Creates a new todo.

**Headers:**

- `Authorization`: Bearer token.

**Request Body:**

- `name`: The name of the todo.
- `done`: Whether the todo is done (default is `false`).

**Response:**

- `id`: The id of the created todo.

### `PUT /todos/{todo_id}`

Updates a todo.

**Headers:**

- `Authorization`: Bearer token.

**Path Parameters:**

- `todo_id`: The id of the todo to update.

**Response:**

- The updated todo.

### `DELETE /todos/{todo_id}`

Deletes a todo.

**Headers:**

- `Authorization`: Bearer token.

**Path Parameters:**

- `todo_id`: The id of the todo to delete.

**Response:**

- `deleted_count`: The number of todos deleted.

## Running the Project

To run the project, use the following command:

```bash
uvicorn main:app --reload