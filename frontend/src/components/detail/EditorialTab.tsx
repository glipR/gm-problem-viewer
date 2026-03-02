import { useState } from 'react'
import { Box, Button, Group, Loader, Alert } from '@mantine/core'
import { IconBrain, IconAlertTriangle, IconCode } from '@tabler/icons-react'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import { getEditorial, openEditorialInEditor, reviewEditorial } from '../../api/problems'
import ProblemMarkdown, { editorialComponents } from './ProblemMarkdown'
import { AiReviewDialog } from './AiReviewDialog'

interface Props {
  slug: string
}

export default function EditorialTab({ slug }: Props) {
  const queryClient = useQueryClient()
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['editorial', slug],
    queryFn: () => getEditorial(slug),
    retry: false,
  })

  const [reviewJobId, setReviewJobId] = useState<string | null>(null)

  const { mutate: startReview, isPending: reviewPending } = useMutation({
    mutationFn: () => reviewEditorial(slug),
    onSuccess: (data) => setReviewJobId(data.job_ids[0]),
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
        <Button
          size="xs"
          variant="light"
          color="violet"
          leftSection={<IconBrain size={14} />}
          loading={reviewPending}
          onClick={() => startReview()}
        >
          Review with Claude
        </Button>
      </Group>

      {reviewJobId && (
        <AiReviewDialog
          jobId={reviewJobId}
          slug={slug}
          checkNames={['Editorial Spelling']}
          onClose={() => {
            setReviewJobId(null)
            queryClient.invalidateQueries({ queryKey: ['editorial', slug] })
          }}
        />
      )}

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
