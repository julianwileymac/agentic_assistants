"use client";

import * as React from "react";
import { EnhancedLogsPanel } from "@/components/logs";
import { CopilotChat } from "@/components/copilot";
import { ScrollText, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";

export function FloatingActions() {
  const [copilotOpen, setCopilotOpen] = React.useState(false);

  return (
    <>
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
        <EnhancedLogsPanel
          trigger={
            <Button
              variant="outline"
              size="icon"
              className="size-12 rounded-full shadow-lg hover:shadow-xl transition-shadow"
            >
              <ScrollText className="size-5" />
            </Button>
          }
        />
        <Button
          variant="outline"
          size="icon"
          className="size-12 rounded-full shadow-lg hover:shadow-xl transition-shadow"
          onClick={() => setCopilotOpen(true)}
        >
          <MessageSquare className="size-5" />
        </Button>
      </div>
      <CopilotChat open={copilotOpen} onOpenChange={setCopilotOpen} />
    </>
  );
}
