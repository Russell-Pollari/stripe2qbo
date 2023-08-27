import * as React from "react";

import QBOConnection from "./QBOConnection";
import StripeConnection from "./StripeConnection";
import SyncSettings from "./settings/SyncSettings";

const App = () => {
  const [qboConnected, setQBOConnected] = React.useState(false);

  React.useEffect(() => {
    fetch("/qbo/info")
      .then((res) => res.json())
      .then((data) => {
        if (data.CompanyName) {
          setQBOConnected(true);
        }
      });
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between flex-wrap bg-green-300 p-4">
        <h1 className="font-semibold text-xl">Stripe 2 QBO</h1>
      </div>
      <div className="container mx-auto p-6">
        <div className="p-6 flex justify-around flex-wrap">
          <div>
            <StripeConnection />
            <div className="text-center mt-4 mb-4">
              <button
                className="inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                onClick={() => {
                  fetch("/sync")
                    .then((res) => res.json())
                    .then((data) => {
                      console.log(data);
                    });
                }}
              >
                Sync transactions
              </button>
            </div>
            <QBOConnection />
          </div>
          {qboConnected && <SyncSettings />}
        </div>
      </div>
    </div>
  );
};

export default App;
