---
name: skill-framework-htmx
description: Best practices HTMX — hypermedia-driven UI, AJAX attributes, server-side rendering patterns, integration với Django/Rails/Go/FastAPI.
---

# Skill: HTMX

## Khi nào dùng

- App đơn giản muốn interactivity mà không cần SPA framework
- Backend-heavy (Django, Rails, Go templates, FastAPI)
- Team mạnh server-side, muốn tránh JS complexity
- Progressive enhancement trên HTML

---

## Core attributes

```html
<!-- hx-get / hx-post / hx-put / hx-delete — HTTP verb -->
<button hx-get="/users" hx-target="#list">Load Users</button>

<!-- hx-target — nơi đặt response HTML -->
<div id="list"></div>

<!-- hx-swap — cách swap content -->
<!-- innerHTML (default), outerHTML, beforeend, afterbegin, delete, none -->
<button hx-get="/more" hx-target="#list" hx-swap="beforeend">Load more</button>

<!-- hx-trigger — event khi nào fire request -->
<input
  hx-get="/search"
  hx-trigger="keyup changed delay:300ms"
  hx-target="#results"
/>

<!-- hx-push-url — update browser URL -->
<a hx-get="/users/1" hx-push-url="true" hx-target="#content">View User</a>

<!-- hx-include — include thêm inputs -->
<button hx-post="/save" hx-include="#my-form">Save</button>

<!-- hx-indicator — loading state -->
<button hx-get="/slow" hx-indicator="#spinner">Load</button>
<div id="spinner" class="htmx-indicator">Loading...</div>
```

---

## Patterns phổ biến

### Inline Edit

```html
<!-- Display mode -->
<div id="user-1">
  <span>John Doe</span>
  <button hx-get="/users/1/edit" hx-target="#user-1" hx-swap="outerHTML">
    Edit
  </button>
</div>

<!-- Server trả về form HTML -->
<form id="user-1" hx-put="/users/1" hx-target="#user-1" hx-swap="outerHTML">
  <input name="name" value="John Doe" />
  <button type="submit">Save</button>
  <button hx-get="/users/1" hx-target="#user-1" hx-swap="outerHTML">
    Cancel
  </button>
</form>
```

### Infinite Scroll

```html
<tbody id="users-list">
  <!-- rows... -->
  <tr
    hx-get="/users?page=2"
    hx-trigger="revealed"
    hx-swap="afterend"
    hx-target="this"
  >
    <td colspan="3">Loading...</td>
  </tr>
</tbody>
```

### Search / Filter

```html
<input
  type="search"
  name="q"
  placeholder="Search..."
  hx-get="/users"
  hx-trigger="keyup changed delay:300ms, search"
  hx-target="#results"
  hx-push-url="true"
/>
<div id="results"><!-- server-rendered rows --></div>
```

### Delete with confirmation

```html
<button
  hx-delete="/users/1"
  hx-target="#user-row-1"
  hx-swap="outerHTML"
  hx-confirm="Delete this user?"
>
  Delete
</button>
```

---

## Server-side patterns

### Django (Python)

```python
# views.py
from django.shortcuts import render

def user_list(request):
    users = User.objects.filter(is_active=True)
    # HTMX partial vs full page
    if request.htmx:
        return render(request, "partials/user_list.html", {"users": users})
    return render(request, "users/index.html", {"users": users})

def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "PUT":
        form = UserForm(request.PUT, instance=user)
        if form.is_valid():
            form.save()
            return render(request, "partials/user_row.html", {"user": user})
    return render(request, "partials/user_form.html", {"user": user})
```

### Go (net/http + html/template)

```go
func (h *UserHandler) List(w http.ResponseWriter, r *http.Request) {
    users, _ := h.service.GetAll(r.Context())

    // Detect HTMX request
    if r.Header.Get("HX-Request") == "true" {
        h.tmpl.ExecuteTemplate(w, "user-rows", users)
        return
    }
    h.tmpl.ExecuteTemplate(w, "index", users)
}
```

### FastAPI (Python)

```python
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@app.get("/users", response_class=HTMLResponse)
async def user_list(request: Request, q: str = ""):
    users = await db.search_users(q)
    # Return partial for HTMX, full page otherwise
    template = "partials/user_list.html" if request.headers.get("HX-Request") else "users/index.html"
    return templates.TemplateResponse(template, {"request": request, "users": users})
```

---

## Response headers từ server

```
HX-Trigger          — trigger client-side events
HX-Redirect         — redirect browser
HX-Refresh          — force full page refresh
HX-Push-Url         — update URL bar
HX-Retarget         — override hx-target
HX-Reswap           — override hx-swap
HX-Location         — navigate + push URL (no full reload)
```

```python
# Django example
from django_htmx.http import trigger_client_event, HttpResponseClientRedirect

response = render(request, "partials/success.html", {})
trigger_client_event(response, "userCreated", {"id": user.pk})
return response
```

---

## JavaScript integration

```html
<!-- hx-on — inline event handlers -->
<button hx-get="/data" hx-on::after-request="console.log('done')">Load</button>

<!-- Events -->
<script>
  document.body.addEventListener("htmx:afterSwap", (e) => {
    // Re-initialize JS plugins after HTMX swap
    initTooltips(e.detail.target);
  });

  document.body.addEventListener("htmx:responseError", (e) => {
    showToast("Request failed", "error");
  });
</script>
```

---

## Security

- ✅ CSRF token trong mọi non-GET request
- ✅ Server validate input — HTMX không có client validation
- ✅ Escape HTML trong template output (tránh XSS)
- ✅ Authorization check trong mọi partial endpoint (không assume vì là fragment)
- ✅ Rate limit search/autocomplete endpoints

```html
<!-- Django CSRF -->
<form hx-post="/users" hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'></form>
```

---

## Checklist

- ✅ `hx-boost` để enhance `<a>` và `<form>` toàn trang
- ✅ `hx-indicator` cho mọi slow request
- ✅ Server trả về đúng HTTP status (422 cho validation errors)
- ✅ Partial templates riêng biệt, có thể render standalone
- ✅ Progressive enhancement — app vẫn chạy khi JS disabled
