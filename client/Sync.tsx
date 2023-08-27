import * as React from "react";

const Sync = () => {
  const [isSyncing, setIsSyncing] = React.useState<boolean>(false);
  const [logs, setLogs] = React.useState<string[]>([]);

  const startSync = () => {
    const ws = new WebSocket("ws://localhost:8000/sync");
    ws.onopen = () => {
      setIsSyncing(true);
    };
    ws.onmessage = (event) => {
      setLogs((logs: string) => [event.data, ...logs]);
    };
    ws.onclose = () => {
      setIsSyncing(false);
    };
  };

  return (
    <div>
      <div className="text-center mt-4 mb-4">
        <button
          onClick={startSync}
          disabled={isSyncing}
          className="inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          {isSyncing ? "Syncing..." : "Sync transactions"}
        </button>
        {logs.map((log: string, index: number) => (
          <div key={index}>{log}</div>
        ))}
      </div>
    </div>
  );
};

export default Sync;
