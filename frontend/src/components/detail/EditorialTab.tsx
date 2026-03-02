import { Box, Button, Group, Loader, Alert } from '@mantine/core'
import { IconAlertTriangle, IconCode } from '@tabler/icons-react'
import { useQuery } from '@tanstack/react-query'
import { getEditorial, openEditorialInEditor } from '../../api/problems'
import ProblemMarkdown, { editorialComponents } from './ProblemMarkdown'

interface Props {
  slug: string
}

export default function EditorialTab({ slug }: Props) {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['editorial', slug],
    queryFn: () => getEditorial(slug),
    retry: false,
  })

  const status = (error as { response?: { status?: number } } | null)?.response?.status

  return (
    <Box p="xl" style={{
      maxWidth: 900,
      margin: '0 auto',
    }}>
      <Group mb="lg">
        <Button
          size="xs"
          variant="light"
          leftSection={<IconCode size={14} />}
          onClick={() => openEditorialInEditor(slug)}
        >
          Open in Cursor
        </Button>
      </Group>

      {isLoading && <Loader size="sm" />}

      {isError && (
        <Alert
          icon={<IconAlertTriangle size={16} />}
          color="orange"
          title="Editorial unavailable"
          maw={500}
        >
          {status === 404
            ? 'No editorial.md found for this problem.'
            : 'Failed to load editorial.'}
        </Alert>
      )}

      {data && (
        <ProblemMarkdown slug={slug} extraComponents={editorialComponents}>
          {data.raw}
        </ProblemMarkdown>
      )}
    </Box>
  )
}
