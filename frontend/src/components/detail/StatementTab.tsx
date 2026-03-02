import { useState } from 'react'
import { Box, Button, Group, Loader, Alert } from '@mantine/core'
import { IconBrain, IconAlertTriangle, IconCode } from '@tabler/icons-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useMutation } from '@tanstack/react-query'
import { getStatement, openStatementInEditor, reviewStatement } from '../../api/problems'
import ProblemMarkdown from './ProblemMarkdown'
import { AiReviewDialog } from './AiReviewDialog'

interface Props {
  slug: string
}

export default function StatementTab({ slug }: Props) {
  const queryClient = useQueryClient()
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['statement', slug],
    queryFn: () => getStatement(slug),
    retry: false,
  })

  const [reviewJobId, setReviewJobId] = useState<string | null>(null)

  const { mutate: startReview, isPending: reviewPending } = useMutation({
    mutationFn: () => reviewStatement(slug),
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
          onClick={() => openStatementInEditor(slug)}
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
          checkNames={['Statement Spelling']}
          onClose={() => {
            setReviewJobId(null)
            queryClient.invalidateQueries({ queryKey: ['statement', slug] })
          }}
        />
      )}

      {isLoading && <Loader size="sm" />}

      {isError && (
        <Alert
          icon={<IconAlertTriangle size={16} />}
          color="orange"
          title="Statement unavailable"
          maw={500}
        >
          {status === 501
            ? 'Statement endpoint not yet implemented.'
            : status === 404
              ? 'No statement.md found for this problem.'
              : 'Failed to load statement.'}
        </Alert>
      )}

      {data && (
        <ProblemMarkdown slug={slug}>{data.raw}</ProblemMarkdown>
      )}
    </Box>
  )
}
