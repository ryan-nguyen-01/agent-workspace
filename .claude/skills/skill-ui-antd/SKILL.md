---
name: skill-ui-antd
description: Best practices dùng Ant Design (antd v5): ConfigProvider theming, Form, Table, Modal patterns và performance optimization.
---

# Skill: Ant Design (antd v5)

## Theme & ConfigProvider

```tsx
// app/providers.tsx
import { ConfigProvider, App as AntdApp } from 'antd'
import { theme } from 'antd'

const { defaultAlgorithm, darkAlgorithm } = theme

export function AntdProviders({ children }: { children: React.ReactNode }) {
  const isDark = useColorScheme() === 'dark'

  return (
    <ConfigProvider
      theme={{
        algorithm: isDark ? darkAlgorithm : defaultAlgorithm,
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 8,
          fontFamily: '"Inter", -apple-system, sans-serif',
          colorBgContainer: isDark ? '#141414' : '#ffffff',
        },
        components: {
          Button: {
            borderRadius: 8,
            fontWeight: 600,
          },
          Table: {
            headerBg: '#fafafa',
          },
        },
      }}
      locale={viVN}  // Vietnamese locale
    >
      <AntdApp>  {/* ✅ Enables message/notification/modal hooks */}
        {children}
      </AntdApp>
    </ConfigProvider>
  )
}
```

## Form

```tsx
import { Form, Input, Select, Button } from 'antd'

interface CreateUserFormValues {
  email: string
  name: string
  role: 'admin' | 'user'
}

function CreateUserForm({ onSuccess }: { onSuccess: () => void }) {
  const [form] = Form.useForm<CreateUserFormValues>()
  const { message } = App.useApp()  // ✅ Dùng hooks thay vì static methods
  const { mutate, isPending } = useCreateUser()

  const handleFinish = async (values: CreateUserFormValues) => {
    mutate(values, {
      onSuccess: () => {
        message.success('User created successfully')
        form.resetFields()
        onSuccess()
      },
      onError: (err) => {
        message.error(err.message)
      },
    })
  }

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleFinish}
      autoComplete="off"
    >
      <Form.Item
        name="email"
        label="Email"
        rules={[
          { required: true, message: 'Email is required' },
          { type: 'email', message: 'Invalid email format' },
        ]}
      >
        <Input placeholder="user@example.com" />
      </Form.Item>

      <Form.Item
        name="name"
        label="Full Name"
        rules={[{ required: true, min: 2, message: 'Min 2 characters' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item name="role" label="Role" initialValue="user">
        <Select options={[
          { value: 'admin', label: 'Admin' },
          { value: 'user', label: 'User' },
        ]} />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit" loading={isPending} block>
          Create User
        </Button>
      </Form.Item>
    </Form>
  )
}
```

## Table

```tsx
import { Table, Tag, Space, Button, Popconfirm } from 'antd'
import type { ColumnsType, TableProps } from 'antd/es/table'

const columns: ColumnsType<User> = [
  {
    title: 'Name',
    dataIndex: 'name',
    sorter: (a, b) => a.name.localeCompare(b.name),
    ellipsis: true,
  },
  {
    title: 'Email',
    dataIndex: 'email',
    copyable: true,
  },
  {
    title: 'Status',
    dataIndex: 'isActive',
    render: (isActive: boolean) => (
      <Tag color={isActive ? 'green' : 'red'}>
        {isActive ? 'Active' : 'Inactive'}
      </Tag>
    ),
    filters: [
      { text: 'Active', value: true },
      { text: 'Inactive', value: false },
    ],
    onFilter: (value, record) => record.isActive === value,
  },
  {
    title: 'Actions',
    key: 'actions',
    render: (_, record) => (
      <Space>
        <Button type="link" size="small" onClick={() => handleEdit(record)}>Edit</Button>
        <Popconfirm
          title="Delete user?"
          description="This action cannot be undone."
          onConfirm={() => handleDelete(record.id)}
          okText="Delete"
          okButtonProps={{ danger: true }}
        >
          <Button type="link" danger size="small">Delete</Button>
        </Popconfirm>
      </Space>
    ),
  },
]

function UsersTable() {
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 })
  const { data, isLoading } = useUsers(pagination)

  return (
    <Table
      rowKey="id"
      columns={columns}
      dataSource={data?.items}
      loading={isLoading}
      pagination={{
        ...pagination,
        total: data?.total,
        showSizeChanger: true,
        showTotal: (total) => `Total ${total} users`,
        onChange: (page, pageSize) => setPagination({ current: page, pageSize }),
      }}
      scroll={{ x: 800 }}  // ✅ Horizontal scroll trên mobile
    />
  )
}
```

## Modal với useModal

```tsx
import { Modal, Button } from 'antd'
import { useBoolean } from 'ahooks'

function UserSection() {
  const [isOpen, { setTrue: open, setFalse: close }] = useBoolean(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)

  const handleEdit = (user: User) => {
    setEditingUser(user)
    open()
  }

  return (
    <>
      <Button type="primary" onClick={open}>Add User</Button>

      <Modal
        title={editingUser ? 'Edit User' : 'Add User'}
        open={isOpen}
        onCancel={() => { close(); setEditingUser(null) }}
        footer={null}  // ✅ Custom footer trong form
        destroyOnHidden  // ✅ Reset form state khi đóng
        width={560}
      >
        <CreateUserForm
          initialValues={editingUser}
          onSuccess={() => { close(); setEditingUser(null) }}
        />
      </Modal>
    </>
  )
}
```

## Notification & Message

```tsx
// ✅ Dùng hooks (antd v5) — không dùng static methods
function MyComponent() {
  const { message, notification, modal } = App.useApp()

  const handleAction = async () => {
    try {
      await doSomething()
      message.success('Done!')
    } catch (err) {
      notification.error({
        message: 'Operation failed',
        description: err.message,
        duration: 5,
      })
    }
  }

  const handleDelete = () => {
    modal.confirm({
      title: 'Confirm Delete',
      content: 'Are you sure?',
      onOk: () => deleteUser(id),
      okButtonProps: { danger: true },
    })
  }
}
```

## Anti-patterns

```tsx
// ❌ Static methods (deprecated, không work với SSR và custom theme)
import { message } from 'antd'
message.success('Done')  // ❌

// ✅ Dùng App.useApp() hooks
const { message } = App.useApp()
message.success('Done')

// ❌ Không dùng ConfigProvider (mất custom theme)
// ❌ moment.js (antd v5 dùng dayjs mặc định)
// ❌ Import toàn bộ antd (dùng tree-shaking)
import antd from 'antd'  // ❌
import { Button, Form } from 'antd'  // ✅

// ❌ Không set rowKey trong Table (performance issues)
<Table dataSource={users} />  // ❌
<Table rowKey="id" dataSource={users} />  // ✅
```
