---
name: skill-lang-scala
description: Best practices viết Scala hiện đại (3.x) — case classes, pattern matching, for-comprehensions, Future, Cats Effect, implicits và functional patterns.
---

# Skill: Scala

## Khi nào dùng

- Data engineering, Spark pipelines
- Functional programming trên JVM
- Akka/Pekko actor systems
- API với Play Framework hoặc http4s

---

## Case classes & sealed traits

```scala
// Case class — immutable data, equals/hashCode/copy free
case class User(
  id: String,
  email: String,
  name: String,
  role: Role = Role.User,
)

// Sealed trait — exhaustive pattern matching (Scala 2)
sealed trait Role
object Role {
  case object User  extends Role
  case object Admin extends Role
}

// Scala 3 — enum (cleaner)
enum Role:
  case User, Admin, Moderator

// Opaque types (Scala 3)
opaque type UserId = String
object UserId:
  def apply(value: String): UserId = value
  extension (id: UserId) def value: String = id
```

---

## Pattern matching

```scala
def describe(user: User): String = user.role match
  case Role.Admin => s"Admin: ${user.name}"
  case Role.User  => s"User: ${user.name}"
  case _          => "Unknown"

// Destructuring
def processEvent(event: Event): Unit = event match
  case UserCreated(id, email)     => sendWelcome(email)
  case UserDeleted(id)            => cleanup(id)
  case OrderPlaced(id, total, _)  => processPayment(total)

// Guard clauses
def classify(n: Int): String = n match
  case x if x < 0  => "negative"
  case 0            => "zero"
  case x if x > 100 => "large"
  case _            => "positive"
```

---

## For-comprehensions (flatMap chains)

```scala
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global

// Sequential async operations
def createOrder(userId: String, items: List[Item]): Future[Order] =
  for
    user  <- userRepo.findById(userId)           // Future[User]
    _     <- validateItems(items)                // Future[Unit]
    total =  items.map(_.price).sum
    order <- orderRepo.create(user.id, total)    // Future[Order]
    _     <- emailService.sendConfirmation(order) // Future[Unit]
  yield order

// Option chaining
def getCity(userId: String): Option[String] =
  for
    user    <- users.get(userId)
    address <- user.address
    city    <- address.city
  yield city
```

---

## Option & Either

```scala
// Option — value có thể null-safe
def findUser(id: String): Option[User] = users.get(id)

findUser("123")
  .map(_.email)
  .getOrElse("unknown@email.com")

// Either — success hoặc error với context
type AppError = String

def validateAge(age: Int): Either[AppError, Int] =
  if age >= 18 then Right(age)
  else Left(s"Age $age is below minimum 18")

// Chain Either
val result: Either[AppError, User] = for
  age     <- validateAge(inputAge)
  email   <- validateEmail(inputEmail)
  user    <- userRepo.create(email, age).toRight("DB error")
yield user
```

---

## Collections

```scala
val users = List(
  User("1", "a@b.com", "Alice", Role.Admin),
  User("2", "c@d.com", "Bob", Role.User),
)

// Map / filter / reduce
val emails = users.map(_.email)
val admins = users.filter(_.role == Role.Admin)
val nameById = users.map(u => u.id -> u.name).toMap

// groupBy
val byRole: Map[Role, List[User]] = users.groupBy(_.role)

// Fold
val count: Int = users.foldLeft(0)((acc, _) => acc + 1)

// flatMap
val allTags: List[String] = posts.flatMap(_.tags)

// Lazy evaluation với LazyList
val naturals: LazyList[Int] = LazyList.from(1)
val firstTen = naturals.take(10).toList
```

---

## Implicits & Type classes (Scala 3 givens)

```scala
// Scala 3 — given/using (không dùng implicit)
trait Encoder[A]:
  def encode(a: A): String

given Encoder[User] with
  def encode(user: User): String =
    s"""{"id":"${user.id}","email":"${user.email}"}"""

def toJson[A](a: A)(using enc: Encoder[A]): String = enc.encode(a)

// Usage
val json = toJson(user) // tự tìm Encoder[User]

// Extension methods (Scala 3)
extension (user: User)
  def displayName: String = s"${user.name} <${user.email}>"
  def isAdmin: Boolean = user.role == Role.Admin
```

---

## Cats Effect (IO monad)

```scala
import cats.effect.*
import cats.syntax.all.*

// IO — lazy, pure computation
def getUser(id: String): IO[User] =
  IO.fromFuture(IO(userRepo.findById(id)))
    .flatMap:
      case Some(u) => IO.pure(u)
      case None    => IO.raiseError(new Exception(s"User $id not found"))

// Parallel
val (user, orders) = (
  userService.get(userId),
  orderService.listByUser(userId),
).parTupled.unsafeRunSync()

// Resource management (auto cleanup)
val dbResource: Resource[IO, DbConnection] =
  Resource.make(IO(openConnection()))(conn => IO(conn.close()))

dbResource.use { conn =>
  IO(conn.query("SELECT * FROM users"))
}
```

---

## Error handling

```scala
import scala.util.{Try, Success, Failure}

// Try — exceptions wrapped
def parseId(s: String): Try[Int] = Try(s.toInt)

parseId("abc") match
  case Success(n) => println(s"Parsed: $n")
  case Failure(e) => println(s"Failed: ${e.getMessage}")

// recover
val n = parseId("abc")
  .recover { case _: NumberFormatException => 0 }
  .getOrElse(-1)
```

---

## Concurrency với Future

```scala
import scala.concurrent.{Future, Promise}
import scala.concurrent.ExecutionContext.Implicits.global
import scala.util.{Success, Failure}

// Basic
val futureUser: Future[User] = Future {
  db.findUser(id) // chạy trên thread pool
}

// Combine parallel
val result = for
  (user, posts) <- Future.zip(getUser(id), getPosts(id))
yield (user, posts)

// Handle results
futureUser.onComplete:
  case Success(user) => println(user.name)
  case Failure(e)    => println(s"Error: ${e.getMessage}")

// Sequence list of futures
val futures: List[Future[User]] = ids.map(getUser)
val users: Future[List[User]] = Future.sequence(futures)
```

---

## Project tools

```
sbt                 # Standard Scala build tool
Mill               # Alternative build tool
scala-cli          # Scripts & single-file apps

Frameworks:
  http4s           # Pure functional HTTP
  Play Framework   # Full-stack web
  ZIO Http         # ZIO-based HTTP
  Tapir            # API definition + multiple backends

Libraries:
  circe            # JSON encoding/decoding
  doobie           # Functional database access
  Cats / Cats Effect # Functional programming
  ZIO              # Alternative effect system
  Spark            # Big data processing
```

---

## Checklist

- ✅ `case class` cho data model — immutable by default
- ✅ `sealed trait` / `enum` cho tập hợp cố định — exhaustive matching
- ✅ `Option` thay vì `null`, `Either` thay vì throw exceptions
- ✅ `for-comprehension` thay vì nested flatMap
- ✅ `given`/`using` (Scala 3) thay vì `implicit`
- ✅ `IO` / `ZIO` cho side effects trong functional codebase
