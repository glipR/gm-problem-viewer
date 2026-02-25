import { Group, Stack, Text, Tooltip } from '@mantine/core'
import {
  IconFileText,
  IconCode,
  IconShield,
  IconDatabase,
} from '@tabler/icons-react'
import type { Problem, CategoryResult } from '../../types/problem'

interface Props {
  problem: Problem
  byCategory?: Record<string, CategoryResult> | null
}

export default function FacetIcons({ problem, byCategory }: Props) {
  const hasStatement = true // always assumed present
  const hasSolutions = problem.solutions.length > 0
  const hasValidators = problem.validators.input.length > 0
  const hasTests = problem.test_sets.length > 0

  function iconColor(cat: string, present: boolean): string {
    const r = byCategory?.[cat]
    if (r) return r.color
    return present ? 'teal' : 'gray'
  }

  function iconLabel(cat: string, fallback: string): React.ReactNode {
    const r = byCategory?.[cat]
    if (r && r.issues.length > 0) {
      return (
        <Stack gap={1}>
          {r.issues.map((issue, i) => (
            <Text key={i} size="xs">• {issue}</Text>
          ))}
        </Stack>
      )
    }
    return fallback
  }

  return (
    <Group gap={6}>
      <Tooltip label={iconLabel('statement', 'Statement')} withArrow multiline maw={240}>
        <IconFileText size={16} color={`var(--mantine-color-${iconColor('statement', hasStatement)}-6)`} />
      </Tooltip>
      <Tooltip label={iconLabel('solution', 'Solutions')} withArrow multiline maw={240}>
        <IconCode size={16} color={`var(--mantine-color-${iconColor('solution', hasSolutions)}-6)`} />
      </Tooltip>
      <Tooltip label={iconLabel('validator', 'Validators')} withArrow multiline maw={240}>
        <IconShield size={16} color={`var(--mantine-color-${iconColor('validator', hasValidators)}-6)`} />
      </Tooltip>
      <Tooltip label={iconLabel('test', 'Tests')} withArrow multiline maw={240}>
        <IconDatabase size={16} color={`var(--mantine-color-${iconColor('test', hasTests)}-6)`} />
      </Tooltip>
    </Group>
  )
}
