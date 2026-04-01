---
name: skill-lang-ruby
description: Best practices viết Ruby hiện đại — blocks/procs/lambdas, modules/concerns, metaprogramming cơ bản, error handling và idiomatic Ruby patterns.
---

# Skill: Ruby

## Blocks, Procs & Lambdas

```ruby
# ✅ Block — implicit yield
def measure
  start = Time.now
  result = yield
  puts "Elapsed: #{Time.now - start}s"
  result
end

measure { expensive_operation() }

# ✅ Block with argument check
def safe_yield(value)
  yield(value) if block_given?
end

# ✅ Proc — closures
double = Proc.new { |n| n * 2 }
double.call(5)  # => 10

# ✅ Lambda — strict arity, own return
square = ->(n) { n * n }
square.(4)   # => 16
square.call(4)

# ✅ Method to proc
[1, 2, 3].map(&method(:puts))
["a", "B", "C"].map(&:upcase)
```

---

## Modules & Mixins

```ruby
# ✅ Module for namespacing
module MyApp
  module Users
    class User
      attr_reader :id, :email, :name

      def initialize(id:, email:, name:)
        @id = id
        @email = email
        @name = name
      end
    end
  end
end

# ✅ Concern (mixin)
module Timestampable
  def self.included(base)
    base.attr_accessor :created_at, :updated_at
  end

  def touch
    self.updated_at = Time.now
  end
end

class Post
  include Timestampable
end

# ✅ extend — add module methods as class methods
module ClassMethods
  def find_active
    all.select(&:active?)
  end
end

class User
  extend ClassMethods
end
```

---

## Error Handling

```ruby
# ✅ Custom exceptions
class NotFoundError < StandardError
  def initialize(resource, id)
    super("#{resource} '#{id}' not found")
  end
end

class ValidationError < StandardError
  attr_reader :errors

  def initialize(errors)
    @errors = errors
    super(errors.join(', '))
  end
end

# ✅ rescue specifics
def find_user(id)
  user = User.find(id)
  raise NotFoundError.new('User', id) unless user
  user
rescue ActiveRecord::RecordNotFound
  raise NotFoundError.new('User', id)
end

# ✅ ensure — always runs
def with_connection
  conn = acquire_connection
  yield conn
rescue => e
  log_error(e)
  raise
ensure
  conn&.release
end

# ✅ retry
attempts = 0
begin
  risky_operation()
rescue TransientError => e
  attempts += 1
  retry if attempts < 3
  raise
end
```

---

## Enumerable

```ruby
# ✅ Rich collection methods
users = [
  { name: "Alice", role: "admin", active: true },
  { name: "Bob", role: "user", active: false },
  { name: "Carol", role: "admin", active: true },
]

active_admins = users
  .select { _1[:active] && _1[:role] == "admin" }
  .map { _1[:name] }
  .sort

# ✅ group_by
by_role = users.group_by { _1[:role] }

# ✅ each_with_object
result = users.each_with_object({}) { |u, h| h[u[:name]] = u[:role] }

# ✅ flat_map
words = [["hello world"], ["foo bar"]].flat_map(&:split)

# ✅ tally (Ruby 2.7+)
['a', 'b', 'a', 'c', 'a'].tally  # => {"a"=>3, "b"=>1, "c"=>1}
```

---

## Keyword Arguments

```ruby
# ✅ Keyword arguments — named, default, required
def create_user(email:, name:, role: :user, active: true)
  User.new(email: email, name: name, role: role, active: active)
end

create_user(email: "a@b.com", name: "Alice")
create_user(email: "b@c.com", name: "Bob", role: :admin)

# ✅ Double splat for hash args
def configure(**options)
  options.each { |k, v| set(k, v) }
end
```

---

## Struct & Data

```ruby
# ✅ Struct — lightweight value object
Point = Struct.new(:x, :y) do
  def distance_to(other)
    Math.sqrt((x - other.x)**2 + (y - other.y)**2)
  end
end

p = Point.new(0, 0)
q = Point.new(3, 4)
p.distance_to(q)  # => 5.0

# ✅ Data class (Ruby 3.2+) — immutable struct
Measure = Data.define(:amount, :unit) do
  def to_s = "#{amount} #{unit}"
end

m = Measure.new(amount: 100, unit: "kg")
m2 = m.with(amount: 200)  # immutable update
```

---

## Pattern Matching (Ruby 3+)

```ruby
# ✅ case/in pattern
response = { status: 200, body: { user: { name: "Alice" } } }

case response
in { status: 200, body: { user: { name: String => name } } }
  puts "Welcome, #{name}"
in { status: 404 }
  puts "Not found"
in { status: 500, body: { error: error } }
  puts "Error: #{error}"
end

# ✅ Find pattern
users = [{ id: 1, role: :admin }, { id: 2, role: :user }]
users in [*, { id:, role: :admin }, *]
puts id  # 1
```

---

## Frozen String Literals

```ruby
# frozen_string_literal: true

# All string literals frozen — better performance
name = "Alice"
name << " Smith"  # raises FrozenError

# Mutable string
name = +"Alice"
name << " Smith"  # ✅
```

---

## Idioms checklist

- ✅ `||=` cho lazy initialization: `@cache ||= {}`
- ✅ `&.` safe navigation: `user&.email`
- ✅ `_1` numbered block parameter (Ruby 2.7+)
- ✅ `yield_self` / `then` cho pipelines
- ✅ `tap` cho side effects in chains
- ✅ Keyword args cho methods với nhiều params
- ✅ Guard clauses (return early) thay nested if
- ✅ `freeze` string constants
- ✅ `Data.define` cho immutable value objects (3.2+)
