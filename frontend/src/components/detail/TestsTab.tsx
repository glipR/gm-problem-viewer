import { useState } from 'react'
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
} from '@tabler/icons-react'
import type { Problem, TestSetDetail } from '../../types/problem'
import {
  getTestSets,
  getTestContent,
  generateTests,
  createTestSet,
  createTestCase,
  updateTestCaseDescription,
} from '../../api/problems'

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
// Main TestsTab
// ---------------------------------------------------------------------------

export default function TestsTab({ problem }: Props) {
  const [selected, setSelected] = useState<SelectedTest | null>(null)
  const [editDescription, setEditDescription] = useState('')
  const [addSetOpen, { open: openAddSet, close: closeAddSet }] = useDisclosure(false)
  const [addTestSet, setAddTestSet] = useState<string | null>(null)

  const qc = useQueryClient()

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
    onSuccess: () => notifications.show({ message: 'Generation started', color: 'blue' }),
    onError: () =>
      notifications.show({ message: 'Test generation not yet implemented', color: 'orange' }),
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
  const sets: TestSetDetail[] =
    testSets ??
    problem.test_sets.map((name) => ({
      name,
      config: undefined,
      test_cases: [],
      generators: [],
    }))

  const selectedTestCase = selected
    ? sets
        .find((s) => s.name === selected.setName)
        ?.test_cases.find((t) => t.name === selected.testName)
    : undefined

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
          width: 320,
          flexShrink: 0,
          borderRight: '1px solid var(--mantine-color-gray-2)',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box px="md" pt="md" pb="xs">
          <Group justify="space-between">
            <Text size="sm" fw={600}>
              Test Sets
            </Text>
            <Button
              size="xs"
              variant="light"
              leftSection={<IconPlus size={12} />}
              onClick={openAddSet}
            >
              Add Set
            </Button>
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
            <Accordion
              multiple
              defaultValue={sets.map((s) => s.name)}
              variant="contained"
              radius="sm"
            >
              {sets.map((set) => (
                <Accordion.Item key={set.name} value={set.name}>
                  <Accordion.Control py="xs">
                    <Group justify="space-between" wrap="nowrap" pr="xs">
                      <Group gap={6} wrap="nowrap">
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
                          <Tooltip label={`Run ${gen.name}`}>
                            <ActionIcon
                              size="xs"
                              variant="subtle"
                              color="violet"
                              onClick={() =>
                                generate({ setName: set.name, genName: gen.name })
                              }
                            >
                              <IconPlayerPlay size={10} />
                            </ActionIcon>
                          </Tooltip>
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
                            onClick={() =>
                              selectTest(set.name, tc.name, tc.description)
                            }
                          >
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
                              style={{ fontFamily: 'monospace', minWidth: 0 }}
                              truncate
                              c={isSelected ? 'blue' : undefined}
                            >
                              {tc.name}
                            </Text>
                            {tc.description && (
                              <Text size="xs" c="dimmed" truncate style={{ opacity: 0.7 }}>
                                {tc.description}
                              </Text>
                            )}
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
              ))}
            </Accordion>
          </Box>
        </ScrollArea>
      </Box>

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
              {selectedTestCase?.description && (
                <Text size="xs" c="dimmed">
                  {selectedTestCase.description}
                </Text>
              )}
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
