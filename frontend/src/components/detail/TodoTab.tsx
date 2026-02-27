import { useState, useEffect, useRef } from 'react'
import { Box, Button, Group, Loader, Alert, Textarea } from '@mantine/core'
import { IconAlertTriangle, IconDeviceFloppy } from '@tabler/icons-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTodo, updateTodo } from '../../api/problems'

interface Props {
  slug: string
}

export default function TodoTab({ slug }: Props) {
  const qc = useQueryClient()
  const { data, isLoading, isError } = useQuery({
    queryKey: ['todo', slug],
    queryFn: () => getTodo(slug),
    retry: false,
  })

  const [content, setContent] = useState('')
  const [dirty, setDirty] = useState(false)
  const contentRef = useRef(content)
  const dirtyRef = useRef(dirty)
  contentRef.current = content
  dirtyRef.current = dirty

  useEffect(() => {
    if (data !== undefined) {
      setContent(data.raw ?? '')
      setDirty(false)
    }
  }, [data])

  const { mutate: save, isPending: saving } = useMutation({
    mutationFn: () => updateTodo(slug, contentRef.current),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['todo', slug] })
      setDirty(false)
    },
  })

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        if (dirtyRef.current) {
          e.preventDefault()
          save()
        }
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [save])

  return (
    <Box p="xl" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {isLoading && <Loader size="sm" />}

      {isError && (
        <Alert
          icon={<IconAlertTriangle size={16} />}
          color="orange"
          title="TODO unavailable"
          maw={500}
        >
          Failed to load TODO.md.
        </Alert>
      )}

      {!isLoading && !isError && (
        <>
          <Textarea
            value={content}
            onChange={(e) => {
              setContent(e.currentTarget.value)
              setDirty(true)
            }}
            placeholder="No TODO items yet. Start with `- [ ] your task` or `* item`."
            autosize
            minRows={12}
            styles={{ input: { fontFamily: 'monospace', fontSize: 13 } }}
          />
          <Group mt="sm">
            <Button
              size="xs"
              leftSection={<IconDeviceFloppy size={14} />}
              disabled={!dirty}
              loading={saving}
              onClick={() => save()}
            >
              Save
            </Button>
          </Group>
        </>
      )}
    </Box>
  )
}
