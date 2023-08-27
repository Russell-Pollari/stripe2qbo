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
      <div className="flex items-center justify-between flex-wrap bg-green-300 p-4">
        <span className="container mx-auto">
          <h1 className="font-semibold text-xl">Stripe 2 QBO</h1>
        </span>
      </div>
      <div className="container mx-auto p-6">
        <div className="p-6 flex justify-around flex-wrap">
          <div>
            <StripeConnection />
            <QBOConnection />
            <Sync />
          </div>
          <SyncSettings isConnected={qboConnected} />
        </div>
      </div>
    </div>
  );
};

export default App;
