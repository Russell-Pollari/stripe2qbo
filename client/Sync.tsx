import * as React from "react";
import { Formik, Field, Form } from "formik";

type SyncOptions = {
  from_date: string;
  to_date: string;
};

const Sync = () => {
  const [isSyncing, setIsSyncing] = React.useState<boolean>(false);
  const [logs, setLogs] = React.useState<string[]>([]);

  const startSync = (options: SyncOptions) => {
    const queryString = new URLSearchParams(options).toString();
    const ws = new WebSocket(`ws://localhost:8000/sync?${queryString}`);
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
      <div className="shadow-lg p-4">
        <h3 className="font-semibold mb-4">Sync Transactions</h3>
        <Formik
          initialValues={{ from_date: "", to_date: "" }}
          onSubmit={(values: SyncOptions) => {
            startSync(values);
          }}
        >
          <Form>
            <div className="flex justify-between">
              <div>
                <label className="font-semibold mx-2" htmlFor="from_date">
                  From:
                </label>
                <Field id="from_date" name="from_date" type="date" />
                <label className="font-semibold mx-2" htmlFor="to_date">
                  To
                </label>
                <Field id="to_date" name="to_date" type="date" />
              </div>
              <button
                disabled={isSyncing}
                className="inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >
                {isSyncing ? "Syncing..." : "Import and sync"}
              </button>
            </div>
          </Form>
        </Formik>
      </div>

      <div className="text-left mt-4 p-4 shadow-lg">
        {logs.map((log: string, index: number) => (
          <div key={index}>{log}</div>
        ))}
      </div>
    </div>
  );
};

export default Sync;
