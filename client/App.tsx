import * as React from "react";

import QBOConnection from "./QBOConnection";
import StripeConnection from "./StripeConnection";
import SyncSettings from "./settings/SyncSettings";
import Sync from "./Sync";

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
      <div className="flex items-center justify-between bg-green-300 p-4">
        <h1 className="font-semibold text-xl">Stripe 2 QBO</h1>
      </div>
      <div className="p-6">
        <div className="flex justify-between">
          <div>
            <StripeConnection />
            <QBOConnection />
            <SyncSettings isConnected={qboConnected} />
          </div>
          <div className="basis-3/4">
            <Sync />
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
