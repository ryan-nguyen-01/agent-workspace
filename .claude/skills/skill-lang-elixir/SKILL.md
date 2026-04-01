---
name: skill-lang-elixir
description: Best practices viết Elixir hiện đại — pattern matching, processes, GenServer, supervision trees, pipe operator, và OTP patterns.
---

# Skill: Elixir

## Pattern Matching

```elixir
# ✅ Pattern matching — first-class feature
{:ok, user} = Users.get_user(id)
{:error, reason} = Users.get_user("invalid")

# ✅ Destructuring
%{name: name, email: email} = user
[head | tail] = [1, 2, 3]

# ✅ Function clauses with pattern matching
def handle_result({:ok, data}), do: process(data)
def handle_result({:error, :not_found}), do: {:error, "User not found"}
def handle_result({:error, reason}), do: {:error, "Unexpected: #{reason}"}

# ✅ Case expression
case Users.get_user(id) do
  {:ok, user} -> {:ok, user}
  {:error, :not_found} -> {:error, "Not found"}
  {:error, reason} -> {:error, "Error: #{reason}"}
end
```

---

## Pipe Operator

```elixir
# ✅ Pipe |> — thread first argument
def create_user(params) do
  params
  |> validate_params()
  |> build_user()
  |> Repo.insert()
  |> notify_if_success()
end

# Without pipe (hard to read)
notify_if_success(Repo.insert(build_user(validate_params(params))))
```

---

## Functions & Modules

```elixir
defmodule MyApp.Users do
  @moduledoc """
  Users context — manages user lifecycle.
  """

  alias MyApp.Repo
  alias MyApp.Users.User

  # ✅ Public function
  @spec get_user(String.t()) :: {:ok, User.t()} | {:error, :not_found}
  def get_user(id) do
    case Repo.get(User, id) do
      nil -> {:error, :not_found}
      user -> {:ok, user}
    end
  end

  # ✅ Bang functions raise on error
  def get_user!(id) do
    case get_user(id) do
      {:ok, user} -> user
      {:error, :not_found} -> raise "User #{id} not found"
    end
  end

  # ✅ Private function
  defp validate_email(email) do
    if String.contains?(email, "@"), do: {:ok, email}, else: {:error, :invalid_email}
  end
end
```

---

## Structs

```elixir
defmodule MyApp.Users.User do
  @enforce_keys [:email, :name]
  defstruct [
    :id,
    :email,
    :name,
    :hashed_password,
    role: :user,
    is_active: true,
    inserted_at: nil,
    updated_at: nil,
  ]

  @type t :: %__MODULE__{
    id: String.t() | nil,
    email: String.t(),
    name: String.t(),
    role: :user | :admin,
    is_active: boolean(),
  }
end
```

---

## GenServer (Stateful Process)

```elixir
defmodule MyApp.Cache do
  use GenServer

  # Client API
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, %{}, opts)
  end

  def get(pid, key), do: GenServer.call(pid, {:get, key})
  def set(pid, key, value), do: GenServer.cast(pid, {:set, key, value})
  def delete(pid, key), do: GenServer.cast(pid, {:delete, key})

  # Server Callbacks
  @impl true
  def init(state), do: {:ok, state}

  @impl true
  def handle_call({:get, key}, _from, state) do
    {:reply, Map.get(state, key), state}
  end

  @impl true
  def handle_cast({:set, key, value}, state) do
    {:noreply, Map.put(state, key, value)}
  end

  @impl true
  def handle_cast({:delete, key}, state) do
    {:noreply, Map.delete(state, key)}
  end
end
```

---

## Supervisor (Supervision tree)

```elixir
defmodule MyApp.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      MyApp.Repo,
      MyAppWeb.Endpoint,
      {MyApp.Cache, name: MyApp.Cache},
      # Registry for named processes
      {Registry, keys: :unique, name: MyApp.Registry},
    ]

    opts = [strategy: :one_for_one, name: MyApp.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
```

---

## Task & Async

```elixir
# ✅ Async concurrent tasks
task1 = Task.async(fn -> fetch_user(id) end)
task2 = Task.async(fn -> fetch_orders(id) end)

user = Task.await(task1)
orders = Task.await(task2)

# ✅ Task.async_stream — parallel map
results =
  ids
  |> Task.async_stream(&fetch_user/1, max_concurrency: 10, timeout: 5_000)
  |> Enum.into([])
```

---

## Ecto (Database)

```elixir
defmodule MyApp.Users.User do
  use Ecto.Schema
  import Ecto.Changeset

  schema "users" do
    field :email, :string
    field :name, :string
    field :password, :string, virtual: true
    field :hashed_password, :string
    field :role, Ecto.Enum, values: [:user, :admin], default: :user
    field :is_active, :boolean, default: true
    timestamps()
  end

  def changeset(user, attrs) do
    user
    |> cast(attrs, [:email, :name, :password])
    |> validate_required([:email, :name, :password])
    |> validate_format(:email, ~r/^[^\s]+@[^\s]+$/)
    |> validate_length(:password, min: 8)
    |> unique_constraint(:email)
    |> put_password_hash()
  end

  defp put_password_hash(%{valid?: true, changes: %{password: pw}} = changeset) do
    change(changeset, hashed_password: Bcrypt.hash_pwd_salt(pw))
  end
  defp put_password_hash(changeset), do: changeset
end
```

---

## Error handling

```elixir
# ✅ with — multi-step pipelines
def create_user(params) do
  with {:ok, validated} <- validate(params),
       {:ok, user} <- Repo.insert(User.changeset(%User{}, validated)),
       :ok <- send_welcome_email(user) do
    {:ok, user}
  else
    {:error, %Ecto.Changeset{} = cs} -> {:error, :validation, cs}
    {:error, :email_failed} -> {:ok, user}  # non-critical
    error -> error
  end
end
```

---

## Idioms checklist

- ✅ `{:ok, value}` / `{:error, reason}` tuples cho responses
- ✅ Pattern matching trong function clauses
- ✅ Pipe operator `|>` cho transformation chains
- ✅ `with` cho multi-step error handling
- ✅ `!` bang functions cho raiseeable operations
- ✅ Supervision trees cho fault tolerance
- ✅ `@spec` type specs cho public functions
- ✅ Contexts để organize business logic (Phoenix)
