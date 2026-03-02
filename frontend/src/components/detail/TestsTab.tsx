import { useState, useCallback, useRef, useEffect, useMemo } from 'react'
import {
  Box,
  Button,
  Group,
  Text,
  Badge,
  ActionIcon,
  Textarea,
  Loader,
  Alert,
  Tooltip,
  Modal,
  TextInput,
  Select,
  NumberInput,
  Stack,
  Code,
  Accordion,
  ScrollArea,
} from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { notifications } from '@mantine/notifications'
import {
  IconPlus,
  IconPlayerPlay,
  IconAlertTriangle,
  IconFile,
  IconCode,
  IconGripVertical,
} from '@tabler/icons-react'
import { DndContext, closestCenter, DragOverlay, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import type { Problem, TestSetDetail, JobStatus } from '../../types/problem'
import {
  getTestSets,
  getTestContent,
  generateTests,
  generateAllTests,
  createTestSet,
  createTestCase,
  updateTestCaseDescription,
  openGeneratorInEditor,
  openTestCaseInEditor,
  reorderTestSets,
} from '../../api/problems'
import { useJobPoller } from '../../hooks/useJobPoller'

interface Props {
  problem: Problem
}

interface SelectedTest {
  setName: string
  testName: string
}

// ---------------------------------------------------------------------------
// Add Test Case modal (inline per test set)
// ---------------------------------------------------------------------------

function AddTestModal({
  opened,
  onClose,
  slug,
  setName,
  onAdded,
}: {
  opened: boolean
  onClose: () => void
  slug: string
  setName: string
  onAdded: () => void
}) {
  const [content, setContent] = useState('')
  const [name, setName2] = useState('')
  const [description, setDescription] = useState('')

  const { mutate: add, isPending } = useMutation({
    mutationFn: () =>
      createTestCase(slug, setName, {
        content,
        name: name || undefined,
        description: description || undefined,
      }),
    onSuccess: () => {
      notifications.show({ message: 'Test case added', color: 'green' })
      onAdded()
      onClose()
      setContent('')
      setName2('')
      setDescription('')
    },
    onError: () =>
      notifications.show({ message: 'Test case creation not yet implemented', color: 'orange' }),
  })

  return (
    <Modal opened={opened} onClose={onClose} title={`Add test to ${setName}`} size="md">
      <Stack>
        <Textarea
          label="Input content"
          placeholder="Paste raw test input here"
          required
          minRows={5}
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <TextInput
          label="Name"
          description="Auto-assigned if left blank"
          placeholder="e.g. edge-case-1"
          value={name}
          onChange={(e) => setName2(e.target.value)}
        />
        <Textarea
          label="Description"
          placeholder="Optional note about this test"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <Group justify="flex-end">
          <Button variant="default" onClick={onClose}>
            Cancel
          </Button>
          <Button loading={isPending} onClick={() => add()} disabled={!content.trim()}>
            Add
          </Button>
        </Group>
      </Stack>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Add Test Set modal
// ---------------------------------------------------------------------------

function AddTestSetModal({
  opened,
  onClose,
  slug,
  onAdded,
}: {
  opened: boolean
  onClose: () => void
  slug: string
  onAdded: () => void
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [points, setPoints] = useState<number | string>(0)
  const [markingStyle, setMarkingStyle] = useState<string>('all_or_nothing')

  const { mutate: add, isPending } = useMutation({
    mutationFn: () =>
      createTestSet(slug, {
        name,
        description: description || undefined,
        points: Number(points),
        marking_style: markingStyle,
      }),
    onSuccess: () => {
      notifications.show({ message: 'Test set created', color: 'green' })
      onAdded()
      onClose()
      setName('')
      setDescription('')
      setPoints(0)
      setMarkingStyle('all_or_nothing')
    },
    onError: () =>
      notifications.show({ message: 'Test set creation not yet implemented', color: 'orange' }),
  })

  return (
    <Modal opened={opened} onClose={onClose} title="Add Test Set" size="sm">
      <Stack>
        <TextInput
          label="Name"
          placeholder="setA"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <Textarea
          label="Description"
          placeholder="Optional"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <NumberInput
          label="Points"
          value={points}
          onChange={setPoints}
          min={0}
        />
        <Select
          label="Marking Style"
          data={[
            { value: 'all_or_nothing', label: 'All or Nothing' },
            { value: 'progressive', label: 'Progressive' },
          ]}
          value={markingStyle}
          onChange={(v) => setMarkingStyle(v ?? 'all_or_nothing')}
        />
        <Group justify="flex-end">
          <Button variant="default" onClick={onClose}>
            Cancel
          </Button>
          <Button loading={isPending} onClick={() => add()} disabled={!name.trim()}>
            Create
          </Button>
        </Group>
      </Stack>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Sortable Accordion Item wrapper
// ---------------------------------------------------------------------------

/** Compact header shown in the DragOverlay while dragging. */
function TestSetDragPreview({ set }: { set: TestSetDetail }) {
  return (
    <Box
      style={{
        background: 'var(--mantine-color-body)',
        border: '1px solid var(--mantine-color-gray-3)',
        borderRadius: 'var(--mantine-radius-sm)',
        padding: '8px 12px',
        boxShadow: 'var(--mantine-shadow-md)',
      }}
    >
      <Group justify="space-between" wrap="nowrap">
        <Group gap={6} wrap="nowrap">
          <IconGripVertical size={14} color="var(--mantine-color-gray-5)" />
          <Text size="sm" fw={600} style={{ fontFamily: 'monospace' }}>
            {set.name}
          </Text>
          {set.config?.points != null && set.config.points > 0 && (
            <Badge size="xs" variant="light" color="teal">
              {set.config.points}pts
            </Badge>
          )}
        </Group>
        <Badge size="xs" color="gray" variant="light">
          {set.test_cases.length}
        </Badge>
      </Group>
    </Box>
  )
}

function SortableTestSetItem({
  set,
  selected,
  genJobId,
  problem,
  generate,
  selectTest,
  setAddTestSet,
  openGeneratorInEditor: openGen,
  openTestCaseInEditor: openTest,
}: {
  set: TestSetDetail
  selected: SelectedTest | null
  genJobId: string | null
  problem: Problem
  generate: (params: { setName: string; genName: string }) => void
  selectTest: (setName: string, testName: string, description?: string) => void
  setAddTestSet: (name: string) => void
  openGeneratorInEditor: typeof openGeneratorInEditor
  openTestCaseInEditor: typeof openTestCaseInEditor
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: set.name,
  })

  const style = {
    // Only apply Y translation — never scaleY which squishes expanded content
    transform: CSS.Translate.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : undefined,
  }

  return (
    <Accordion.Item ref={setNodeRef} style={style} value={set.name}>
      <Accordion.Control py="xs">
        <Group justify="space-between" wrap="nowrap" pr="xs">
          <Group gap={6} wrap="nowrap">
            <Box
              {...attributes}
              {...listeners}
              style={{ cursor: 'grab', display: 'flex', alignItems: 'center' }}
              onClick={(e: React.MouseEvent) => e.stopPropagation()}
            >
              <IconGripVertical size={14} color="var(--mantine-color-gray-5)" />
            </Box>
            <Text
              size="sm"
              fw={600}
              style={{ fontFamily: 'monospace' }}
            >
              {set.name}
            </Text>
            {set.config?.points != null && set.config.points > 0 && (
              <Badge size="xs" variant="light" color="teal">
                {set.config.points}pts
              </Badge>
            )}
          </Group>
          <Badge size="xs" color="gray" variant="light">
            {set.test_cases.length}
          </Badge>
        </Group>
      </Accordion.Control>

      <Accordion.Panel p={0}>
        <Stack gap={0}>
          {/* Generators */}
          {set.generators.map((gen) => (
            <Group
              key={gen.name}
              px="sm"
              py={5}
              justify="space-between"
              style={{
                borderBottom: '1px solid var(--mantine-color-gray-1)',
                background: 'var(--mantine-color-violet-0)',
              }}
            >
              <Group gap={6} wrap="nowrap">
                <IconCode size={12} color="var(--mantine-color-violet-6)" />
                <Text
                  size="xs"
                  style={{ fontFamily: 'monospace' }}
                  c="violet"
                >
                  {gen.name}
                </Text>
              </Group>
              <Group gap={2} wrap="nowrap">
                <Tooltip label="Open in Cursor">
                  <ActionIcon
                    size="xs"
                    variant="subtle"
                    color="violet"
                    onClick={() =>
                      openGen(problem.slug, set.name, gen.name)
                    }
                  >
                    <IconCode size={10} />
                  </ActionIcon>
                </Tooltip>
                <Tooltip label={genJobId ? 'Generation in progress…' : `Run ${gen.name}`}>
                  <ActionIcon
                    size="xs"
                    variant="subtle"
                    color="violet"
                    loading={!!genJobId}
                    onClick={() =>
                      generate({ setName: set.name, genName: gen.name })
                    }
                  >
                    <IconPlayerPlay size={10} />
                  </ActionIcon>
                </Tooltip>
              </Group>
            </Group>
          ))}

          {/* Test cases */}
          {set.test_cases.map((tc) => {
            const isSelected =
              selected?.setName === set.name &&
              selected?.testName === tc.name
            return (
              <Group
                key={tc.name}
                px="sm"
                py={5}
                gap="xs"
                wrap="nowrap"
                style={{
                  cursor: 'pointer',
                  borderBottom: '1px solid var(--mantine-color-gray-1)',
                  background: isSelected
                    ? 'var(--mantine-color-blue-0)'
                    : undefined,
                }}
                justify="space-between"
                onClick={() =>
                  selectTest(set.name, tc.name, tc.description)
                }
              >
                <Group gap={6} wrap="nowrap" style={{ minWidth: 0, flex: 1 }}>
                  <IconFile
                    size={12}
                    color={
                      isSelected
                        ? 'var(--mantine-color-blue-6)'
                        : 'var(--mantine-color-gray-5)'
                    }
                    style={{ flexShrink: 0 }}
                  />
                  <Text
                    size="xs"
                    style={{ fontFamily: 'monospace', minWidth: 0, flex: 1 }}
                    truncate
                    c={isSelected ? 'blue' : undefined}
                  >
                    {tc.name}
                  </Text>
                </Group>
                <Group gap={2} wrap="nowrap" style={{ flexShrink: 0 }}>
                  <Tooltip label="Open in Cursor">
                    <ActionIcon
                      size="xs"
                      variant="subtle"
                      onClick={() =>
                        openTest(problem.slug, tc.set_name, tc.name)
                      }
                    >
                      <IconCode size={12} />
                    </ActionIcon>
                  </Tooltip>
                </Group>
              </Group>
            )
          })}

          {set.test_cases.length === 0 && set.generators.length === 0 && (
            <Text size="xs" c="dimmed" px="sm" py="xs" fs="italic">
              No tests yet
            </Text>
          )}

          {/* Add test button */}
          <Group
            px="xs"
            py={4}
            style={{ borderTop: '1px solid var(--mantine-color-gray-1)' }}
          >
            <Button
              size="xs"
              variant="subtle"
              color="gray"
              leftSection={<IconPlus size={10} />}
              onClick={() => setAddTestSet(set.name)}
            >
              Add test
            </Button>
          </Group>
        </Stack>
      </Accordion.Panel>
    </Accordion.Item>
  )
}

// ---------------------------------------------------------------------------
// Main TestsTab
// ---------------------------------------------------------------------------

const SIDEBAR_WIDTH_KEY = 'tests-tab-sidebar-width'
const DEFAULT_SIDEBAR_WIDTH = 320
const MIN_SIDEBAR_WIDTH = 200
const MAX_SIDEBAR_WIDTH = 600

function useDraggableSidebar() {
  const [width, setWidth] = useState(() => {
    const stored = localStorage.getItem(SIDEBAR_WIDTH_KEY)
    return stored ? Math.max(MIN_SIDEBAR_WIDTH, Math.min(MAX_SIDEBAR_WIDTH, Number(stored))) : DEFAULT_SIDEBAR_WIDTH
  })
  const dragging = useRef(false)
  const startX = useRef(0)
  const startWidth = useRef(0)

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    dragging.current = true
    startX.current = e.clientX
    startWidth.current = width

    const onMouseMove = (ev: MouseEvent) => {
      if (!dragging.current) return
      const newWidth = Math.max(MIN_SIDEBAR_WIDTH, Math.min(MAX_SIDEBAR_WIDTH, startWidth.current + ev.clientX - startX.current))
      setWidth(newWidth)
    }

    const onMouseUp = () => {
      dragging.current = false
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseup', onMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', onMouseUp)
  }, [width])

  useEffect(() => {
    localStorage.setItem(SIDEBAR_WIDTH_KEY, String(width))
  }, [width])

  return { width, onMouseDown }
}

export default function TestsTab({ problem }: Props) {
  const [selected, setSelected] = useState<SelectedTest | null>(null)
  const [editDescription, setEditDescription] = useState('')
  const [addSetOpen, { open: openAddSet, close: closeAddSet }] = useDisclosure(false)
  const [addTestSet, setAddTestSet] = useState<string | null>(null)
  const [genJobId, setGenJobId] = useState<string | null>(null)
  const [activeDragId, setActiveDragId] = useState<string | null>(null)

  const qc = useQueryClient()

  const handleGenDone = useCallback(
    (job: JobStatus) => {
      setGenJobId(null)
      if (job.status === 'done') {
        qc.invalidateQueries({ queryKey: ['tests', problem.slug] })
        notifications.show({ message: 'Tests generated', color: 'green' })
      } else {
        notifications.show({
          message: `Generation failed${job.error ? `: ${job.error}` : ''}`,
          color: 'red',
        })
      }
    },
    [qc, problem.slug],
  )

  useJobPoller(genJobId, { onDone: handleGenDone })

  const { data: testSets, isLoading, isError } = useQuery({
    queryKey: ['tests', problem.slug],
    queryFn: () => getTestSets(problem.slug),
    retry: false,
  })

  const { data: testContent, isLoading: contentLoading, isError: contentError } = useQuery({
    queryKey: ['test-content', problem.slug, selected?.setName, selected?.testName],
    queryFn: () => getTestContent(problem.slug, selected!.setName, selected!.testName),
    enabled: !!selected,
    retry: false,
  })

  const { mutate: generate } = useMutation({
    mutationFn: (params: { setName: string; genName: string }) =>
      generateTests(problem.slug, params.setName, params.genName),
    onSuccess: (data) => {
      setGenJobId(data.job_ids[0])
      notifications.show({ message: 'Generation started…', color: 'blue' })
    },
    onError: () =>
      notifications.show({ message: 'Test generation not yet implemented', color: 'orange' }),
  })

  const { mutate: generateAll, isPending: generateAllPending } = useMutation({
    mutationFn: (requests: { test_set: string; generator_name: string }[]) =>
      generateAllTests(problem.slug, requests),
    onSuccess: (data) => {
      setGenJobId(data.job_ids[0])
      notifications.show({ message: 'Running all generators…', color: 'blue' })
    },
    onError: () =>
      notifications.show({ message: 'Test generation failed to start', color: 'red' }),
  })

  const { mutate: saveDesc } = useMutation({
    mutationFn: () =>
      updateTestCaseDescription(
        problem.slug,
        selected!.setName,
        selected!.testName,
        editDescription,
      ),
    onSuccess: () => {
      notifications.show({ message: 'Description saved', color: 'green' })
      qc.invalidateQueries({ queryKey: ['tests', problem.slug] })
    },
    onError: () =>
      notifications.show({ message: 'Description update not yet implemented', color: 'orange' }),
  })

  // Fall back to stub sets from problem.test_sets if the endpoint isn't available yet
  const serverSets: TestSetDetail[] =
    testSets ??
    problem.test_sets.map((name) => ({
      name,
      config: undefined,
      test_cases: [],
      generators: [],
    }))

  // Local ordering state — initialised from server, updated optimistically on drag
  const [localOrder, setLocalOrder] = useState<string[] | null>(null)

  // When server data arrives (or changes), reset local order to match
  const serverOrder = useMemo(() => serverSets.map((s) => s.name), [serverSets])
  const prevServerOrder = useRef<string>(JSON.stringify(serverOrder))
  useEffect(() => {
    const key = JSON.stringify(serverOrder)
    if (key !== prevServerOrder.current) {
      prevServerOrder.current = key
      setLocalOrder(null)
    }
  }, [serverOrder])

  // Build display list based on localOrder (optimistic) or server order
  const sets: TestSetDetail[] = useMemo(() => {
    if (!localOrder) return serverSets
    const byName = new Map(serverSets.map((s) => [s.name, s]))
    return localOrder.map((n) => byName.get(n)!).filter(Boolean)
  }, [localOrder, serverSets])

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }))

  const { mutate: persistOrder } = useMutation({
    mutationFn: (order: string[]) => reorderTestSets(problem.slug, order),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tests', problem.slug] }),
    onError: () => {
      setLocalOrder(null) // revert
      notifications.show({ message: 'Failed to save test set order', color: 'red' })
    },
  })

  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveDragId(event.active.id as string)
  }, [])

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      setActiveDragId(null)
      const { active, over } = event
      if (!over || active.id === over.id) return
      const currentOrder = localOrder ?? sets.map((s) => s.name)
      const oldIdx = currentOrder.indexOf(active.id as string)
      const newIdx = currentOrder.indexOf(over.id as string)
      if (oldIdx === -1 || newIdx === -1) return
      const newOrder = [...currentOrder]
      newOrder.splice(oldIdx, 1)
      newOrder.splice(newIdx, 0, active.id as string)
      setLocalOrder(newOrder)
      persistOrder(newOrder)
    },
    [localOrder, sets, persistOrder],
  )

  const handleDragCancel = useCallback(() => {
    setActiveDragId(null)
  }, [])

  const selectedTestCase = selected
    ? sets
        .find((s) => s.name === selected.setName)
        ?.test_cases.find((t) => t.name === selected.testName)
    : undefined

  const { width: sidebarWidth, onMouseDown: onDragStart } = useDraggableSidebar()

  function selectTest(setName: string, testName: string, description?: string) {
    setSelected({ setName, testName })
    setEditDescription(description ?? '')
  }

  return (
    <Box style={{ display: 'flex', height: 'calc(100vh - 260px)', overflow: 'hidden' }}>
      {/* ------------------------------------------------------------------ */}
      {/* Left panel — test set list                                          */}
      {/* ------------------------------------------------------------------ */}
      <Box
        style={{
          width: sidebarWidth,
          flexShrink: 0,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box px="md" pt="md" pb="xs">
          <Group justify="space-between">
            <Text size="sm" fw={600}>
              Test Sets
            </Text>
            <Group gap={6}>
              <Button
                size="xs"
                variant="light"
                color="violet"
                leftSection={<IconPlayerPlay size={12} />}
                loading={generateAllPending || !!genJobId}
                disabled={sets.every((s) => s.generators.length === 0)}
                onClick={() => {
                  const requests = sets.flatMap((s) =>
                    s.generators.map((g) => ({ test_set: s.name, generator_name: g.name })),
                  )
                  generateAll(requests)
                }}
              >
                Run All Generators
              </Button>
              <Button
                size="xs"
                variant="light"
                leftSection={<IconPlus size={12} />}
                onClick={openAddSet}
              >
                Add Set
              </Button>
            </Group>
          </Group>
        </Box>

        {isLoading && (
          <Box p="md">
            <Loader size="xs" />
          </Box>
        )}

        {isError && (
          <Box px="md" pb="xs">
            <Alert icon={<IconAlertTriangle size={14} />} color="orange" p="xs">
              Could not load test details. Showing set names only.
            </Alert>
          </Box>
        )}

        <ScrollArea style={{ flex: 1 }}>
          <Box px="md" pb="md">
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragStart={handleDragStart}
              onDragEnd={handleDragEnd}
              onDragCancel={handleDragCancel}
            >
              <SortableContext items={sets.map((s) => s.name)} strategy={verticalListSortingStrategy}>
                <Accordion
                  multiple
                  defaultValue={[]}
                  variant="contained"
                  radius="sm"
                >
                  {sets.map((set) => (
                    <SortableTestSetItem
                      key={set.name}
                      set={set}
                      selected={selected}
                      genJobId={genJobId}
                      problem={problem}
                      generate={generate}
                      selectTest={selectTest}
                      setAddTestSet={setAddTestSet}
                      openGeneratorInEditor={openGeneratorInEditor}
                      openTestCaseInEditor={openTestCaseInEditor}
                    />
                  ))}
                </Accordion>
              </SortableContext>
              <DragOverlay dropAnimation={null}>
                {activeDragId
                  ? (() => {
                      const dragSet = sets.find((s) => s.name === activeDragId)
                      return dragSet ? <TestSetDragPreview set={dragSet} /> : null
                    })()
                  : null}
              </DragOverlay>
            </DndContext>
          </Box>
        </ScrollArea>
      </Box>

      {/* Drag handle */}
      <Box
        onMouseDown={onDragStart}
        style={{
          width: 5,
          flexShrink: 0,
          cursor: 'col-resize',
          background: 'var(--mantine-color-gray-2)',
          transition: 'background 150ms',
        }}
        onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = 'var(--mantine-color-blue-3)' }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = 'var(--mantine-color-gray-2)' }}
      />

      {/* ------------------------------------------------------------------ */}
      {/* Right panel — test content viewer                                   */}
      {/* ------------------------------------------------------------------ */}
      <Box
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
        p="md"
      >
        {!selected ? (
          <Box
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
            }}
          >
            <Text c="dimmed" size="sm">
              Click a test case to view its input
            </Text>
          </Box>
        ) : (
          <Stack gap="sm" style={{ height: '100%', overflow: 'hidden' }}>
            <Group justify="space-between">
              <Text size="sm" fw={600} style={{ fontFamily: 'monospace' }}>
                {selected.setName}/{selected.testName}.in
              </Text>
              <Group gap={6}>
                {selectedTestCase?.description && (
                  <Text size="xs" c="dimmed">
                    {selectedTestCase.description}
                  </Text>
                )}
                <Tooltip label="Open in Cursor">
                  <ActionIcon
                    size="xs"
                    variant="subtle"
                    onClick={() => openTestCaseInEditor(problem.slug, selected.setName, selected.testName)}
                  >
                    <IconCode size={12} />
                  </ActionIcon>
                </Tooltip>
              </Group>
            </Group>

            <ScrollArea style={{ flex: 1, minHeight: 0 }}>
              {contentLoading && <Loader size="sm" />}
              {contentError && (
                <Alert
                  icon={<IconAlertTriangle size={14} />}
                  color="orange"
                  p="xs"
                >
                  Test content not yet loadable (API pending)
                </Alert>
              )}
              {testContent && (
                <Code
                  block
                  style={{
                    fontFamily: 'monospace',
                    whiteSpace: 'pre',
                    fontSize: 13,
                    lineHeight: 1.5,
                  }}
                >
                  {testContent.content}
                </Code>
              )}
            </ScrollArea>

            <Box>
              <Text size="xs" c="dimmed" mb={4} fw={500}>
                Description
              </Text>
              <Textarea
                size="xs"
                placeholder="Add a note about this test case…"
                value={editDescription}
                onChange={(e) => setEditDescription(e.currentTarget.value)}
                autosize
                minRows={2}
                maxRows={4}
                onBlur={() => {
                  if (editDescription !== (selectedTestCase?.description ?? '')) {
                    saveDesc()
                  }
                }}
              />
            </Box>
          </Stack>
        )}
      </Box>

      {/* ------------------------------------------------------------------ */}
      {/* Modals                                                               */}
      {/* ------------------------------------------------------------------ */}
      <AddTestSetModal
        opened={addSetOpen}
        onClose={closeAddSet}
        slug={problem.slug}
        onAdded={() => qc.invalidateQueries({ queryKey: ['tests', problem.slug] })}
      />

      {addTestSet && (
        <AddTestModal
          opened
          onClose={() => setAddTestSet(null)}
          slug={problem.slug}
          setName={addTestSet}
          onAdded={() => qc.invalidateQueries({ queryKey: ['tests', problem.slug] })}
        />
      )}
    </Box>
  )
}
