import { useState, useEffect, useRef } from 'react'
import { Modal, TextInput, Select, Group, Button } from '@mantine/core'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createProblem } from '../../api/problems'

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

interface Props {
  opened: boolean
  initialState: string
  onClose: () => void
  onCreated: (slug: string) => void
}

export default function CreateProblemModal({ opened, initialState, onClose, onCreated }: Props) {
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [slugManual, setSlugManual] = useState(false)
  const [problemType, setProblemType] = useState<string>('standard')
  const queryClient = useQueryClient()
  const slugManualRef = useRef(false)

  // Sync ref with state so the effect closure sees the latest value
  slugManualRef.current = slugManual

  useEffect(() => {
    if (!slugManualRef.current) {
      setSlug(slugify(name))
    }
  }, [name])

  // Reset form when modal opens
  useEffect(() => {
    if (opened) {
      setName('')
      setSlug('')
      setSlugManual(false)
      setProblemType('standard')
    }
  }, [opened])

  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      createProblem({ name, slug, state: initialState, type: problemType }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['problems'] })
      onClose()
      onCreated(slug)
    },
  })

  return (
    <Modal opened={opened} onClose={onClose} title="Create Problem" centered>
      <TextInput
        label="Title"
        placeholder="Problem name"
        value={name}
        onChange={(e) => setName(e.currentTarget.value)}
        mb="sm"
        data-autofocus
      />
      <TextInput
        label="Slug"
        placeholder="problem-slug"
        value={slug}
        onChange={(e) => {
          setSlugManual(true)
          setSlug(e.currentTarget.value)
        }}
        mb="sm"
      />
      <Select
        label="Type"
        data={[
          { value: 'standard', label: 'Standard' },
          { value: 'interactive', label: 'Interactive' },
          { value: 'multi', label: 'Multi' },
        ]}
        value={problemType}
        onChange={(v) => setProblemType(v ?? 'standard')}
        mb="lg"
      />
      <Group justify="flex-end">
        <Button variant="default" onClick={onClose}>
          Cancel
        </Button>
        <Button onClick={() => mutate()} loading={isPending} disabled={!name || !slug}>
          Create
        </Button>
      </Group>
    </Modal>
  )
}
