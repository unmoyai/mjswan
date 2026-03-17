import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Box, Collapse, Divider, Paper, Text } from '@mantine/core';
import { IconChevronDown, IconChevronUp } from '@tabler/icons-react';
import type { mjswanRuntime } from '../core/engine/runtime';

const POLL_MS = 100;
const MAX_VALS = 6;

interface ObsTerm {
  name: string;
  values: number[];
  truncated: boolean;
}

function fmt(v: number): string {
  const s = v.toFixed(3);
  return v >= 0 ? ` ${s}` : s;
}

function TermRow({ term }: { term: ObsTerm }) {
  const preview = term.values.slice(0, MAX_VALS).map(fmt).join('  ');
  return (
    <Box style={{ marginBottom: '0.35em' }}>
      <Text size="xs" c="dimmed" style={{ fontFamily: 'monospace', marginBottom: '0.1em' }}>
        {term.name}{' '}
        <span style={{ opacity: 0.5 }}>[{term.values.length}]</span>
      </Text>
      <Text size="xs" style={{ fontFamily: 'monospace', whiteSpace: 'pre', lineHeight: 1.4 }}>
        {preview}
        {term.truncated && <span style={{ opacity: 0.5 }}>  …</span>}
      </Text>
    </Box>
  );
}

interface Props {
  runtimeRef: { readonly current: mjswanRuntime | null };
}

export default function ObservationPanel({ runtimeRef }: Props) {
  const [terms, setTerms] = useState<ObsTerm[]>([]);
  const [open, setOpen] = useState(true);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const poll = useCallback(() => {
    const rt = runtimeRef.current;
    if (!rt) return;

    const layouts = rt.getObsLayouts();
    const obs = rt.getLastObservations();

    // Prefer the "monitor" group (Python-defined mdp obs) over "policy"
    const key =
      'monitor' in layouts
        ? 'monitor'
        : 'policy' in layouts
          ? 'policy'
          : Object.keys(layouts)[0];

    if (!key) return;
    const layout = layouts[key];
    const vec = obs[key];
    if (!layout || !vec) return;

    let offset = 0;
    const next: ObsTerm[] = [];
    for (const entry of layout) {
      const slice = Array.from(vec.slice(offset, offset + entry.size));
      next.push({ name: entry.name, values: slice, truncated: slice.length > MAX_VALS });
      offset += entry.size;
    }
    setTerms(next);
  }, [runtimeRef]);

  useEffect(() => {
    intervalRef.current = setInterval(poll, POLL_MS);
    return () => {
      if (intervalRef.current !== null) clearInterval(intervalRef.current);
    };
  }, [poll]);

  if (!terms.length) return null;

  return (
    <Paper
      radius="xs"
      shadow="0.1em 0 1em 0 rgba(0,0,0,0.1)"
      style={{
        position: 'absolute',
        bottom: '1em',
        right: '1em',
        width: '15em',
        zIndex: 10,
        overflow: 'hidden',
        boxSizing: 'border-box',
      }}
    >
      <Box
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 0.75em',
          height: '2.75em',
          cursor: 'pointer',
          userSelect: 'none',
        }}
        onClick={() => setOpen((v) => !v)}
      >
        <Text size="sm" fw={500}>Observations</Text>
        {open ? <IconChevronDown size={14} /> : <IconChevronUp size={14} />}
      </Box>
      <Collapse in={open}>
        <Divider mx="xs" />
        <Box style={{ padding: '0.6em 0.75em 0.75em', maxHeight: '22em', overflowY: 'auto' }}>
          {terms.map((t) => <TermRow key={t.name} term={t} />)}
        </Box>
      </Collapse>
    </Paper>
  );
}
