"use client";

import { Sandpack } from "@codesandbox/sandpack-react";

export default function PreviewPane() {
  return (
    <div className="h-full w-full flex flex-col">
      <div className="bg-gray-900 text-green-500 text-xs p-2 border-b border-green-900 font-mono">
        👁️ SANDPACK_PREVIEW // RUNTIME: WASM
      </div>
      <div className="flex-1 overflow-hidden">
        <Sandpack 
          template="react"
          theme="dark"
          options={{
            showNavigator: true,
            showLineNumbers: true,
            showInlineErrors: true,
            wrapContent: true,
            editorHeight: "100%", 
            editorWidthPercentage: 0, // Hide editor, just show preview
          }}
        />
      </div>
    </div>
  );
}
