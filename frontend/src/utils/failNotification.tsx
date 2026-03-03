import { Anchor, Group, Text } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { openJobInEditor } from '../api/problems'

/**
 * Show a red failure notification. When a jobId is provided, includes
 * a "View log" link that opens the cache YAML file in the editor.
 */
export function showFailNotification(message: string, jobId?: string) {
  notifications.show({
    color: 'red',
    message: jobId ? (
      <Group gap="xs">
        <Text size="sm">{message}</Text>
        <Anchor
          size="sm"
          component="button"
          onClick={() => openJobInEditor(jobId)}
        >
          View log
        </Anchor>
      </Group>
    ) : message,
  })
}
