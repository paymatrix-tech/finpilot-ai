export type ParsedSseEvent = {
  event: string;
  data: unknown;
};

export function parseSseChunk(chunk: string): ParsedSseEvent[] {
  const events: ParsedSseEvent[] = [];
  const blocks = chunk.split("\n\n").filter((block) => block.trim().length > 0);

  for (const block of blocks) {
    let event = "message";
    const dataLines: string[] = [];

    for (const line of block.split("\n")) {
      if (line.startsWith("event:")) {
        event = line.slice("event:".length).trim();
      } else if (line.startsWith("data:")) {
        dataLines.push(line.slice("data:".length).trim());
      }
    }

    if (dataLines.length === 0) {
      continue;
    }

    const raw = dataLines.join("\n");
    try {
      events.push({ event, data: JSON.parse(raw) as unknown });
    } catch {
      events.push({ event, data: raw });
    }
  }

  return events;
}

export async function readSseStream(
  response: Response,
  onEvent: (event: ParsedSseEvent) => void,
): Promise<void> {
  if (!response.body) {
    throw new Error("Streaming response has no body.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      for (const parsed of parseSseChunk(part + "\n\n")) {
        onEvent(parsed);
      }
    }
  }

  if (buffer.trim()) {
    for (const parsed of parseSseChunk(buffer)) {
      onEvent(parsed);
    }
  }
}
