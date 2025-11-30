"use client"

import { Thread } from "@/components/assistant-ui/thread";
import { AssistantRuntimeProvider, AttachmentAdapter, ChatModelAdapter, useLocalRuntime } from "@assistant-ui/react";
import { useEffect, useState } from "react";

const attachmentAdapter: AttachmentAdapter = {
  accept: "image/*,application/pdf",
  async add(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const { id, url } = await response.json();
    return {
      id,
      type: file.type.startsWith("image/") ? "image" : "document",
      name: file.name,
      url,
    };
  },
  async remove(attachment) {
    await fetch(`/api/upload/${attachment.id}`, {
      method: "DELETE",
    });
  },
};

const MyModelAdapter: ChatModelAdapter = {
  async run({ messages, abortSignal }) {
    const metadata = (window as any).chatMetadata || {
      isResearchEnabled: false,
      isMemorizeEnabled: false,
    };

    const result = await fetch("/api/python", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id: localStorage.getItem("uuid"),
        messages,
        metadata: {
          isResearchEnabled: metadata.isResearchEnabled,
          isMemorizeEnabled: metadata.isMemorizeEnabled,
        },
      }),
      signal: abortSignal,
    });

    window.dispatchEvent(new Event('chatMessageSent'));

    const data = await result.json();
    return {
      content: [
        {
          type: "text",
          text: data.text,
        },
      ],
    };
  },
};

export default function Chat() {
  const runtime = useLocalRuntime(MyModelAdapter, { adapters: { attachments: attachmentAdapter } });

  const [localUuid, setLocalUuid] = useState("");

  useEffect(() => {
    let local = localStorage.getItem("uuid")
    if (local) {
      setLocalUuid(local)
    }
  })

  return (
    <main className="flex flex-col h-screen">
      <AssistantRuntimeProvider runtime={runtime}>
        <Thread />
      </AssistantRuntimeProvider>
    </main>
  );
}