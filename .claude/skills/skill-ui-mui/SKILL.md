---
name: skill-ui-mui
description: Best practices dùng Material UI (MUI v6): theming, component customization, sx prop, responsive design và performance patterns.
---

# Skill: Material UI (MUI v6)

## Theme Setup

```typescript
// theme/index.ts
import { createTheme, alpha } from '@mui/material/styles'

declare module '@mui/material/styles' {
  interface Palette {
    neutral: Palette['primary']
  }
  interface PaletteOptions {
    neutral?: PaletteOptions['primary']
  }
}

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2', light: '#42a5f5', dark: '#1565c0' },
    secondary: { main: '#9c27b0' },
    neutral: { main: '#64748b', light: '#94a3b8', dark: '#475569' },
    background: { default: '#f8fafc', paper: '#ffffff' },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", sans-serif',
    h1: { fontSize: '2.25rem', fontWeight: 700 },
    button: { textTransform: 'none' },  // ✅ Disable uppercase buttons
  },
  shape: { borderRadius: 8 },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: 8, fontWeight: 600 },
      },
    },
    MuiTextField: {
      defaultProps: { size: 'small', variant: 'outlined' },
    },
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: ({ theme }) => ({
          border: `1px solid ${theme.palette.divider}`,
        }),
      },
    },
  },
})
```

## Component Patterns

```tsx
// ✅ sx prop cho one-off styles (không tạo component riêng)
<Box
  sx={{
    display: 'flex',
    alignItems: 'center',
    gap: 2,               // theme.spacing(2) = 16px
    p: { xs: 2, md: 3 }, // Responsive padding
    borderRadius: 2,
    bgcolor: 'background.paper',
    border: 1,
    borderColor: 'divider',
  }}
>

// ✅ styled() cho reusable components
import { styled } from '@mui/material/styles'

const StyledCard = styled(Card)(({ theme }) => ({
  padding: theme.spacing(3),
  transition: theme.transitions.create(['box-shadow']),
  '&:hover': {
    boxShadow: theme.shadows[4],
  },
}))

// ✅ Responsive với useMediaQuery
function UserList() {
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))

  return (
    <Grid container spacing={isMobile ? 1 : 3}>
      {users.map(user => (
        <Grid key={user.id} size={{ xs: 12, sm: 6, md: 4 }}>
          <UserCard user={user} />
        </Grid>
      ))}
    </Grid>
  )
}
```

## Form với React Hook Form + MUI

```tsx
import { Controller, useForm } from 'react-hook-form'
import { TextField, Button, Stack } from '@mui/material'

function CreateUserForm() {
  const { control, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>()

  return (
    <Stack component="form" onSubmit={handleSubmit(onSubmit)} spacing={2}>
      <Controller
        name="email"
        control={control}
        rules={{ required: 'Email is required', pattern: { value: /\S+@\S+/, message: 'Invalid email' } }}
        render={({ field }) => (
          <TextField
            {...field}
            label="Email"
            error={!!errors.email}
            helperText={errors.email?.message}
            fullWidth
          />
        )}
      />

      <Controller
        name="role"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Role" fullWidth>
            <MenuItem value="admin">Admin</MenuItem>
            <MenuItem value="user">User</MenuItem>
          </TextField>
        )}
      />

      <Button type="submit" variant="contained" loading={isSubmitting}>
        Create User
      </Button>
    </Stack>
  )
}
```

## Data Grid

```tsx
import { DataGrid, GridColDef, GridActionsCellItem } from '@mui/x-data-grid'

const columns: GridColDef<User>[] = [
  { field: 'name', headerName: 'Name', flex: 1 },
  { field: 'email', headerName: 'Email', flex: 1.5 },
  {
    field: 'createdAt',
    headerName: 'Created',
    width: 160,
    valueFormatter: (value: Date) => formatDate(value),
  },
  {
    field: 'actions',
    type: 'actions',
    getActions: ({ id }) => [
      <GridActionsCellItem icon={<EditIcon />} label="Edit" onClick={() => handleEdit(id)} />,
      <GridActionsCellItem icon={<DeleteIcon />} label="Delete" onClick={() => handleDelete(id)} />,
    ],
  },
]

function UsersTable() {
  return (
    <DataGrid
      rows={users}
      columns={columns}
      pageSizeOptions={[20, 50, 100]}
      initialState={{ pagination: { paginationModel: { pageSize: 20 } } }}
      disableRowSelectionOnClick
      loading={isLoading}
      slots={{ loadingOverlay: LinearProgress }}
      sx={{ border: 0 }}
    />
  )
}
```

## Notifications với Snackbar

```tsx
// ✅ Global snackbar hook
function useNotification() {
  const [snack, setSnack] = useState<{ message: string; severity: AlertColor } | null>(null)

  const notify = useCallback((message: string, severity: AlertColor = 'success') => {
    setSnack({ message, severity })
  }, [])

  const Snackbar = () => (
    <MuiSnackbar
      open={!!snack}
      autoHideDuration={4000}
      onClose={() => setSnack(null)}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
    >
      <Alert severity={snack?.severity} onClose={() => setSnack(null)}>
        {snack?.message}
      </Alert>
    </MuiSnackbar>
  )

  return { notify, Snackbar }
}
```

## Anti-patterns

```tsx
// ❌ Inline styles thay vì sx
<Box style={{ marginTop: 16, padding: 8 }}>  // Không dùng theme values

// ❌ Hardcode colors
<Typography sx={{ color: '#1976d2' }}>  // ❌
<Typography sx={{ color: 'primary.main' }}>  // ✅ Dùng theme tokens

// ❌ Override với !important
sx={{ '& .MuiButton-root': { color: 'red !important' } }}

// ❌ Import toàn bộ icon package
import * as Icons from '@mui/icons-material'  // Bundle toàn bộ!
// ✅ Named import
import EditIcon from '@mui/icons-material/Edit'
```
